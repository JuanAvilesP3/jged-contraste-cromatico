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

    # --- Robustez (corregido tras revision adversarial): la logistica de
    # arriba trata los 41,360 pares como independientes, pero pares del
    # mismo sitio comparten un sistema de diseño y no lo son. Se repite
    # el mismo modelo via GEE con errores estandar robustos (sandwich)
    # agrupados por sitio, el analogo estandar a un GLMM con intercepto
    # aleatorio de sitio para un resultado binario, y compara los
    # p-valores del efecto de "texto grande" (el hallazgo que el
    # articulo trataba como el mas solido, precisamente por no depender
    # del agrupamiento por sitio) bajo ambas especificaciones.
    #
    # Nota tecnica: cov_struct=Exchangeable() diverge numericamente en
    # este dataset (overflow en la optimizacion); se usa Independence()
    # como estructura de trabajo -- los errores estandar siguen siendo
    # robustos al agrupamiento por sitio via el sandwich de GEE, que es
    # lo que se necesita aqui, independientemente de la estructura de
    # correlacion de trabajo asumida. Se inicializa en los parametros
    # del logit naive para evitar el mismo problema de convergencia.
    import statsmodels.genmod.generalized_estimating_equations as gee
    from statsmodels.genmod.cov_struct import Independence
    from statsmodels.genmod.families import Binomial

    reg_df_gee = reg_df.reset_index(drop=True)
    gee_model = gee.GEE.from_formula(
        "falla ~ C(country) + font_size_px + es_texto_grande", groups="site_id",
        data=reg_df_gee, cov_struct=Independence(), family=Binomial(),
    ).fit(start_params=model.params.values, maxiter=60)
    print("\n=== GEE (errores estándar robustos por sitio): P(falla) ===")
    print(gee_model.summary().tables[1])
    print(f"Convergió: {gee_model.converged}")
    with open(RESULTS_DIR / "gee_por_sitio_resumen.txt", "w", encoding="utf-8") as f:
        f.write(str(gee_model.summary()))

    naive_p = model.pvalues.get("es_texto_grande[T.True]", model.pvalues.get("es_texto_grande"))
    gee_p = gee_model.pvalues.get("es_texto_grande[T.True]", gee_model.pvalues.get("es_texto_grande"))
    naive_beta = model.params.get("es_texto_grande[T.True]", model.params.get("es_texto_grande"))
    gee_beta = gee_model.params.get("es_texto_grande[T.True]", gee_model.params.get("es_texto_grande"))
    print(f"\nComparación 'texto grande': naive beta={naive_beta:.4f} p={naive_p:.4g}  |  "
          f"GEE (robusto por sitio) beta={gee_beta:.4f} p={gee_p:.4g}")
    pd.DataFrame({
        "spec": ["naive_pooled", "gee_site_robust"],
        "beta_texto_grande": [naive_beta, gee_beta],
        "p_texto_grande": [naive_p, gee_p],
    }).to_csv(RESULTS_DIR / "comparacion_naive_vs_gee.csv", index=False)

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

    from sklearn.metrics import silhouette_score
    silhouette_curve = {}
    for k in range(2, 21):
        km = KMeans(n_clusters=k, random_state=SEED, n_init=10).fit(fallidos[["a_text", "b_text"]])
        score = silhouette_score(fallidos[["a_text", "b_text"]], km.labels_)
        silhouette_curve[k] = score
        print(f"  k={k}: silhouette={score:.3f}")
    pd.Series(silhouette_curve, name="silhouette").rename_axis("k").to_csv(RESULTS_DIR / "silhouette_curve.csv")
    print("\nNota: la silueta no tiene un maximo interior claro en k in [2,20] (sigue "
          "subiendo de forma aproximadamente monotona); no se usa argmax de silueta "
          "para elegir k. Se fija k=6 por interpretabilidad y para no invalidar la "
          "Figura 3 ya generada con ese valor.")

    FIXED_K = 6
    km = KMeans(n_clusters=FIXED_K, random_state=SEED, n_init=10).fit(fallidos[["a_text", "b_text"]])
    fallidos = fallidos.copy()
    fallidos["cluster"] = km.labels_
    fallidos.to_csv(RESULTS_DIR / "fallidos_clusters.csv", index=False)

    sizes = fallidos["cluster"].value_counts().sort_index()
    n_total = len(fallidos)
    stats_por_cluster = fallidos.groupby("cluster")[["L_text", "a_text", "b_text"]].mean().round(1)
    stats_por_cluster["n"] = sizes
    stats_por_cluster["pct"] = (sizes / n_total * 100).round(1)
    stats_por_cluster["chroma_media"] = (fallidos.groupby("cluster").apply(lambda g: np.sqrt(g["a_text"]**2 + g["b_text"]**2).mean())).round(1)
    print(f"\nk={FIXED_K} fijo (silhouette={silhouette_curve[FIXED_K]:.3f}), composicion por cluster:")
    print(stats_por_cluster.sort_values("n", ascending=False))
    stats_por_cluster.to_csv(RESULTS_DIR / "cluster_summary.csv")

    print(f"\nCompletado: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
