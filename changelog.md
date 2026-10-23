# 📝 Registro de Cambios (CHANGELOG) — Proyecto SAOCOM

Historial técnico y metodológico del pipeline de inteligencia satelital para el establecimiento **La Rosaura**, Tandil.

---

## [v3.0.0] - Transición a SAR real y ambientes de fertilización - 2026-10-23

### 🎯 Nuevo objetivo
- Se redefine el objetivo operativo hacia la construcción de **ambientes de manejo para fertilización variable en potreros sembrados con maíz**.
- Se adopta un enfoque multitemporal: las zonas de manejo no se determinarán a partir de una única escena SAR, sino mediante patrones espaciales persistentes y su posterior validación agronómica.

### 🛰️ Selección de datos reales
- Revisión del catálogo disponible de **167 productos SAOCOM L1D** que cubren el área de interés.
- Priorización de adquisiciones comparables en nivel **L1D**, polarización **QP**, modo **TOPSAR/TNB**, observación **RIGHT**, órbita **DESCENDING**, **Path 145** y **Row 214**.
- Selección de una serie piloto de la campaña 2024/25:
  - `EOL1DSARSAO1A14948810` — 07/09/2024
  - `EOL1DSARSAO1A14948841` — 23/09/2024
  - `EOL1DSARSAO1A14056208` — 09/10/2024
  - `EOL1DSARSAO1A14948886` — 25/10/2024
  - `EOL1DSARSAO1A14948797` — 10/11/2024
  - `EOL1DSARSAO1A15392623` — 12/12/2024
- Se selecciona `EOL1DSARSAO1A14948810` (07/09/2024) como **producto piloto** para iniciar la ingesta raster real.

### 🔬 Correcciones metodológicas
- Se establece una separación explícita entre **metadatos reales del catálogo** y **datos raster SAR reales**.
- Los mapas generados por las versiones previas contienen componentes simulados y no deben considerarse mediciones observadas de humedad, biomasa o rendimiento.
- Se elimina como supuesto metodológico la interpretación de HH como medición directa de “humedad profunda”.
- Se elimina como supuesto la conversión directa de HV a biomasa o TN/ha sin calibración de campo.
- No se realizará ninguna conversión radiométrica a dB hasta verificar en los metadatos del producto L1D si los valores almacenados representan amplitud, intensidad, sigma0 lineal u otra magnitud.
- Las etapas fenológicas asociadas a las fechas del catálogo se consideran hipótesis hasta disponer de las fechas reales de siembra y manejo.

### 🌽 Arquitectura objetivo

```text
SAOCOM L1D real
    ↓
Polarizaciones SAR + metadatos
    ↓
Calibración / control de calidad
    ↓
Recorte a La Rosaura y potreros
    ↓
Serie temporal por píxel
    ↓
Patrones espaciales persistentes
    ↓
Ambientes de manejo
    ↓
Análisis de suelo + manejo + rendimiento
    ↓
Prescripción de fertilización variable
```

### ⏭️ Próximo hito
- Descargar e inspeccionar el producto completo `EOL1DSARSAO1A14948810`.
- Verificar XML, polarizaciones, CRS, resolución, dimensiones, NoData y representación radiométrica.
- Recortar el producto al AOI de La Rosaura.
- Generar el **primer mapa del proyecto basado exclusivamente en píxeles SAR observados**.

---

## [v2.1.0] - Conexión al catálogo CONAE - 2026-08-30

### Añadido
- Integración de `pandas` y `openpyxl` para leer el catálogo SAOCOM distribuido en formato Excel.
- Extracción de identificadores de producto y fechas de adquisición desde el catálogo.
- Exportación de mapas experimentales a la carpeta `data/`.

### Aclaración posterior (v3.0.0)
Los valores de **38.16 TN/HA** de promedio y **49.71 TN/HA** de máximo producidos en esta etapa procedían de un modelo que todavía utilizaba matrices aleatorias/simuladas. Se conservan como parte del historial de desarrollo, pero **no constituyen resultados geoespaciales reales ni mediciones SAOCOM**.

---

## [v2.0.0] - Preparación metodológica L1D - 2026-08-30

### Añadido
- Migración conceptual desde el entorno simulado hacia la indexación de **167 productos reales del catálogo SAOCOM**.
- Selección del nivel L1D como base para la futura ingesta de productos geocodificados.
- Incorporación conceptual de las polarizaciones QP para análisis SAR multitemporal.

### Aclaración posterior (v3.0.0)
Esta versión indexó **metadatos de productos reales**, pero todavía no procesaba los píxeles de los GeoTIFF L1D. Las relaciones entre retrodispersión, humedad del suelo y biomasa deberán calibrarse y validarse antes de su utilización agronómica.

---

## [v1.1.0] - Segmentación espacial y gráficos - 2026-08-29

### Añadido
- Desarrollo experimental de una grilla matricial para análisis espacial.
- Generación de mapas 2D con `matplotlib`.
- Primer prototipo de visualización de variabilidad espacial.

---

## [v1.0.0] - Infraestructura base y Git - 2021-10-26

### Añadido
- Configuración inicial del entorno Python.
- Incorporación de librerías científicas y geoespaciales básicas.
- Publicación inicial del proyecto en GitHub.
