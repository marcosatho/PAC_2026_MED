# -*- coding: utf-8 -*-
"""House-style maps of land surface temperature (LST) for the Medellin district.

Figure A: continuous surface (30 m) of the median LST (8 Landsat 8 scenes, 2013-2016, ~10 am local time).
Figure B: mean LST per barrio, using the LST after removing the topographic bias (slope / orientation effect).
Source: AMVA heat-island package, Guzman Echavarria (2018). Inputs prepared by uhi_lst_prepare.py (EPSG:9377).

usage: mapas_temperatura_superficial.py <prepared_dir> <out_dir>"""
import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

PREP, OUT = sys.argv[1], sys.argv[2]
GPKG = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
        r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg")
divisions = gpd.read_file(GPKG, layer="comunas_corregimientos")
boundary = gpd.read_file(GPKG, layer="limite_medellin")
barrios = gpd.read_file(GPKG, layer="barrios")


def frame():
    fig, ax = plt.subplots(figsize=(7.2, 6.8))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.285, top=0.87)
    divisions.plot(ax=ax, facecolor="#f3f3f3", edgecolor="none", zorder=1)
    return fig, ax


def finish(fig, ax, title, vmin, vmax, mappable, cb_label, source, out, ticks):
    divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.9, zorder=4)
    boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.8, zorder=5)
    xmin, ymin, xmax, ymax = boundary.total_bounds
    pad = 750
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)
    ax.set_aspect("equal")
    ax.set_xlabel("Este (m) — MAGNA-SIRGAS / Origen Nacional")
    ax.set_ylabel("Norte (m)")
    ax.grid(color="#9ca3af", linewidth=0.45, alpha=0.35)
    ax.set_axisbelow(True)
    fmt = ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
    ax.tick_params(axis="x", rotation=25)
    ax.annotate("N", xy=(0.955, 0.94), xytext=(0.955, 0.84), xycoords="axes fraction", ha="center", va="center", fontsize=11,
                arrowprops={"arrowstyle": "-\x3e", "lw": 1.3, "color": "black"})
    sx = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2 - 2500
    sy = ymin - pad + (ymax - ymin + 2 * pad) * 0.045
    ax.plot([sx, sx + 5000], [sy, sy], color="black", lw=2.4, zorder=10)
    ax.text(sx + 2500, sy + (ymax - ymin) * 0.016, "5 km", ha="center", fontsize=9, zorder=10)
    cax = fig.add_axes([0.28, 0.115, 0.44, 0.02])
    cb = fig.colorbar(mappable, cax=cax, orientation="horizontal", ticks=ticks)
    cb.ax.tick_params(labelsize=8)
    cb.set_label(cb_label, fontsize=8.6, labelpad=2)
    ax.set_title(title, fontsize=14.2, pad=9)
    fig.text(0.5, 0.012, source, ha="center", va="bottom", fontsize=6.3, color="#444444", linespacing=1.5)
    fig.savefig(out, dpi=300, facecolor="white")
    plt.close(fig)
    print("saved", out)


# ---- Figure A: continuous surface ---------------------------------------------------------------------------------
with rasterio.open(os.path.join(PREP, "Mediana_LST_9377_Medellin.tif")) as s:
    a = s.read(1)
    tr = s.transform
h, w = a.shape
ext = (tr.c, tr.c + w * tr.a, tr.f + h * tr.e, tr.f)
fig, ax = frame()
im = ax.imshow(np.ma.masked_invalid(a), extent=ext, cmap="YlOrRd", vmin=20, vmax=38, interpolation="nearest", zorder=3)
finish(fig, ax, "Temperatura de la superficie\nDistrito de Medellín, mañanas de 2013 a 2016", 20, 38, im,
       "Temperatura de la superficie (°C)",
       "Fuente: elaboración propia a partir de Guzmán Echavarría (2018): mediana de ocho imágenes Landsat 8 (2013–2016)\ntomadas hacia las 10 a. m.; resolución de 30 m.",
       os.path.join(OUT, "Figura_8_1_7_2_temperatura_superficie_continua.png"), [20, 24, 28, 32, 36])

# ---- Figure B: mean per barrio --------------------------------------------------------------------------------------
z = pd.read_csv(os.path.join(PREP, "LST_norm_por_barrio.csv"), dtype={"codigo": str})
bar = barrios.merge(z[["codigo", "mean"]], on="codigo", how="left")
fig, ax = frame()
bar.plot(ax=ax, column="mean", cmap="YlOrRd", vmin=25, vmax=35, edgecolor="#ffffff", linewidth=0.15, zorder=3, missing_kwds={"color": "#e6e6e6"})
sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=25, vmax=35))
finish(fig, ax, "Temperatura de la superficie por barrio\nDistrito de Medellín, sin el efecto de la pendiente", 25, 35, sm,
       "Temperatura promedio de la superficie del barrio (°C)",
       "Fuente: elaboración propia a partir de Guzmán Echavarría (2018): promedio de celdas de 30 m en cada barrio,\ndescontado el efecto de la pendiente y la orientación de las laderas.",
       os.path.join(OUT, "Figura_8_1_7_3_temperatura_superficie_por_barrio.png"), [25, 27, 29, 31, 33, 35])
