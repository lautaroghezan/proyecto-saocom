#!/usr/bin/env python3
"""Visualiza una escena Sentinel-2 L2A sobre La Rosaura.

Selecciona por defecto la escena con menor nubosidad global de la campaña
2024/25, lee remotamente sólo la ventana que cubre los 16 potreros y genera:
  - RGB verdadero B04/B03/B02 a 10 m
  - NDVI B08/B04 a 10 m
con límites y etiquetas L01-L16.

La nubosidad global sólo sirve para elegir una escena piloto. Este script no
clasifica cultivos ni reemplaza el control local posterior con SCL/CLD.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom

from sentinel2_la_rosaura import load_farm_bbox, search_items

DEFAULT_GEOJSON = Path("data/potreros_la_rosaura.geojson")
DEFAULT_OUT = Path("salidas_sentinel2")
START = "2024-08-01T00:00:00Z"
END = "2025-06-30T23:59:59Z"


def cloud(item):
    try:
        return float(item.get("properties", {}).get("eo:cloud_cover"))
    except (TypeError, ValueError):
        return float("inf")


def choose_item(items, product_id=None):
    if product_id:
        for item in items:
            if item.get("id") == product_id:
                return item
        raise ValueError(f"No se encontró producto_id={product_id}")
    return min(items, key=lambda x: (cloud(x), x.get("properties", {}).get("datetime", "")))


def asset_href(item, key):
    asset = item.get("assets", {}).get(key)
    if not asset or not asset.get("href"):
        raise KeyError(f"El producto no expone el asset {key}")
    return asset["href"]


def load_features(path):
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("features", [])


def read_crop(href, features):
    with rasterio.Env(GDAL_HTTP_MULTIRANGE="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(href) as src:
            geoms = [transform_geom("EPSG:4326", src.crs, f["geometry"], precision=6) for f in features]
            arr, transform = mask(src, geoms, crop=True, filled=True, nodata=0)
            return arr[0].astype("float32"), transform, src.crs


def stretch(x):
    valid = x[np.isfinite(x) & (x > 0)]
    if valid.size == 0:
        return np.zeros_like(x, dtype="float32")
    lo, hi = np.percentile(valid, [2, 98])
    if hi <= lo:
        hi = lo + 1
    return np.clip((x - lo) / (hi - lo), 0, 1)


def transformed_boundaries(features, crs):
    result = []
    for f in features:
        g = transform_geom("EPSG:4326", crs, f["geometry"], precision=6)
        result.append((f, g))
    return result


def plot_boundaries(ax, boundaries):
    for feature, geom in boundaries:
        rings = geom["coordinates"] if geom["type"] == "Polygon" else [p for poly in geom["coordinates"] for p in poly]
        for ring in rings:
            xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
            ax.plot(xs, ys, linewidth=0.8)
        ring = rings[0]
        cx = sum(p[0] for p in ring[:-1]) / max(1, len(ring)-1)
        cy = sum(p[1] for p in ring[:-1]) / max(1, len(ring)-1)
        pid = feature.get("properties", {}).get("potrero_id", "")
        ax.text(cx, cy, pid, fontsize=7, ha="center", va="center")


def extent_from_transform(transform, shape):
    h, w = shape
    left = transform.c; top = transform.f
    right = left + transform.a * w
    bottom = top + transform.e * h
    return [left, right, bottom, top]


def main():
    ap = argparse.ArgumentParser(description="RGB y NDVI Sentinel-2 piloto sobre La Rosaura")
    ap.add_argument("--potreros", type=Path, default=DEFAULT_GEOJSON)
    ap.add_argument("--producto-id", default=None, help="ID STAC exacto; si se omite elige menor nubosidad global")
    ap.add_argument("--salida", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    features = load_features(args.potreros)
    if len(features) != 16:
        raise ValueError(f"Se esperaban 16 potreros y se encontraron {len(features)}")
    bbox = load_farm_bbox(args.potreros)
    items = search_items(bbox, START, END)
    item = choose_item(items, args.producto_id)
    props = item.get("properties", {})
    date = str(props.get("datetime", ""))[:10]
    print(f"Producto: {item.get('id')}")
    print(f"Fecha: {date}; nubosidad global: {cloud(item)}%")
    print("Leyendo sólo el recorte de La Rosaura desde B02/B03/B04/B08...")

    b02, tr, crs = read_crop(asset_href(item, "B02_10m"), features)
    b03, _, _ = read_crop(asset_href(item, "B03_10m"), features)
    b04, _, _ = read_crop(asset_href(item, "B04_10m"), features)
    b08, _, _ = read_crop(asset_href(item, "B08_10m"), features)

    rgb = np.dstack([stretch(b04), stretch(b03), stretch(b02)])
    denom = b08 + b04
    ndvi = np.full(b04.shape, np.nan, dtype="float32")
    valid = (b04 > 0) & (b08 > 0) & (denom != 0)
    ndvi[valid] = (b08[valid] - b04[valid]) / denom[valid]

    args.salida.mkdir(parents=True, exist_ok=True)
    extent = extent_from_transform(tr, b04.shape)
    boundaries = transformed_boundaries(features, crs)

    rgb_path = args.salida / f"{date}_RGB_La_Rosaura.png"
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(rgb, extent=extent, origin="upper")
    plot_boundaries(ax, boundaries)
    ax.set_title(f"La Rosaura — Sentinel-2 RGB — {date}")
    ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
    fig.tight_layout(); fig.savefig(rgb_path, dpi=180); plt.close(fig)

    ndvi_path = args.salida / f"{date}_NDVI_La_Rosaura.png"
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(ndvi, extent=extent, origin="upper", vmin=-0.2, vmax=1.0)
    plot_boundaries(ax, boundaries)
    ax.set_title(f"La Rosaura — Sentinel-2 NDVI — {date}")
    ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
    fig.colorbar(im, ax=ax, label="NDVI")
    fig.tight_layout(); fig.savefig(ndvi_path, dpi=180); plt.close(fig)

    print(f"RGB guardado: {rgb_path}")
    print(f"NDVI guardado: {ndvi_path}")
    print("Control visual solamente: una fecha aislada no permite clasificar maíz/pastura ni definir fertilización.")

if __name__ == "__main__":
    main()
