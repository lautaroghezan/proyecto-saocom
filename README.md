# 🛰️ Proyecto SAOCOM — La Rosaura

Pipeline de análisis satelital para el establecimiento **La Rosaura**, Tandil, Provincia de Buenos Aires, orientado al estudio multitemporal del cultivo de maíz y al desarrollo de **ambientes de manejo para fertilización variable**.

## Estado actual del proyecto

El proyecto se encuentra en transición desde un entorno de simulación hacia el procesamiento de **datos SAR reales de SAOCOM 1A/1B (CONAE)**.

Se dispone de un catálogo de **167 productos SAOCOM L1D** que cubren el área de interés. El catálogo contiene metadatos reales de adquisición. Desde la versión v3, `La_rosaura.py` ya no genera matrices aleatorias ni estimaciones simuladas de humedad, biomasa o rendimiento: está preparado para inspeccionar y recortar productos raster L1D reales.

> **Importante:** los mapas y métricas generados por versiones anteriores del script contienen componentes simulados. No deben interpretarse como mediciones reales de humedad, biomasa, rendimiento o materia seca.

## Área de interés (AOI)

Polígono general del establecimiento en WGS84:

```text
POLYGON((-59.329905 -37.217237, -59.346728 -37.204268, -59.339732 -37.198320, -59.322652 -37.211309, -59.329905 -37.217237))
```

## Objetivo actual: fertilización variable

La nueva etapa busca identificar **ambientes de manejo dentro de los potreros sembrados con maíz** mediante análisis multitemporal.

```text
SAOCOM L1D real
   ↓
Bandas/polarizaciones SAR + XML
   ↓
Control de calidad y calibración radiométrica
   ↓
Recorte al establecimiento y potreros
   ↓
Serie temporal por píxel
   ↓
Patrones espaciales persistentes
   ↓
Ambientes de manejo
   ↓
Validación con información agronómica
   ↓
Mapa de prescripción de fertilización
```

La señal SAR no se convertirá directamente en dosis de fertilizante. La prescripción deberá calibrarse con información de campo como análisis de suelo, fertilización histórica y, cuando esté disponible, rendimiento o producción de silo.

## Serie piloto seleccionada — campaña 2024/25

Se priorizó una serie homogénea de productos **L1D, QP, TOPSAR/TNB, RIGHT, órbita descendente, Path 145 y Row 214**.

| Fecha | Product ID | Uso preliminar |
|---|---|---|
| 07/09/2024 | `EOL1DSARSAO1A14948810` | Línea base / pre-siembra |
| 23/09/2024 | `EOL1DSARSAO1A14948841` | Pre-siembra |
| 09/10/2024 | `EOL1DSARSAO1A14056208` | Implantación (a validar) |
| 25/10/2024 | `EOL1DSARSAO1A14948886` | Emergencia (a validar) |
| 10/11/2024 | `EOL1DSARSAO1A14948797` | Desarrollo inicial (a validar) |
| 12/12/2024 | `EOL1DSARSAO1A15392623` | Desarrollo vegetativo (a validar) |

Las etapas fenológicas son hipótesis de trabajo basadas en la fecha y deberán contrastarse con las fechas reales de siembra y manejo.

## Producto piloto y pedido CONAE

El primer producto elegido para procesamiento raster real es:

**`EOL1DSARSAO1A14948810` — 07/09/2024**

El producto fue solicitado en el catálogo SAOCOM de CONAE el **23/10/2026**:

- Pedido: **#1189052**
- Título: `La_Rosaura_SAOCOM_20240907`
- Nivel: **L1D**
- Modo: **TOPSAR / TNB**
- Polarización: **QP**
- Órbita: **DESCENDING / RIGHT**
- Aplicación temática: **Agriculture and Forestry**
- Estado al momento de esta actualización: **REQUESTED**

## Pipeline v3 — `La_rosaura.py`

La versión actual elimina la simulación y acepta como entrada el **ZIP original entregado por CONAE** o un directorio donde el producto ya haya sido extraído.

El pipeline actualmente puede:

1. Extraer el ZIP sin modificar el archivo original.
2. Buscar recursivamente archivos GeoTIFF (`.tif` / `.tiff`) y metadatos XML.
3. Inventariar CRS, dimensiones, número de bandas, tipo de dato, NoData, resolución y extensión geográfica de cada raster.
4. Transformar el AOI WGS84 al CRS propio de cada raster.
5. Recortar cada raster al polígono de La Rosaura conservando los valores originales.
6. Calcular estadísticas descriptivas básicas de los valores observados sin asignarles todavía una interpretación agronómica.
7. Exportar un reporte reproducible `inspeccion_saocom.json`.
8. Detenerse de forma segura si no encuentra rasters o si un archivo no declara CRS.

### Ejecución

Una vez recibido el producto de CONAE:

```bash
python La_rosaura.py "ruta/al/producto_CONAE.zip"
```

Por defecto, para el producto piloto las salidas se almacenarán en:

```text
data/
└── procesado/
    └── EOL1DSARSAO1A14948810/
        ├── extraidos/
        ├── recortes_aoi/
        │   └── *_La_Rosaura.tif
        └── inspeccion_saocom.json
```

También pueden definirse otro ID y directorio de salida mediante `--product-id` y `--salida`.

## Qué todavía NO hace el pipeline

Hasta inspeccionar el XML y los rasters reales del producto, el software deliberadamente **no**:

- convierte los valores a dB;
- interpreta HH como humedad del suelo;
- interpreta HV como biomasa;
- calcula RVI u otros índices sin verificar primero las polarizaciones y representación radiométrica;
- estima TN/ha o porcentaje de materia seca;
- genera dosis de fertilización.

La fórmula radiométrica correcta se determinará a partir de los metadatos oficiales del producto. No se asumirá de antemano si corresponde una transformación basada en amplitud, potencia, sigma0 u otra magnitud.

## Próximos hitos

1. Esperar la publicación del pedido CONAE **#1189052**.
2. Descargar y conservar el ZIP original de `EOL1DSARSAO1A14948810`.
3. Ejecutar el pipeline v3 y revisar `inspeccion_saocom.json`.
4. Inspeccionar los XML para identificar polarizaciones y representación radiométrica.
5. Implementar y validar la calibración correspondiente.
6. Generar el primer mapa basado exclusivamente en píxeles SAR observados.
7. Incorporar los límites de los potreros y determinar cuáles estuvieron sembrados con maíz en 2024/25.
8. Procesar las restantes escenas comparables de la serie piloto.
9. Construir ambientes de manejo multitemporales y validarlos agronómicamente.

## Dependencias

```bash
pip install numpy rasterio
```

Las dependencias adicionales se incorporarán únicamente cuando sean necesarias para las siguientes etapas del pipeline.
