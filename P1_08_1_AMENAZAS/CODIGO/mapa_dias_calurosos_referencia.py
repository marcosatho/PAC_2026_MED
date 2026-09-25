# -*- coding: utf-8 -*-
"""Days per year above 28 and 29 degC (daily maximum) in Medellin under the reference climate 1990-2000.
Source: SIATA (2019) dynamic downscaling (WRF), 1 km cells; rasters in the local 'MAGNA Medellin' plane, reprojected
to EPSG:9377 with nearest-neighbour resampling (no invented detail) and clipped to the district outline.
Each panel has its own colour scale (0-140 days for 28 degC, 0-26 days for 29 degC).

usage: mapa_dias_calurosos_referencia.py <out_dir>"""
import os
import sys
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.ticker import ScalarFormatter

sys.stdout.reconfigure(encoding="utf-8")
OUT_DIR = sys.argv[1]
SRC = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
       r"\02_DOCUMENTOS_EN_ELABORACION\08_1_AMENAZAS\01_DAGRD_SIATA_ESCENARIOS\01_DATOS_ORIGINALES\Archivos_Soporte\4_Num_dias_Tmax")
GPKG = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
        r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg")
divisions = gpd.read_file(GPKG, layer="comunas_corregimientos")
boundary = gpd.read_file(GPKG, layer="limite_medellin")
bpoly = boundary.geometry.iloc[0]


def load(threshold):
    path = os.path.join(SRC, f"Temp_1990_Num_DiasTmaxh_Umbral_{threshold}.tif")
    with rasterio.open(path) as s:
        tr, w, h = calculate_default_transform(s.crs, "EPSG:9377", s.width, s.height, *s.bounds)
        arr = np.full((h, w), np.nan, "float32")
        reproject(rasterio.band(s, 1), arr, src_transform=s.transform, src_crs=s.crs, dst_transform=tr, dst_crs="EPSG:9377",
                  resampling=Resampling.nearest, src_nodata=s.nodata, dst_nodata=np.nan)
    arr[arr > 1e30] = np.nan
    inside = rasterio.features.rasterize([bpoly.__geo_interface__], out_shape=arr.shape, transform=tr, fill=0, default_value=1,
                                         dtype="uint8", all_touched=True).astype(bool)
    # fill the few district cells without data with the mean of their valid neighbours
    for _ in range(3):
        miss = np.argwhere(inside & np.isnan(arr))
        for r, c in miss:
            win = arr[max(r - 1, 0): r + 2, max(c - 1, 0): c + 2]
            if np.isfinite(win).any():
                arr[r, c] = np.nanmean(win)
    return arr, tr, inside


data = {t: load(t) for t in (28, 29)}
for t, (a, tr, inside) in data.items():
    v = a[inside]
    print(f"threshold {t} degC: district cells {int(inside.sum())} | days/yr min {np.nanmin(v):.0f} max {np.nanmax(v):.0f} mean {np.nanmean(v):.1f} | "
          f"cells with >=20 days: {int((v >= 20).sum())} ({100 * (v >= 20).mean():.0f} % of the district), >=1 day: {100 * (v >= 1).mean():.0f} %")

VMAX = 140
fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.7))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.32, top=0.82, wspace=0.16)
xmin, ymin, xmax, ymax = boundary.total_bounds
pad = 600
clip_verts = np.array(bpoly.exterior.coords)
im = None
for ax, (thr, VMAX) in zip(axes, ((28, 140), (29, 26))):     # each panel keeps its own colour scale
    arr, tr, inside = data[thr]
    ext = (tr.c, tr.c + arr.shape[1] * tr.a, tr.f + arr.shape[0] * tr.e, tr.f)
    divisions.plot(ax=ax, facecolor="#f3f3f3", edgecolor="none", zorder=1)
    im = ax.imshow(np.ma.masked_invalid(arr), extent=ext, cmap="YlOrRd", vmin=0, vmax=VMAX, interpolation="nearest", zorder=3)
    clip = PathPatch(Path(clip_verts), transform=ax.transData, facecolor="none", edgecolor="none")
    ax.add_patch(clip)
    im.set_clip_path(clip)      # draw only inside the district
    divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.3, alpha=0.8, zorder=4)
    boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.4, zorder=5)
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)
    ax.set_aspect("equal")
    vmax_here = int(np.nanmax(arr[inside]))
    ax.set_title(f"Máxima superior a {thr} °C\n(hasta {vmax_here} días al año)", fontsize=10, pad=4, linespacing=1.15)
    ax.grid(color="#9ca3af", linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    fmt = ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
    ax.set_xticks(range(4700000, 4727000, 10000))
    ax.tick_params(axis="x", labelsize=6.2, rotation=30)
    ax.tick_params(axis="y", labelsize=6.2)
    cax = ax.inset_axes([0.08, -0.29, 0.84, 0.035])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.ax.tick_params(labelsize=6.8)
    cb.set_label("Días al año", fontsize=7.2, labelpad=2)
    ax.annotate("N", xy=(0.93, 0.95), xytext=(0.93, 0.83), xycoords="axes fraction", ha="center", va="center", fontsize=8.5,
                arrowprops={"arrowstyle": "-\x3e", "lw": 1.0, "color": "black"})
    sx = (xmin + xmax) / 2 - 2500
    sy = ymin - pad + (ymax - ymin + 2 * pad) * 0.04
    ax.plot([sx, sx + 5000], [sy, sy], color="black", lw=2.0, zorder=10)
    ax.text(sx + 2500, sy + (ymax - ymin) * 0.018, "5 km", ha="center", fontsize=6.8, zorder=10,
            path_effects=[pe.withStroke(linewidth=2, foreground="white")])
axes[0].set_ylabel("Norte (m)", fontsize=7.5)
fig.suptitle("Días de calor fuerte al año en el Distrito de Medellín\nClima de referencia 1990–2000", fontsize=12.2, y=0.985)
fig.text(0.5, 0.04, "Fuente: elaboración propia a partir de SIATA (2019), simulación climática regional con celdas de 1 km.",
         ha="center", fontsize=6.3, color="#444444")
out = os.path.join(OUT_DIR, "Figura_8_1_7_1_dias_calurosos_referencia_1990_2000.png")
fig.savefig(out, dpi=300, facecolor="white")
print("saved", out)
