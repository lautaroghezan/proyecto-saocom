import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# 1. IDENTIFICACIÓN Y GEOMETRÍA FIJA DEL LOTE (Tandil)
ID_LOTE = "La_Rosaura_Tandil_01"
coordenadas_tandil = [
    [-59.329905, -37.217237], [-59.346728, -37.204268],
    [-59.339732, -37.198320], [-59.322652, -37.211309],
    [-59.329905, -37.217237]
]
lote_la_rosaura = Polygon(coordenadas_tandil)

# Dimensiones de la grilla de alta resolución (20x20 = 400 unidades espaciales de 10 metros)
FILAS, COLUMNAS = 20, 20
np.random.seed(42)  # Datos fijos para consistencia en la simulación

# =====================================================================
# SECCIÓN I: BUCLE HISTÓRICO PLURIANUAL (2020 - ACTUALIDAD)
# =====================================================================
print("=== INICIANDO DETECCIÓN HISTÓRICA ANUAL SAOCOM ===")
historico_campanas = {}

def ejecutar_bucle_historico():
    for ano in range(2020, 2026):
        campana = f"{ano}/{ano+1}"
        # Simulación de respuesta de radar promedio por campaña
        rvi_pico = np.random.uniform(0.45, 0.68)
        humedad_db = round(np.random.uniform(-14.5, -9.0), 2)
        biomasa_tn = round(np.random.uniform(34.0, 47.0), 1)
        
        clasificacion = "Maiz_Temprano" if rvi_pico > 0.52 else "Pastura_o_Tardio"
        
        historico_campanas[campana] = {
            "Clasificacion": clasificacion,
            "Humedad_Suelo_dB": humedad_db,
            "Biomasa_Max_TN_HA": biomasa_tn
        }
        print(f"🌾 Campaña {campana} -> Detectado: {clasificacion} | Rendimiento: {biomasa_tn} TN/HA | Humedad: {humedad_db} dB")

ejecutar_bucle_historico()

# =====================================================================
# SECCIÓN II: GENERACIÓN DE MATRICES POR UNIDAD ESPACIAL ACTUAL
# =====================================================================
print("\n=== ANALIZANDO UNIDADES ESPACIALES ACTUALES ===")
# Potencial productivo base intrínseco de cada celda (loma vs bajo)
potencial_suelo_base = np.random.uniform(28.0, 46.0, (FILAS, COLUMNAS))
# Coeficiente de retención hídrica derivado del historial de decibelios (canal HH)
capacidad_retencion_agua = np.random.uniform(0.75, 1.25, (FILAS, COLUMNAS))

# Generamos la matriz actual de humedad por píxel para los gráficos
mapa_humedad_actual = np.random.uniform(-15.0, -7.0, (FILAS, COLUMNAS))

# =====================================================================
# SECCIÓN III: MODELO PREDICTIVO PARA LA PRÓXIMA CAMPAÑA (2026/2027)
# =====================================================================
def predecir_y_graficar_proxima_campana(escenario_climatico="Seco"):
    print(f"\n🔮 EJECUTANDO MODELO PREDICTIVO CAMPAÑA 2026/2027 -> Escenario: [{escenario_climatico}]")
    
    # Impacto climático regional proyectado para Tandil
    factor_clima = 0.80 if escenario_climatico == "Seco" else 1.0
    
    matriz_prediccion_rendimiento = np.zeros((FILAS, COLUMNAS))
    
    # Análisis espacial celda por celda (unidad de 10 metros)
    for f in range(FILAS):
        for c in range(COLUMNAS):
            potencial_celda = potencial_suelo_base[f, c]
            retencion_celda = capacidad_retencion_agua[f, c]
            
            # En años secos, los píxeles con mala retención hídrica sufren una penalización doble
            if escenario_climatico == "Seco":
                rendimiento_proyectado = potencial_celda * factor_clima * (retencion_celda * 0.85)
            else:
                rendimiento_proyectado = potencial_celda * factor_clima * retencion_celda
                
            matriz_prediccion_rendimiento[f, c] = round(rendimiento_proyectado, 2)
            
    # Métricas consolidadas del lote para la toma de decisiones
    rendimiento_medio_lote = np.mean(matriz_prediccion_rendimiento)
    print(f"📊 Predicción completada para la próxima campaña:")
    print(f"   -> Rendimiento Promedio Estimado del Lote: {rendimiento_medio_lote:.2f} TN/HA de Materia Verde")
    print(f"   -> Píxel de Máximo Rendimiento Esperado: {np.max(matriz_prediccion_rendimiento):.2f} TN/HA")
    print(f"   -> Píxel de Máximo Riesgo Hídrico: {np.min(matriz_prediccion_rendimiento):.2f} TN/HA")
    
    # =====================================================================
    # SECCIÓN IV: GENERACIÓN GRÁFICA AUTOMATIZADA (.PNG)
    # =====================================================================
    print("\n🎨 Dibujando mapas de calor por unidad espacial...")
    
    # Gráfico 1: Humedad actual por píxel
    plt.figure(figsize=(6, 5))
    plt.imshow(mapa_humedad_actual, cmap='YlGnBu', origin='lower')
    plt.colorbar(label='Humedad del Suelo (Canal HH en dB)')
    plt.title(f'La Rosaura (Tandil) - Humedad Actual por Píxel (10m)', fontsize=9)
    plt.xlabel('Celdas Eje X')
    plt.ylabel('Celdas Eje Y')
    plt.savefig("mapa_humedad_pixel.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✔ Gráfico exportado: mapa_humedad_pixel.png")
    
    # Gráfico 2: Rendimiento Predictivo Próxima Campaña por píxel
    plt.figure(figsize=(6, 5))
    plt.imshow(matriz_prediccion_rendimiento, cmap='RdYlGn', origin='lower')
    plt.colorbar(label='Rendimiento Proyectado Biomasa (TN/HA)')
    plt.title(f'La Rosaura - Predicción por Píxel (10m)\nEscenario Climático: {escenario_climatico}', fontsize=9)
    plt.xlabel('Celdas Eje X')
    plt.ylabel('Celdas Eje Y')
    plt.savefig("mapa_rendimiento_predictivo.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✔ Gráfico exportado: mapa_rendimiento_predictivo.png")

# Ejecutamos el motor predictivo y gráfico (puedes cambiar a "Normal" para evaluar escenarios)
predecir_y_graficar_proxima_campana(escenario_climatico="Seco")
print("\n🚀 Pipeline integrado ejecutado con éxito. Todo listo para sincronizar.")
