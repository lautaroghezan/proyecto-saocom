# 🛰️ Proyecto SAOCOM — La Rosaura

Pipeline de análisis SAR para el establecimiento **La Rosaura**, Tandil, orientado actualmente a **fertilización selectiva de los potreros de maíz**.

## Estado actual — primer producto real validado

El producto piloto `EOL1DSARSAO1A14948810` (adquisición 07/09/2024), solicitado a CONAE mediante el pedido **#1189052**, ya fue recibido e inspeccionado.

La inspección del ZIP y sus XML confirmó:

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

**Corrección importante:** este producto TOPSAR/TNB no tiene resolución de 10 m. La resolución observada es aproximadamente **43 × 42 m**. Toda documentación y análisis del proyecto debe utilizar la resolución real del producto.

## Área de interés

```text
POLYGON((-59.329905 -37.217237, -59.346728 -37.204268, -59.339732 -37.198320, -59.322652 -37.211309, -59.329905 -37.217237))
```

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

La versión actual fue adaptada al formato efectivamente entregado por CONAE.

### 1. Detección del producto real

El script ya no depende de la extensión `.tif`: abre los archivos de `Data/` con `rasterio` y verifica que sean GeoTIFF. Esto permite reconocer los cuatro rasters que CONAE entrega sin extensión.

### 2. Identificación automática de polarizaciones

Se identifican **HH, HV, VH y VV** a partir de los nombres de los archivos y se registran en `inspeccion_saocom.json`.

### 3. Recorte a La Rosaura

El AOI se transforma desde WGS84 al CRS real del raster (**EPSG:32721**) y cada polarización se recorta conservando los valores originales de amplitud.

En el producto piloto, el recorte del establecimiento ocupa aproximadamente **50 × 51 píxeles** antes de aplicar la máscara exacta del polígono.

### 4. Representación radiométrica verificada

El archivo `Config/L1PROCConf.xml` declara:

```xml
<Sigma0Type>AMPLITUDE</Sigma0Type>
```

Por lo tanto, para píxeles positivos y válidos, el pipeline genera la representación de sigma cero en decibeles mediante:

```text
σ⁰_dB = 20 · log10(amplitud)
```

Los valores no positivos se excluyen de la transformación logarítmica.

### 5. Productos generados

Para cada polarización se generan:

- GeoTIFF del recorte en amplitud original;
- GeoTIFF de `σ⁰` en dB;
- mapa PNG de `σ⁰` en dB;
- estadísticas descriptivas;
- reporte técnico `inspeccion_saocom.json`.

### 6. Primer mapa SAR real

El pipeline ya puede generar mapas del establecimiento basados **exclusivamente en píxeles SAOCOM observados**, sin matrices aleatorias ni rendimiento simulado.

Estos mapas representan retrodispersión SAR. **No deben etiquetarse directamente como mapas de humedad, biomasa o rendimiento.**

## Ejecución

```bash
python La_rosaura.py "ruta/al/S1A_OPER_SAR_EOSSP__CORE_L1D_OLF_20260521T202537.zip"
```

Salida esperada:

```text
data/procesado/EOL1DSARSAO1A14948810/
├── extraidos/
├── recortes_aoi/
│   ├── HH_La_Rosaura_amplitud.tif
│   ├── HH_La_Rosaura_sigma0_db.tif
│   ├── HV_La_Rosaura_amplitud.tif
│   ├── HV_La_Rosaura_sigma0_db.tif
│   ├── VH_La_Rosaura_amplitud.tif
│   ├── VH_La_Rosaura_sigma0_db.tif
│   ├── VV_La_Rosaura_amplitud.tif
│   └── VV_La_Rosaura_sigma0_db.tif
├── mapas/
│   ├── HH_La_Rosaura_sigma0_db.png
│   ├── HV_La_Rosaura_sigma0_db.png
│   ├── VH_La_Rosaura_sigma0_db.png
│   └── VV_La_Rosaura_sigma0_db.png
└── inspeccion_saocom.json
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
- Los ambientes se construirán con **series temporales y patrones persistentes**.
- La dosis final requerirá análisis de suelo, manejo, objetivo productivo y validación de campo.
- No se utilizarán los antiguos valores simulados de 38,16–49,71 TN/ha como resultados del proyecto.

## Próximos hitos — fertilización selectiva

1. Procesar las escenas restantes de la serie 2024/25 con el mismo pipeline.
2. Incorporar los límites de los **16 potreros** de La Rosaura.
3. Identificar los potreros de maíz y su historial de manejo.
4. Incorporar topografía/DEM y variables de suelo disponibles.
5. Construir una tabla por píxel/potrero/fecha con variables SAR y agronómicas.
6. Explorar clustering para ambientes de manejo.
7. Validar los ambientes con información de campo antes de definir dosis.
8. Utilizar la campaña 2026/27 como campaña prospectiva de seguimiento y generación de datos.

## Proyecto académico de Machine Learning

El desarrollo académico asociado se documenta por separado en [`PROYECTO_FACULTAD_ML.md`](PROYECTO_FACULTAD_ML.md). El problema de ML se centrará en la **identificación y validación de ambientes para fertilización selectiva**, utilizando SAOCOM como una de las fuentes de atributos.

## Dependencias

```bash
pip install numpy rasterio matplotlib
```
