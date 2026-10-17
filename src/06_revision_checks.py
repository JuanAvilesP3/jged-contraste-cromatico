"""Comprobaciones anadidas tras la revision cruzada interna (16/10/2026).

Lee las tablas ya generadas por 03 y 04 y escribe results/tables/revision_checks.csv con:
  - perfil de fondo de cada cluster de pares fallidos (cuanto texto es blanco puro, ratio mediano, L* del fondo);
  - tasa de renderizado por pais y prueba chi-cuadrado (sesgo de no respuesta);
  - umbrales alternativos de "sitio con fallo" (>10 % y >25 % de pares fallidos);
  - proporcion de pares con transparencia (rgba);
  - variables tipograficas por separado (GEE agrupado por sitio), por la colinealidad entre px y texto grande.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "results" / "tables"
RAW = ROOT / "data" / "raw"

rows = []
def add(name, value):
    rows.append({"medida": name, "valor": value})
    print(f"{name}: {value}")

f = pd.read_csv(T / "fallidos_clusters.csv")
for c, g in f.groupby("cluster"):
    add(f"cluster{c}_n", len(g))
    add(f"cluster{c}_pct_texto_blanco_puro", round(100 * (g.text_color == "rgb(255, 255, 255)").mean(), 1))
    add(f"cluster{c}_ratio_mediano", round(g.contrast_ratio.median(), 2))
    add(f"cluster{c}_L_fondo_mediana", round(g.L_bg.median(), 1))
add("pct_fallidos_ratio_menor_1.5", round(100 * (f.contrast_ratio < 1.5).mean(), 1))

dom = pd.read_csv(RAW / "dominios_universidades.csv")
agg = pd.read_csv(T / "agregado_por_sitio.csv")
dom["analizado"] = dom.id.isin(agg.site_id)
tasa = dom.groupby("country").analizado.mean()
add("tasa_analizado_min", f"{tasa.idxmin()} {100 * tasa.min():.0f}%")
add("tasa_analizado_max", f"{tasa.idxmax()} {100 * tasa.max():.0f}%")
chi2, p, dof, exp = chi2_contingency(pd.crosstab(dom.country, dom.analizado))
add("no_respuesta_chi2", f"chi2={chi2:.2f} df={dof} p={p:.3f} esperada_min={exp.min():.2f}")

add("pct_sitios_mas_10pct_fallidos", round(100 * (agg.pct_falla_aa > 10).mean(), 1))
add("pct_sitios_mas_25pct_fallidos", round(100 * (agg.pct_falla_aa > 25).mean(), 1))

d = pd.read_csv(T / "pares_clasificados.csv")
add("pct_pares_con_rgba", round(100 * (d.text_color.str.startswith("rgba") | d.bg_color.str.startswith("rgba")).mean(), 1))
d["falla"] = (d.clasificacion == "falla").astype(int)
d["es_texto_grande"] = d.es_texto_grande.astype(int)
add("pct_falla_texto_grande", round(100 * d[d.es_texto_grande == 1].falla.mean(), 1))
add("pct_falla_texto_normal", round(100 * d[d.es_texto_grande == 0].falla.mean(), 1))
add("r_px_vs_texto_grande", round(np.corrcoef(d.font_size_px, d.es_texto_grande)[0, 1], 2))
for var in ["font_size_px", "es_texto_grande"]:
    m = smf.gee(f"falla ~ C(country) + {var}", groups="site_id", data=d,
                family=sm.families.Binomial(), cov_struct=sm.cov_struct.Independence()).fit()
    add(f"gee_solo_{var}", f"beta={m.params[var]:+.4f} p={m.pvalues[var]:.3f}")

pd.DataFrame(rows).to_csv(T / "revision_checks.csv", index=False)
print(f"\nGuardado {T / 'revision_checks.csv'}")
