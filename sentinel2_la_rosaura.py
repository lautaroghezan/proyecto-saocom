#!/usr/bin/env python3
"""Consulta reproducible del catálogo STAC de Copernicus para La Rosaura.

Etapa 1: inventariar escenas Sentinel-2 Level-2A de una campaña.
Etapa 2: resumir cobertura temporal y generar una selección preliminar por fecha.

No descarga imágenes ni infiere uso del suelo. La nubosidad usada en esta etapa
corresponde al producto completo, no a cada potrero.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
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
            xs.append(float(coords[0])); ys.append(float(coords[1])); return
        for child in coords:
            collect(child)

    for feature in features:
        collect((feature.get("geometry") or {}).get("coordinates", []))
    if not xs or not ys:
        raise ValueError("No se pudieron extraer coordenadas del GeoJSON")
    return [min(xs), min(ys), max(xs), max(ys)]


def post_json(url: str, payload: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/json", "Accept": "application/geo+json"}, method="POST")
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
    payload: dict[str, Any] = {"collections": [COLLECTION], "bbox": bbox,
        "datetime": f"{start}/{end}", "limit": limit,
        "sortby": [{"field": "properties.datetime", "direction": "asc"}]}
    page = post_json(STAC_SEARCH_URL, payload)
    items = list(page.get("features", []))
    while True:
        next_link = next((link for link in page.get("links", []) if link.get("rel") == "next"), None)
        if not next_link or not next_link.get("href"):
            break
        if str(next_link.get("method", "GET")).upper() == "POST":
            page = post_json(next_link["href"], next_link.get("body", payload))
        else:
            page = get_json(next_link["href"])
        items.extend(page.get("features", [])); time.sleep(0.1)
    unique = {item.get("id"): item for item in items if item.get("id")}
    return sorted(unique.values(), key=lambda x: (x.get("properties", {}).get("datetime", ""), x.get("id", "")))


def first_property(props: dict[str, Any], *names: str) -> Any:
    for name in names:
        if props.get(name) is not None:
            return props[name]
    return ""


def item_row(item: dict[str, Any]) -> dict[str, Any]:
    props = item.get("properties", {})
    dt = first_property(props, "datetime", "start_datetime")
    return {"fecha": str(dt)[:10] if dt else "", "datetime_utc": dt,
        "producto_id": item.get("id", ""), "satelite": first_property(props, "platform", "constellation"),
        "tile": first_property(props, "s2:mgrs_tile", "mgrs:utm_zone", "grid:code"),
        "cloud_cover_producto_pct": first_property(props, "eo:cloud_cover"),
        "collection": item.get("collection", COLLECTION)}


def write_rows(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["fecha", "datetime_utc", "producto_id", "satelite", "tile", "cloud_cover_producto_pct", "collection"]
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(rows)


def safe_cloud(row: dict[str, Any]) -> float:
    try:
        return float(row["cloud_cover_producto_pct"])
    except (TypeError, ValueError):
        return float("inf")


def analyze(rows: list[dict[str, Any]], output: Path) -> None:
    if not rows:
        return
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_date[row["fecha"]].append(row)
    selected = [min(group, key=safe_cloud) for _, group in sorted(by_date.items())]
    selected_path = output.with_name(output.stem + "_seleccion_preliminar.csv")
    write_rows(selected, selected_path)

    dates = sorted(datetime.strptime(d, "%Y-%m-%d").date() for d in by_date)
    gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
    clouds = [safe_cloud(r) for r in rows if safe_cloud(r) != float("inf")]
    platforms = Counter(str(r["satelite"]) for r in rows)
    tiles = Counter(str(r["tile"]) for r in rows)
    monthly = Counter(d.strftime("%Y-%m") for d in dates)

    summary_path = output.with_name(output.stem + "_resumen.txt")
    with summary_path.open("w", encoding="utf-8") as fh:
        fh.write(f"Escenas: {len(rows)}\nFechas únicas: {len(by_date)}\n")
        fh.write(f"Primera fecha: {dates[0]}\nÚltima fecha: {dates[-1]}\n")
        if gaps:
            fh.write(f"Intervalo mediano entre fechas únicas: {statistics.median(gaps):.1f} días\n")
            fh.write(f"Intervalo máximo entre fechas únicas: {max(gaps)} días\n")
        if clouds:
            fh.write(f"Nubosidad mediana del producto: {statistics.median(clouds):.1f}%\n")
        fh.write("Plataformas: " + ", ".join(f"{k}={v}" for k, v in platforms.items()) + "\n")
        fh.write("Tiles/códigos: " + ", ".join(f"{k}={v}" for k, v in tiles.items()) + "\n")
        fh.write("Fechas únicas por mes:\n")
        for month, n in sorted(monthly.items()):
            fh.write(f"  {month}: {n}\n")
        fh.write("\nADVERTENCIA: la selección preliminar usa nubosidad del producto completo. No descarta escenas definitivamente.\n")
        fh.write("La selección científica final se hará después de medir nubes/sombras y píxeles válidos dentro de L01-L16.\n")

    print(f"Fechas únicas: {len(by_date)}")
    if gaps:
        print(f"Intervalo mediano entre fechas: {statistics.median(gaps):.1f} días; máximo: {max(gaps)} días")
    print(f"Selección preliminar por fecha: {selected_path}")
    print(f"Resumen temporal: {summary_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Catálogo Sentinel-2 L2A para La Rosaura vía Copernicus STAC")
    parser.add_argument("--potreros", type=Path, default=DEFAULT_GEOJSON)
    parser.add_argument("--inicio", default=DEFAULT_START); parser.add_argument("--fin", default=DEFAULT_END)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    bbox = load_farm_bbox(args.potreros)
    print(f"Colección: {COLLECTION}\nBBox exacto derivado de los 16 potreros: {bbox}\nPeríodo: {args.inicio} / {args.fin}")
    print("Consultando metadatos; no se descargarán imágenes...")
    items = search_items(bbox, args.inicio, args.fin)
    rows = [item_row(x) for x in items]
    write_rows(rows, args.salida)
    print(f"Escenas encontradas: {len(rows)}\nCatálogo guardado en: {args.salida}")
    if rows:
        print(f"Primera fecha: {min(r['fecha'] for r in rows)}\nÚltima fecha: {max(r['fecha'] for r in rows)}")
        analyze(rows, args.salida)
        print("Nota: cloud_cover_producto_pct corresponde al producto completo; todavía no mide nubosidad dentro de cada potrero.")


if __name__ == "__main__":
    main()
