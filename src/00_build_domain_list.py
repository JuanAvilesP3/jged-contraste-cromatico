"""
Construye la lista de dominios universitarios latinoamericanos para P2.

Fuente: Hipo/university-domains-list (dataset abierto, MIT license),
descargado en data/raw/world_universities_and_domains.json.

Selecciona una muestra estratificada por pais (para no sesgar hacia
paises con muchas instituciones registradas, p.ej. Brasil) y guarda
data/raw/dominios_universidades.csv con las columnas que usara
01_download.py.
"""

import json
import random
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
SOURCE_JSON = RAW_DIR / "world_universities_and_domains.json"
OUTPUT_CSV = RAW_DIR / "dominios_universidades.csv"

LATAM_COUNTRIES = [
    "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Costa Rica",
    "Cuba", "Dominican Republic", "Ecuador", "El Salvador", "Guatemala",
    "Honduras", "Mexico", "Nicaragua", "Panama", "Paraguay", "Peru",
    "Uruguay", "Venezuela",
]

TARGET_PER_COUNTRY = 16  # ~16 x 19 paises ~= 300, luego se recorta a 250
SEED = 42


def main():
    with open(SOURCE_JSON, encoding="utf-8") as f:
        universities = json.load(f)

    df = pd.DataFrame(universities)
    df = df[df["country"].isin(LATAM_COUNTRIES)].copy()

    # Una fila por universidad, con su primer dominio y primera web_page
    df["domain"] = df["domains"].apply(lambda ds: ds[0] if ds else None)
    df["web_page"] = df["web_pages"].apply(lambda ws: ws[0] if ws else None)
    df = df.dropna(subset=["domain", "web_page"])
    df = df.drop_duplicates(subset=["domain"])

    rng = random.Random(SEED)
    sampled_frames = []
    for country, group in df.groupby("country"):
        n = min(TARGET_PER_COUNTRY, len(group))
        idx = rng.sample(list(group.index), n)
        sampled_frames.append(group.loc[idx])

    sample = pd.concat(sampled_frames).sample(frac=1, random_state=SEED)
    sample = sample[["name", "country", "domain", "web_page"]].reset_index(drop=True)
    sample.insert(0, "id", [f"U{n:04d}" for n in range(1, len(sample) + 1)])

    # Tope de 250 (dentro del objetivo 200-300 de la ficha)
    sample = sample.iloc[:250]

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    print(f"{len(sample)} dominios guardados en {OUTPUT_CSV}")
    print(sample["country"].value_counts())


if __name__ == "__main__":
    main()
