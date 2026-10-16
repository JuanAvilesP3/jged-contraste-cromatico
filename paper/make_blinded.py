"""Genera main_blinded.tex a partir de main.tex para la revision doble ciego de JGED.

Quita todo lo que identifica a los autores: bloque de autores, afiliacion, ORCID,
DOI de Zenodo y URL de GitHub (el registro de Zenodo se llama JuanAvilesP3/...),
financiamiento institucional y contribuciones CRediT. El resto del texto queda
identico, asi las dos versiones no se desincronizan.

Uso: python make_blinded.py   (desde paper/)
"""
import re
import sys

SRC, DST = "main.tex", "main_blinded.tex"

ANON_AUTHORS = (
    "\\author{\n"
    "  \\normalsize \\textit{Anonymous Authors for Double-Blind Peer Review} \\\\[0.8ex]\n"
    "  \\small \\textit{(Author details and institutional affiliations omitted per JGED double-blind review policy)}\n"
    "}"
)
SECTIONS = {
    "Data Availability": (
        "The domain list, crawl logs, extracted colour pairs, and analysis code are permanently archived "
        "in a public repository with a persistent DOI. The identifier and repository URL are withheld "
        "during double-blind review and will be added upon acceptance."
    ),
    "Funding": "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.",
    "Author Contributions": "\\textit{Author contribution statements omitted for double-blind peer review.}",
}


def replace_section(t, title, new_body):
    pat = re.compile(r"(\\section\*\{" + re.escape(title) + r"\}\s*\n)(.*?)(?=\n\\section\*?\{|\n\\bibliographystyle|\n\\end\{document\})", re.S)
    t, n = pat.subn(lambda m: m.group(1) + new_body + "\n", t)
    if n != 1:
        sys.exit(f"seccion '{title}' encontrada {n} veces")
    return t


def main():
    t = open(SRC, encoding="utf-8").read()
    t, n = re.subn(r"\\author\{.*?\n\}", lambda _: ANON_AUTHORS, t, count=1, flags=re.S)
    if n != 1:
        sys.exit("bloque \\author no encontrado")
    for title, body in SECTIONS.items():
        t = replace_section(t, title, body)
    leaks = [w for w in ("Aviles", "Tenempaguay", "Torres", "ESPOCH", "Chimborazo", "0009-", "zenodo",
                         "JuanAvilesP3", "github.com", "espoch.edu.ec") if w.lower() in t.lower()]
    if leaks:
        sys.exit(f"quedan datos identificables en {DST}: {leaks}")
    open(DST, "w", encoding="utf-8").write(t)
    print(f"OK -> {DST}")


if __name__ == "__main__":
    main()
