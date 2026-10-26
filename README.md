# 🛰️ Proyecto SAOCOM — La Rosaura

Pipeline geoespacial para **La Rosaura (Tandil)**. El objetivo es integrar SAOCOM con Sentinel-2 como **sistema multisensor / constelación virtual** para: (1) reconstruir el uso histórico de los 16 potreros y distinguir `maíz / pastura / otro / incierto`; (2) dentro de los potreros identificados como maíz, estudiar ambientes de manejo para fertilización selectiva.

## Geometrías maestras

Los **16 potreros reales aportados por el productor** están versionados en `data/potreros_la_rosaura.geojson`, con IDs estables `L01`–`L16`. Estas geometrías son la unidad espacial principal; el perímetro exterior funciona como envolvente aproximada.

## SAOCOM

Producto piloto validado: `EOL1DSARSAO1A14948810`, adquisición **07/09/2024**, L1D, TOPSAR/TNB, QP HH/HV/VH/VV, EPSG:32721, `Sigma0Type=AMPLITUDE`. Para amplitudes positivas y válidas: `sigma0_dB = 20 * log10(amplitud)`.

`La_rosaura.py` detecta los GeoTIFF SAOCOM, valida radiometría, recorta L01–L16 y genera estadísticas por potrero.

```bash
python La_rosaura.py "ruta/al/producto.zip"
```

## Sentinel-2 vía Copernicus STAC

`sentinel2_la_rosaura.py` consulta `sentinel-2-l2a` para la campaña exploratoria 2024/25 usando el bounding box calculado desde los 16 potreros. La consulta real recuperó **73 productos y 69 fechas únicas**, desde 05/08/2024 hasta 26/06/2025, con intervalo mediano de 5 días y máximo de 10 días.

```bash
python sentinel2_la_rosaura.py
```

La nubosidad informada por el catálogo corresponde al producto completo y no equivale a nubosidad efectiva dentro de La Rosaura.

### Inspección de assets

`inspeccionar_sentinel2.py` selecciona una escena piloto y lista los assets STAC reales. En la prueba se identificaron B02/B03/B04/B08 a 10 m, red-edge a 20 m y capas SCL/CLD para control de calidad.

```bash
python inspeccionar_sentinel2.py
```

### Primera visualización RGB + NDVI

`visualizar_sentinel2.py` selecciona por defecto la escena de menor nubosidad global, lee remotamente sólo la ventana correspondiente a los 16 potreros y genera:

- `salidas_sentinel2/YYYY-MM-DD_RGB_La_Rosaura.png` con B04/B03/B02 a 10 m;
- `salidas_sentinel2/YYYY-MM-DD_NDVI_La_Rosaura.png` con `(B08-B04)/(B08+B04)` a 10 m;
- límites y etiquetas L01–L16 sobre ambas imágenes.

```bash
python visualizar_sentinel2.py
```

También puede fijarse un producto STAC concreto:

```bash
python visualizar_sentinel2.py --producto-id "ID_STAC_EXACTO"
```

La primera visualización es **control visual**, no clasificación de cultivo. Una escena aislada no permite inferir de forma robusta maíz/pastura ni dosis de fertilización. La etapa siguiente incorporará SCL/CLD para medir píxeles válidos y construir series temporales por potrero.

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

No se asumirá que “mayor biomasa = maíz”. La clasificación histórica deberá usar la **dinámica fenológica temporal** y la complementariedad de sensores.

## Guardrails científicos

- sigma0 no equivale directamente a humedad, biomasa, rendimiento o dosis;
- HH/HV/VH/VV dependen de humedad, rugosidad, estructura vegetal y geometría;
- maíz vs. pastura se inferirá con series temporales multisensor y nivel de confianza;
- clases ambiguas permanecerán como `incierto`;
- clusters no serán llamados alto/medio/bajo potencial sin validación agronómica;
- dosis final requiere suelo, manejo, objetivo productivo y evidencia de campo;
- no se usarán targets ni rendimientos simulados como resultados.

## Próximos pasos

1. Generar y revisar la escena piloto RGB + NDVI.
2. Incorporar SCL/CLD y calcular porcentaje válido dentro de L01–L16.
3. Extraer B2/B3/B4/B5/B6/B7/B8/B8A e índices NDVI/EVI/red-edge por potrero y fecha.
4. Procesar la serie SAOCOM 2024/25 y fusionarla por `potrero + fecha` sin inventar observaciones faltantes.
5. Reconstruir `potrero × campaña → maíz/pastura/otro/incierto + confianza`.
6. Incorporar DEM, suelo y manejo para estudiar ambientes de fertilización selectiva.

## Dependencias

```bash
pip install numpy rasterio matplotlib
```

La consulta STAC utiliza biblioteca estándar; la visualización usa `numpy`, `rasterio` y `matplotlib`.
