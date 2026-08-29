# Importamos las herramientas científicas que instalamos
import numpy as np
from shapely.geometry import Polygon

# 1. Definimos las coordenadas del lote La Rosaura en Tandil (Longitud, Latitud)
coordenadas_tandil = [
    [-59.329905, -37.217237],  # Esquina 1
    [-59.346728, -37.204268],  # Esquina 2
    [-59.339732, -37.198320],  # Esquina 3
    [-59.322652, -37.211309],  # Esquina 4
    [-59.329905, -37.217237]   # Cierre del lote (vuelve al punto 1)
]

# 2. Convertimos la lista de números en un polígono geográfico real
lote_la_rosaura = Polygon(coordenadas_tandil)

print("--- PROYECTO SAOCOM: CAMPO LA ROSAURA ---")
print(f"El polígono matemático fue creado con éxito.")
print(f"Área aproximada del lote (en grados al cuadrado): {lote_la_rosaura.area:.6f}")
print("El entorno geoespacial está listo para recibir imágenes satelitales.")
