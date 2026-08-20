"""
P2 - Accesibilidad cromatica en sitios web universitarios
04_stats.py

  - Chi-cuadrado de independencia entre cumplimiento y pais (SUSTITUYE
    "tipo de institucion" de la ficha: no se pudo clasificar
    publica/privada de forma confiable con los datos disponibles del
    dataset abierto de universidades; el pais si esta disponible para
    los 278 sitios y es la variable categorica mas cercana).
  - Regresion logistica sobre probabilidad de fallo (pais + tamano de
    fuente + si es texto grande), con corrección de continuidad en el
    chi-cuadrado y V de Cramer como tamano del efecto.
  - Agrupamiento (KMeans) de los pares fallidos en el plano a*b* de
    CIELAB del color de TEXTO (el color activamente elegido por quien
    diseño el sitio).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import chi2_contingency
from sklearn.cluster import KMeans

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"
SEED = 42


def cramers_v(chi2, n, r, k):
    return np.sqrt((chi2 / n) / (min(r - 1, k - 1)))


def main():
    df = pd.read_csv(RESULTS_DIR / "pares_clasificados.csv")
    df["cumple_aa"] = df["clasificacion"] != "falla"

    # --- Chi-cuadrado: cumplimiento x pais ---
    # Solo paises con suficientes pares para que el chi2 sea valido
    counts_per_country = df["country"].value_counts()
    valid_countries = counts_per_country[counts_per_country >= 30].index
    sub = df[df.country.isin(valid_countries)]

    contingency = pd.crosstab(sub["country"], sub["cumple_aa"])
    chi2, p, dof, expected = chi2_contingency(contingency, correction=True)
    v = cramers_v(chi2, contingency.values.sum(), *contingency.shape)

    print("=== Chi-cuadrado: cumplimiento AA × país ===")
    print(f"chi2={chi2:.2f}  dof={dof}  p={p:.6f}  V de Cramér={v:.3f}")
    print(f"(países incluidos, ≥30 pares: {list(valid_countries)})")
    contingency.to_csv(RESULTS_DIR / "tabla_contingencia_pais.csv")

    # --- Regresion logistica ---
    reg_df = sub.copy()
    reg_df["falla"] = (reg_df["clasificacion"] == "falla").astype(int)
    reg_df["country"] = reg_df["country"].astype("category")

    model = smf.logit("falla ~ C(country) + font_size_px + es_texto_grande", data=reg_df).fit(disp=0)
    print("\n=== Regresión logística: P(falla) ===")
    print(model.summary().tables[1])
    with open(RESULTS_DIR / "regresion_logistica_resumen.txt", "w", encoding="utf-8") as f:
        f.write(str(model.summary()))

    or_table = pd.DataFrame({
        "odds_ratio": np.exp(model.params),
        "ci_lower": np.exp(model.conf_int()[0]),
        "ci_upper": np.exp(model.conf_int()[1]),
        "p_valor": model.pvalues,
    })
    or_table.to_csv(RESULTS_DIR / "odds_ratios.csv")

    # --- Agrupamiento CIELAB de los pares fallidos (color de texto) ---
    fallidos = df[df.clasificacion == "falla"].dropna(subset=["a_text", "b_text", "L_text"])
    print(f"\n=== Agrupamiento CIELAB de {len(fallidos)} pares fallidos ===")

    best_k, best_score = 2, -1
    from sklearn.metrics import silhouette_score
    for k in range(2, 7):
        km = KMeans(n_clusters=k, random_state=SEED, n_init=10).fit(fallidos[["a_text", "b_text"]])
        score = silhouette_score(fallidos[["a_text", "b_text"]], km.labels_)
        print(f"  k={k}: silhouette={score:.3f}")
        if score > best_score:
            best_k, best_score = k, score

    km = KMeans(n_clusters=best_k, random_state=SEED, n_init=10).fit(fallidos[["a_text", "b_text"]])
    fallidos = fallidos.copy()
    fallidos["cluster"] = km.labels_
    fallidos.to_csv(RESULTS_DIR / "fallidos_clusters.csv", index=False)

    print(f"\nMejor k={best_k} (silhouette={best_score:.3f})")
    print(fallidos.groupby("cluster")[["L_text", "a_text", "b_text"]].mean().round(1))

    print(f"\nCompletado: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
