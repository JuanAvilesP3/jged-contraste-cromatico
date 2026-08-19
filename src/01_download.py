"""
P2 - Accesibilidad cromatica en sitios web universitarios
01_download.py

Lee data/raw/dominios_universidades.csv, verifica robots.txt y que el
sitio este activo, y para cada dominio permitido abre la portada con
Playwright, espera a que cargue el CSS y guarda:
  - el DOM ya renderizado (data/raw/html/{id}.html)
  - una captura de pantalla (data/raw/screenshots/{id}.png)

Limite de 1 peticion cada 2 segundos (ver ficha tecnica, seccion 3 y
seccion 8 "Sitios que bloquean el rastreo automatizado"). Los sitios
excluidos quedan documentados en data/raw/download_log.csv para
citarlos en la seccion de limitaciones del manuscrito.

Nota tecnica: se usa la API asincrona de Playwright (no la sincrona)
porque necesitamos un limite duro de tiempo por sitio (algunos sitios
cuelgan la navegacion indefinidamente, p.ej. por un dialogo JS sin
manejar) y la API sincrona de Playwright no es segura para eso via
hilos (rompe su modelo interno de greenlets). asyncio.wait_for si
funciona de forma segura porque todo corre en el mismo hilo/loop.
"""

import argparse
import asyncio
import csv
import time
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from playwright.async_api import async_playwright

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DOMAIN_LIST = DATA_DIR / "dominios_universidades.csv"
HTML_DIR = DATA_DIR / "html"
SHOT_DIR = DATA_DIR / "screenshots"
LOG_PATH = DATA_DIR / "download_log.csv"

REQUEST_DELAY_SECONDS = 2.0
PAGE_TIMEOUT_MS = 20_000
SITE_HARD_TIMEOUT_SECONDS = 45  # watchdog: por encima de goto+screenshot timeouts
USER_AGENT = (
    "Mozilla/5.0 (compatible; ESPOCH-AccesibilidadWebLatam/1.0; "
    "investigacion academica FIE-ESPOCH; +https://espoch.edu.ec)"
)


def robots_allows(url: str) -> bool:
    """Descarga robots.txt identificandose con USER_AGENT (no con el
    user-agent generico de urllib, que varios sitios bloquean con 403 y
    hace que el parser asuma, por convencion, que todo esta prohibido)."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)

    req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="replace")
        rp.parse(content.splitlines())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False  # disallow-all, por convencion
        return True  # 404 u otro: no hay robots.txt, se asume permitido
    except Exception:
        # Error de red al pedir robots.txt: se intenta igual: Playwright
        # fallara por su cuenta si el sitio es inalcanzable.
        return True

    return rp.can_fetch(USER_AGENT, url)


async def fetch_one(browser, site_id: str, url: str):
    context = await browser.new_context(user_agent=USER_AGENT, viewport={"width": 1366, "height": 900})
    page = await context.new_page()
    page.set_default_timeout(PAGE_TIMEOUT_MS)
    # Algunos sitios disparan un dialogo JS (alert/confirm) al cargar.
    # Sin manejador, Playwright se queda esperando la navegacion
    # indefinidamente (se detecto un cuelgue real de horas por esto).
    page.on("dialog", lambda dialog: asyncio.ensure_future(dialog.dismiss()))
    try:
        # "domcontentloaded" en vez de "load"/"networkidle": estas
        # ultimas dependen de que terminen todas las imagenes o de que
        # la red quede inactiva, y varios sitios reales (con trackers o
        # medios pesados) nunca cumplen eso a tiempo. Lo que pide la
        # ficha es que cargue el CSS, no la pagina completa;
        # domcontentloaded + espera fija cubre eso.
        await page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)  # margen para CSS/fuentes tardías

        html = await page.content()
        (HTML_DIR / f"{site_id}.html").write_text(html, encoding="utf-8")
        await page.screenshot(path=str(SHOT_DIR / f"{site_id}.png"), full_page=True, timeout=15_000)
        return "ok", ""
    except Exception as exc:
        return "error", str(exc)[:200]
    finally:
        try:
            await asyncio.wait_for(context.close(), timeout=5)
        except Exception:
            pass  # si hasta cerrar el contexto cuelga, se abandona igual


async def run(sites: pd.DataFrame, log_writer, log_file):
    n_new_ok = 0
    n_new_total = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for _, row in sites.iterrows():
            site_id, url = row["id"], row["web_page"]

            if not robots_allows(url):
                status, detail = "excluido_robots", ""
                log_writer.writerow([site_id, url, status, detail])
                log_file.flush()
                n_new_total += 1
                print(f"[{site_id}] excluido por robots.txt: {url}")
                continue

            task = asyncio.ensure_future(fetch_one(browser, site_id, url))
            try:
                status, detail = await asyncio.wait_for(task, timeout=SITE_HARD_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                task.cancel()
                status, detail = "error", f"timeout_global > {SITE_HARD_TIMEOUT_SECONDS}s (colgado)"
                print(f"[{site_id}] cuelgue detectado, se abandona y se continua: {url}")
            except Exception as exc:
                status, detail = "error", str(exc)[:200]

            if status == "error" and "timeout_global" not in detail:
                print(f"[{site_id}] error en {url}: {detail}")

            log_writer.writerow([site_id, url, status, detail])
            log_file.flush()
            n_new_total += 1
            if status == "ok":
                n_new_ok += 1
            await asyncio.sleep(REQUEST_DELAY_SECONDS)

        await browser.close()

    return n_new_ok, n_new_total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Procesar solo los primeros N sitios pendientes (pruebas)")
    args = parser.parse_args()

    HTML_DIR.mkdir(parents=True, exist_ok=True)
    SHOT_DIR.mkdir(parents=True, exist_ok=True)

    sites = pd.read_csv(DOMAIN_LIST)

    log_existed = LOG_PATH.exists()
    n_already_done = 0
    if log_existed:
        prev = pd.read_csv(LOG_PATH)
        n_already_done = len(prev)
        sites = sites[~sites["id"].isin(set(prev["id"]))]
        print(f"Reanudando: {n_already_done} sitios ya procesados, {len(sites)} pendientes.")

    if args.limit:
        sites = sites.head(args.limit)

    log_file = open(LOG_PATH, "a" if log_existed else "w", newline="", encoding="utf-8")
    log_writer = csv.writer(log_file)
    if not log_existed:
        log_writer.writerow(["id", "url", "status", "detail"])

    n_new_ok, n_new_total = asyncio.run(run(sites, log_writer, log_file))
    log_file.close()

    print(f"\nCompletado esta corrida: {n_new_ok}/{n_new_total} nuevos sitios descargados. Log en {LOG_PATH}")


if __name__ == "__main__":
    main()
