#!/usr/bin/env python3
"""Consulta reproducible del catálogo STAC de Copernicus para La Rosaura.

Primera etapa: inventariar escenas Sentinel-2 Level-2A de la campaña 2024/25.
No descarga imágenes ni infiere uso del suelo.

Salida por defecto:
    data/catalogos/sentinel2_2024_25.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

STAC_SEARCH_URL = "https://stac.dataspace.copernicus.eu/v1/search"
COLLECTION = "sentinel-2-l2a"
DEFAULT_START = "2024-08-01T00:00:00Z"
DEFAULT_END = "2025-06-30T23:59:59Z"
DEFAULT_GEOJSON = Path("data/potreros_la_rosaura.geojson")
DEFAULT_OUTPUT = Path("data/catalogos/sentinel2_2024_25.csv")


def load_farm_bbox(path: Path) -> list[float]:
    """Calcula [oeste, sur, este, norte] desde los 16 potreros GeoJSON."""
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    features = data.get("features", [])
    if len(features) != 16:
        raise ValueError(f"Se esperaban 16 potreros y se encontraron {len(features)}")

    xs: list[float] = []
    ys: list[float] = []

    def collect(coords: Any) -> None:
        if not coords:
            return
        if isinstance(coords[0], (int, float)):
            xs.append(float(coords[0]))
            ys.append(float(coords[1]))
            return
        for child in coords:
            collect(child)

    for feature in features:
        geometry = feature.get("geometry") or {}
        collect(geometry.get("coordinates", []))

    if not xs or not ys:
        raise ValueError("No se pudieron extraer coordenadas del GeoJSON")

    return [min(xs), min(ys), max(xs), max(ys)]


def post_json(url: str, payload: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/geo+json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"STAC respondió HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"No se pudo conectar con Copernicus STAC: {exc}") from exc


def get_json(url: str, timeout: int = 60) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/geo+json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def search_items(bbox: list[float], start: str, end: str, limit: int = 100) -> list[dict[str, Any]]:
    """Consulta STAC y sigue enlaces rel=next hasta agotar resultados."""
    payload: dict[str, Any] = {
        "collections": [COLLECTION],
        "bbox": bbox,
        "datetime": f"{start}/{end}",
        "limit": limit,
        "sortby": [{"field": "properties.datetime", "direction": "asc"}],
    }

    page = post_json(STAC_SEARCH_URL, payload)
    items = list(page.get("features", []))

    while True:
        next_link = next((link for link in page.get("links", []) if link.get("rel") == "next"), None)
        if not next_link:
            break
        href = next_link.get("href")
        if not href:
            break
        method = str(next_link.get("method", "GET")).upper()
        if method == "POST":
            page = post_json(href, next_link.get("body", payload))
        else:
            page = get_json(href)
        items.extend(page.get("features", []))
        time.sleep(0.1)

    # Protección ante duplicados por paginación o solapes de catálogo.
    unique: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        if item_id:
            unique[item_id] = item
    return sorted(unique.values(), key=lambda x: (x.get("properties", {}).get("datetime", ""), x.get("id", "")))


def first_property(props: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = props.get(name)
        if value is not None:
            return value
    return ""


def item_row(item: dict[str, Any]) -> dict[str, Any]:
    props = item.get("properties", {})
    item_id = item.get("id", "")
    dt = first_property(props, "datetime", "start_datetime")
    date = str(dt)[:10] if dt else ""
    platform = first_property(props, "platform", "constellation")
    tile = first_property(props, "s2:mgrs_tile", "mgrs:utm_zone", "grid:code")
    cloud = first_property(props, "eo:cloud_cover")

    return {
        "fecha": date,
        "datetime_utc": dt,
        "producto_id": item_id,
        "satelite": platform,
        "tile": tile,
        "cloud_cover_producto_pct": cloud,
        "collection": item.get("collection", COLLECTION),
    }


def write_csv(items: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "fecha",
        "datetime_utc",
        "producto_id",
        "satelite",
        "tile",
        "cloud_cover_producto_pct",
        "collection",
    ]
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for item in items:
            writer.writerow(item_row(item))


def main() -> None:
    parser = argparse.ArgumentParser(description="Catálogo Sentinel-2 L2A para La Rosaura vía Copernicus STAC")
    parser.add_argument("--potreros", type=Path, default=DEFAULT_GEOJSON, help="GeoJSON con los 16 potreros")
    parser.add_argument("--inicio", default=DEFAULT_START, help="Inicio ISO-8601 UTC")
    parser.add_argument("--fin", default=DEFAULT_END, help="Fin ISO-8601 UTC")
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT, help="CSV de salida")
    args = parser.parse_args()

    bbox = load_farm_bbox(args.potreros)
    print(f"Colección: {COLLECTION}")
    print(f"BBox exacto derivado de los 16 potreros: {bbox}")
    print(f"Período: {args.inicio} / {args.fin}")
    print("Consultando metadatos; no se descargarán imágenes...")

    items = search_items(bbox, args.inicio, args.fin)
    write_csv(items, args.salida)

    print(f"Escenas encontradas: {len(items)}")
    print(f"Catálogo guardado en: {args.salida}")
    if items:
        dates = [item_row(x)["fecha"] for x in items]
        print(f"Primera fecha: {min(dates)}")
        print(f"Última fecha: {max(dates)}")
        print("Nota: cloud_cover_producto_pct corresponde al producto completo; todavía no mide nubosidad dentro de cada potrero.")


if __name__ == "__main__":
    main()
