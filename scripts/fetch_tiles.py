#!/usr/bin/env python3
"""Fetch raster map tiles for offline self-hosting.

Downloads OpenStreetMap raster tiles (rendered by FOSSGIS, the OSM
Germany servers) into assets/tiles/map/ so the site's map needs no
external tile server and no API key. One map style is bundled; the
site's dark theme applies a CSS invert filter to the tiles instead.

Note on sources/licensing: tiles are rendered from OpenStreetMap data
(c) OpenStreetMap contributors; the site shows the required
attribution. Only small, one-off downloads like this are appropriate -
never bulk-scrape a tile server.

The homepage map is fixed at a single zoom level (default 6), so by
default only that level is fetched for a bounding box covering the
Mediterranean sailing area plus the Canary Islands.

Usage:
  python3 scripts/fetch_tiles.py --dry-run   # just count tiles
  python3 scripts/fetch_tiles.py             # download
  python3 scripts/fetch_tiles.py --zoom 6-9 --bbox 5,35,25,48
  python3 scripts/fetch_tiles.py --zoom 6 --bbox -18,27,32,50
"""

import argparse
import math
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_BASE = os.path.join(REPO, "assets", "tiles")

TILE_HOSTS = [
    "https://tile.openstreetmap.de/{z}/{x}/{y}.png",
]


def deg2num(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def tiles_for_zoom(zoom, bbox):
    lon_min, lat_min, lon_max, lat_max = bbox
    x0, y0 = deg2num(lat_max, lon_min, zoom)
    x1, y1 = deg2num(lat_min, lon_max, zoom)
    n = int(2.0 ** zoom)
    for x in range(max(0, int(x0)), min(n, int(x1) + 1)):
        for y in range(max(0, int(y0)), min(n, int(y1) + 1)):
            yield zoom, x, y


def parse_zooms(spec):
    zooms = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            zooms.update(range(int(a), int(b) + 1))
        else:
            zooms.add(int(part))
    return sorted(zooms)


def parse_bbox(spec):
    return tuple(float(v) for v in spec.split(","))


def fetch(path, zoom, x, y, retries=4):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return "cached"
    url = TILE_HOSTS[0].format(z=zoom, x=x, y=y)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "sailing-kiruna-tile-fetch/1.0 (github.com/relyant/relyant.github.io)"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            if not data.startswith(b"\x89PNG"):
                raise ValueError("not a PNG")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
            return "ok"
        except Exception as e:
            if attempt == retries - 1:
                return f"error: {e}"
            time.sleep(1.5 * (attempt + 1))
    return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zoom", default="6",
                    help="zoom level(s), e.g. '6' or '0-5' or '2,6-8'")
    ap.add_argument("--bbox", default="-18,27,32,50",
                    help="lon_min,lat_min,lon_max,lat_max")
    ap.add_argument("--themes", default="map", help="(kept for compatibility, ignored)")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    bbox = parse_bbox(args.bbox)
    zooms = parse_zooms(args.zoom)

    jobs = []
    for zoom in zooms:
        for z, x, y in tiles_for_zoom(zoom, bbox):
            path = os.path.join(OUT_BASE, "map", str(z), str(x), f"{y}.png")
            jobs.append((path, z, x, y))

    total = len(jobs)
    print(f"{total} tiles (zoom {args.zoom})")
    if args.dry_run:
        return

    done = errors = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [(job, pool.submit(fetch, *job)) for job in jobs]
        for job, fut in futures:
            result = fut.result()
            done += 1
            if result.startswith("error"):
                errors += 1
                print(f"FAILED z{job[1]} {job[2]},{job[3]}: {result}",
                      file=sys.stderr)
            if done % 100 == 0 or done == total:
                print(f"  {done}/{total} done, {errors} failed, "
                      f"{time.time() - t0:.0f}s")
                sys.stdout.flush()

    print(f"Finished: {done} tiles, {errors} failures.")


if __name__ == "__main__":
    main()
