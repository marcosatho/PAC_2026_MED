# -*- coding: utf-8 -*-
"""Full classification of the POT 2026 mass-movement plate (Cartografia 1, plate 05).
Every pixel inside the district belongs to one of the three hazard classes (the classes tile the district),
so each pixel takes the nearest legend colour. Thin 'medium' (orange) fringes that appear where red meets green
(colour blending at class borders) are reassigned to the nearest of red/green (2x2 opening).
Output: uint8 GeoTIFF (EPSG:9377), 1 = high, 2 = medium, 3 = low, 0 = outside the district."""
import sys
import numpy as np
import pymupdf
import rasterio
from rasterio.transform import Affine
from rasterio.features import rasterize
from shapely.geometry import mapping
import extract_plate as ep
from scipy import ndimage as ndi

OUT = sys.argv[1]
EBA = {1: 37.25, 2: 14.80, 3: 47.95}
COLORS = {1: (255, 0, 0), 2: (255, 170, 0), 3: (152, 230, 0)}

doc = pymupdf.open(ep.PDF)
page = doc[4]
ax, bx, ay, by = ep.georef(page)
img, (x0, y0, x1, y1) = ep.stack_strips(page)
h, w = img.shape[:2]
transform = Affine((x1 - x0) / w * ax, 0, ax * x0 + bx, 0, -abs((y1 - y0) / h * ay), ay * y0 + by)
inside = rasterize([mapping(ep.read_boundary())], out_shape=(h, w), transform=transform, fill=0,
                   default_value=1, dtype="uint8").astype(bool)
f = img.astype(np.float32)
dist = np.stack([np.sqrt(((f - np.array(COLORS[k], np.float32)) ** 2).sum(axis=2)) for k in (1, 2, 3)], axis=0)


def shares(cls, label):
    n = {k: int(((cls == k) & inside).sum()) for k in (1, 2, 3)}
    t = sum(n.values())
    print("%-42s" % label, " ".join("%s %5.2f (%+.2f)" % (nm, 100 * n[k] / t, 100 * n[k] / t - EBA[k])
                                    for k, nm in ((1, "alta"), (2, "media"), (3, "baja"))))


nearest = dist.argmin(axis=0) + 1
shares(nearest, "nearest colour, no cleanup")
media = nearest == 2
opened = ndi.binary_opening(media, structure=np.ones((2, 2)))
cls = nearest.copy()
removed = media & ~opened
cls[removed] = np.where(dist[0][removed] < dist[2][removed], 1, 3)
shares(cls, "nearest + 2x2 opening on medium")
opened3 = ndi.binary_opening(media, structure=np.ones((3, 3)))
cls3 = nearest.copy()
rem3 = media & ~opened3
cls3[rem3] = np.where(dist[0][rem3] < dist[2][rem3], 1, 3)
shares(cls3, "nearest + 3x3 opening on medium")

cls = np.where(inside, cls, 0).astype(np.uint8)
with rasterio.open(OUT, "w", driver="GTiff", height=h, width=w, count=1, dtype="uint8", crs="EPSG:9377",
                   transform=transform, nodata=0, compress="lzw") as dst:
    dst.write(cls, 1)
print("saved", OUT, "| cells inside:", int(inside.sum()), "| cell size %.2f x %.2f m" % (transform.a, -transform.e))
