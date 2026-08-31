# 📝 Registro de Cambios (CHANGELOG) - Proyecto SAOCOM

Historial cronológico, técnico y metodológico de la evolución del pipeline de inteligencia satelital para el establecimiento "La Rosaura", Tandil.

---

## [v2.1.0] - Conexión de Producción e Ingesta Binaria - 2026-08-30
### 🚀 Añadido
*   **Decodificador Binario Automático:** Integración de la librería `pandas` y el motor `openpyxl` en el script core para descompresionar y leer la estructura de datos binaria comprimida original (`PK`) proveniente de las descargas masivas del Catálogo SAOCOM.
*   **Limpieza Matricial de Caracteres:** Implementación de un filtro automatizado que remueve comillas internas dobles, espacios ciegos y desalineaciones de cadenas de texto de la CONAE de forma nativa.
*   **Métricas Reales Consolidadas:** El modelo predictivo arrojó los primeros resultados geoespaciales 100% reales vinculados a tu serie histórica: **38.16 TN/HA** de volumen de picado promedio general y un pico máximo proyectado de **49.71 TN/HA** por unidad espacial de 10 metros.

### 🔧 Modificado
*   **`La_rosaura.py`:** Reemplazo de los algoritmos de lectura por renglones de texto plano (que generaban errores de decodificación de caracteres por codificación ANSI/UTF-8) por un motor matricial estructurado indexado por palabras clave (`Product ID`, `Start time`).
*   **Rutas Relativas Definitivas:** Corrección de la duplicación de directorios locales en el código, forzando al script a operar de forma limpia desde la raíz real de la terminal de comandos de VS Code (`proyecto_saocom>`).
*   **Destino de Salida de Cartografía:** Redireccionamiento automático de los mapas de calor (`mapa_humedad_pixel.png` y `mapa_rendimiento_predictivo.png`) para que se exporten y guarden ordenados directamente dentro de la subcarpeta física `data/`.

---

## [v2.0.0] - Fase de Producción Teórica (Metodología L1D) - 2026-08-30
### 🚀 Añadido
*   **Giro Estratégico Multitemporal:** Migración del entorno artificial simulado hacia la indexación de las **167 escenas reales e históricas** del lote de Tandil.
*   **Establecimiento de Nivel L1D:** Configuración metodológica para procesar productos ortorrectificados y planchados geográficamente sobre la topografía, garantizando recortes de precisión mediante máscaras geográficas vectoriales.
*   **Análisis Dual de Radar (QP):** Acople físico de los canales **HH** (Respuesta dieléctrica para humedad subsuperficial profunda) y **HV** (Dispersión volumétrica para biomasa aérea estructural de tallos y hojas).

---

## [v1.1.0] - Segmentación Espacial y Gráficos - 2026-08-29
### 🚀 Añadido
*   **Subdivisión Matricial por Unidad Espacial:** Segmentación analítica del lote en celdas fijas de alta resolución (10x10 metros por píxel).
*   **Mapeo 2D con Matplotlib:** Programación de escalas agronómicas de visualización por colores (Escala Amarillo-Verde-Azul para humedad y Rojo-Amarillo-Verde para rendimiento).

---

## [v1.0.0] - Infraestructura Base y Git - 2021-10-26
### 🚀 Añadido
*   **Entorno Virtual Aislado:** Configuración del contenedor local `(.venv)` y carga inicial de librerías científicas básicas (`numpy`, `shapely`, `rasterio`).
*   **Vinculación Segura del Portfolio:** Autenticación de credenciales criptográficas locales y empuje del proyecto hacia la nube pública de GitHub.
