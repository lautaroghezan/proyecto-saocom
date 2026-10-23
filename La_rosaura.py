"""Pipeline SAOCOM — La Rosaura.

Etapa v3: transición desde datos simulados hacia productos SAR L1D reales.

Este módulo NO estima humedad del suelo, biomasa, rendimiento, materia seca ni
recomendaciones de fertilización. Primero inspecciona el producto SAOCOM,
identifica sus rasters y metadatos, valida cobertura/CRS y recorta las bandas al
AOI del establecimiento conservando los valores originales.

La conversión radiométrica (por ejemplo a dB) se incorporará únicamente después
de verificar en los metadatos oficiales del producto qué magnitud almacenan los
rasters (amplitud, intensidad, sigma0 u otra).
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom


PRODUCTO_PILOTO = "EOL1DSARSAO1A14948810"

# AOI general de La Rosaura en WGS84 (lon, lat).
AOI_WGS84 = {
    "type": "Polygon",
    "coordinates": [[
        [-59.329905, -37.217237],
        [-59.346728, -37.204268],
        [-59.339732, -37.198320],
        [-59.322652, -37.211309],
        [-59.329905, -37.217237],
    ]],
}

EXTENSIONES_RASTER = {".tif", ".tiff"}
EXTENSIONES_METADATA = {".xml"}


def listar_archivos(ruta: Path, extensiones: set[str]) -> list[Path]:
    """Busca archivos recursivamente por extensión."""
    return sorted(
        p for p in ruta.rglob("*")
        if p.is_file() and p.suffix.lower() in extensiones
    )


def extraer_zip(zip_path: Path, destino: Path) -> Path:
    """Extrae un producto ZIP sin modificar el archivo original."""
    destino.mkdir(parents=True, exist_ok=True)
    print(f"📦 Extrayendo producto: {zip_path.name}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(destino)
    return destino


def preparar_producto(entrada: Path, workdir: Path) -> Path:
    """Acepta un ZIP de CONAE o una carpeta ya extraída."""
    if entrada.is_dir():
        return entrada
    if entrada.is_file() and entrada.suffix.lower() == ".zip":
        return extraer_zip(entrada, workdir / entrada.stem)
    raise ValueError("La entrada debe ser el ZIP original de CONAE o una carpeta extraída.")


def resumir_raster(path: Path) -> dict:
    """Lee únicamente metadatos raster; no aplica transformaciones radiométricas."""
    with rasterio.open(path) as src:
        return {
            "archivo": str(path),
            "driver": src.driver,
            "crs": str(src.crs) if src.crs else None,
            "ancho": src.width,
            "alto": src.height,
            "bandas": src.count,
            "dtype": list(src.dtypes),
            "nodata": src.nodata,
            "resolucion": [abs(src.transform.a), abs(src.transform.e)],
            "bounds": [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top],
            "descripciones": list(src.descriptions),
        }


def estadisticas_validas(data: np.ndarray, nodata: float | int | None) -> dict:
    """Calcula estadísticas descriptivas de valores observados, sin interpretarlos."""
    arr = np.asarray(data, dtype="float64")
    validos = np.isfinite(arr)
    if nodata is not None:
        validos &= arr != nodata
    valores = arr[validos]
    if valores.size == 0:
        return {"n": 0, "min": None, "media": None, "max": None}
    return {
        "n": int(valores.size),
        "min": float(np.min(valores)),
        "media": float(np.mean(valores)),
        "max": float(np.max(valores)),
    }


def recortar_aoi(src_path: Path, salida: Path) -> dict:
    """Recorta un raster al AOI y conserva sus valores y tipo de datos originales."""
    with rasterio.open(src_path) as src:
        if src.crs is None:
            raise ValueError(f"El raster no declara CRS: {src_path.name}")

        geom = transform_geom("EPSG:4326", src.crs, AOI_WGS84, precision=7)
        recorte, transform = mask(src, [geom], crop=True, nodata=src.nodata)

        perfil = src.profile.copy()
        perfil.update(
            height=recorte.shape[1],
            width=recorte.shape[2],
            transform=transform,
        )

        salida.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(salida, "w", **perfil) as dst:
            dst.write(recorte)

        return {
            "archivo_origen": str(src_path),
            "archivo_salida": str(salida),
            "crs": str(src.crs),
            "shape": list(recorte.shape),
            "estadisticas_banda_1": estadisticas_validas(recorte[0], src.nodata),
        }


def contiene_id_producto(paths: Iterable[Path], product_id: str) -> bool:
    """Comprueba si el ID esperado aparece en algún nombre/ruta del producto."""
    product_id = product_id.upper()
    return any(product_id in str(p).upper() for p in paths)


def ejecutar(entrada: Path, salida: Path, product_id: str) -> int:
    salida.mkdir(parents=True, exist_ok=True)
    producto_dir = preparar_producto(entrada, salida / "extraidos")

    rasters = listar_archivos(producto_dir, EXTENSIONES_RASTER)
    metadatos = listar_archivos(producto_dir, EXTENSIONES_METADATA)
    todos = rasters + metadatos

    print("=== 🛰️ SAOCOM — INGESTA RASTER REAL ===")
    print(f"Producto esperado: {product_id}")
    print(f"Directorio inspeccionado: {producto_dir}")
    print(f"GeoTIFF encontrados: {len(rasters)}")
    print(f"XML encontrados: {len(metadatos)}")

    if not rasters:
        print("❌ No se encontraron archivos .tif/.tiff. No se generarán mapas ni inferencias.")
        return 2

    if todos and not contiene_id_producto(todos, product_id):
        print("⚠️ El ID esperado no aparece en los nombres de los archivos. Revisar antes de interpretar resultados.")

    inventario = {
        "producto_esperado": product_id,
        "entrada": str(entrada),
        "directorio_producto": str(producto_dir),
        "xml": [str(p) for p in metadatos],
        "rasters": [],
        "recortes": [],
        "advertencias": [
            "No se aplicó conversión a dB.",
            "No se interpretaron polarizaciones como humedad o biomasa.",
            "No se estimaron TN/ha, materia seca ni dosis de fertilizante.",
        ],
    }

    recortes_dir = salida / "recortes_aoi"

    for raster in rasters:
        try:
            resumen = resumir_raster(raster)
            inventario["rasters"].append(resumen)
            print(
                f"✔ {raster.name}: {resumen['ancho']}x{resumen['alto']} px | "
                f"{resumen['bandas']} banda(s) | CRS={resumen['crs']} | "
                f"res={resumen['resolucion']}"
            )

            destino = recortes_dir / f"{raster.stem}_La_Rosaura.tif"
            info_recorte = recortar_aoi(raster, destino)
            inventario["recortes"].append(info_recorte)
            print(f"  ↳ AOI recortado: {destino}")
        except Exception as exc:
            mensaje = f"{raster.name}: {type(exc).__name__}: {exc}"
            inventario.setdefault("errores", []).append(mensaje)
            print(f"⚠️ {mensaje}")

    reporte = salida / "inspeccion_saocom.json"
    reporte.write_text(json.dumps(inventario, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n📄 Reporte técnico: {reporte}")
    print("ℹ️ Próximo paso: inspeccionar los XML para definir calibración radiométrica y polarizaciones.")

    return 0 if inventario["recortes"] else 3


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspecciona y recorta un producto SAOCOM L1D real para La Rosaura."
    )
    parser.add_argument(
        "entrada",
        type=Path,
        help="Ruta al ZIP original de CONAE o al directorio del producto ya extraído.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("data") / "procesado" / PRODUCTO_PILOTO,
        help="Directorio de salida del procesamiento.",
    )
    parser.add_argument(
        "--product-id",
        default=PRODUCTO_PILOTO,
        help="ID SAOCOM esperado para control de integridad.",
    )
    return parser


def main() -> int:
    args = construir_parser().parse_args()
    try:
        return ejecutar(args.entrada, args.salida, args.product_id)
    except Exception as exc:
        print(f"❌ Error fatal: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
