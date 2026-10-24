"""Pipeline SAOCOM — La Rosaura.

Procesamiento del producto L1D real de CONAE para fertilización selectiva.
El producto piloto confirmó GeoTIFF sin extensión, QP (HH/HV/VH/VV), FLOAT32,
EPSG:32721 y Sigma0Type=AMPLITUDE. Por ello la visualización en dB usa
20*log10(amplitud) únicamente para píxeles positivos y válidos.

El pipeline NO transforma la retrodispersión en humedad, biomasa, rendimiento ni
dosis de fertilizante. Esas inferencias requieren series temporales y validación
agronómica.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom

PRODUCTO_PILOTO = "EOL1DSARSAO1A14948810"
AOI_WGS84 = {
    "type": "Polygon",
    "coordinates": [[
        [-59.329905, -37.217237], [-59.346728, -37.204268],
        [-59.339732, -37.198320], [-59.322652, -37.211309],
        [-59.329905, -37.217237],
    ]],
}
POL_RE = re.compile(r"-(hh|hv|vh|vv)-m$", re.IGNORECASE)


def extraer_zip(zip_path: Path, destino: Path) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    print(f"📦 Extrayendo producto: {zip_path.name}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(destino)
    return destino


def preparar_producto(entrada: Path, workdir: Path) -> Path:
    if entrada.is_dir():
        return entrada
    if entrada.is_file() and entrada.suffix.lower() == ".zip":
        return extraer_zip(entrada, workdir / entrada.stem)
    raise ValueError("La entrada debe ser el ZIP original de CONAE o una carpeta extraída.")


def es_raster_saocom(path: Path) -> bool:
    """Detecta los GeoTIFF L1D aun cuando CONAE los entrega sin extensión."""
    if not path.is_file() or path.suffix.lower() == ".xml":
        return False
    if "Data" not in path.parts:
        return False
    try:
        with rasterio.open(path) as src:
            return src.driver == "GTiff" and src.count >= 1
    except rasterio.errors.RasterioIOError:
        return False


def listar_rasters(producto_dir: Path) -> list[Path]:
    data_dir = producto_dir / "Data"
    if not data_dir.exists():
        return []
    return sorted(p for p in data_dir.iterdir() if es_raster_saocom(p))


def listar_xml(producto_dir: Path) -> list[Path]:
    return sorted(p for p in producto_dir.rglob("*.xml") if p.is_file())


def polarizacion(path: Path) -> str | None:
    m = POL_RE.search(path.name)
    return m.group(1).upper() if m else None


def leer_sigma0_type(producto_dir: Path) -> str | None:
    """Lee Sigma0Type desde Config/L1PROCConf.xml."""
    cfg = producto_dir / "Config" / "L1PROCConf.xml"
    if not cfg.exists():
        return None
    root = ET.parse(cfg).getroot()
    node = root.find(".//Sigma0Type")
    return node.text.strip().upper() if node is not None and node.text else None


def resumir_raster(path: Path) -> dict:
    with rasterio.open(path) as src:
        return {
            "archivo": str(path), "polarizacion": polarizacion(path),
            "driver": src.driver, "crs": str(src.crs) if src.crs else None,
            "ancho": src.width, "alto": src.height, "bandas": src.count,
            "dtype": list(src.dtypes), "nodata": src.nodata,
            "resolucion_m": [abs(src.transform.a), abs(src.transform.e)],
            "bounds": [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top],
        }


def valores_validos(data: np.ndarray, nodata=None) -> np.ndarray:
    arr = np.asarray(data, dtype="float64")
    ok = np.isfinite(arr)
    if nodata is not None:
        ok &= arr != nodata
    return arr[ok]


def estadisticas(data: np.ndarray, nodata=None) -> dict:
    v = valores_validos(data, nodata)
    if not v.size:
        return {"n": 0, "min": None, "media": None, "mediana": None, "max": None}
    return {"n": int(v.size), "min": float(v.min()), "media": float(v.mean()),
            "mediana": float(np.median(v)), "max": float(v.max())}


def amplitud_a_db(data: np.ndarray) -> np.ndarray:
    """Sigma0Type=AMPLITUDE -> sigma0 dB = 20 log10(amplitud)."""
    arr = np.asarray(data, dtype="float64")
    out = np.full(arr.shape, np.nan, dtype="float32")
    ok = np.isfinite(arr) & (arr > 0)
    out[ok] = 20.0 * np.log10(arr[ok])
    return out


def guardar_geotiff(path: Path, data: np.ndarray, perfil: dict, transform, dtype="float32", nodata=np.nan):
    path.parent.mkdir(parents=True, exist_ok=True)
    p = perfil.copy()
    p.update(driver="GTiff", height=data.shape[-2], width=data.shape[-1], count=1,
             transform=transform, dtype=dtype, nodata=nodata)
    with rasterio.open(path, "w", **p) as dst:
        dst.write(data.astype(dtype), 1)


def guardar_mapa_png(db: np.ndarray, path: Path, pol: str):
    valid = db[np.isfinite(db)]
    if not valid.size:
        return
    vmin, vmax = np.percentile(valid, [2, 98])
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(db, vmin=vmin, vmax=vmax, origin="upper", cmap="gray")
    fig.colorbar(im, ax=ax, label="σ⁰ (dB)")
    ax.set_title(f"La Rosaura — SAOCOM L1D {pol} — 07/09/2024")
    ax.set_xlabel("Píxel")
    ax.set_ylabel("Píxel")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def procesar_raster(src_path: Path, salida: Path, sigma0_type: str | None) -> dict:
    pol = polarizacion(src_path) or "NA"
    with rasterio.open(src_path) as src:
        if src.crs is None:
            raise ValueError(f"El raster no declara CRS: {src_path.name}")
        geom = transform_geom("EPSG:4326", src.crs, AOI_WGS84, precision=7)
        recorte_ma, transform = mask(src, [geom], crop=True, filled=False)
        amp = recorte_ma[0].filled(np.nan).astype("float32")
        base = salida / "recortes_aoi" / f"{pol}_La_Rosaura"
        guardar_geotiff(base.with_name(base.name + "_amplitud.tif"), amp, src.profile, transform)

        resultado = {
            "polarizacion": pol,
            "shape": list(amp.shape),
            "estadisticas_amplitud": estadisticas(amp),
            "amplitud_tif": str(base.with_name(base.name + "_amplitud.tif")),
        }
        if sigma0_type == "AMPLITUDE":
            db = amplitud_a_db(amp)
            tif_db = base.with_name(base.name + "_sigma0_db.tif")
            png_db = salida / "mapas" / f"{pol}_La_Rosaura_sigma0_db.png"
            guardar_geotiff(tif_db, db, src.profile, transform)
            guardar_mapa_png(db, png_db, pol)
            resultado.update({
                "sigma0_db_tif": str(tif_db), "mapa_png": str(png_db),
                "estadisticas_sigma0_db": estadisticas(db),
            })
        return resultado


def ejecutar(entrada: Path, salida: Path, product_id: str) -> int:
    salida.mkdir(parents=True, exist_ok=True)
    producto_dir = preparar_producto(entrada, salida / "extraidos")
    rasters = listar_rasters(producto_dir)
    xmls = listar_xml(producto_dir)
    sigma0_type = leer_sigma0_type(producto_dir)

    print("=== 🛰️ SAOCOM — PRODUCTO L1D REAL ===")
    print(f"Producto: {product_id}")
    print(f"GeoTIFF detectados: {len(rasters)}")
    print(f"Polarizaciones: {[polarizacion(p) for p in rasters]}")
    print(f"Sigma0Type: {sigma0_type}")

    if not rasters:
        print("❌ No se detectaron GeoTIFF L1D en Data/.")
        return 2

    inventario = {
        "producto": product_id, "directorio_producto": str(producto_dir),
        "sigma0_type": sigma0_type, "xml_encontrados": len(xmls),
        "rasters": [resumir_raster(p) for p in rasters], "recortes": [],
        "criterio_radiometrico": (
            "20*log10(amplitud) para píxeles > 0" if sigma0_type == "AMPLITUDE"
            else "No aplicado: Sigma0Type no confirmado como AMPLITUDE"
        ),
        "advertencias": [
            "σ0 no se interpreta directamente como humedad, biomasa o rendimiento.",
            "Las dosis de fertilización requieren análisis multitemporal y validación agronómica.",
        ],
    }
    for p in rasters:
        try:
            r = procesar_raster(p, salida, sigma0_type)
            inventario["recortes"].append(r)
            print(f"✔ {r['polarizacion']}: AOI procesado {r['shape']}")
        except Exception as exc:
            inventario.setdefault("errores", []).append(f"{p.name}: {type(exc).__name__}: {exc}")
            print(f"⚠️ {p.name}: {exc}")

    reporte = salida / "inspeccion_saocom.json"
    reporte.write_text(json.dumps(inventario, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"📄 Reporte: {reporte}")
    return 0 if inventario["recortes"] else 3


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Procesa un producto SAOCOM L1D real para La Rosaura.")
    p.add_argument("entrada", type=Path, help="ZIP original de CONAE o directorio extraído.")
    p.add_argument("--salida", type=Path, default=Path("data") / "procesado" / PRODUCTO_PILOTO)
    p.add_argument("--product-id", default=PRODUCTO_PILOTO)
    return p


def main() -> int:
    args = construir_parser().parse_args()
    try:
        return ejecutar(args.entrada, args.salida, args.product_id)
    except Exception as exc:
        print(f"❌ Error fatal: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
