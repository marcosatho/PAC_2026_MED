# -*- coding: utf-8 -*-
"""Utilidades comunes para los mapas del P2 (prospectiva climática). Solo lectura de los datos del PAC; las salidas van al scratchpad."""
import sys, os, json, warnings
SCR = r"C:\Users\marco\AppData\Local\Temp\claude\G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude\446a2666-30c7-4c61-98e1-c82458a0665f\scratchpad"
sys.path.append(SCR + r"\libs")
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import PathPatch, Polygon as MplPolygon
from matplotlib.path import Path
from matplotlib.ticker import ScalarFormatter
from shapely.geometry import shape, mapping
from shapely.ops import transform as shp_transform
from pyproj import Transformer

P2 = SCR + r"\p2"
FIG = P2 + r"\figs"
os.makedirs(FIG, exist_ok=True)
BASE = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA"
        r"\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION")
SIATA = BASE + r"\08_1_AMENAZAS\01_DAGRD_SIATA_ESCENARIOS\01_DATOS_ORIGINALES\Archivos_Soporte"
LIM = BASE + r"\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910"
T4326_9377 = Transformer.from_crs("EPSG:4326", "EPSG:9377", always_xy=True)

def _geoms(path):
    d = json.load(open(path, encoding="utf-8"))
    return [shape(f["geometry"]) for f in d["features"]], d["features"]

def district():
    gs, _ = _geoms(LIM + r"\limite_medellin_4326.geojson")
    g = gs[0] if len(gs) == 1 else gs[0].union(*gs[1:]) if hasattr(gs[0], "union") else gs[0]
    from shapely.ops import unary_union
    g = unary_union(gs)
    return shp_transform(lambda x, y, z=None: T4326_9377.transform(x, y), g)

def divisions():
    gs, feats = _geoms(LIM + r"\comunas_corregimientos_4326.geojson")
    return [shp_transform(lambda x, y, z=None: T4326_9377.transform(x, y), g) for g in gs]

BOUND = district()
DIVS = divisions()
XMIN, YMIN, XMAX, YMAX = BOUND.bounds

def load9377(path, resolution=None, resampling=Resampling.nearest, nodata_gt=1e30, kelvin=False):
    with rasterio.open(path) as s:
        kw = {"resolution": resolution} if resolution else {}
        tr, w, h = calculate_default_transform(s.crs, "EPSG:9377", s.width, s.height, *s.bounds, **kw)
        arr = np.full((h, w), np.nan, "float32")
        reproject(rasterio.band(s, 1), arr, src_transform=s.transform, src_crs=s.crs, dst_transform=tr, dst_crs="EPSG:9377",
                  resampling=resampling, src_nodata=s.nodata, dst_nodata=np.nan)
    arr[np.abs(arr) > nodata_gt] = np.nan
    arr[arr == -9999] = np.nan
    if kelvin: arr = arr - 273.15
    return arr, tr

def inside_mask(shape_hw, tr, all_touched=True):
    return rasterize([mapping(BOUND)], out_shape=shape_hw, transform=tr, fill=0, default_value=1, dtype="uint8", all_touched=all_touched).astype(bool)

def extent(arr, tr):
    return (tr.c, tr.c + arr.shape[1] * tr.a, tr.f + arr.shape[0] * tr.e, tr.f)

def fill_district_gaps(arr, tr, n=3):
    inside = inside_mask(arr.shape, tr)
    for _ in range(n):
        for r, c in np.argwhere(inside & np.isnan(arr)):
            win = arr[max(r - 1, 0): r + 2, max(c - 1, 0): c + 2]
            if np.isfinite(win).any(): arr[r, c] = np.nanmean(win)
    return arr, inside

def poly_patch(ax, g=BOUND, **kw):
    from shapely.geometry import MultiPolygon
    polys = list(g.geoms) if isinstance(g, MultiPolygon) else [g]
    verts, codes = [], []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            xy = np.array(ring.coords)
            verts.extend(xy); codes.extend([Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY])
    return PathPatch(Path(verts, codes), **kw)

def draw_lines(ax, color="#252525", lw=0.3, alpha=0.8, z=4):
    for g in DIVS:
        for p in (g.geoms if hasattr(g, "geoms") else [g]):
            xy = np.array(p.exterior.coords); ax.plot(xy[:, 0], xy[:, 1], color=color, lw=lw, alpha=alpha, zorder=z)
    from shapely.geometry import MultiPolygon
    for p in (BOUND.geoms if isinstance(BOUND, MultiPolygon) else [BOUND]):
        xy = np.array(p.exterior.coords); ax.plot(xy[:, 0], xy[:, 1], color="#bd1f36", lw=1.3, zorder=z + 1)

def district_panel(ax, arr, tr, cmap, vmin, vmax, title, pad=600, clip=True, norm=None, interpolation="nearest", grid=True):
    ext = extent(arr, tr)
    for g in DIVS:
        for p in (g.geoms if hasattr(g, "geoms") else [g]):
            ax.fill(*p.exterior.xy, facecolor="#f3f3f3", edgecolor="none", zorder=1)
    kw = dict(extent=ext, cmap=cmap, interpolation=interpolation, zorder=3)
    if norm is not None: kw["norm"] = norm
    else: kw.update(vmin=vmin, vmax=vmax)
    im = ax.imshow(np.ma.masked_invalid(arr), **kw)
    if clip:
        patch = poly_patch(ax, facecolor="none", edgecolor="none", transform=ax.transData); ax.add_patch(patch); im.set_clip_path(patch)
    draw_lines(ax)
    ax.set_xlim(XMIN - pad, XMAX + pad); ax.set_ylim(YMIN - pad, YMAX + pad); ax.set_aspect("equal")
    ax.set_title(title, fontsize=8.6, pad=3, linespacing=1.15)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_linewidth(0.5); sp.set_color("#6b7280")
    return im

def north_scale(ax, km=5, arrow=True):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    if arrow:
        ax.annotate("N", xy=(0.92, 0.97), xytext=(0.92, 0.87), xycoords="axes fraction", ha="center", va="center", fontsize=7.5,
                    arrowprops={"arrowstyle": "->", "lw": 0.8, "color": "black"})
    sx = x0 + (x1 - x0) * 0.06; sy = y0 + (y1 - y0) * 0.035
    ax.plot([sx, sx + km * 1000], [sy, sy], color="black", lw=1.6, zorder=10)
    ax.text(sx + km * 500, sy + (y1 - y0) * 0.018, f"{km} km", ha="center", fontsize=5.8, zorder=10, path_effects=[pe.withStroke(linewidth=2, foreground="white")])

def colorbar_below(fig, ax, im, label, frac=(0.08, -0.24, 0.84, 0.035)):
    cax = ax.inset_axes(list(frac))
    cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.ax.tick_params(labelsize=6.3); cb.set_label(label, fontsize=6.8, labelpad=2)
    return cb

def source_note(fig, text, y=0.012, size=6.0):
    fig.text(0.5, y, text, ha="center", fontsize=size, color="#444444")

def save(fig, name, dpi=250):
    out = os.path.join(FIG, name); fig.savefig(out, dpi=dpi, facecolor="white"); plt.close(fig); print("guardada", out); return out


def hcbar(fig, ax, im, label, shrink=0.92, pad=0.03, fraction=0.05):
    cb = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=fraction, pad=pad, shrink=shrink)
    cb.ax.tick_params(labelsize=6); cb.set_label(label, fontsize=6.6, labelpad=1); cb.ax.xaxis.set_major_formatter(ES_FMT)
    return cb


from matplotlib.ticker import FuncFormatter
def es(x, nd=1, sign=False):
    s = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    return s.replace(".", ",").replace("-", "−")
ES_FMT = FuncFormatter(lambda v, p: ("%g" % v).replace(".", ",").replace("-", "−"))
