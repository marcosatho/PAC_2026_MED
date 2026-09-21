# -*- coding: utf-8 -*-
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

PREP = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\08_1_AMENAZAS\01_DAGRD_SIATA_ESCENARIOS\02_DATOS_PREPARADOS"
GPKG = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg"
OUT = r"C:\Users\marco\AppData\Local\Temp\claude\G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude\446a2666-30c7-4c61-98e1-c82458a0665f\scratchpad\figs\precipitacion_extrema_medellin_1990_2030_2040.png"

divisions = gpd.read_file(GPKG, layer="comunas_corregimientos")
boundary = gpd.read_file(GPKG, layer="limite_medellin")
xmin, ymin, xmax, ymax = boundary.total_bounds
pad = 750
extent = (xmin - pad, xmax + pad, ymin - pad, ymax + pad)

muni_geom = [boundary.geometry.iloc[0].__geo_interface__]

def read_clipped(path):
    with rasterio.open(path) as src:
        data, transform = mask(src, muni_geom, crop=True, nodata=np.nan, all_touched=True)
        arr = data[0]
        h, w = arr.shape
        xs = transform.c + transform.a * (np.arange(w) + 0.5)
        ys = transform.f + transform.e * (np.arange(h) + 0.5)
        return arr, xs, ys

periods = ["1990", "2030", "2040"]
pcts = ["90", "95"]

fig, axes = plt.subplots(2, 3, figsize=(10.6, 8.2))
fig.subplots_adjust(left=0.075, right=0.90, bottom=0.10, top=0.90, wspace=0.28, hspace=0.30)

cmap = plt.get_cmap("YlGnBu")

for row, pct in enumerate(pcts):
    arrs = {}
    for period in periods:
        arr, xs, ys = read_clipped(f"{PREP}/PPT_{period}_Percentil_{pct}_9377.tif")
        arrs[period] = (arr, xs, ys)
    vmin = min(np.nanmin(a[0]) for a in arrs.values())
    vmax = max(np.nanmax(a[0]) for a in arrs.values())

    ims = []
    for col, period in enumerate(periods):
        ax = axes[row, col]
        arr, xs, ys = arrs[period]
        im = ax.imshow(arr, extent=[xs.min(), xs.max(), ys.min(), ys.max()], origin="upper",
                        cmap=cmap, vmin=vmin, vmax=vmax, interpolation="bilinear")
        ims.append(im)
        divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.35, alpha=0.9, zorder=4)
        boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.5, zorder=5)
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#888888")
            spine.set_linewidth(0.6)
        if row == 0:
            ax.set_title(period, fontsize=12, pad=5)
        if col == 0:
            ax.set_ylabel(f"Percentil {pct}", fontsize=10.5)
        if row == 0 and col == 0:
            ax.annotate("N", xy=(0.90, 0.93), xytext=(0.90, 0.80), xycoords="axes fraction",
                        ha="center", va="center", fontsize=8,
                        arrowprops={"arrowstyle": "-\x3e", "lw": 1.0, "color": "black"})
        if row == 1 and col == 0:
            scale_m = 5000
            sx = extent[0] + (extent[1] - extent[0]) * 0.06
            sy = extent[2] + (extent[3] - extent[2]) * 0.06
            ax.plot([sx, sx + scale_m], [sy, sy], color="black", lw=1.8, zorder=10)
            ax.text(sx + scale_m / 2, sy + (extent[3] - extent[2]) * 0.02, "5 km", ha="center", fontsize=6.5, zorder=10)

    cax = fig.add_axes([0.915, 0.565 - row * 0.40, 0.016, 0.30])
    cb = fig.colorbar(ims[-1], cax=cax)
    cb.set_label(f"P{pct} (mm/hora)", fontsize=7.6)
    cb.ax.tick_params(labelsize=6.8)

fig.suptitle("Precipitación horaria extrema en Medellín · 1990-2000, 2030 y 2040",
             fontsize=14.5, y=0.965)

fig.text(0.5, 0.045,
         "Fuente: elaboración propia a partir de SIATA (2019), Convenio DAGRD-SIATA 4600082037 de 2019.",
         ha="center", fontsize=7, color="#444444")
fig.text(0.5, 0.02,
         "Malla nativa ~1 km (modelo WRF, RCP4.5), reproyectada MAGNA-SIRGAS / Origen Nacional e interpolada a 200 m.",
         ha="center", fontsize=7, color="#444444")

fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT)
