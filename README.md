# 🛰️ Proyecto SAOCOM — La Rosaura

Pipeline de análisis satelital para el establecimiento **La Rosaura**, Tandil, Provincia de Buenos Aires, orientado al estudio multitemporal del cultivo de maíz y al desarrollo de **ambientes de manejo para fertilización variable**.

## Estado actual del proyecto

El proyecto se encuentra en transición desde un entorno de simulación hacia el procesamiento de **datos SAR reales de SAOCOM 1A/1B (CONAE)**.

Actualmente se dispone de un catálogo de **167 productos SAOCOM L1D** que cubren el área de interés. El catálogo contiene metadatos reales de adquisición, pero el pipeline todavía no debe considerarse un procesador de píxeles SAR reales hasta incorporar y validar los productos raster L1D descargados de CONAE.

> **Importante:** los mapas y métricas generados por versiones anteriores del script contienen componentes simulados. No deben interpretarse como mediciones reales de humedad, biomasa, rendimiento o materia seca.

## Área de interés (AOI)

Polígono general del establecimiento:

```text
POLYGON((-59.329905 -37.217237, -59.346728 -37.204268, -59.339732 -37.198320, -59.322652 -37.211309, -59.329905 -37.217237))
```

## Objetivo actual: fertilización variable

La nueva etapa busca identificar **ambientes de manejo dentro de los potreros sembrados con maíz** mediante análisis multitemporal.

```text
SAOCOM L1D
   ↓
Bandas/polarizaciones SAR reales
   ↓
Calibración y control de calidad
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

Las etapas fenológicas indicadas son hipótesis de trabajo basadas en la fecha y deberán contrastarse con las fechas reales de siembra y manejo.

### Producto piloto

El primer producto elegido para pasar a procesamiento raster real es:

**`EOL1DSARSAO1A14948810` — 07/09/2024**

Se eligió como línea base por encontrarse antes del período principal de desarrollo del cultivo y formar parte de una secuencia temporal comparable aproximadamente cada 16 días.

## Próxima etapa técnica

1. Descargar el producto L1D completo `EOL1DSARSAO1A14948810` desde CONAE.
2. Inspeccionar la estructura del producto y sus metadatos XML.
3. Identificar las polarizaciones disponibles (HH, HV, VH, VV).
4. Verificar CRS, resolución espacial, NoData, dimensiones y representación radiométrica.
5. Determinar a partir de los metadatos si los valores corresponden a amplitud, intensidad u otra magnitud antes de realizar cualquier conversión a dB.
6. Recortar el raster al AOI de La Rosaura.
7. Generar el primer mapa basado exclusivamente en píxeles SAR observados.
8. Repetir el procesamiento sobre las restantes escenas comparables de la campaña.
9. Construir ambientes de manejo multitemporales y validarlos agronómicamente.

## Criterios metodológicos

- No interpretar HH como una medición directa de “humedad profunda”.
- No interpretar HV como toneladas de biomasa sin calibración.
- No estimar TN/ha o porcentaje de materia seca únicamente a partir de SAR sin datos de campo.
- Mantener geometrías de adquisición comparables en los análisis multitemporales siempre que sea posible.
- Separar claramente variables observadas por el radar de variables agronómicas inferidas mediante modelos.

## Dependencias previstas

```bash
pip install numpy pandas shapely matplotlib rasterio openpyxl
```

El pipeline definitivo de ingesta raster será actualizado una vez inspeccionado el primer producto L1D real.
