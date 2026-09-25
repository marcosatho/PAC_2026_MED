# -*- coding: utf-8 -*-
"""Population health risk to climate change and variability by comuna and corregimiento (Medellin).
Values: Table 9 of PASCCM Tomo II (Secretaria de Salud de Medellin), 2005-2018 data.
Risk = exposure x vulnerability; vulnerability = sensitivity / adaptive capacity (checked below against the table).
Map (house style) + ranking chart.

usage: mapa_riesgo_salud_clima.py <out_dir>"""
import os
import sys
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter

OUT = sys.argv[1]
GPKG = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
        r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg")

# code: (name, exposure, sensitivity, capacity, vulnerability, risk)  -- Table 9
T9 = {
    "01": ("Popular", 0.451, 0.411, 0.527, 0.780, 0.351), "02": ("Santa Cruz", 0.567, 0.337, 0.349, 0.965, 0.547),
    "03": ("Manrique", 0.508, 0.342, 0.498, 0.687, 0.349), "04": ("Aranjuez", 0.693, 0.260, 0.545, 0.478, 0.331),
    "05": ("Castilla", 0.162, 0.207, 0.568, 0.364, 0.059), "06": ("Doce de Octubre", 0.555, 0.260, 0.656, 0.396, 0.220),
    "07": ("Robledo", 0.392, 0.241, 0.775, 0.310, 0.122), "08": ("Villa Hermosa", 0.783, 0.332, 0.566, 0.587, 0.459),
    "09": ("Buenos Aires", 0.815, 0.253, 0.531, 0.476, 0.388), "10": ("La Candelaria", 0.460, 0.317, 0.609, 0.520, 0.239),
    "11": ("Laureles-Estadio", 0.234, 0.248, 0.698, 0.355, 0.083), "12": ("La América", 0.315, 0.276, 0.526, 0.524, 0.165),
    "13": ("San Javier", 0.395, 0.244, 0.596, 0.410, 0.162), "14": ("El Poblado", 0.493, 0.100, 1.000, 0.100, 0.049),
    "15": ("Guayabal", 0.100, 0.158, 0.468, 0.338, 0.034), "16": ("Belén", 0.203, 0.220, 0.752, 0.292, 0.059),
    "50": ("San Sebastián de Palmitas", 0.186, 1.000, 0.100, 10.000, 1.859), "60": ("San Cristóbal", 0.615, 0.207, 0.607, 0.341, 0.210),
    "70": ("Altavista", 0.296, 0.499, 0.204, 2.443, 0.724), "80": ("San Antonio de Prado", 1.000, 0.110, 0.486, 0.226, 0.226),
    "90": ("Santa Elena", 0.204, 0.580, 0.252, 2.302, 0.470),
}
# consistency check of the published table: risk = exposure x vulnerability, vulnerability = sensitivity / capacity
bad = [(c, round(v[1] * v[4], 3), v[5]) for c, v in T9.items() if abs(v[1] * v[4] - v[5]) > 0.006]
badv = [(c, round(v[2] / v[3], 3), v[4]) for c, v in T9.items() if abs(v[2] / v[3] - v[4]) > 0.02 and c != "50"]
print("risk != exposure x vulnerability:", bad, "| vulnerability != sensitivity/capacity:", badv)

BREAKS = [0.10, 0.20, 0.30, 0.40, 0.60]
LABELS = ["Menos de 0,10", "0,10 a 0,20", "0,20 a 0,30", "0,30 a 0,40", "0,40 a 0,60", "Más de 0,60"]
COLORS = ["#ffffb2", "#fed976", "#feb24c", "#fd8d3c", "#e31a1c", "#800026"]


def cls(v):
    return int(np.searchsorted(BREAKS, v, side="right"))


div = gpd.read_file(GPKG, layer="comunas_corregimientos")
boundary = gpd.read_file(GPKG, layer="limite_medellin")
div["cls"] = div["codigo"].map(lambda c: cls(T9[c][5]) if c in T9 else np.nan)
div["color"] = div["cls"].map(lambda i: COLORS[int(i)] if i == i else "#e6e6e6")

# ---- map --------------------------------------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 6.6))
fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)
div.plot(ax=ax, color=div["color"], edgecolor="none", zorder=2)
div.boundary.plot(ax=ax, color="#252525", linewidth=0.5, alpha=0.9, zorder=4)
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
ax.annotate("N", xy=(0.60, 0.94), xytext=(0.60, 0.84), xycoords="axes fraction", ha="center", va="center", fontsize=11,
            arrowprops={"arrowstyle": "-\x3e", "lw": 1.3, "color": "black"})
sx = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2 - 2500
sy = ymin - pad + (ymax - ymin + 2 * pad) * 0.045
ax.plot([sx, sx + 5000], [sy, sy], color="black", lw=2.4, zorder=10)
ax.text(sx + 2500, sy + (ymax - ymin) * 0.016, "5 km", ha="center", fontsize=9, zorder=10)
for _, r in div[div["codigo"].isin(["50", "60", "70", "80", "90"])].iterrows():
    p = r.geometry.representative_point()
    ax.text(p.x, p.y, T9[r["codigo"]][0].replace("San Sebastián de ", "").replace("San Antonio de Prado", "San Antonio\nde Prado")
            + f"\n{T9[r['codigo']][5]:.2f}".replace(".", ","), ha="center", va="center", fontsize=6.3, color="#222222", zorder=6,
            path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
handles = [Patch(facecolor=c, edgecolor="#555", linewidth=0.35, label=l) for c, l in zip(COLORS, LABELS)]
ax.legend(handles=handles, title="Índice de riesgo\nen salud por el clima", loc="upper right", bbox_to_anchor=(0.995, 0.985), fontsize=7.7, title_fontsize=8.6,
          framealpha=0.94, borderpad=0.55, labelspacing=0.35, handletextpad=0.55).set_zorder(20)
ax.set_title("Riesgo de la población en salud por el clima\nDistrito de Medellín", fontsize=14.2, pad=9)
fig.text(0.5, 0.05, "Fuente: elaboración propia a partir de Secretaría de Salud de Medellín (s. f.), Tabla 9, datos 2005–2018.", ha="center", fontsize=6.0, color="#444444")
fig.text(0.5, 0.02, "Riesgo = exposición × vulnerabilidad. Los corregimientos se calcularon por separado de las comunas en el estudio.", ha="center", fontsize=6.0, color="#444444")
p1 = os.path.join(OUT, "Figura_8_1_9_2_riesgo_salud_clima_comunas.png")
fig.savefig(p1, dpi=300, facecolor="white")
plt.close(fig)
print("saved", p1)

# ---- ranking chart -----------------------------------------------------------------------------------------------------
rows = sorted(T9.items(), key=lambda kv: kv[1][5])
fig, ax = plt.subplots(figsize=(7.2, 6.3))
fig.subplots_adjust(left=0.29, right=0.93, bottom=0.13, top=0.88)
XMAX = 0.85
for i, (c, v) in enumerate(rows):
    val = v[5]
    ax.barh(i, min(val, XMAX), color=COLORS[cls(val)], edgecolor="#777", linewidth=0.3, height=0.72, zorder=3)
    lab = f"{val:.2f}".replace(".", ",")
    if val > XMAX:
        ax.text(XMAX - 0.01, i, lab + " ►", ha="right", va="center", fontsize=7.6, fontweight="bold", color="white", zorder=5)
    else:
        ax.text(val + 0.01, i, lab, ha="left", va="center", fontsize=7.6)
names = [(v[0] + (" (rural)" if c in ("50", "60", "70", "80", "90") else "")) for c, v in rows]
ax.set_yticks(range(len(rows)))
ax.set_yticklabels(names, fontsize=8)
ax.set_xlim(0, 0.9)
ax.set_xlabel("Índice de riesgo en salud por el clima", fontsize=8.8)
ax.tick_params(axis="y", length=0)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.grid(axis="x", color="#d8d8d8", linewidth=0.6, zorder=0)
ax.set_axisbelow(True)
ax.set_title("Riesgo de la población en salud por el clima\npor comuna y corregimiento", fontsize=12.2, pad=8)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
ax.tick_params(axis="x", labelsize=8)
fig.text(0.5, 0.02, "Fuente: elaboración propia a partir de Secretaría de Salud de Medellín (s. f.), Tabla 9, datos 2005–2018. Palmitas (1,86) sale de la escala.",
         ha="center", fontsize=6.3, color="#444444")
p2 = os.path.join(OUT, "Figura_8_1_9_3_riesgo_salud_clima_ranking.png")
fig.savefig(p2, dpi=300, facecolor="white")
print("saved", p2)
