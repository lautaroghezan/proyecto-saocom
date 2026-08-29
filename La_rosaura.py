import numpy as np
from shapely.geometry import Polygon

# 1. Coordenadas de tu campo en Tandil
coordenadas_tandil = [
    [-59.329905, -37.217237],
    [-59.346728, -37.204268],
    [-59.339732, -37.198320],
    [-59.322652, -37.211309],
    [-59.329905, -37.217237]
]
lote_la_rosaura = Polygon(coordenadas_tandil)

# 2. FUNCIÓN MATEMÁTICA PRINCIPAL
def analizar_humedad_y_volumen(matriz_hh, matriz_hv):
    """
    Simula el comportamiento del radar SAOCOM a máxima resolución (10 metros).
    - matriz_hh: Datos de polarización copular (Suelo/Agua)
    - matriz_hv: Datos de polarización cruzada (Hojas/Tallos)
    """
    # Calculamos el RVI (Radar Vegetation Index) para medir el VOLUMEN de las plantas.
    # La fórmula estándar internacional para radares duales es: (4 * HV) / (HH + HV)
    volumen_plantas = (4 * matriz_hv) / (matriz_hh + matriz_hv)
    
    # Calculamos la HUMEDAD transformando la energía del canal HH a Decibelios (dB)
    # En Banda L, a mayor valor de dB (valores más cercanos a cero), más húmedo está el suelo.
    humedad_suelo_db = 10 * np.log10(matriz_hh)
    
    return volumen_plantas, humedad_suelo_db

# 3. PROBANDO EL ALGORITMO (Simulación con datos artificiales de alta resolución)
# Creamos una grilla de 5x5 píxeles de prueba para simular tu lote a 10m de resolución
np.random.seed(42) # Para que los números sean fijos en la prueba
datos_satelitales_hh = np.random.uniform(0.1, 0.5, (5, 5))
datos_satelitales_hv = np.random.uniform(0.01, 0.1, (5, 5))

# Ejecutamos el análisis científico
indice_volumen, mapa_humedad = analizar_humedad_y_volumen(datos_satelitales_hh, datos_satelitales_hv)

print("--- PIPELINE SAOCOM PROCESADO ---")
print(f"Lote: La Rosaura (Tandil)")
print(f"Volumen promedio de vegetación (RVI): {np.mean(indice_volumen):.3f} (Escala 0 a 1)")
print(f"Humedad promedio estimada del suelo: {np.mean(mapa_humedad):.2f} dB")
