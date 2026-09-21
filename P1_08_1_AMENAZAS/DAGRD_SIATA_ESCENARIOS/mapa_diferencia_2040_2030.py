# -*- coding: utf-8 -*-
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import ScalarFormatter

PREP = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\08_1_AMENAZAS\01_DAGRD_SIATA_ESCENARIOS\02_DATOS_PREPARADOS"
GPKG = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg"
OUT = r"C:\Users\marco\AppData\Local\Temp\claude\G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude\446a2666-30c7-4c61-98e1-c82458a0665f\scratchpad\figs\diferencia_precipitacion_extrema_2040_2030.png"

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

fig, axes = plt.subplots(1, 2, figsize=(9.8, 5.0))
fig.subplots_adjust(left=0.08, right=0.90, bottom=0.18, top=0.87, wspace=0.32)

panels = [("90", axes[0], "Percentil 90"), ("95", axes[1], "Percentil 95")]
vmax = 0
diffs = {}
for pct, ax, label in panels:
    a2030, xs, ys = read_clipped(f"{PREP}/PPT_2030_Percentil_{pct}_9377.tif")
    a2040, _, _ = read_clipped(f"{PREP}/PPT_2040_Percentil_{pct}_9377.tif")
    diff = a2040 - a2030
    diffs[pct] = (diff, xs, ys)
    vmax = max(vmax, np.nanmax(np.abs(diff)))

norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
cmap = plt.get_cmap("RdBu")

images = []
for pct, ax, label in panels:
    diff, xs, ys = diffs[pct]
    im = ax.imshow(diff, extent=[xs.min(), xs.max(), ys.min(), ys.max()], origin="upper",
                    cmap=cmap, norm=norm, interpolation="bilinear")
    images.append(im)
    divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.9, zorder=4)
    boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.8, zorder=5)
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_aspect("equal")
    ax.set_title(label, fontsize=11.5, pad=6)
    ax.set_xlabel("Este (m)\nMAGNA-SIRGAS / Origen Nacional", fontsize=7.3)
    if ax is axes[0]:
        ax.set_ylabel("Norte (m)", fontsize=8.5)
    ax.grid(color="#9ca3af", linewidth=0.4, alpha=0.3)
    ax.set_axisbelow(True)
    formatter = ScalarFormatter(useOffset=False)
    formatter.set_scientific(False)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.tick_params(axis="both", labelsize=6.6, rotation=25)

    ax.annotate("N", xy=(0.93, 0.94), xytext=(0.93, 0.84), xycoords="axes fraction",
                ha="center", va="center", fontsize=9,
                arrowprops={"arrowstyle": "-\x3e", "lw": 1.1, "color": "black"})
    scale_m = 5000
    sx = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2 - scale_m / 2
    sy = extent[2] + (extent[3] - extent[2]) * 0.04
    ax.plot([sx, sx + scale_m], [sy, sy], color="black", lw=2, zorder=10)
    ax.text(sx + scale_m / 2, sy + (extent[3] - extent[2]) * 0.014, "5 km", ha="center", fontsize=7, zorder=10)

cax = fig.add_axes([0.915, 0.22, 0.018, 0.55])
cb = fig.colorbar(images[0], cax=cax)
cb.set_label("Cambio (mm)\n2040 menos 2030", fontsize=8)
cb.ax.tick_params(labelsize=7.5)

fig.suptitle("Diferencia en precipitación extrema horaria entre 2040 y 2030",
             fontsize=13.5, y=0.975)

fig.text(0.5, 0.055,
         "Fuente: elaboración propia a partir de SIATA (2019), Convenio DAGRD-SIATA 4600082037 de 2019.",
         ha="center", fontsize=6.6, color="#444444")
fig.text(0.5, 0.025,
         "Malla nativa ~1 km (WRF), reproyectada e interpolada a 200 m. Azul = más lluvia en 2040 que en 2030; rojo = menos.",
         ha="center", fontsize=6.6, color="#444444")

fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT)
