#!/usr/bin/env python3
"""Inspecciona los assets STAC de una escena Sentinel-2 L2A sobre La Rosaura.

Objetivo: antes de implementar descargas/recortes masivos, comprobar cómo el
catálogo real de Copernicus expone bandas ópticas y capas de calidad.

No descarga rasters. Genera un JSON con el item seleccionado y un CSV con sus
assets, href, tipo y roles. Por defecto elige la escena con menor nubosidad
global del producto dentro de la campaña 2024/25; esa nubosidad NO equivale a
nubosidad local sobre los potreros.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from sentinel2_la_rosaura import DEFAULT_END, DEFAULT_GEOJSON, DEFAULT_START, item_row, load_farm_bbox, search_items

DEFAULT_DIR = Path("data/catalogos/inspeccion_sentinel2")


def cloud_value(item: dict[str, Any]) -> float:
    value = (item.get("properties") or {}).get("eo:cloud_cover")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def select_item(items: list[dict[str, Any]], item_id: str | None) -> dict[str, Any]:
    if not items:
        raise RuntimeError("La consulta STAC no devolvió escenas.")
    if item_id:
        for item in items:
            if item.get("id") == item_id:
                return item
        raise RuntimeError(f"No se encontró el producto solicitado: {item_id}")
    return min(items, key=lambda x: (cloud_value(x), (x.get("properties") or {}).get("datetime", "")))


def asset_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, asset in sorted((item.get("assets") or {}).items()):
        eo_bands = asset.get("eo:bands") or []
        band_names = ",".join(str(b.get("name", "")) for b in eo_bands if isinstance(b, dict))
        common_names = ",".join(str(b.get("common_name", "")) for b in eo_bands if isinstance(b, dict))
        rows.append({
            "asset_key": key,
            "title": asset.get("title", ""),
            "roles": ",".join(asset.get("roles") or []),
            "type": asset.get("type", ""),
            "band_names": band_names,
            "common_names": common_names,
            "href": asset.get("href", ""),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspecciona assets de una escena Sentinel-2 L2A real")
    parser.add_argument("--potreros", type=Path, default=DEFAULT_GEOJSON)
    parser.add_argument("--inicio", default=DEFAULT_START)
    parser.add_argument("--fin", default=DEFAULT_END)
    parser.add_argument("--producto-id", default=None, help="ID exacto; si se omite elige menor nubosidad global")
    parser.add_argument("--salida-dir", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()

    bbox = load_farm_bbox(args.potreros)
    print("Consultando STAC para seleccionar una escena piloto...")
    items = search_items(bbox, args.inicio, args.fin)
    item = select_item(items, args.producto_id)
    row = item_row(item)

    args.salida_dir.mkdir(parents=True, exist_ok=True)
    safe_id = str(item.get("id", "sentinel2_item")).replace("/", "_")
    json_path = args.salida_dir / f"{safe_id}.json"
    csv_path = args.salida_dir / f"{safe_id}_assets.csv"

    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(item, fh, ensure_ascii=False, indent=2)

    rows = asset_rows(item)
    fields = ["asset_key", "title", "roles", "type", "band_names", "common_names", "href"]
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

    print(f"Producto piloto: {row['producto_id']}")
    print(f"Fecha: {row['fecha']}")
    print(f"Nubosidad global del producto: {row['cloud_cover_producto_pct']}%")
    print(f"Assets encontrados: {len(rows)}")
    print(f"Item STAC: {json_path}")
    print(f"Tabla de assets: {csv_path}")
    print("\nAssets disponibles:")
    for r in rows:
        label = r["title"] or r["common_names"] or r["band_names"]
        print(f"  {r['asset_key']}: {label}")
    print("\nSiguiente etapa: identificar B2/B3/B4/B8 y capa de calidad en esta salida real; después implementar recorte RGB/NDVI sobre La Rosaura.")


if __name__ == "__main__":
    main()
