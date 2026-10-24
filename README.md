# 🛰️ Proyecto SAOCOM — La Rosaura

Pipeline de análisis SAR para el establecimiento **La Rosaura**, Tandil, orientado actualmente a **fertilización selectiva de los potreros de maíz**.

## Estado actual — primer producto real validado

El producto piloto `EOL1DSARSAO1A14948810` (adquisición 07/09/2024), solicitado a CONAE mediante el pedido **#1189052**, ya fue recibido e inspeccionado.

| Propiedad | Valor observado |
|---|---|
| Nivel | L1D |
| Modo | TOPSAR / TNB |
| Polarización | QP: HH, HV, VH, VV |
| Formato raster | GeoTIFF, entregado sin extensión `.tif` |
| Tipo de dato | FLOAT32 |
| Dimensiones | 4.396 × 7.104 píxeles por polarización |
| CRS | EPSG:32721 — WGS84 / UTM 21S |
| Resolución de píxel | ~43,55 m × 42,33 m |
| Proyección | GEOCODED_TERRAIN |
| Órbita | DESCENDING / RIGHT |
| `Sigma0Type` | `AMPLITUDE` |

**Corrección importante:** este producto TOPSAR/TNB no tiene resolución de 10 m. La resolución observada es aproximadamente **43 × 42 m**.

## Área de interés — geometría maestra

El 24/10/2026 se confirmó manualmente el polígono aproximado del establecimiento. Desde esta versión, esta geometría es la **referencia maestra del proyecto**.

Coordenadas suministradas originalmente en orden latitud, longitud:

```text
-37.204333, -59.346855
-37.198350, -59.339680
-37.211288, -59.322638
-37.217224, -59.329805
-37.204333, -59.346855
```

Para GeoJSON/WKT se almacenan en orden **longitud, latitud**:

```text
POLYGON((-59.346855 -37.204333, -59.339680 -37.198350, -59.322638 -37.211288, -59.329805 -37.217224, -59.346855 -37.204333))
```

Esta geometría reemplaza al polígono aproximado utilizado en versiones anteriores y debe usarse para todos los nuevos recortes, mapas y datasets.

## Objetivo actual: fertilización selectiva

El objetivo inmediato es construir ambientes de manejo dentro de los potreros sembrados con maíz. SAOCOM será una fuente de variables espaciales y temporales, no un estimador directo de dosis.

```text
SAOCOM L1D HH/HV/VH/VV
        ↓
σ⁰ y variables SAR multitemporales
        ↓
Recorte por establecimiento/potrero
        ↓
Topografía + suelo + manejo + clima
        ↓
Patrones espaciales persistentes
        ↓
Ambientes de manejo
        ↓
Validación agronómica
        ↓
Fertilización selectiva
```

## Pipeline real — `La_rosaura.py`

1. Detecta los GeoTIFF L1D aun cuando CONAE los entrega sin extensión.
2. Identifica automáticamente HH, HV, VH y VV.
3. Transforma la geometría maestra WGS84 al CRS real EPSG:32721 y recorta las cuatro polarizaciones.
4. Lee `Sigma0Type=AMPLITUDE` y aplica `σ⁰_dB = 20·log10(amplitud)` sólo para valores positivos.
5. Genera GeoTIFF en amplitud, GeoTIFF en dB, PNG y estadísticas por polarización.
6. Genera mapas basados exclusivamente en píxeles SAOCOM observados, sin matrices aleatorias.

El reporte `inspeccion_saocom.json` registra además la geometría WGS84 utilizada en cada ejecución para mantener trazabilidad espacial.

## Ejecución

```bash
python La_rosaura.py "ruta/al/S1A_OPER_SAR_EOSSP__CORE_L1D_OLF_20260521T202537.zip"
```

## Serie piloto 2024/25

| Fecha | Product ID | Uso preliminar |
|---|---|---|
| 07/09/2024 | `EOL1DSARSAO1A14948810` | Producto real validado / línea base |
| 23/09/2024 | `EOL1DSARSAO1A14948841` | Pre-siembra |
| 09/10/2024 | `EOL1DSARSAO1A14056208` | Implantación (a validar) |
| 25/10/2024 | `EOL1DSARSAO1A14948886` | Emergencia (a validar) |
| 10/11/2024 | `EOL1DSARSAO1A14948797` | Desarrollo inicial (a validar) |
| 12/12/2024 | `EOL1DSARSAO1A15392623` | Desarrollo vegetativo (a validar) |

## Criterios metodológicos

- `σ⁰` mide retrodispersión radar; no equivale por sí sola a humedad del suelo.
- HH/HV/VH/VV responden conjuntamente a humedad, rugosidad, estructura vegetal, geometría y otras propiedades.
- Una escena individual no define ambientes de fertilización.
- Los ambientes se construirán con series temporales y patrones persistentes.
- La dosis final requerirá análisis de suelo, manejo, objetivo productivo y validación de campo.
- No se utilizarán los antiguos valores simulados de 38,16–49,71 TN/ha como resultados del proyecto.

## Próximos hitos

1. Ejecutar el producto piloto con la geometría maestra confirmada.
2. Procesar las escenas restantes de la serie 2024/25.
3. Incorporar los límites de los **16 potreros**.
4. Identificar potreros de maíz y su historial de manejo.
5. Incorporar DEM/topografía y variables de suelo.
6. Construir la tabla por píxel/potrero/fecha para Machine Learning.
7. Explorar y validar ambientes de manejo antes de definir dosis.

## Proyecto académico de Machine Learning

El desarrollo académico asociado se documenta en [`PROYECTO_FACULTAD_ML.md`](PROYECTO_FACULTAD_ML.md) y en el repositorio `ml_fertilizacion_la_rosaura`.

## Dependencias

```bash
pip install numpy rasterio matplotlib
```
