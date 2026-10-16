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
PAPER_FIG_DIR = Path(__file__).resolve().parent.parent / "paper" / "figures"
PAPER_FIG_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "screenshots"


def fig1_histograma(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["contrast_ratio"], bins=60, range=(1, 21), color=COLORS["secondary"], edgecolor="white", linewidth=0.3)
    ax.set_xlim(1, 21)
    for thresh, label in [(3, "3:1"), (4.5, "4.5:1"), (7, "7:1")]:
        ax.axvline(thresh, color=COLORS["primary"], linestyle="--", linewidth=1.2)
        ax.text(thresh, ax.get_ylim()[1] * 0.95, label, rotation=90, va="top", ha="right", fontsize=8, color=COLORS["primary"])
    ax.set_xlabel("WCAG Contrast Ratio")
    ax.set_ylabel("Number of Colour Pairs")
    save_figure(fig, FIG_DIR / "fig1_histograma_contraste")
    save_figure(fig, PAPER_FIG_DIR / "fig1_histograma_contraste")
    plt.close(fig)


def fig2_cumplimiento_por_pais(agg):
    by_country = agg.groupby("country").agg(
        pct_cumple=("pct_falla_aa", lambda s: 100 - s.mean()), n=("site_id", "count")
    ).query("n >= 3").sort_values("pct_cumple")

    fig, ax = plt.subplots(figsize=(7.5, max(4.5, len(by_country) * 0.3)))
    ax.barh(by_country.index, by_country["pct_cumple"], color=COLORS["primary"])
    ax.set_xlabel("Mean AA Compliance Rate per Website (%)")
    ax.set_ylabel("Country")
    save_figure(fig, FIG_DIR / "fig2_cumplimiento_por_pais")
    save_figure(fig, PAPER_FIG_DIR / "fig2_cumplimiento_por_pais")
    plt.close(fig)


def fig3_dispersion_cielab(fallidos):
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    sizes = 8 + (fallidos["L_text"] / fallidos["L_text"].max()) * 60
    okabe_ito = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2"]
    markers = ["o", "s", "^", "D", "v", "P"]
    for i in range(6):
        cluster_mask = fallidos["cluster"] == i
        ax.scatter(fallidos.loc[cluster_mask, "a_text"], fallidos.loc[cluster_mask, "b_text"], 
                   s=sizes[cluster_mask], c=okabe_ito[i], marker=markers[i], alpha=0.6, edgecolors="none")
    ax.axhline(0, color="grey", linewidth=0.5)
    ax.axvline(0, color="grey", linewidth=0.5)
    ax.set_xlabel(r"$a^*$ (Green $\leftrightarrow$ Red)")
    ax.set_ylabel(r"$b^*$ (Blue $\leftrightarrow$ Yellow)")
    save_figure(fig, FIG_DIR / "fig3_dispersion_cielab")
    save_figure(fig, PAPER_FIG_DIR / "fig3_dispersion_cielab")
    plt.close(fig)


def fig4_capturas_ejemplo(agg):
    from PIL import Image, ImageFilter
    worst = agg.sort_values("pct_falla_aa", ascending=False)
    chosen = []
    for _, row in worst.iterrows():
        path = SCREENSHOTS_DIR / f"{row['site_id']}.png"
        if path.exists():
            chosen.append((row["site_id"], row["country"], row["pct_falla_aa"], path))
        if len(chosen) == 4:
            break

    labels = ["A", "B", "C", "D"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax, (site_id, country, pct, path), label in zip(axes.flat, chosen, labels):
        pil_img = Image.open(path).convert("RGB")
        w, h = pil_img.size
        # Anonymize institutional header bar (blur top 200px)
        header_h = 200
        header_crop = pil_img.crop((0, 0, w, header_h))
        blurred_header = header_crop.filter(ImageFilter.GaussianBlur(radius=35))
        pil_img.paste(blurred_header, (0, 0))

        if site_id == "U0035":
            # Anonymize central popups/banners (like UERJ 75 anos) in the first viewport
            center_crop = pil_img.crop((300, 200, 1100, 800))
            blurred_center = center_crop.filter(ImageFilter.GaussianBlur(radius=50))
            pil_img.paste(blurred_center, (300, 200))

        arr = np.array(pil_img)
        ax.imshow(arr[: min(arr.shape[0], 900), :])
        ax.axis("off")

    save_figure(fig, FIG_DIR / "fig4_capturas_ejemplo")
    save_figure(fig, PAPER_FIG_DIR / "fig4_capturas_ejemplo")
    plt.close(fig)


def fig4_pares_frecuentes():
    """Fig. 4: muestras renderizadas de los pares de colores que mas fallan (Tabla 3, top10_pares_frecuentes.csv).

    Reemplaza al panel de capturas (fig4_capturas_ejemplo): el desenfoque necesario para anonimizar las
    portadas tapaba justamente el texto con falla, y una captura dejaba visible el nombre de una institucion.
    Aqui se muestran los colores medidos tal cual, sin identificar a ningun sitio. Se omiten los pares
    blanco-sobre-blanco/gris muy claro (texto invisible, ratio < 1.2) porque no hay nada que mostrar.
    """
    from matplotlib.patches import Rectangle
    top = pd.read_csv(RESULTS_DIR / "top10_pares_frecuentes.csv")
    top = top[top["ratio_mediano"] >= 1.2].head(6).reset_index(drop=True)

    def hexc(rgb):
        r, g, b = [int(v) for v in rgb.strip("rgb() ").split(",")]
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

    fig, axes = plt.subplots(3, 2, figsize=(7.16, 5.4))
    for ax, (_, row) in zip(axes.flat, top.iterrows()):
        fg, bg = hexc(row["text_color"]), hexc(row["bg_color"])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        ax.add_patch(Rectangle((0, 0.38), 1, 0.62, facecolor=bg, edgecolor="#000000", linewidth=0.6))
        ax.text(0.04, 0.80, "Admissions", color=fg, fontsize=12, fontweight="bold", family="sans-serif", va="center")
        ax.text(0.04, 0.55, "Programmes · Research · News", color=fg, fontsize=9, family="sans-serif", va="center")
        ax.text(0.0, 0.20, f"{fg} on {bg}   ratio {row['ratio_mediano']:.2f}:1   n = {int(row['n'])}",
                color="#000000", fontsize=8, va="center")
        ax.text(0.0, 0.04, "fails AA for body text (needs 4.5:1)" + ("; also fails for large text (3:1)" if row["ratio_mediano"] < 3 else ""),
                color="#000000", fontsize=7.5, style="italic", va="center")
    fig.tight_layout()
    save_figure(fig, FIG_DIR / "fig4_pares_frecuentes")
    save_figure(fig, PAPER_FIG_DIR / "fig4_pares_frecuentes")
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
    fig4_pares_frecuentes()
    print("Fig. 4 lista")

    print(f"\nCompletado: 4 figuras guardadas en {FIG_DIR}")


if __name__ == "__main__":
    main()
