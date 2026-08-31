# 🛰️ Pipeline de Inteligencia Satelital SAOCOM - Ingesta Histórica Real (Tandil)

Este repositorio aloja el núcleo del software diseñado para el análisis **histórico, espacial y predictivo** del cultivo de maíz para silo en el lote **"La Rosaura"**, Tandil, Provincia de Buenos Aires. El sistema procesa la información por **Unidad Espacial** a una resolución nativa de 10 metros por píxel utilizando datos de Radar de Apertura Sintética (SAR) en **Banda L** provenientes de la constelación argentina **SAOCOM 1A y 1B (CONAE)**.

Al operar en Banda L (microondas), el pipeline evita la interferencia de la cubierta de nubes (frecuente en la primavera/otoño de Tandil) y penetra la canopia del cultivo, midiendo el volumen estructural real de la planta entera y la humedad de la tierra subsuperficial.

---

## 📌 El Núcleo del Proyecto: Área de Interés (AOI)

El polígono del establecimiento agrícola está georreferenciado de forma estricta al este de la Ruta Nacional 226 por las siguientes coordenadas geográficas de precisión (Longitud, Latitud):
*   **Esquina 1:** `-59.329905, -37.217237`
*   **Esquina 2:** `-59.346728, -37.204268`
*   **Esquina 3:** `-59.339732, -37.198320`
*   **Esquina 4:** `-59.322652, -37.211309`

### Formato de Consulta WKT Internacional
```text
POLYGON((-59.329905 -37.217237, -59.346728 -37.204268, -59.339732 -37.198320, -59.322652 -37.211309, -59.329905 -37.217237))
```

---

## 🔬 Especificaciones de la Base de Datos Real Ingestada

El software ha dejado atrás la etapa de simulación y se encuentra acoplado a un paquete masivo de **167 escenas satelitales reales** descargadas del catálogo oficial, que cubren cronológicamente toda la vida operativa de la misión (2020 a la actualidad). 

La idoneidad y precisión del set de datos se fundamenta en tres pilares técnicos:

### 1. Nivel de Procesamiento L1D (Mapeo Terrestre Plano)
A diferencia de los productos crudos (L1A), las imágenes seleccionadas corresponden al nivel **L1D**. Esto significa que la CONAE entregó los archivos con **ortorrectificación geométrica completa**, totalmente planchados sobre la topografía real de Tandil. Esto permite que la máscara geográfica del campo calce con precisión milimétrica sobre las matrices numéricas, descartando el resto de la provincia de forma automatizada.

### 2. Polarización Cuádruple QP (Quad-Pol)
Todas las órbitas ingestadas operan en modo **QP**, el cual emite y recibe pulsos de energía en todas las combinaciones de ondas posibles. De este paquete, el pipeline extrae por separado los dos canales indispensables para el negocio:
*   **Canal HH:** Mide la respuesta dieléctrica del agua en el suelo. El script convierte la amplitud a **Decibelios (dB)** para calcular la humedad profunda de la tierra, incluso con el maíz totalmente cerrado.
*   **Canal HV:** Registra la despolarización volumétrica que ocurre cuando la onda de radar choca contra estructuras erectas y gruesas. Se utiliza para calcular el **Índice de Vegetación de Radar (RVI)** y estimar el volumen de biomasa de la planta entera sin sufrir la saturación que afecta al NDVI óptico.

---

## 🔄 Flujo Operativo del Pipeline (Análisis y Segmentación Anual)

El script de Python ejecuta un procesamiento secuencial integrado sobre los archivos `.tif` de la carpeta `data/`:

1.  **Ingesta de Campo Completo:** El software abre la imagen satelital general del establecimiento descargada del [Catálogo SAOCOM de la CONAE](https://conae.gov.ar). Esto optimiza el disco duro y el tiempo de procesamiento, realizando una sola descarga multitemporal cada 8 días.
2.  **Segmentación Geoespacial Interna:** Utilizando la librería `shapely`, el script divide matemáticamente la grilla general para extraer y procesar de forma independiente los datos de los **16 lotes internos** del establecimiento.
3.  **Modelo Predictivo Acoplado:** Evalúa el potencial histórico de cada lote frente a las variables hídricas de la campaña, proyectando qué sectores específicos sostendrán su volumen verde y cuáles corren riesgo de secado forzado.
4.  **Generación de Alertas de MS:** Monitorea la pérdida de agua en los tejidos para alertar al productor el momento exacto en que cada lote ingresa en la ventana óptima de picado (**32% a 35% de Materia Seca**).

---

## 📊 Cartografía de Salida por Píxel (10m)

El pipeline utiliza la librería `matplotlib` para exportar de manera automatizada mapas de calor 2D de alta resolución:
*   **`mapa_humedad_pixel.png`:** Mapea el patrón hídrico estable promedio del suelo (bajos hidrológicos vs lomas secas).
*   **`mapa_rendimiento_predictivo.png`:** Proyecta la distribución de toneladas de biomasa por hectárea (TN/HA) esperadas para la próxima campaña.

---

## 🚀 Cómo Ejecutar el Entorno Local

1. Activar tu entorno virtual e instalar las dependencias científicas necesarias en la consola:
   ```bash
   pip install numpy shapely matplotlib rasterio
   ```
2. Colocar las bandas `.tif` extraídas del ZIP en la carpeta `data/` respetando el formato de fecha: `S1B_AAAAMMDD_L1D_HH.tif`.
3. Correr el pipeline integrado:
   ```bash
   python La_rosaura.py
   ```
