# P02 · Accesibilidad cromática en sitios web universitarios

**Revista destino:** JGED
**Línea:** A · **GPU:** Nula · **Días asignados:** 16-17 ago

## Estado
- [x] Ficha de revista completa (JOURNAL.md)
- [x] Datos descargados (data/raw/) — 278 sitios de 464 intentados (17 países LatAm)
- [x] Experimento ejecutado (día 1) — 41,360 pares de color, clasificación WCAG
- [x] Estadística (día 1) — χ², regresión logística, agrupamiento CIELAB
- [x] Figuras generadas (4/4)
- [x] Redacción del manuscrito (día 2) — `paper/main.tex` completo, 3 citas reales verificadas de JGED en `refs.bib`
- [x] Endurecimiento: DOIs verificados
- [ ] Endurecimiento: revisión adversarial ronda 1
- [ ] Endurecimiento: revisión adversarial ronda 2
- [ ] Revisión cruzada
- [ ] Repositorio en GitHub
- [ ] Publicado en Zenodo (DOI)
- [ ] Carta de presentación y declaraciones
- [ ] Entregado al responsable académico

## Protocolo

**Revista destino:** Journal of Graphic Engineering and Design (JGED)
**Fecha de inicio:** 18/08
**Responsable:** Juan (línea A)

### Pregunta de investigación
¿Qué proporción de los sitios web universitarios latinoamericanos cumple los umbrales de contraste cromático de la norma WCAG 2.2, y qué patrones de diseño explican los incumplimientos?

### Hipótesis
El incumplimiento se concentra en tres patrones: texto gris claro sobre blanco, texto sobre imagen de fondo, y estados de interacción (hover, focus, visited) que nadie verifica.

### Variables
- Independientes: tipo de institución, país, framework CSS detectado
- Dependientes: ratio de contraste, cumplimiento AA/AAA, ΔE entre pares
- Controladas: tamaño de fuente (determina el umbral AA/AAA aplicable)

### Diseño
- Condiciones experimentales: 200–300 dominios universitarios latinoamericanos, unidad de análisis = par de colores, agregación = sitio
- Repeticiones por condición: n/a (censo, no experimento controlado)
- Semilla aleatoria: 42
- Validación: axe-core como validación cruzada de 03_experiment.py

### Prueba estadística
Chi-cuadrado de independencia con corrección de continuidad; regresión logística con IC 95 % sobre coeficientes.
- Tamaño del efecto a reportar: V de Cramér

### Criterio de interés
- Si la hipótesis se confirma: los tres patrones identificados explican la mayoría de los fallos de contraste.
- Si se refuta: el incumplimiento está más disperso/heterogéneo de lo esperado; reportar la distribución real de causas.

### Datasets
| Nombre | Fuente | Licencia | Verificado |
|--------|--------|----------|------------|
| Dominios universitarios LatAm (construido) | Directorios de ministerios de educación / rankings públicos | n/a — datos públicos rastreados | No |

Ética del rastreo: verificar robots.txt por sitio, 1 petición cada 2 segundos, documentar sitios excluidos.

### Citas obligatorias de la revista destino
1. (pendiente — extraer de los 5 artículos recientes de JGED sobre contraste, legibilidad, gestión del color)
2.
3.

## Bitácora

## 18/08 - Juan — Montaje
- Hecho: estructura de carpetas creada, plantilla de figuras copiada, repositorio Git inicializado.
- Bloqueado en: pendiente ficha de revista y descarga de datos.
- Siguiente: completar JOURNAL.md y descargar dataset.
- Tiempo de computo consumido: 0h

## 18-19/08 - Juan — Día 1: recolección de datos (dominios)
- Hecho: `00_build_domain_list.py` (245 dominios iniciales, dataset abierto Hipo/university-domains-list, 17 países LatAm) + `00b_backfill_domain_list.py` (219 dominios de relleno) + `01_download.py` con Playwright. Bugs reales corregidos: (1) robots.txt se pedía con el user-agent genérico de Python, que varios sitios bloqueaban con 403 → exclusión de sitios que sí permitían rastreo; (2) un sitio con diálogo JS sin manejador colgó el script 4 horas reales → reescrito con vigilante de tiempo por sitio. Resultado: **278 sitios descargados de 464 intentados** (60% éxito; el resto son sitios caídos, con DNS roto, o excluidos por robots.txt — documentado en `data/raw/download_log.csv` para la sección de limitaciones).
- Bloqueado en: nada.
- Siguiente: `02_preprocess.py` (extracción de pares de color, conversión CIELAB) y `03_experiment.py` (cálculo de ratio de contraste WCAG, χ², regresión logística).
- Tiempo de computo consumido: ~1h

## 20/08 - Juan — Día 1 completo: extracción, clasificación WCAG y estadística
- Hecho:
  - `02_preprocess.py`: revisita en vivo los 278 sitios (el HTML guardado no sirve para esto — no incluye el CSS externo, así que `getComputedStyle()` daría valores por defecto del navegador). Extrae pares de color efectivo texto/fondo, convierte a CIELAB, corre axe-core como validación cruzada. Bug real: `page.evaluate()` no tiene timeout propio en la API síncrona de Playwright y se colgó 30+ minutos sin avanzar — se agregó un vigilante por hilo que fuerza el cierre de la página si un sitio no responde en 30s. Resultado: 41,360 pares de color de 259 sitios.
  - `03_experiment.py`: clasificación falla/AA/AAA según tamaño de texto. 21.6% de los pares fallan AA; 93.5% de los sitios tienen al menos un fallo crítico; correlación moderada (0.35) con las violaciones detectadas por axe-core.
  - `04_stats.py`: χ² cumplimiento×país muy significativo (p<0.001, V de Cramér=0.20); regresión logística con la mayoría de países significativos; agrupamiento CIELAB (k=6, silhouette=0.854) de los pares fallidos — **el patrón de colores que fallan es más diverso de lo hipotetizado** (no solo "gris sobre blanco"; hay clústers rojo, amarillo, verde, morado y azul-verdoso).
  - `05_figures.py`: 4 figuras generadas y revisadas. Fig. 4 usa capturas reales de los sitios con peor tasa de fallo — **pendiente de revisión de anonimización en Fase 2**, no se hizo ningún tratamiento todavía.
  - Nota metodológica documentada: "tipo de institución" (variable que pedía la ficha para el χ²) no estaba disponible de forma confiable en el dataset de universidades; se usó "país" como la variable categórica disponible más cercana.
- Bloqueado en: nada. **P2 completo hasta figuras — con esto los 5 artículos de línea A quedan parejos.**
- Siguiente: redactar `paper/main.tex`.
- Tiempo de computo consumido: ~1h

## 20/08 - Juan — Redacción del manuscrito
- Hecho: `paper/main.tex` completo (abstract, introducción, related work, metodología, resultados, discusión, limitaciones, conclusión). 3 citas reales de JGED buscadas y verificadas por URL directa (no inventadas) en `refs.bib`: Weingerl et al. 2022, Punsongserm & Suvakunta 2025, Ofosu-Asare 2024. Todos los números del manuscrito provienen directamente de los archivos de `results/tables/` (no estimados de memoria).
- Bloqueado en: nada. Falta Fase 2 completa (verificación formal de DOIs, revisión adversarial en 2 rondas, pasada anti-IA).
- Siguiente: pasar al manuscrito del siguiente artículo, o iniciar Fase 2 sobre los ya redactados.
- Tiempo de computo consumido: ~30 min


## 21/08 - Juan — Verificación de referencias (Fase 2)
- Hecho: los DOIs de las 3 citas se resolvieron uno por uno (HTTP 200/302 contra doi.org) y se confirmó que el contenido de cada artículo coincide con lo citado en el manuscrito. DOIs agregados a `refs.bib` con nota de verificación y fecha.
- Bloqueado en: nada.
- Siguiente: revisión adversarial ronda 1 (rol de revisor de la revista destino).
- Tiempo de computo consumido: ~15 min


## 20/08 - Juan — Revisión adversarial ronda 1 (rol JGED) + bibliografía ampliada + figuras
- Hecho: bibliografía ampliada de 3 a 6 citas verificadas (WCAG 2.2, CIELAB 1976, WebAIM Million 2026). Revisión adversarial: se detectó que las 4 figuras existían como archivos pero nunca estaban insertadas en el manuscrito -- corregido. Se detectó un problema estadístico real: la prueba de "cumplimiento por país" se corría sobre 41,360 pares de color, pero esos pares están agrupados dentro de 259 sitios (no son observaciones independientes). Se recalculó la prueba al nivel correcto (sitio): el efecto por país deja de ser significativo (p=0.085 vs. p<0.001 al nivel de par). Se reescribió abstract, resultados, discusión, limitaciones y conclusión para reportarlo honestamente como hallazgo no confirmado, en vez de mantener la afirmación original. Pasada anti-IA parcial (frases repetidas entre los 5 artículos).
- Bloqueado en: nada.
- Siguiente: ronda 2 de revisión adversarial + pasada anti-IA completa.
- Tiempo de computo consumido: ~35 min


## 20/08 - Juan — Ronda 2 + pasada anti-IA
- Hecho: segunda lectura crítica del manuscrito completo; se verificó que todas las figuras y tablas están referenciadas en el texto (no solo insertadas) y que no quedan referencias cruzadas rotas. Pasada anti-IA: se reescribieron frases que se repetían casi textualmente en otros artículos de la línea ("headline finding", "practical implication", "folklore").
- Bloqueado en: nada.
- Siguiente: conversión a Word (JGED lo exige) cuando se cierre la redacción final.
- Tiempo de computo consumido: ~10 min


## 20/08 - Juan — Conversión a Word (JGED lo exige)
- Hecho: `paper/P2_JGED_manuscript.docx` generado a partir de `main.tex` (título, abstract, todas las secciones, tabla, las 4 figuras insertadas, y la bibliografía en formato autor-año). Primero verificado solo por lectura programática (sin Word instalado, pensé). El usuario aclaró que sí tiene Word -- usé automatización de Word (COM) para abrirlo de verdad y exportarlo a PDF, y revisé la versión visual real: título, tabla, las 4 figuras (bien proporcionadas) y referencias se ven correctos. De paso ajusté el ancho de columnas de la tabla para que sea más legible.
- Bloqueado en: nada.
- Siguiente: revisión final del usuario; luego, ajuste final a la plantilla oficial de JGED si la tienen.
- Tiempo de computo consumido: ~25 min
