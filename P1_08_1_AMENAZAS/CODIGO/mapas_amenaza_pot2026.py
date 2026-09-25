# -*- coding: utf-8 -*-
"""House-style maps (POMCA-like sheet) of the three direct hazards in the POT 2026 basic hazard study.

Inputs (EPSG:9377), built by prepare_pot2026_hazard_layers.py from Cartografia 1 (POT 2026):
  - pot2026_amenaza_inundacion_9377.gpkg              (plate 06, vector zones)
  - pot2026_amenaza_avenidas_torrenciales_9377.gpkg   (plate 07, vector zones)
  - pot2026_amenaza_movimientos_masa_clase_9377.tif   (plate 05, class raster: 1 high, 2 medium, 3 low)
Legend figures come from the basic hazard study (EBA, Universidad EAFIT for DAP, 2026)."""
import sys
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter

PREP = sys.argv[1]
OUTDIR = sys.argv[2]
GPKG = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA"
        r"\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE"
        r"\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg")

# Same three-step scale for every hazard: low -> medium -> high
C_LOW, C_MED, C_HIGH = "#fecc5c", "#fd8d3c", "#bd0026"
NAMES = {"50": "San Sebastián\nde Palmitas", "60": "San Cristóbal", "70": "Altavista",
         "80": "San Antonio\nde Prado", "90": "Santa Elena"}

divisions = gpd.read_file(GPKG, layer="comunas_corregimientos")
boundary = gpd.read_file(GPKG, layer="limite_medellin")
bpoly = boundary.geometry.iloc[0]


def base_axes(title):
    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)
    divisions.plot(ax=ax, facecolor="#f3f3f3", edgecolor="none", zorder=1)
    return fig, ax


def finish(fig, ax, title, handles, legend_title, source, out):
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
    ax.annotate("N", xy=(0.955, 0.94), xytext=(0.955, 0.84), xycoords="axes fraction",
                ha="center", va="center", fontsize=11,
                arrowprops={"arrowstyle": "-\x3e", "lw": 1.3, "color": "black"})
    scale_m = 5000
    start_x = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2 - scale_m / 2
    start_y = ymin - pad + (ymax - ymin + 2 * pad) * 0.045
    ax.plot([start_x, start_x + scale_m], [start_y, start_y], color="black", lw=2.4, zorder=10)
    ax.text(start_x + scale_m / 2, start_y + (ymax - ymin) * 0.016, "5 km", ha="center", fontsize=9, zorder=10)
    for _, r in divisions[divisions["codigo"].isin(NAMES)].iterrows():
        p = r.geometry.representative_point()
        ax.text(p.x, p.y, NAMES[r["codigo"]], ha="center", va="center", fontsize=6.3,
                color="#333333", style="italic", zorder=6,
                path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    handles = list(handles) + [
        plt.Line2D([0], [0], color="#252525", lw=0.7, label="Comunas y corregimientos"),
        plt.Line2D([0], [0], color="#bd1f36", lw=2, label="Límite municipal")]
    ax.legend(handles=handles, title=legend_title, loc="upper center", bbox_to_anchor=(0.66, 0.985), ncol=1,
              fontsize=7.7, title_fontsize=8.6, framealpha=0.94, borderpad=0.55, labelspacing=0.35,
              handletextpad=0.55).set_zorder(20)
    ax.set_title(title, fontsize=14.2, pad=9)
    fig.text(0.5, 0.012, source, ha="center", fontsize=6.0, color="#444444", wrap=True)
    fig.savefig(out, dpi=300, facecolor="white")
    plt.close(fig)
    print("saved", out)


def vector_map(layer_file, layer, title, legend_title, labels, out):
    gdf = gpd.read_file(f"{PREP}/{layer_file}", layer=layer).set_index("clase")
    fig, ax = base_axes(title)
    for cls, color in (("baja", C_LOW), ("media", C_MED), ("alta", C_HIGH)):
        g = gpd.GeoSeries([gdf.loc[cls, "geometry"]], crs="EPSG:9377")
        # thin corridors: outline in the same colour keeps them visible at page scale
        g.plot(ax=ax, facecolor=color, edgecolor=color, linewidth=0.5, zorder=3)
    handles = [Patch(facecolor=c, edgecolor="#555", linewidth=0.35, label=labels[k])
               for k, c in (("alta", C_HIGH), ("media", C_MED), ("baja", C_LOW))]
    finish(fig, ax, title, handles, legend_title,
           "Fuente: elaboración propia con zonas vectorizadas de la lámina de Cartografía 1 del POT 2026\n"
           "(Departamento Administrativo de Planeación [DAP], 2026b);\n"
           "áreas según el estudio básico de amenaza (Universidad EAFIT, en DAP, 2026a).", out)


def raster_map(tif, title, legend_title, labels, out):
    with rasterio.open(tif) as src:
        img, tr = mask(src, [bpoly.__geo_interface__], crop=True, nodata=0, all_touched=True)
    cls = img[0]
    h, w = cls.shape
    extent = (tr.c, tr.c + w * tr.a, tr.f + h * tr.e, tr.f)
    inside = (cls > 0).sum()
    fig, ax = base_axes(title)
    cmap = ListedColormap([C_HIGH, C_MED, C_LOW])
    ax.imshow(np.ma.masked_equal(cls, 0), cmap=cmap, vmin=0.5, vmax=3.5, extent=extent,
              interpolation="nearest", zorder=3)
    handles = [Patch(facecolor=c, edgecolor="#555", linewidth=0.35, label=labels[k])
               for k, c in (("alta", C_HIGH), ("media", C_MED), ("baja", C_LOW))]
    finish(fig, ax, title, handles, legend_title,
           "Fuente: elaboración propia a partir de la lámina de amenaza por movimientos en masa de Cartografía 1 del POT 2026\n"
           "(Departamento Administrativo de Planeación [DAP], 2026b), reconstruida en celdas de unos 32 m;\n"
           "porcentajes según el estudio básico de amenaza (Universidad EAFIT, en DAP, 2026a).", out)
    print("classified cells inside district:", inside, "| share of district area: %.1f %%" %
          (100 * inside * abs(tr.a * tr.e) / bpoly.area))


vector_map("pot2026_amenaza_inundacion_9377.gpkg", "amenaza_inundacion",
           "Amenaza por inundaciones\nDistrito de Medellín, POT 2026", "Amenaza por\ninundaciones",
           {"alta": "Alta (575 ha)", "media": "Media (195 ha)", "baja": "Baja (364 ha)"},
           f"{OUTDIR}/Figura_8_1_3_1_amenaza_inundaciones_POT2026.png")
vector_map("pot2026_amenaza_avenidas_torrenciales_9377.gpkg", "amenaza_avenidas_torrenciales",
           "Amenaza por avenidas torrenciales\nDistrito de Medellín, POT 2026", "Amenaza por\navenidas torrenciales",
           {"alta": "Alta (587 ha)", "media": "Media (207 ha)", "baja": "Baja (169 ha)"},
           f"{OUTDIR}/Figura_8_1_4_1_amenaza_avenidas_torrenciales_POT2026.png")
raster_map(f"{PREP}/pot2026_amenaza_movimientos_masa_clase_9377.tif",
           "Amenaza por movimientos en masa\nDistrito de Medellín, POT 2026", "Amenaza por\nmovimientos en masa",
           {"alta": "Alta (37,25 % del Distrito)", "media": "Media (14,80 %)", "baja": "Baja (47,95 %)"},
           f"{OUTDIR}/Figura_8_1_5_1_amenaza_movimientos_en_masa_POT2026.png")
