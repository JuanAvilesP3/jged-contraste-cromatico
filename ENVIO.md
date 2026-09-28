# Ficha de Instrucciones de Envío — Paper P2
**Proyecto:** Accesibilidad Cromática en Sitios Web Universitarios Latinoamericanos (WCAG 2.2 y CIELAB)  
**Marco Institucional:** FIE-ESPOCH 2026 (Planificación Oficial de Producción Científica)  
**Fecha de Actualización:** 28 de septiembre de 2026  

---

## 1. Identificación de la Revista y Política Editorial
- **Revista destino:** *Journal of Graphic Engineering and Design* (JGED)
- **Entidad editora:** University of Novi Sad, Faculty of Technical Sciences, Department of Graphic Engineering and Design, Novi Sad, Serbia.
- **ISSN:** 2217-379X (Impreso) | 2217-9860 (En línea).
- **Indexación oficial:** Scopus, DOAJ, SCImago, Google Scholar, Serbian Citation Index (SCIndeks).
- **Portal oficial de envíos (OJS):** [https://jged.uns.ac.rs/index.php/jged/about/submissions](https://jged.uns.ac.rs/index.php/jged/about/submissions)
- **Editor en Jefe:** Prof. Dr. Nemanja Kašiković (`knemanja@uns.ac.rs`).
- **Modalidad de revisión por pares:** **DOBLE CIEGO (Double-Blind Peer Review) ESTRICTO**.
  - La identidad de los autores y evaluadores debe permanecer totalmente oculta durante todo el proceso.
  - El archivo principal para los revisores **NO** debe contener nombres, filiaciones, agradecimientos ni menciones a repositorios que identifiquen a los autores.
  - Toda la información de autoría se envía en una **Página de Título separada (Title Page)** para uso exclusivo del Editor.
- **Sección en OJS:** **Regular Research Paper**.
- **Cobra APC (Article Processing Charges)?:** **NO ($0 USD)**. Publicación 100% gratuita y de acceso abierto diamante (*"JGED does not have Article Processing Charges nor article submission charges"*). Evidencia en `JOURNAL.md`.
- **Formato:** JGED exige entrega en formato Microsoft Word (`.docx`), complementada con el PDF. Límite máximo de 12 páginas A4 (nuestro manuscrito cuenta con 10 páginas).

---

## 2. Metadatos del Manuscrito (para carga en el formulario OJS)

### Título del artículo:
```text
Chromatic Accessibility in Latin American University Websites: A Large-Scale Survey of WCAG Contrast Compliance
```

### Resumen en inglés (Abstract):
```text
Web accessibility audits at scale have historically concentrated on North American and European institutions, leaving higher education in Latin America largely unexamined. We crawled the homepages of 464 Latin American university websites across 17 countries and successfully extracted computed text/background color pairs from 259 of them (41,360 pairs in total). Each pair was converted from sRGB to CIELAB and evaluated against the WCAG 2.2 contrast thresholds, with the axe-core accessibility engine used as an independent cross-check. We find that 21.6% of all color pairs fail the AA threshold, and 93.5% of sites contain at least one critical failure. A pair-level chi-square test suggests compliance differs by country (chi^2 = 1625.04, df = 16, p < 0.001, Cramer's V = 0.198), but because color pairs are clustered within sites rather than independent, we treat this as exploratory: a site-level test on the true unit of analysis (256 sites, countries with >= 5 sites) is not significant (chi^2 = 22.98, df = 15, p = 0.085). We also checked whether a within-site typography effect (large text failing less often) would remain resilient to this clustering concern; it is not: the effect does not survive site-clustered sandwich standard errors (p = 0.473), though continuous font size in pixels retains a small, marginally significant association with failure (p = 0.027). Unsupervised clustering of the failing pairs in the full CIELAB L*a*b* space confirms our initial hypothesis rather than complicating it: near-neutral, low-chroma clusters consistent with the "light gray on white" pattern account for 80.0% of all failing pairs, with four smaller chromatic clusters spanning the remaining 20.0%.
```

### Palabras clave (Keywords):
```text
Color contrast, Chromatic accessibility, WCAG 2.2, CIELAB color space, Web accessibility, Information design, Delta E 2000, Web typography
```

---

## 3. Autores y Filiación Institucional Oficial (para Title Page y Formulario OJS)
1. **Juan Pablo Aviles-Esparza** (*Primer Autor y Autor de Correspondencia*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `juan.aviles@espoch.edu.ec`
   - *ORCID:* [0009-0007-0058-8069](https://orcid.org/0009-0007-0058-8069)
2. **Italo Javier Tenempaguay-Granizo** (*Coautor*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `italo.tenempaguay@espoch.edu.ec`
   - *ORCID:* [0009-0001-5753-4279](https://orcid.org/0009-0001-5753-4279)
3. **Isaac David Torres-Paredes** (*Coautor y Tutor Académico*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `isaac.torres@espoch.edu.ec`
   - *ORCID:* [0009-0001-7057-9316](https://orcid.org/0009-0001-7057-9316)

---

## 4. Archivos a Subir en la Plataforma OJS (Protocolo Doble Ciego)
- **Paso 2 de OJS (Upload Submission / Manuscrito para Evaluadores - ANONIMIZADO):**
  - Subir: `P2_JGED_manuscript.docx` (documento Word oficial formateado bajo la plantilla JGED, 10 páginas A4, sin datos de autoría) y/o el PDF anonimizado `P2_JGED_manuscript_blinded.pdf`.
- **Paso 4 de OJS (Upload Supplementary Files / Archivos para el Editor):**
  1. **Title Page separada (con datos completos de autoría):** `Title_Page_JGED.docx` y `Title_Page_JGED.pdf`.
  2. `cover_letter.md` (Carta formal dirigida al Editor en Jefe Prof. Dr. Nemanja Kašiković).
  3. `declaraciones.md` (Declaraciones de autoría CRediT, ética COPE de uso de IA, disponibilidad de datos en Zenodo y ausencia de conflictos).
  4. Manuscrito identificado completo (para archivo editorial): `P2_JGED_manuscript.pdf`.
  5. `P02_JGED_paquete_envio.zip` (Paquete comprimido con fuentes completas LaTeX: `main.tex`, `main_blinded.tex`, `refs.bib`, subcarpeta `figures/` con las 8 figuras vectoriales/raster 300 DPI, `README.md`).

---

## 5. Revisores Pares Sugeridos (3 Expertos Internacionales en Colorimetría y Diseño Gráfico)
1. **Prof. Dr. Nemanja Kašiković**  
   - *Filiación:* Department of Graphic Engineering and Design, University of Novi Sad, Novi Sad, Serbia.  
   - *Correo electrónico:* `knemanja@uns.ac.rs`  
   - *Especialidad:* Colorimetría, reproducción gráfica, gestión de color en artes gráficas y diseño visual.
2. **Prof. Dr. Dragoljub Novaković**  
   - *Filiación:* Department of Graphic Engineering and Design, University of Novi Sad, Novi Sad, Serbia.  
   - *Correo electrónico:* `novakd@uns.ac.rs`  
   - *Especialidad:* Tecnología gráfica, ergonomía de la información visual y diseño web accesible.
3. **Prof. Dr. Mark D. Wilkinson**  
   - *Filiación:* Center for Biotechnology and Plant Genomics (CBGP), Universidad Politécnica de Madrid, Madrid, España.  
   - *Correo electrónico:* `mark.wilkinson@upm.es`  
   - *Especialidad:* Arquitectura de información digital, principios FAIR, estándares internacionales de diseño y accesibilidad web.

---

## 6. Enlaces de Reproducibilidad y Datos Abiertos
- **Repositorio público en GitHub:** [https://github.com/JuanAvilesP3/jged-contraste-cromatico.git](https://github.com/JuanAvilesP3/jged-contraste-cromatico.git)
- **Depósito permanente en Zenodo:** [https://doi.org/10.5281/zenodo.23005763](https://doi.org/10.5281/zenodo.23005763) (DOI: `10.5281/zenodo.23005763`).

---

## 7. Lista de Chequeo Previa al Envío (Directrices FIE-ESPOCH 2026)
- [x] Manuscrito de evaluación anonimizado sin nombres, correos ni filiaciones (versión `blinded`).
- [x] Página de título (*Title Page*) preparada por separado con la totalidad de los datos de autoría para el editor.
- [x] Manuscrito ajustado a 10 páginas A4 (dentro del límite máximo de 12 páginas de JGED).
- [x] Estilo de citación autor-año Harvard estricto verificado en `refs.bib`.
- [x] 8 figuras de alta resolución alojadas en la subcarpeta `figures/` e insertadas como `figures/figX...`.
- [x] Ninguna figura generada con IA de imágenes.
- [x] Implementación rigurosa del algoritmo de composición alfa W3C ($C_{\text{eff}} = \text{round}(\alpha C + (1-\alpha) 255)$) en el preprocesamiento de color.
- [x] Resolución dinámica y portable del motor `axe-core` en `src/02_preprocess.py`.
- [x] 2 citas locales a artículos de JGED incorporadas (*Abd El-Rahman et al. 2021, Aydemir et al. 2021*).
- [x] Filiación institucional corregida con acentuación oficial LaTeX (`Polit\'ecnica`).
- [x] Exclusividad estricta de envío garantizada.
