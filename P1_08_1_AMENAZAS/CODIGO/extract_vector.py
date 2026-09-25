# -*- coding: utf-8 -*-
"""Extract hazard polygons stored as vector paths in POT-2026 cartography plates (Cartografia 1).
Zones are drawn as filled/stroked paths with legend colours; georeferenced with the 5 km grid labels."""
import sys
import numpy as np
import pymupdf
from osgeo import ogr  # noqa: F401  (import before scipy/shapely deps)
import extract_plate as ep
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
import geopandas as gpd

MAP_XMAX = 985.0     # pt; legend panel starts beyond this


def _rnd(c):
    return tuple(round(x, 2) for x in c) if c else None


def _bez(p0, p1, p2, p3, n=6):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3).tolist()


def _paths(d):
    """Split a drawing into sub-paths (list of point lists)."""
    subs, cur = [], []
    for it in d["items"]:
        k = it[0]
        if k == "re":
            r = it[1]
            subs.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]); continue
        if k == "qu":
            q = it[1]
            subs.append([tuple(q.ul), tuple(q.ur), tuple(q.lr), tuple(q.ll)]); continue
        if k == "l":
            a, b = tuple(it[1]), tuple(it[2]); pts = [a, b]
        elif k == "c":
            pts = [tuple(p) for p in _bez(it[1], it[2], it[3], it[4])]
        else:
            continue
        if cur and np.hypot(cur[-1][0] - pts[0][0], cur[-1][1] - pts[0][1]) < 1e-6:
            cur.extend(pts[1:])
        else:
            if len(cur) > 1: subs.append(cur)
            cur = list(pts)
    if len(cur) > 1: subs.append(cur)
    return subs


def extract(pdf_page_index, colors):
    """colors: dict rgb-tuple -> class name. Returns (polys, lines) dicts class -> shapely geometry in EPSG:9377."""
    doc = pymupdf.open(ep.PDF)
    page = doc[pdf_page_index]
    ax, bx, ay, by = ep.georef(page)
    def tr(pts): return [(ax * x + bx, ay * y + by) for x, y in pts]
    polys = {v: [] for v in colors.values()}
    lines = {v: [] for v in colors.values()}
    for d in page.get_drawings():
        if d["rect"].x0 > MAP_XMAX: continue
        f, c = _rnd(d.get("fill")), _rnd(d.get("color"))
        key = f if f in colors else (c if c in colors else None)
        if key is None: continue
        cls = colors[key]
        subs = _paths(d)
        if f in colors:                               # filled (+ optional stroke)
            geom = None
            for s in subs:
                if len(s) < 3: continue
                p = Polygon(tr(s))
                if not p.is_valid: p = p.buffer(0)
                if p.is_empty: continue
                if d.get("even_odd", True) and geom is not None:
                    geom = geom.symmetric_difference(p)
                else:
                    geom = p if geom is None else geom.union(p)
            if geom is not None and not geom.is_empty: polys[cls].append(geom)
        else:                                          # stroke only
            for s in subs:
                if len(s) < 2: continue
                lines[cls].append(LineString(tr(s)))
    return ({k: unary_union(v) if v else None for k, v in polys.items()},
            {k: unary_union(v) if v else None for k, v in lines.items()})


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    b = ep.read_boundary()
    plates = {
        "inundacion": (5, {(1.0, 0.0, 0.0): "alta", (1.0, 0.83, 0.5): "media", (0.69, 0.88, 0.0): "baja"},
                       {"alta": 575, "media": 195, "baja": 364}),
        "avenidas": (6, {(0.0, 0.15, 0.45): "alta", (0.0, 0.44, 1.0): "media", (0.75, 0.91, 1.0): "baja"},
                     {"alta": 587, "media": 207, "baja": 169}),
    }
    for name, (pi, cols, eba) in plates.items():
        polys, lines = extract(pi, cols)
        print("==", name)
        for cls in ("alta", "media", "baja"):
            p = polys[cls]; l = lines[cls]
            pa = (p.intersection(b).area / 1e4) if p is not None else 0
            la = l.intersection(b).length if l is not None else 0
            print("  %-6s polygon area in district %8.1f ha | stroke lines length %9.0f m | EBA %s ha" % (cls, pa, la, eba[cls]))
