# 📝 Registro de Cambios (CHANGELOG) — Proyecto SAOCOM

## [v3.3.0] - 16 potreros y constelación virtual - 2026-10-26

- Incorporadas las geometrías reales de `L01`–`L16` en `data/potreros_la_rosaura.geojson` a partir de las coordenadas aportadas por el productor.
- `La_rosaura.py` valida los 16 IDs y recorta cada polarización SAOCOM por establecimiento y por potrero.
- Nuevo `resumen_saocom_por_potrero.csv` con estadísticos por polarización/potrero.
- El reporte JSON registra fuente de geometrías y advertencias metodológicas.
- Se redefine la arquitectura como sistema multisensor / constelación virtual SAOCOM–Sentinel-2.
- Se agrega una etapa previa de reconstrucción histórica `potrero × campaña → maíz/pastura/otro/incierto + confianza` basada en dinámica fenológica temporal, no en un umbral simple de biomasa.
- El análisis de ambientes para fertilización queda condicionado a potreros/campañas identificados como maíz y a validación agronómica.

## [v3.2.0] - Primer producto SAOCOM real validado - 2026-10-24

- Validado `EOL1DSARSAO1A14948810` (07/09/2024): L1D, TOPSAR/TNB, QP HH/HV/VH/VV, FLOAT32, EPSG:32721, ~43,55 × 42,33 m.
- `Sigma0Type=AMPLITUDE`; conversión `sigma0_dB=20*log10(amplitud)` para valores positivos.
- Eliminadas interpretaciones directas de sigma0 como humedad, biomasa, rendimiento o dosis.
- Pipeline de ingesta/recorte raster real y `inspeccion_saocom.json`.

## [v3.1.0] - Pipeline de ingesta raster real - 2026-10-23
- Eliminación de matrices aleatorias y resultados simulados; recorte y reporte reproducible.

## [v3.0.0] - Transición a SAR real y ambientes de fertilización - 2026-10-23
- Objetivo redefinido hacia fertilización variable; selección de serie piloto real.

## Versiones anteriores
Las versiones 1.x–2.x corresponden a infraestructura, catálogo y prototipos previos. Los mapas/rendimientos simulados históricos no constituyen resultados observados del proyecto.
