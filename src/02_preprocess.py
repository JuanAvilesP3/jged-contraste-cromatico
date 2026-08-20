"""
P2 - Accesibilidad cromatica en sitios web universitarios
02_preprocess.py

Extrae los pares (color de texto, color de fondo) EFECTIVOS de cada
sitio: color computado y fondo efectivo (subiendo por los ancestros
si el fondo inmediato es transparente), descartando elementos
invisibles o de tamano cero (ficha tecnica, seccion 4).

Por que se revisita el sitio en vivo en vez de reusar el HTML guardado
en 01_download.py: el HTML guardado con page.content() serializa el
DOM pero NO inlinea las reglas CSS externas (<link rel=stylesheet>) --
sin volver a cargar la pagina con su CSS real, getComputedStyle()
devolveria los valores por defecto del navegador, no los del sitio.

De paso, se corre axe-core (la misma libreria que usan las
herramientas de accesibilidad profesionales) como validacion cruzada
del calculo propio de contraste, tal como pide la ficha.

Conversion sRGB -> CIELAB: formula estandar (D65), implementada
directamente sin dependencias extra.
"""

import csv
import json
import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
AXE_JS_PATH = Path("C:/Users/Juan/AppData/Roaming/npm/node_modules/axe-core/axe.min.js")

REQUEST_DELAY_SECONDS = 2.0
PAGE_TIMEOUT_MS = 20_000
USER_AGENT = (
    "Mozilla/5.0 (compatible; ESPOCH-AccesibilidadWebLatam/1.0; "
    "investigacion academica FIE-ESPOCH; +https://espoch.edu.ec)"
)

EXTRACT_JS = """
() => {
    function effectiveBg(el) {
        let node = el;
        while (node && node !== document.body.parentElement) {
            const bg = getComputedStyle(node).backgroundColor;
            const m = bg.match(/rgba?\\(([^)]+)\\)/);
            if (m) {
                const parts = m[1].split(',').map(s => parseFloat(s));
                if (parts.length < 4 || parts[3] > 0) return bg;
            }
            node = node.parentElement;
        }
        return 'rgb(255, 255, 255)';
    }

    const results = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
        const text = node.textContent.trim();
        if (!text) continue;
        const el = node.parentElement;
        if (!el) continue;
        const rect = el.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) continue;
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || style.display === 'none' || parseFloat(style.opacity) === 0) continue;

        results.push({
            text_color: style.color,
            bg_color: effectiveBg(el),
            font_size_px: parseFloat(style.fontSize),
            font_weight: style.fontWeight,
        });
    }
    return results;
}
"""


def rgb_string_to_tuple(rgb_str):
    import re
    m = re.match(r"rgba?\(([^)]+)\)", rgb_str or "")
    if not m:
        return None
    parts = [float(x) for x in m.group(1).split(",")]
    return tuple(parts[:3])


def srgb_to_lab(rgb):
    """rgb: tupla (r,g,b) 0-255. Devuelve (L*, a*, b*), D65."""
    rgb_lin = []
    for c in rgb:
        c = c / 255.0
        c = ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
        rgb_lin.append(c)
    r, g, b = rgb_lin
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else (7.787 * t + 16 / 116)

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    bb = 200 * (fy - fz)
    return L, a, bb


def relative_luminance(rgb):
    vals = []
    for c in rgb:
        c = c / 255.0
        vals.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = vals
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_contrast_ratio(rgb1, rgb2):
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def main():
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    sites = pd.read_csv(DATA_DIR / "dominios_universidades.csv")
    log = pd.read_csv(DATA_DIR / "download_log.csv")
    ok_ids = set(log[log.status == "ok"]["id"])
    sites = sites[sites["id"].isin(ok_ids)]
    print(f"Revisitando {len(sites)} sitios exitosos para extraer pares de color...")

    axe_js = AXE_JS_PATH.read_text(encoding="utf-8") if AXE_JS_PATH.exists() else None
    if axe_js is None:
        print("AVISO: axe-core no encontrado, se omite la validación cruzada.")

    pairs_path = PROC_DIR / "color_pairs.csv"
    axe_path = PROC_DIR / "axe_results.csv"
    already_done = set()
    if pairs_path.exists():
        already_done = set(pd.read_csv(pairs_path)["site_id"].unique())
        print(f"Reanudando: {len(already_done)} sitios ya procesados.")

    pairs_fields = ["site_id", "country", "text_color", "bg_color", "font_size_px", "font_weight",
                     "contrast_ratio", "L_text", "a_text", "b_text", "L_bg", "a_bg", "b_bg"]
    axe_fields = ["site_id", "axe_color_contrast_violations", "axe_color_contrast_passes"]

    pairs_f = open(pairs_path, "a" if pairs_path.exists() else "w", newline="", encoding="utf-8")
    axe_f = open(axe_path, "a" if axe_path.exists() else "w", newline="", encoding="utf-8")
    pairs_writer = csv.DictWriter(pairs_f, fieldnames=pairs_fields)
    axe_writer = csv.DictWriter(axe_f, fieldnames=axe_fields)
    if pairs_path.stat().st_size == 0:
        pairs_writer.writeheader()
    if axe_path.stat().st_size == 0:
        axe_writer.writeheader()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT, viewport={"width": 1366, "height": 900})

        for i, row in enumerate(sites.itertuples()):
            if row.id in already_done:
                continue
            page = context.new_page()
            page.set_default_timeout(PAGE_TIMEOUT_MS)
            page.on("dialog", lambda d: d.dismiss())

            # Vigilante de tiempo: page.evaluate() (usado para extraer los
            # pares de color y para axe.run()) NO respeta
            # set_default_timeout ni acepta un parametro de timeout propio
            # en la API sincrona -- un sitio pesado puede colgar la llamada
            # indefinidamente (se confirmo: 30+ min sin avanzar). Si el
            # sitio no termina en SITE_TIMEOUT segundos, se fuerza el
            # cierre de la pagina desde otro hilo, lo que hace que
            # cualquier llamada bloqueada lance una excepcion y el flujo
            # principal pueda seguir con el siguiente sitio.
            SITE_TIMEOUT = 30
            watchdog = threading.Timer(SITE_TIMEOUT, lambda pg=page: pg.close())
            watchdog.daemon = True
            watchdog.start()
            try:
                page.goto(row.web_page, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                raw_pairs = page.evaluate(EXTRACT_JS)
                n_written = 0
                for pair in raw_pairs:
                    text_rgb = rgb_string_to_tuple(pair["text_color"])
                    bg_rgb = rgb_string_to_tuple(pair["bg_color"])
                    if text_rgb is None or bg_rgb is None:
                        continue
                    ratio = wcag_contrast_ratio(text_rgb, bg_rgb)
                    lt, at, bt = srgb_to_lab(text_rgb)
                    lb, ab, bb = srgb_to_lab(bg_rgb)
                    pairs_writer.writerow(dict(
                        site_id=row.id, country=row.country,
                        text_color=pair["text_color"], bg_color=pair["bg_color"],
                        font_size_px=pair["font_size_px"], font_weight=pair["font_weight"],
                        contrast_ratio=ratio, L_text=lt, a_text=at, b_text=bt,
                        L_bg=lb, a_bg=ab, b_bg=bb,
                    ))
                    n_written += 1
                pairs_f.flush()

                if axe_js:
                    try:
                        page.evaluate(axe_js)
                        axe_result = page.evaluate(
                            "async () => { const r = await axe.run(document, {runOnly: ['cat.color']}); "
                            "return {violations: r.violations.reduce((a,v)=>a+v.nodes.length,0), "
                            "passes: r.passes.reduce((a,v)=>a+v.nodes.length,0)}; }"
                        )
                    except Exception:
                        axe_result = {"violations": None, "passes": None}
                else:
                    axe_result = {"violations": None, "passes": None}

                axe_writer.writerow(dict(
                    site_id=row.id, axe_color_contrast_violations=axe_result["violations"],
                    axe_color_contrast_passes=axe_result["passes"],
                ))
                axe_f.flush()

                print(f"[{i+1}/{len(sites)}] {row.id} ({row.country}): {n_written} pares")
            except Exception as exc:
                print(f"[{i+1}/{len(sites)}] {row.id} error: {str(exc)[:150]}")
            finally:
                watchdog.cancel()
                try:
                    page.close()
                except Exception:
                    pass  # el vigilante ya pudo haberla cerrado
            time.sleep(REQUEST_DELAY_SECONDS)

        browser.close()

    pairs_f.close()
    axe_f.close()
    print(f"\nCompletado: {pairs_path} y {axe_path}")


if __name__ == "__main__":
    main()
