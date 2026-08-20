"""
P2 - Accesibilidad cromatica en sitios web universitarios
03_experiment.py

Clasifica cada par de color en falla / AA / AAA segun el tamano de
fuente (ficha tecnica, seccion 4): el umbral WCAG es mas laxo para
texto grande (>=18pt / 24px, o >=14pt/18.66px en negrita).

Agrega por sitio: mediana de ratio, % de pares que fallan AA, % de
sitios con al menos un fallo critico (ficha, seccion 5).
"""

from pathlib import Path

import numpy as np
import pandas as pd

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"

LARGE_TEXT_PX = 24.0  # ~18pt
LARGE_BOLD_TEXT_PX = 18.66  # ~14pt bold


def is_large_text(row) -> bool:
    if row["font_size_px"] >= LARGE_TEXT_PX:
        return True
    try:
        weight = float(row["font_weight"])
    except (ValueError, TypeError):
        weight = 700 if row["font_weight"] == "bold" else 400
    return row["font_size_px"] >= LARGE_BOLD_TEXT_PX and weight >= 700


def classify(row) -> str:
    large = is_large_text(row)
    aa_threshold = 3.0 if large else 4.5
    aaa_threshold = 4.5 if large else 7.0
    if row["contrast_ratio"] < aa_threshold:
        return "falla"
    if row["contrast_ratio"] < aaa_threshold:
        return "AA"
    return "AAA"


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROC_DIR / "color_pairs.csv")
    axe = pd.read_csv(PROC_DIR / "axe_results.csv")

    df["es_texto_grande"] = df.apply(is_large_text, axis=1)
    df["clasificacion"] = df.apply(classify, axis=1)
    df.to_csv(RESULTS_DIR / "pares_clasificados.csv", index=False)

    print(f"{len(df)} pares de color de {df['site_id'].nunique()} sitios")
    print(f"\nDistribución de clasificación:\n{df['clasificacion'].value_counts(normalize=True).round(3)}")

    # --- Agregacion por sitio ---
    agg = df.groupby(["site_id", "country"]).agg(
        n_pares=("contrast_ratio", "size"),
        mediana_ratio=("contrast_ratio", "median"),
        pct_falla_aa=("clasificacion", lambda s: (s == "falla").mean() * 100),
        tiene_fallo_critico=("clasificacion", lambda s: (s == "falla").any()),
    ).reset_index()
    agg = agg.merge(axe, on="site_id", how="left")

    print(f"\n% de sitios con al menos un fallo crítico: {agg['tiene_fallo_critico'].mean()*100:.1f}%")
    print(f"Mediana de % de fallas AA por sitio: {agg['pct_falla_aa'].median():.1f}%")

    agg.to_csv(RESULTS_DIR / "agregado_por_sitio.csv", index=False)

    # --- Validacion cruzada con axe-core ---
    valid = agg.dropna(subset=["axe_color_contrast_violations"])
    if len(valid) > 5:
        corr = valid["pct_falla_aa"].corr(valid["axe_color_contrast_violations"] /
                                            (valid["axe_color_contrast_violations"] + valid["axe_color_contrast_passes"]) * 100)
        print(f"\nCorrelación entre % fallas propio y % violaciones axe-core: {corr:.3f}")

    print(f"\nCompletado: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
