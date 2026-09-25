# -*- coding: utf-8 -*-
"""Rebuild a georeferenced class raster from a POT-2026 cartography plate (Cartografia 1, PDF).
The map body is stored as native raster strips (~31.75 m/px at 1:90.000); we decode the strips
without resampling, classify by legend colours and georeference with the 5 km grid labels."""
import sys, glob, re
import numpy as np
import pymupdf
import rasterio
from rasterio.transform import Affine
from rasterio.features import rasterize
from osgeo import ogr
from shapely import wkt
from shapely.geometry import mapping

PDF = glob.glob("C:/Users/marco/Downloads/Cartograf*1.pdf")[0]
BOUND = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg"


def read_boundary():
    ds = ogr.Open(BOUND)
    lyr = ds.GetLayerByName("limite_medellin")
    feat = lyr.GetNextFeature()
    g = feat.GetGeometryRef()
    return wkt.loads(g.ExportToWkt())


def georef(page):
    words = page.get_text("words")
    ex, ey = [], []
    for w in words:
        s = w[4]
        if re.fullmatch(r"4,7\d\d,000", s) and w[1] < 40:      # top labels
            ex.append((int(s.replace(",", "")), (w[0] + w[2]) / 2))
        if re.fullmatch(r"2,2\d\d,000", s) and w[0] < 40:      # left labels
            ey.append((int(s.replace(",", "")), (w[1] + w[3]) / 2))
    E = np.array(ex, float); N = np.array(ey, float)
    ax, bx = np.polyfit(E[:, 1], E[:, 0], 1)     # easting = ax*xpt + bx
    ay, by = np.polyfit(N[:, 1], N[:, 0], 1)     # northing = ay*ypt + by
    return ax, bx, ay, by


def stack_strips(page):
    """Return (array HxWx3 uint8, bbox in pt) from the map body strips (972 px wide)."""
    strips = []
    for info in page.get_image_info(xrefs=True):
        if info["width"] == 972:
            strips.append(info)
    strips.sort(key=lambda i: i["bbox"][1])
    rows = []
    doc = page.parent
    for info in strips:
        pix = pymupdf.Pixmap(doc, info["xref"])
        if pix.n - pix.alpha != 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        arr = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        rows.append(arr)
    img = np.vstack(rows)
    x0 = min(i["bbox"][0] for i in strips); x1 = max(i["bbox"][2] for i in strips)
    y0 = min(i["bbox"][1] for i in strips); y1 = max(i["bbox"][3] for i in strips)
    return img, (x0, y0, x1, y1)


def classify(img, colors, tol=28):
    """colors: dict class_id -> (r,g,b). Returns uint8 class raster (0 = none)."""
    out = np.zeros(img.shape[:2], np.uint8)
    best = np.full(img.shape[:2], 1e9)
    f = img.astype(np.float32)
    for cid, rgb in colors.items():
        d = np.sqrt(((f - np.array(rgb, np.float32)) ** 2).sum(axis=2))
        m = (d < tol) & (d < best)
        out[m] = cid
        best[m] = d[m]
    return out


def build(plate_index, colors, out_tif, tol=28):
    doc = pymupdf.open(PDF)
    page = doc[plate_index]
    ax, bx, ay, by = georef(page)
    img, (x0, y0, x1, y1) = stack_strips(page)
    h, w = img.shape[:2]
    # native pixel size in map units
    px = (x1 - x0) / w * ax
    py = (y1 - y0) / h * ay
    west = ax * x0 + bx
    north = ay * y0 + by
    transform = Affine(px, 0, west, 0, -abs(py), north)
    cls = classify(img, colors, tol)
    with rasterio.open(out_tif, "w", driver="GTiff", height=h, width=w, count=1, dtype="uint8",
                       crs="EPSG:9377", transform=transform, nodata=0, compress="lzw") as dst:
        dst.write(cls, 1)
    return cls, transform, (px, py)


def shares(cls, transform, ids, names):
    b = read_boundary()
    inside = rasterize([mapping(b)], out_shape=cls.shape, transform=transform, fill=0, default_value=1, dtype="uint8").astype(bool)
    cell_ha = abs(transform.a * transform.e) / 1e4
    tot = 0
    res = {}
    for i in ids:
        n = int(((cls == i) & inside).sum())
        res[i] = n
        tot += n
    print("pixel(ha) = %.4f | pixels classified inside the district = %d (= %.0f ha; district polygon = %.0f ha)" % (cell_ha, tot, tot * cell_ha, b.area / 1e4))
    for i in ids:
        print("  %-8s %8.0f ha  %5.2f %%" % (names[i], res[i] * cell_ha, 100 * res[i] / tot))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    OUT = r"C:/Users/marco/AppData/Local/Temp/claude/G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude/446a2666-30c7-4c61-98e1-c82458a0665f/scratchpad/cart1"
    colors = {1: (255, 0, 0), 2: (255, 170, 0), 3: (152, 230, 0)}
    cls, tr, (px, py) = build(4, colors, OUT + "/mm_2026_class.tif")
    print("cell size (m): %.2f x %.2f" % (px, py), "| grid", cls.shape, "| origin", tr.c, tr.f)
    shares(cls, tr, [1, 2, 3], {1: "alta", 2: "media", 3: "baja"})
    print("EBA (Tabla 93): alta 37,25 % | media 14,80 % | baja 47,95 %  (Distrito, 37.639,66 ha)")
