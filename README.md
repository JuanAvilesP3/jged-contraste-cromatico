# P02 · Accesibilidad cromática en sitios web universitarios

**Revista destino:** JGED
**Línea:** A · **GPU:** Nula · **Días asignados:** 16-17 ago

## Estado
- [x] Ficha de revista completa (JOURNAL.md)
- [x] Datos descargados (data/raw/) — 278 sitios de 464 intentados (17 países LatAm)
- [ ] Experimento ejecutado (día 1) — falta 03_experiment.py: análisis de contraste WCAG, estadística
- [ ] Redacción y figuras (día 2)
- [ ] Endurecimiento: DOIs verificados
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

## 18/08 - Montaje
- Hecho: estructura de carpetas creada, plantilla de figuras copiada, repositorio Git inicializado.
- Bloqueado en: pendiente ficha de revista y descarga de datos.
- Siguiente: completar JOURNAL.md y descargar dataset.
- Tiempo de computo consumido: 0h

## 18-19/08 - Día 1: recolección de datos (dominios)
- Hecho: `00_build_domain_list.py` (245 dominios iniciales, dataset abierto Hipo/university-domains-list, 17 países LatAm) + `00b_backfill_domain_list.py` (219 dominios de relleno) + `01_download.py` con Playwright. Bugs reales corregidos: (1) robots.txt se pedía con el user-agent genérico de Python, que varios sitios bloqueaban con 403 → exclusión de sitios que sí permitían rastreo; (2) un sitio con diálogo JS sin manejador colgó el script 4 horas reales → reescrito con vigilante de tiempo por sitio. Resultado: **278 sitios descargados de 464 intentados** (60% éxito; el resto son sitios caídos, con DNS roto, o excluidos por robots.txt — documentado en `data/raw/download_log.csv` para la sección de limitaciones).
- Bloqueado en: nada.
- Siguiente: `02_preprocess.py` (extracción de pares de color, conversión CIELAB) y `03_experiment.py` (cálculo de ratio de contraste WCAG, χ², regresión logística).
- Tiempo de computo consumido: ~1h
