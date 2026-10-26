# -*- coding: utf-8 -*-
"""Version 2 of the house-style maps (POMCA-like sheet) of the three direct hazards in the POT 2026 basic hazard study.

Inputs (EPSG:9377), built by prepare_pot2026_hazard_layers_v2.py from the official DAP geodatabase mj_rev_pot_2025_med.gdb:
  - pot2026_amenazas_oficial_v2_9377.gpkg  layers amenaza_inundacion, amenaza_avenidas_torrenciales, amenaza_movimientos_masa
All three hazards are now official vector polygons (v1 rebuilt movimientos en masa as a ~32 m class raster from a PDF plate).
Same layout, colours and class order as v1 so the figures can replace the v1 ones.

Usage: python mapas_amenaza_pot2026_v2.py <prepared.gpkg> <output_dir>   (or env V2_PREP, V2_FIGS)"""
import os, sys, json, textwrap
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator

PREP = sys.argv[1] if len(sys.argv) > 1 else os.environ["V2_PREP"]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.environ["V2_FIGS"]
GPKG = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA"
        r"\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE"
        r"\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg")

C_LOW, C_MED, C_HIGH = "#fecc5c", "#fd8d3c", "#bd0026"
NAMES = {"50": "San Sebastián\nde Palmitas", "60": "San Cristóbal", "70": "Altavista",
         "80": "San Antonio\nde Prado", "90": "Santa Elena"}

divisions = gpd.read_file(GPKG, layer="comunas_corregimientos")
boundary = gpd.read_file(GPKG, layer="limite_medellin")
bpoly = boundary.geometry.iloc[0]
stats = {}


def base_axes():
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
    ax.set_xlabel("Este (km) — MAGNA-SIRGAS / Origen Nacional")
    ax.set_ylabel("Norte (km)")
    ax.grid(color="#9ca3af", linewidth=0.45, alpha=0.35)
    ax.set_axisbelow(True)
    # kilometres with a mark every 5 km (same convention as the CHELSA ENSO panel); the projection and the geometry are unchanged
    km = FuncFormatter(lambda v, _: f"{v / 1000:.0f}")
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(MultipleLocator(5000))
        axis.set_major_formatter(km)
    ax.tick_params(axis="x", rotation=0)
    ax.annotate("N", xy=(0.955, 0.94), xytext=(0.955, 0.84), xycoords="axes fraction",
                ha="center", va="center", fontsize=11,
                arrowprops={"arrowstyle": "-\x3e", "lw": 1.3, "color": "black"})
    scale_m = 5000
    # the 5 km rule starts on a 5 km tick of the axis (e.g. 4710 km to 4715 km) so it lines up with the grid
    start_x = round(((ax.get_xlim()[0] + ax.get_xlim()[1]) / 2 - scale_m / 2) / 5000) * 5000
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
    fig.text(0.5, 0.988, "Propuesta de revisión del POT 2026, información aún no protocolizada", ha="center", va="top",
             fontsize=8.6, style="italic", color="#7f1d1d")
    ax.set_title(title, fontsize=14.2, pad=9)
    source = textwrap.fill(" ".join(source.split()), width=112)  # keeps the credit inside the sheet width
    fig.text(0.5, 0.012, source, ha="center", fontsize=6.0, color="#444444")
    fig.savefig(out, dpi=300, facecolor="white")
    plt.close(fig)
    print("saved", out)


ONLY = [s for s in os.environ.get("V2_ONLY", "").split(",") if s]  # optional: redraw only some maps


def hazard_map(layer, title, legend_title, name, lw, unit, source, out):
    if ONLY and name not in ONLY:
        return
    gdf =gpd.read_file(PREP, layer=layer, engine="pyogrio")
    ha = gdf.groupby("categoria")["area_ha"].sum()
    district_ha = bpoly.area / 1e4
    outside_ha = gdf.geometry.difference(bpoly).area.sum() / 1e4
    stats[name] = {"polygons": len(gdf), "ha": {k: round(float(v), 2) for k, v in ha.items()},
                   "total_ha": round(float(ha.sum()), 2), "district_ha": round(district_ha, 2),
                   "outside_boundary_ha": round(float(outside_ha), 3),
                   "pct_of_district": {k: round(100 * float(v) / district_ha, 2) for k, v in ha.items()}}
    fig, ax = base_axes()
    for cls, color in (("Baja", C_LOW), ("Media", C_MED), ("Alta", C_HIGH)):
        sub = gdf[gdf["categoria"] == cls]
        # same-colour outline hides hairline gaps between adjacent polygons and keeps thin corridors visible
        sub.plot(ax=ax, facecolor=color, edgecolor=color, linewidth=lw, zorder=3)
    if unit == "ha":
        lab = {k: f"{k} ({ha[k]:,.0f} ha)".replace(",", ".") for k in ("Alta", "Media", "Baja")}
    else:
        lab = {k: f"{k} ({100 * ha[k] / district_ha:.2f} % del Distrito)".replace(".", ",") for k in ("Alta", "Media", "Baja")}
    handles = [Patch(facecolor=c, edgecolor="#555", linewidth=0.35, label=lab[k])
               for k, c in (("Alta", C_HIGH), ("Media", C_MED), ("Baja", C_LOW))]
    finish(fig, ax, title, handles, legend_title, source, out)


SRC = ("Fuente: elaboración propia con la capa de amenaza por {fen} de la propuesta de revisión del POT 2026 (Departamento Administrativo de "
       "Planeación [DAP], 2026; aún no protocolizada), construida con el estudio básico de amenaza (Universidad EAFIT, en DAP, 2026){extra}.")
hazard_map("amenaza_inundacion", "Amenaza por inundaciones\nDistrito de Medellín, POT 2026", "Amenaza por\ninundaciones",
           "inundacion", 0.5, "ha",
           SRC.format(fen="inundaciones", extra=" y estudios de detalle"),
           f"{OUTDIR}/Figura_8_1_3_1_amenaza_inundaciones_POT2026_v2.png")
hazard_map("amenaza_avenidas_torrenciales", "Amenaza por avenidas torrenciales\nDistrito de Medellín, POT 2026",
           "Amenaza por\navenidas torrenciales", "avenidas_torrenciales", 0.5, "ha",
           SRC.format(fen="avenidas torrenciales", extra=" y estudios de detalle"),
           f"{OUTDIR}/Figura_8_1_4_1_amenaza_avenidas_torrenciales_POT2026_v2.png")
hazard_map("amenaza_movimientos_masa", "Amenaza por movimientos en masa\nDistrito de Medellín, POT 2026",
           "Amenaza por\nmovimientos en masa", "movimientos_masa", 0.12, "pct",
           SRC.format(fen="movimientos en masa", extra=" y estudios de detalle"),
           f"{OUTDIR}/Figura_8_1_5_1_amenaza_movimientos_en_masa_POT2026_v2.png")
stats_file = f"{OUTDIR}/estadisticas_mapas_v2.json"
if ONLY and os.path.exists(stats_file):  # keep the entries of the maps that were not redrawn
    with open(stats_file, encoding="utf-8") as f:
        stats = {**json.load(f), **stats}
with open(stats_file, "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
print(json.dumps(stats, ensure_ascii=False, indent=1))
