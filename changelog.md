# 📝 Registro de Cambios (CHANGELOG) — Proyecto SAOCOM

Historial técnico y metodológico del pipeline para **La Rosaura**, Tandil.

---

## [v3.2.0] - Primer producto SAOCOM real validado - 2026-10-24

### 🛰️ Producto real
- Recibido el pedido CONAE **#1189052** correspondiente a `EOL1DSARSAO1A14948810` (07/09/2024).
- Confirmadas cuatro polarizaciones QP: **HH, HV, VH y VV**.
- Confirmado formato **GeoTIFF FLOAT32** entregado sin extensión `.tif`.
- Confirmado CRS **EPSG:32721 (UTM 21S)**.
- Dimensiones por raster: **4.396 × 7.104 píxeles**.
- Resolución observada: aproximadamente **43,55 × 42,33 m**.
- Se corrige el supuesto previo de 10 m para este producto TOPSAR/TNB.

### 🔬 Radiometría
- `Config/L1PROCConf.xml` declara `Sigma0Type=AMPLITUDE`.
- Para valores positivos se adopta `σ⁰_dB = 20·log10(amplitud)`.
- Se preservan también los recortes en amplitud original.
- Los valores de retrodispersión no se interpretan directamente como humedad, biomasa, rendimiento o dosis de fertilizante.

### 💻 Pipeline
- `La_rosaura.py` detecta GeoTIFF aun sin extensión.
- Identifica automáticamente HH/HV/VH/VV.
- Reproyecta el AOI al CRS del raster.
- Recorta las cuatro polarizaciones a La Rosaura.
- Genera GeoTIFF en amplitud y `σ⁰` dB.
- Genera mapas PNG de retrodispersión observada.
- Exporta estadísticas y `inspeccion_saocom.json`.

### 🎓 Machine Learning
- Se incorpora `PROYECTO_FACULTAD_ML.md`.
- El trabajo académico se centra en ambientes para fertilización selectiva mediante SAOCOM + topografía + suelo + manejo.
- Se prioriza inicialmente clustering y, si existen etiquetas de campo confiables, modelos supervisados con validación espacial.

### ⏭️ Próximo hito
- Procesar la serie temporal 2024/25.
- Incorporar los 16 potreros y los potreros de maíz.
- Incorporar DEM/topografía.
- Construir el dataset espacial para Machine Learning.

---

## [v3.1.0] - Pipeline de ingesta raster real - 2026-10-23

- Eliminación de matrices aleatorias y resultados simulados.
- Preparación del script para ZIP L1D reales.
- Recorte geográfico y reporte técnico reproducible.
- Separación explícita entre observaciones SAR e inferencias agronómicas.

---

## [v3.0.0] - Transición a SAR real y ambientes de fertilización - 2026-10-23

- Objetivo redefinido hacia fertilización variable en potreros de maíz.
- Selección de serie piloto L1D QP TOPSAR/TNB.
- Selección de `EOL1DSARSAO1A14948810` como primer producto.
- Se invalidan como resultados reales los mapas y métricas simulados de versiones anteriores.

---

## [v2.1.0] - Conexión al catálogo CONAE - 2026-08-30

- Lectura del catálogo mediante `pandas`/`openpyxl`.
- Extracción de IDs y fechas reales.
- Los valores históricos de 38,16 y 49,71 TN/ha procedían de simulación y no constituyen mediciones SAOCOM.

---

## [v2.0.0] - Preparación metodológica L1D - 2026-08-30

- Indexación de productos reales del catálogo.
- Preparación conceptual para datos L1D y QP.

---

## [v1.1.0] - Segmentación espacial y gráficos - 2026-08-29

- Grilla experimental y mapas 2D.

---

## [v1.0.0] - Infraestructura base y Git - 2021-10-26

- Configuración inicial del entorno Python y publicación del proyecto.
