"""
P2 - relleno de la lista de dominios.

La primera muestra (245 dominios) resulto en solo 144 descargas
exitosas (58.8%), por debajo del objetivo de 200-300 de la ficha
tecnica. Este script agrega candidatos nuevos (sin repetir los ya
usados) a data/raw/dominios_universidades.csv, continuando la
numeracion de ids, para que 01_download.py (ya hecho reanudable)
procese solo los nuevos.
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

TARGET_PER_COUNTRY = 26
SEED = 43  # distinto de la muestra original, para no repetir el mismo orden


def main():
    with open(SOURCE_JSON, encoding="utf-8") as f:
        universities = json.load(f)

    df = pd.DataFrame(universities)
    df = df[df["country"].isin(LATAM_COUNTRIES)].copy()
    df["domain"] = df["domains"].apply(lambda ds: ds[0] if ds else None)
    df["web_page"] = df["web_pages"].apply(lambda ws: ws[0] if ws else None)
    df = df.dropna(subset=["domain", "web_page"]).drop_duplicates(subset=["domain"])

    existing = pd.read_csv(OUTPUT_CSV)
    used_domains = set(existing["domain"])
    remaining = df[~df["domain"].isin(used_domains)]

    rng = random.Random(SEED)
    sampled_frames = []
    for country, group in remaining.groupby("country"):
        n = min(TARGET_PER_COUNTRY, len(group))
        idx = rng.sample(list(group.index), n)
        sampled_frames.append(group.loc[idx])

    new_sample = pd.concat(sampled_frames).sample(frac=1, random_state=SEED)
    new_sample = new_sample[["name", "country", "domain", "web_page"]].reset_index(drop=True)

    next_id = len(existing) + 1
    new_sample.insert(0, "id", [f"U{n:04d}" for n in range(next_id, next_id + len(new_sample))])

    combined = pd.concat([existing, new_sample], ignore_index=True)
    combined.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    print(f"{len(new_sample)} dominios nuevos agregados (total: {len(combined)})")
    print(new_sample["country"].value_counts())


if __name__ == "__main__":
    main()
