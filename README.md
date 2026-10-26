# 🛰️ Proyecto SAOCOM — La Rosaura

Pipeline geoespacial para **La Rosaura (Tandil)**. El objetivo principal es integrar SAOCOM con Sentinel-2 como **sistema multisensor / constelación virtual** para: (1) reconstruir el uso histórico de los 16 potreros y distinguir `maíz / pastura / otro / incierto`; (2) dentro de los potreros identificados como maíz, estudiar ambientes de manejo para fertilización selectiva.

Como línea futura separada se documenta una segunda aplicación de la misma infraestructura: **manejo inteligente de pasturas para el tambo**, orientado a estimar estado, utilización y recuperación de cada potrero y apoyar la rotación del rodeo.

## Geometrías maestras

Los **16 potreros reales aportados por el productor** están versionados en `data/potreros_la_rosaura.geojson`, con IDs estables `L01`–`L16`. Estas geometrías son la unidad espacial principal; el perímetro exterior funciona como envolvente aproximada.

Las subdivisiones temporarias de pastoreo pueden dejar franjas y patrones intrapotrero persistentes. Por ello, una diferencia espacial de NDVI o retrodispersión no se interpretará automáticamente como diferencia de potencial productivo o cultivo actual.

## SAOCOM

Producto piloto validado: `EOL1DSARSAO1A14948810`, adquisición **07/09/2024**, L1D, TOPSAR/TNB, QP HH/HV/VH/VV, EPSG:32721, resolución aproximada **43,55 × 42,33 m**, `Sigma0Type=AMPLITUDE`. Para amplitudes positivas y válidas: `sigma0_dB = 20 * log10(amplitud)`.

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

### Inspección y acceso a assets

`inspeccionar_sentinel2.py` selecciona una escena piloto y lista los assets STAC reales. Se verificaron B02/B03/B04/B08 a 10 m, red-edge a 20 m y capas SCL/CLD para control de calidad.

El acceso autenticado a Copernicus Data Space S3 quedó verificado mediante credenciales almacenadas sólo como variables de entorno locales; **no se versionan secretos**.

### Visualización RGB + NDVI validada

`visualizar_sentinel2.py` fue ejecutado correctamente sobre el producto:

`S2A_MSIL2A_20240904T134701_N0511_R024_T21HTU_20240904T212846`

Fecha **04/09/2024**, nubosidad global informada **0,0 %**. Se leyeron B02/B03/B04/B08 y se generaron correctamente:

- `salidas_sentinel2/2024-09-04_RGB_La_Rosaura.png`;
- `salidas_sentinel2/2024-09-04_NDVI_La_Rosaura.png`;
- límites y etiquetas L01–L16.

La inspección visual confirma una fuerte heterogeneidad entre e intra-potreros. Parte de las franjas visibles corresponde a subdivisiones temporarias usadas para encerrar el rodeo durante el pastoreo y puede persistir desde campañas anteriores. También un tono distinto puede reflejar pastoreo reciente y reducción temporal de biomasa. Por eso estas texturas no deben convertirse sin validación en etiquetas de cultivo, productividad o ambiente.

## Arquitectura principal: maíz forrajero

```text
SAOCOM L (~43 m; HH/HV/VH/VV) ─┐
                                ├─> potrero + fecha ─> serie temporal multisensor
Sentinel-2 (óptico 10/20 m) ────┘                         │
                                                         ├─> uso histórico: maíz/pastura/otro/incierto
DEM + suelo + manejo ────────────────────────────────────┘
                                                               │
                                                               └─> ambientes de manejo en maíz
                                                                      │
                                                                      └─> fertilización selectiva validada
```

No se asumirá que “mayor biomasa = maíz”. La clasificación histórica se apoyará prioritariamente en la **dinámica fenológica temporal**: establecimiento, crecimiento, máximo y senescencia/cosecha frente a patrones de pastura y manejo.

## Línea futura: manejo inteligente de pasturas

La misma constelación virtual puede investigarse como sistema de apoyo al pastoreo de precisión:

```text
Sentinel-2 + SAOCOM + clima + historial de pastoreo
                         ↓
estado + heterogeneidad + utilización + recuperación
                         ↓
tiempo desde último pastoreo + demanda del rodeo
                         ↓
prioridad de potrero / apoyo a la rotación
                         ↓
validación con manejo y producción de leche
```

La hipótesis a evaluar es si la fusión **óptico Sentinel-2 + SAR banda L SAOCOM** aporta información complementaria respecto de cada sensor por separado. Para demostrarlo deberán compararse modelos Sentinel-2, SAOCOM y multisensor con datos reales de campo.

## Guardrails científicos

- sigma0 no equivale directamente a humedad, biomasa, rendimiento o dosis;
- HH/HV/VH/VV dependen de humedad, rugosidad, estructura vegetal y geometría;
- maíz vs. pastura se inferirá con series temporales multisensor y nivel de confianza;
- el efecto reciente del rodeo puede alterar índices ópticos dentro de una pastura;
- huellas de pastoreo de campañas anteriores pueden persistir espacialmente;
- clases ambiguas permanecerán como `incierto`;
- clusters no serán llamados alto/medio/bajo potencial sin validación agronómica;
- dosis final requiere suelo, manejo, objetivo productivo y evidencia de campo;
- una recomendación de pastoreo requerirá registros de entrada/salida, recuperación y validación productiva;
- no se usarán targets ni rendimientos simulados como resultados.

## Próximos pasos — proyecto activo de maíz

1. Incorporar SCL/CLD y calcular porcentaje válido dentro de L01–L16.
2. Extraer B2/B3/B4/B5/B6/B7/B8/B8A e índices NDVI/EVI/red-edge por potrero y fecha.
3. Construir las 16 curvas fenológicas y estadísticas robustas (mediana, P25, P75, dispersión).
4. Procesar la serie SAOCOM 2024/25 y fusionarla por `potrero + fecha` sin inventar observaciones faltantes.
5. Reconstruir `potrero × campaña → maíz/pastura/otro/incierto + confianza`.
6. Incorporar DEM, suelo y manejo para estudiar ambientes de fertilización selectiva.

## Dependencias

```bash
pip install numpy rasterio matplotlib boto3
```

La consulta STAC utiliza biblioteca estándar; la visualización usa `numpy`, `rasterio`, `matplotlib` y acceso autenticado S3.