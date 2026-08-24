"""
P2 - Accesibilidad cromatica en sitios web universitarios
05_figures.py

Las 4 figuras de la ficha (seccion 6):
  Fig. 1: histograma de ratios de contraste, con lineas en 3:1, 4.5:1, 7:1.
  Fig. 2: barras horizontales de % cumplimiento AA por pais, ordenado.
  Fig. 3 (la que sostiene el argumento): dispersion de los pares
         fallidos en el plano a*b* de CIELAB, L* como tamano de punto.
  Fig. 4: panel de 4 capturas ilustrando patrones de fallo frecuentes.
         NOTA: capturas reales, SIN anonimizar todavia -- la revision
         de que no muestren datos identificables sensibles (mas alla
         del propio dominio publico de la universidad) es tarea de
         Fase 2 (figuras finales), no de este script.
"""

from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from figures_style import COLORS, apply_style, save_figure

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"
FIG_DIR = Path(__file__).resolve().parent.parent / "results" / "figures"
SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "screenshots"


def fig1_histograma(df):
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.hist(df["contrast_ratio"].clip(upper=15), bins=60, color=COLORS["secondary"], edgecolor="white", linewidth=0.3)
    for thresh, label in [(3, "3:1"), (4.5, "4.5:1"), (7, "7:1")]:
        ax.axvline(thresh, color=COLORS["primary"], linestyle="--", linewidth=1.2)
        ax.text(thresh, ax.get_ylim()[1] * 0.95, label, rotation=90, va="top", ha="right", fontsize=8, color=COLORS["primary"])
    ax.set_xlabel("Ratio de contraste WCAG")
    ax.set_ylabel("Número de pares de color")
    ax.set_title("Fig. 1 — Distribución de ratios de contraste (41,360 pares)")
    save_figure(fig, FIG_DIR / "fig1_histograma_contraste")
    plt.close(fig)


def fig2_cumplimiento_por_pais(agg):
    by_country = agg.groupby("country").agg(
        pct_cumple=("pct_falla_aa", lambda s: 100 - s.mean()), n=("site_id", "count")
    ).query("n >= 3").sort_values("pct_cumple")

    fig, ax = plt.subplots(figsize=(8, max(5, len(by_country) * 0.32)))
    ax.barh(by_country.index, by_country["pct_cumple"], color=COLORS["primary"])
    ax.set_xlabel("% medio de pares que cumplen AA por sitio")
    ax.set_title("Fig. 2 — Cumplimiento AA por país (≥3 sitios)")
    save_figure(fig, FIG_DIR / "fig2_cumplimiento_por_pais")
    plt.close(fig)


def fig3_dispersion_cielab(fallidos):
    fig, ax = plt.subplots(figsize=(8, 7))
    sizes = 8 + (fallidos["L_text"] / fallidos["L_text"].max()) * 60
    scatter = ax.scatter(fallidos["a_text"], fallidos["b_text"], s=sizes, c=fallidos["cluster"],
                          cmap="tab10", alpha=0.5, edgecolors="none")
    ax.axhline(0, color="grey", linewidth=0.5)
    ax.axvline(0, color="grey", linewidth=0.5)
    ax.set_xlabel("a* (verde ↔ rojo)")
    ax.set_ylabel("b* (azul ↔ amarillo)")
    ax.set_title("Fig. 3 — Pares fallidos en el plano a*b* de CIELAB\n(tamaño = L*, color = clúster)")
    save_figure(fig, FIG_DIR / "fig3_dispersion_cielab")
    plt.close(fig)


def fig4_capturas_ejemplo(agg):
    worst = agg.sort_values("pct_falla_aa", ascending=False)
    chosen = []
    for _, row in worst.iterrows():
        path = SCREENSHOTS_DIR / f"{row['site_id']}.png"
        if path.exists():
            chosen.append((row["site_id"], row["country"], path))
        if len(chosen) == 4:
            break

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    for ax, (site_id, country, path) in zip(axes.flat, chosen):
        img = mpimg.imread(path)
        h = img.shape[0]
        ax.imshow(img[: min(h, 900), :, :])  # recorte a la parte superior visible
        ax.set_title(f"{site_id} ({country})", fontsize=9)
        ax.axis("off")

    fig.suptitle("Fig. 4 — Ejemplos de sitios con mayor tasa de fallo\n(capturas de portadas públicas institucionales, sin datos personales de estudiantes)", fontsize=10)
    save_figure(fig, FIG_DIR / "fig4_capturas_ejemplo")
    plt.close(fig)


def main():
    apply_style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RESULTS_DIR / "pares_clasificados.csv")
    agg = pd.read_csv(RESULTS_DIR / "agregado_por_sitio.csv")
    fallidos = pd.read_csv(RESULTS_DIR / "fallidos_clusters.csv")

    fig1_histograma(df)
    print("Fig. 1 lista")
    fig2_cumplimiento_por_pais(agg)
    print("Fig. 2 lista")
    fig3_dispersion_cielab(fallidos)
    print("Fig. 3 lista")
    fig4_capturas_ejemplo(agg)
    print("Fig. 4 lista")

    print(f"\nCompletado: 4 figuras guardadas en {FIG_DIR}")


if __name__ == "__main__":
    main()
