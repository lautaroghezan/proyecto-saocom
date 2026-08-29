# 🛰️ Pipeline de Monitoreo de Maíz con Satélite SAOCOM (Tandil)

Este proyecto implementa un pipeline automatizado en Python para analizar de forma **anual e histórica** el ciclo biológico del maíz para silo en la región serrana de Tandil, Provincia de Buenos Aires. El software utiliza datos de Radar de Apertura Sintética (SAR) en **Banda L** provenientes de la constelación argentina **SAOCOM (1A y 1B)** de la CONAE.

A diferencia de los sensores ópticos tradicionales (NDVI), la tecnología de radar atraviesa la cubierta de nubes y el follaje de las plantas, midiendo la estructura tridimensional y la humedad real del suelo a una resolución espacial máxima de **10 metros por píxel**.

---

## 📌 El Núcleo del Proyecto: Área de Interés (AOI)

El análisis está centrado exclusivamente en el lote **"La Rosaura"**, ubicado al este de la ciudad de Tandil. El polígono geométrico está definido por las siguientes coordenadas geográficas de precisión (Longitud, Latitud):

*   **Esquina 1:** `-59.329905, -37.217237`
*   **Esquina 2:** `-59.346728, -37.204268`
*   **Esquina 3:** `-59.339732, -37.198320`
*   **Esquina 4:** `-59.322652, -37.211309`

### Formato de consulta internacional (WKT)
Para realizar búsquedas directas en el **Catálogo SAOCOM de la CONAE**, se utiliza el formato Well-Known Text (WKT):
```text
POLYGON((-59.329905 -37.217237, -59.346728 -37.204268, -59.339732 -37.198320, -59.322652 -37.211309, -59.329905 -37.217237))
```

---

## 🔄 Pipeline Cronológico Anual de Procesamiento

El script ejecuta un bucle retrospectivo que procesa la información **año por año desde el inicio de las transmisiones operativas del satélite (2020) hasta la actualidad**, dividiendo el análisis en tres fases críticas por campaña:

### 🌾 Fase 1: Identificación y Clasificación de Lotes (15 Oct – 30 Dic)
*   **Métrica de Radar:** Índice de Vegetación de Radar (RVI) simplificado mediante la fórmula `(4 * HV) / (HH + HV)`.
*   **Lógica:** Detecta el paso de suelo desnudo (mínima vegetación) a crecimiento exponencial. Clasifica el lote automáticamente como *Maíz Temprano*, *Maíz Tardío* o *Pastura Estable* (línea de base sin variaciones abruptas).

### 💧 Fase 2: Monitoreo Crítico de Estrés Hídrico (15 Dic – 15 Mar)
*   **Métrica de Radar:** Amplitud de retrodispersión en polarización copular **HH** convertida a Decibelios (dB).
*   **Lógica:** La Banda L mide la constante dieléctrica del agua en el suelo debajo del cultivo cerrado. Si la señal cae por debajo de los umbrales críticos de sequía durante la floración (R1), el modelo emite una alerta temprana para reprogramar los equipos de picado.

### 🚜 Fase 3: Volumen de Biomasa y Ventana de Picado (Enero – Mayo)
*   **Métrica de Radar:** Polarización cruzada **HV** (sensible a la dispersión volumétrica de tallos y hojas gruesas).
*   **Lógica:** Estima las Toneladas de Materia Verde por Hectárea (TN/HA) sin sufrir la saturación que afecta al NDVI óptico. Monitorea la pérdida de agua libre para alertar cuándo el cultivo entra en la ventana óptima de cosecha (**32% a 35% de Materia Seca**).

---

## 🛠️ Arquitectura de la Base de Datos Geoservicial

Cada ciclo anual alimenta un registro estructurado con las siguientes variables clave:

| Variable | Tipo de Dato | Propósito del Atributo |
| :--- | :--- | :--- |
| **ID_Lote** | Alfanumérico | Identificador único del polígono georreferenciado de Tandil. |
| **Clasificacion** | String | Categoría asignada (Maiz_Temprano, Maiz_Tardio, Pastura). |
| **Humedad_Suelo_dB** | Float (dB) | Nivel de humedad superficial detectado en el canal HH. |
| **Biomasa_Max_TN_HA**| Float (TN/HA) | Volumen verde máximo calculado antes del secado de planta. |
| **Aviso_Contratista**| Booleano | Alerta de disparo (True/False) basada en el rango óptimo de MS. |

---

## 🚀 Cómo Ejecutar el Entorno Local

1. Instalar las dependencias científicas necesarias en tu consola:
   ```bash
   pip install numpy shapely rasterio
   ```
2. Correr el script principal desde la terminal de Visual Studio Code:
   ```bash
   python src/La_rosaura.py
   ```
