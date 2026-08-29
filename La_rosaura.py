import numpy as np
from shapely.geometry import Polygon

# 1. Identificación fija del Lote (Tandil)
ID_LOTE = "La_Rosaura_Tandil_01"
coordenadas_tandil = [
    [-59.329905, -37.217237], [-59.346728, -37.204268],
    [-59.339732, -37.198320], [-59.322652, -37.211309],
    [-59.329905, -37.217237]
]
lote_la_rosaura = Polygon(coordenadas_tandil)

# 2. BASE DE DATOS DEL PROYECTO (Diccionario histórico por campaña)
# Almacenará el resultado del procesamiento SAOCOM año tras año
historico_campanas = {}

# 3. PIPELINE DE PROCESAMIENTO REPETITIVO ANUAL
def procesar_ciclo_anual_saocom(ano_siembra):
    """
    Ejecuta las 3 fases del pipeline para una campaña específica.
    Abarca desde la siembra (Octubre del año_siembra) hasta la cosecha (Mayo del año_siguiente).
    """
    ano_cosecha = ano_siembra + 1
    nombre_campana = f"{ano_siembra}/{ano_cosecha}"
    
    print(f"\n==================================================")
    print(f"🔄 PROCESANDO CAMPAÑA AGRÍCOLA: {nombre_campana}")
    print(f"==================================================")
    
    # --- FASE 1: Identificación (Octubre - Diciembre del año de siembra) ---
    print(f"🛰️ [Fase 1] Analizando datos SAOCOM (HV/HH) desde 15-Oct-{ano_siembra} a 30-Dic-{ano_siembra}...")
    # Simulación de datos: Suelo desnudo inicial en Octubre -> Crecimiento exponencial en Diciembre
    rvi_inicio = np.random.uniform(0.1, 0.2)
    rvi_pico_fase1 = np.random.uniform(0.5, 0.7)
    
    if rvi_pico_fase1 > 0.5:
        clasificacion = "Maiz_Temprano"
    else:
        clasificacion = "Pastura_o_Tardio"
        
    print(f"     -> Resultado: Curva RVI detectada. Clasificado como: {clasificacion}")

    # --- FASE 2: Estrés Hídrico (Diciembre - Marzo) ---
    print(f"🛰️ [Fase 2] Monitoreando humedad de suelo (HH dB) desde 15-Dic-{ano_siembra} a 15-Mar-{ano_cosecha}...")
    # Simulación de índice de humedad en Tandil (Valores típicos entre -16 dB seco y -6 dB muy húmedo)
    humedad_suelo_db = round(np.random.uniform(-15.0, -8.0), 2)
    alerta_estres = "⚠️ ALERTA: Sequía en floración. Adelantar ventana de picado." if humedad_suelo_db < -13.5 else "✔ Humedad óptima."
    print(f"     -> Resultado: Humedad media: {humedad_suelo_db} dB | Estado: {alerta_estres}")

    # --- FASE 3: Biomasa Máxima y Ventana de Cosecha (Enero - Mayo del año de cosecha) ---
    print(f"🛰️ [Fase 3] Calculando volumen máximo de biomasa y secado de planta hasta Mayo-{ano_cosecha}...")
    # Simulación de rendimiento total alcanzado (Banda L midiendo estructura completa del cultivo)
    biomasa_maxima_tn = round(np.random.uniform(35.0, 48.0), 1)
    materia_seca_final = round(np.random.uniform(31.5, 35.5), 1)
    disparo_picadora = 32.0 <= materia_seca_final <= 35.0
    print(f"     -> Resultado: Biomasa máxima estimada: {biomasa_maxima_tn} TN/HA | Materia Seca: {materia_seca_final}%")

    # --- GUARDAR RESULTADOS EN LA BASE DE DATOS HISTÓRICA ---
    historico_campanas[nombre_campana] = {
        "Clasificacion": clasificacion,
        "Humedad_Suelo_dB": humedad_suelo_db,
        "Biomasa_Max_TN_HA": biomasa_maxima_tn,
        "Materia_Seca_Porcentaje": materia_seca_final,
        "Aviso_Contratista": disparo_picadora
    }

# 4. BUCLE CRONOLÓGICO: Desde el inicio de SAOCOM (2020) hasta la campaña actual (2026)
# El bucle toma el año de inicio de siembra de cada ciclo agrícola
ano_inicio_satelite = 2020
ano_actual_sistema = 2026

for ano in range(ano_inicio_satelite, ano_actual_sistema):
    procesar_ciclo_anual_saocom(ano_siembra=ano)

# 5. RESUMEN FINAL HISTÓRICO
print("\n" + "="*60)
print("📊 RESUMEN EJECUTIVO HISTÓRICO EN GITHUB (2020 - ACTUALIDAD)")
print("="*60)
for campana, datos in historico_campanas.items():
    print(f"Campaña {campana} -> Tipo: {datos['Clasificacion']} | Rendimiento: {datos['Biomasa_Max_TN_HA']} TN/HA | Humedad: {datos['Humedad_Suelo_dB']} dB")
