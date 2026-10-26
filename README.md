# 🛰️ Proyecto SAOCOM — La Rosaura

Pipeline geoespacial para **La Rosaura (Tandil)**. El objetivo es integrar SAOCOM con Sentinel-2 como **sistema multisensor / constelación virtual** para: (1) reconstruir el uso histórico de los 16 potreros y distinguir `maíz / pastura / otro / incierto`; (2) dentro de los potreros identificados como maíz, estudiar ambientes de manejo para fertilización selectiva.

## Geometrías maestras

El perímetro aproximado del establecimiento es:

```text
POLYGON((-59.346855 -37.204333, -59.339680 -37.198350, -59.322638 -37.211288, -59.329805 -37.217224, -59.346855 -37.204333))
```

Los **16 potreros reales aportados por el productor** están versionados en `data/potreros_la_rosaura.geojson`, con IDs estables `L01`–`L16`. Estas geometrías son la unidad espacial principal; el perímetro exterior funciona como envolvente aproximada.

## Producto SAOCOM piloto validado

`EOL1DSARSAO1A14948810`, adquisición **07/09/2024**: L1D, TOPSAR/TNB, QP HH/HV/VH/VV, GeoTIFF FLOAT32 sin extensión, EPSG:32721, 4.396 × 7.104 px, ~43,55 × 42,33 m, GEOCODED_TERRAIN, DESCENDING/RIGHT y `Sigma0Type=AMPLITUDE`.

Para amplitudes positivas y válidas:

```text
sigma0_dB = 20 * log10(amplitud)
```

## Arquitectura

```text
SAOCOM L (HH/HV/VH/VV) ─┐
                         ├─> potrero + fecha ─> serie temporal multisensor
Sentinel-2 (óptico) ─────┘                         │
                                                  ├─> uso histórico: maíz/pastura/otro/incierto
DEM + suelo + manejo ─────────────────────────────┘
                                                        │
                                                        └─> ambientes de manejo en maíz
```

No se asumirá que “mayor biomasa = maíz”. La clasificación histórica deberá usar la **dinámica fenológica temporal** y la complementariedad de sensores. Una escena SAOCOM aislada no identifica cultivo ni define dosis.

## `La_rosaura.py`

El pipeline ahora:

1. detecta los cuatro GeoTIFF SAOCOM aunque no tengan `.tif`;
2. valida `Sigma0Type` y convierte amplitud a dB cuando corresponde;
3. recorta el establecimiento;
4. carga y valida exactamente 16 geometrías desde `data/potreros_la_rosaura.geojson`;
5. recorta HH/HV/VH/VV por `L01`–`L16`;
6. genera estadísticas por potrero (n, media, mediana, P25, P75);
7. exporta `tablas/resumen_saocom_por_potrero.csv` y `inspeccion_saocom.json`.

```bash
python La_rosaura.py "ruta/al/producto.zip"
```

Puede usarse otra capa con `--potreros ruta.geojson` siempre que tenga 16 features y `potrero_id` único.

## Serie piloto 2024/25

| Fecha | Product ID | Estado |
|---|---|---|
| 07/09/2024 | `EOL1DSARSAO1A14948810` | real validado |
| 23/09/2024 | `EOL1DSARSAO1A14948841` | pendiente de procesamiento |
| 09/10/2024 | `EOL1DSARSAO1A14056208` | pendiente |
| 25/10/2024 | `EOL1DSARSAO1A14948886` | pendiente |
| 10/11/2024 | `EOL1DSARSAO1A14948797` | pendiente |
| 12/12/2024 | `EOL1DSARSAO1A15392623` | pendiente |

## Guardrails científicos

- sigma0 no equivale directamente a humedad, biomasa, rendimiento o dosis.
- HH/HV/VH/VV dependen de humedad, rugosidad, estructura vegetal y geometría.
- maíz vs. pastura se inferirá con series temporales multisensor y nivel de confianza.
- clases ambiguas permanecerán como `incierto`.
- clusters no serán llamados alto/medio/bajo potencial sin validación agronómica.
- dosis final requiere suelo, manejo, objetivo productivo y evidencia de campo.
- no se usarán targets ni rendimientos simulados como resultados.

## Próximos pasos

1. Ejecutar el producto piloto sobre L01–L16 y verificar recortes/estadísticas.
2. Procesar la serie SAOCOM 2024/25.
3. Construir series Sentinel-2 históricas por potrero.
4. Reconstruir `potrero × campaña → maíz/pastura/otro/incierto + confianza`.
5. Incorporar DEM, suelo y manejo.
6. Analizar ambientes dentro de los potreros/campañas identificados como maíz.

## Dependencias

```bash
pip install numpy rasterio matplotlib
```
