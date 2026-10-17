# Chromatic accessibility in Latin American university websites

Data and code for the article *Chromatic Accessibility in Latin American University Websites: A Large-Scale Survey of WCAG Contrast Compliance*, submitted to the *Journal of Graphic Engineering and Design* (JGED).

**Authors:** Juan Pablo Aviles-Esparza, Italo Javier Tenempaguay-Granizo, Isaac David Torres-Paredes. Software Engineering, Faculty of Informatics and Electronics, Escuela Superior Politécnica de Chimborazo (ESPOCH), Riobamba, Ecuador.

## What the study does

We sampled 464 university homepages from 17 Latin American countries, rendered each one in a headless browser, and extracted the computed text and background colour of every visible text element (41,360 pairs from 259 sites). Each pair is classified against the WCAG 2.2 contrast thresholds, converted to CIELAB, and the failing pairs are clustered by colour. The analysis compares countries at the pair and at the site level and checks the results against the axe-core accessibility engine.

## Repository layout

| Path | Content |
|---|---|
| `src/00_build_domain_list.py`, `src/00b_backfill_domain_list.py` | Build the stratified sample of university domains |
| `src/01_download.py` | Crawl the homepages (Playwright, robots.txt respected, one request every 2 s) |
| `src/02_preprocess.py` | Extract computed colour pairs, convert sRGB to CIELAB, run axe-core |
| `src/03_experiment.py` | WCAG classification, per-site aggregation, clustering of failing pairs |
| `src/04_stats.py` | Chi-square and Kruskal-Wallis tests, logistic regression and GEE, permutation test |
| `src/05_figures.py` | Figures 1-4 |
| `src/06_revision_checks.py` | Additional checks (cluster backgrounds, non-response by country, typography) |
| `src/run_all.py` | Runs the pipeline in order and logs package versions to `results/logs/` |
| `data/raw/dominios_universidades.csv` | Sampled domains (country, institution, URL) |
| `data/raw/download_log.csv` | Crawl outcome for each domain |
| `data/processed/` | Extracted colour pairs and axe-core results, the input of the analysis |
| `results/tables/` | Classified colour pairs and every table reported in the article |
| `results/figures/` | Figures as PDF and PNG |
| `paper/` | LaTeX source and compiled manuscript |

## Reproducing the analysis

```bash
pip install -r requirements.txt
playwright install chromium
python src/run_all.py            # full pipeline, including the crawl
python src/run_all.py --from 03  # from the published colour pairs in data/processed/, without crawling
```

The crawl reflects the websites as they were in August 2026; a new crawl will return different pages. Homepage screenshots are not redistributed.

## Citation

Archived on Zenodo: [10.5281/zenodo.22907769](https://doi.org/10.5281/zenodo.22907769) (this DOI always resolves to the latest version).
