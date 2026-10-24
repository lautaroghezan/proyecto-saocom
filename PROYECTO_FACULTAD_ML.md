# 🎓 Proyecto de Machine Learning — Fertilización Selectiva de Maíz

## Caso de estudio: La Rosaura, Tandil

### Pregunta de investigación

**¿Es posible identificar ambientes de manejo útiles para fertilización selectiva en maíz mediante la combinación de series temporales SAR SAOCOM, topografía y datos agronómicos?**

## Objetivo

Desarrollar y evaluar un modelo reproducible de Machine Learning que permita caracterizar la variabilidad espacial de los potreros de maíz de **La Rosaura** y construir ambientes de manejo que puedan ser validados agronómicamente.

El modelo no buscará predecir directamente `kg de fertilizante/ha` a partir de una imagen radar. Primero se modelará el **ambiente o potencial/respuesta del sitio**; la recomendación de dosis será una etapa agronómica posterior.

## Fuente satelital validada

El primer producto real utilizado es `EOL1DSARSAO1A14948810`, adquirido el **07/09/2024**.

La inspección del producto confirmó:

- SAOCOM 1A, nivel L1D;
- TOPSAR / TNB;
- QP: HH, HV, VH y VV;
- GeoTIFF FLOAT32;
- EPSG:32721 (UTM 21S);
- resolución de píxel aproximada de **43,55 × 42,33 m**;
- `Sigma0Type = AMPLITUDE`;
- conversión para valores positivos: `σ⁰_dB = 20·log10(amplitud)`.

Por lo tanto, el trabajo académico utilizará la **resolución observada del producto (~43 m)** y no el supuesto previo de 10 m.

## Unidad de análisis

La unidad de trabajo podrá definirse a nivel de **píxel dentro de potrero y fecha de adquisición**, preservando identificadores que permitan realizar validación espacial y evitar fuga de información entre entrenamiento y prueba.

## Variables candidatas

### SAR SAOCOM
- `σ⁰_HH_dB`
- `σ⁰_HV_dB`
- `σ⁰_VH_dB`
- `σ⁰_VV_dB`
- diferencias/razones entre polarizaciones cuando estén justificadas;
- estadísticos temporales por píxel: media, mediana, variabilidad y evolución;
- índices polarimétricos únicamente cuando su formulación sea compatible con los datos disponibles.

### Topografía
- elevación;
- pendiente;
- posición topográfica relativa;
- variables derivadas de un DEM.

### Agronomía y manejo
Cuando estén disponibles:
- potrero;
- fecha de siembra;
- híbrido;
- densidad;
- análisis de suelo;
- fertilización aplicada;
- precipitaciones/clima;
- observaciones de cultivo;
- rendimiento o producción final de silo.

## Estrategia de Machine Learning

### Etapa 1 — EDA y calidad de datos
- distribución de variables SAR;
- valores faltantes y atípicos;
- correlaciones;
- variabilidad dentro y entre potreros;
- estabilidad temporal de los patrones espaciales.

### Etapa 2 — Ingeniería de atributos
Construcción de atributos multitemporales y combinación con topografía y datos agronómicos.

### Etapa 3 — Aprendizaje no supervisado
Como primera aproximación, identificar ambientes sin imponer una etiqueta de rendimiento:

- K-means como línea base;
- comparación con otros métodos de clustering si aportan valor;
- análisis de estabilidad de los grupos entre fechas/campañas.

Los clusters no se denominarán automáticamente “alto”, “medio” o “bajo potencial” hasta ser contrastados con evidencia agronómica.

### Etapa 4 — Aprendizaje supervisado
Si se obtiene una variable objetivo confiable (rendimiento, materia seca, respuesta a fertilización u otra medición de campo), comparar modelos como:

- regresión/modelo simple de referencia;
- Random Forest;
- Gradient Boosting / XGBoost.

### Etapa 5 — Validación
La partición entrenamiento/prueba deberá respetar la estructura espacial y temporal. Se evitará dividir aleatoriamente píxeles vecinos de un mismo potrero de forma que el modelo vea prácticamente el mismo ambiente en entrenamiento y prueba.

### Etapa 6 — Interpretabilidad
Evaluar importancia de variables y, cuando corresponda, herramientas como SHAP para analizar qué atributos contribuyen a las predicciones.

## Campañas

### 2024/25 — construcción retrospectiva
Se utilizará para desarrollar el pipeline, procesar la serie histórica y construir las primeras variables multitemporales.

### 2026/27 — seguimiento prospectivo
La campaña actual se utilizará para registrar desde el inicio información de manejo y campo, aplicar el pipeline sobre nuevas adquisiciones y generar datos de entrenamiento/validación con mejor trazabilidad.

## Resultado esperado

El resultado académico buscado no es un mapa de fertilización generado automáticamente por el radar, sino un flujo reproducible:

```text
SAOCOM + topografía + suelo + manejo
                 ↓
         dataset espacial
                 ↓
       Machine Learning
                 ↓
     ambientes/potencial
                 ↓
      validación de campo
                 ↓
 decisión agronómica de fertilización
```

## Hipótesis de trabajo

La combinación de información SAR multitemporal con variables topográficas y agronómicas puede capturar patrones espaciales persistentes dentro de los potreros de maíz que sean útiles para definir ambientes de manejo, siempre que esos patrones sean posteriormente validados con datos de campo.

## Estado actual

- [x] AOI de La Rosaura definido.
- [x] Catálogo SAOCOM disponible.
- [x] Primer producto L1D real descargado.
- [x] HH/HV/VH/VV identificados.
- [x] CRS y resolución real verificados.
- [x] Representación `Sigma0Type=AMPLITUDE` verificada.
- [x] Pipeline adaptado para recorte y `σ⁰` en dB.
- [ ] Incorporar geometría de los 16 potreros.
- [ ] Identificar potreros con maíz por campaña.
- [ ] Procesar serie multitemporal.
- [ ] Incorporar DEM/topografía.
- [ ] Incorporar datos de suelo y manejo.
- [ ] Construir dataset de ML.
- [ ] Entrenar y validar modelos.
