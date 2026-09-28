# -*- coding: utf-8 -*-
"""House-style choropleth maps of floods and torrential floods attended by the DAGRD, by comuna and corregimiento.

Figura_8_5_7: DAGRD tables (PASCCM Tomo I, Tabla 14), 2005-2018: floods and torrential floods.
Figura_8_5_8: SIRMED 'Inundaciones', 2021-2025.
Variable: events per square kilometre per year (same class breaks in both maps); the period total is printed in each unit.

usage: mapas_inundaciones_por_territorio.py <dagrd_long.csv> <sirmed.csv> <limites.gpkg> <out_dir>"""
from osgeo import gdal  # noqa: F401
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter

sys.stdout.reconfigure(encoding="utf-8")
DAG, SIR, LIM, OUT = sys.argv[1:5]
div = gpd.read_file(LIM, layer="comunas_corregimientos").set_crs(9377, allow_override=True)
boundary = gpd.read_file(LIM, layer="limite_medellin").set_crs(9377, allow_override=True)
div["cod"] = div["codigo"].astype(str)
div["km2"] = div.geometry.area / 1e6

# ---- series 1: DAGRD Tabla 14 (2005-2018)
d = pd.read_csv(DAG, dtype={"cod": str})
t14 = d[(d["amenaza"] == "inundación y avenida torrencial") & ~d["territorio_raw"].str.startswith("Total")]
s1 = t14.groupby("cod")["eventos"].sum()
Y1 = 14
# ---- series 2: SIRMED inundaciones (2021-2025)
s = pd.read_csv(SIR, low_memory=False)
s["year"] = pd.to_datetime(s["fecha_registro"]).dt.year
w = s[(s["tipo_incidente"] == "Inundaciones") & s["year"].between(2021, 2025)].copy()
CORR = {"Palmitas": "50", "San Cristóbal": "60", "Altavista": "70", "San Antonio de Prado": "80", "Santa Elena": "90"}


def code(x):
    if isinstance(x, str) and x.startswith("Comuna "):
        return x.split()[1].zfill(2)
    if isinstance(x, str):
        for k, v in CORR.items():
            if k in x:
                return v
    return None


w["cod"] = w["comuna"].map(code)
print("SIRMED floods 2021-2025:", len(w), "| without territory code:", int(w["cod"].isna().sum()), w.loc[w["cod"].isna(), "comuna"].value_counts().to_dict())
s2 = w.dropna(subset=["cod"]).groupby("cod").size()
Y2 = 5
for name, ser, yrs in (("2005-2018", s1, Y1), ("2021-2025", s2, Y2)):
    tmp = div.set_index("cod").join(ser.rename("n")).dropna(subset=["n"])
    tmp["dens"] = tmp["n"] / tmp["km2"] / yrs
    print(f"\n{name}: total {int(ser.sum())} | density per km2 per year (comunas/corregimientos):")
    print(tmp[["nombre", "n", "km2", "dens"]].sort_values("dens", ascending=False).round(2).to_string())

BREAKS = [0, 0.25, 0.5, 1.0, 2.0, 50]
LABELS = ["menos de 0,25", "0,25 a 0,5", "0,5 a 1", "1 a 2", "más de 2"]
COLORS = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"]
NAMES = {"50": "San Sebastián\nde Palmitas", "60": "San Cristóbal", "70": "Altavista", "80": "San Antonio\nde Prado", "90": "Santa Elena"}


def draw(series, years, title, source, fname):
    g = div.set_index("cod").join(series.rename("n"))
    g["n"] = g["n"].fillna(0)
    g["dens"] = g["n"] / g["km2"] / years
    g = g.reset_index()
    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)
    cmap = ListedColormap(COLORS)
    norm = BoundaryNorm(BREAKS, cmap.N)
    g.plot(ax=ax, column="dens", cmap=cmap, norm=norm, edgecolor="none", zorder=2)
    div.boundary.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.9, zorder=4)
    boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.8, zorder=5)
    for _, r in g.iterrows():
        if r["n"] <= 0:
            continue
        p = r.geometry.representative_point()
        ax.text(p.x, p.y, f"{int(r['n'])}", ha="center", va="center", fontsize=6.4, color="#111111", zorder=7,
                path_effects=[pe.withStroke(linewidth=1.8, foreground="white")])
    xmin, ymin, xmax, ymax = boundary.total_bounds
    pad = 750
    ax.set_xlim(xmin - pad, xmax + pad); ax.set_ylim(ymin - pad, ymax + pad); ax.set_aspect("equal")
    ax.set_xlabel("Este (m) — MAGNA-SIRGAS / Origen Nacional"); ax.set_ylabel("Norte (m)")
    ax.grid(color="#9ca3af", linewidth=0.45, alpha=0.35); ax.set_axisbelow(True)
    fmt = ScalarFormatter(useOffset=False); fmt.set_scientific(False)
    ax.xaxis.set_major_formatter(fmt); ax.yaxis.set_major_formatter(fmt); ax.tick_params(axis="x", rotation=25)
    ax.annotate("N", xy=(0.58, 0.955), xytext=(0.58, 0.855), xycoords="axes fraction", ha="center", va="center", fontsize=11,
                arrowprops={"arrowstyle": "->", "lw": 1.3, "color": "black"})
    scale_m = 5000
    sx = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2 - scale_m / 2
    sy = ymin - pad + (ymax - ymin + 2 * pad) * 0.045
    ax.plot([sx, sx + scale_m], [sy, sy], color="black", lw=2.4, zorder=10)
    ax.text(sx + scale_m / 2, sy + (ymax - ymin) * 0.016, "5 km", ha="center", fontsize=9, zorder=10)
    for _, r in div[div["cod"].isin(NAMES)].iterrows():
        p = r.geometry.representative_point()
        ax.text(p.x, p.y - 700, NAMES[r["cod"]], ha="center", va="top", fontsize=6.3, color="#333333", style="italic", zorder=6,
                path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    handles = [Patch(facecolor=c, edgecolor="#555", linewidth=0.35, label=l) for c, l in zip(COLORS, LABELS)]
    ax.legend(handles=handles, title="Eventos atendidos\npor km² al año", loc="upper right", bbox_to_anchor=(0.985, 0.985), fontsize=7.6, title_fontsize=8.4,
              framealpha=0.94, borderpad=0.55, labelspacing=0.35, handletextpad=0.55).set_zorder(20)
    ax.text(0.985, 0.03, "Cifra: total de\neventos del periodo", transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color="#333333", zorder=20)
    ax.set_title(title, fontsize=14.2, pad=9)
    fig.text(0.5, 0.012, source, ha="center", fontsize=6.0, color="#444444")
    fig.savefig(f"{OUT}/{fname}", dpi=300, facecolor="white")
    plt.close(fig)
    print("saved", fname)


draw(s1, Y1, "Inundaciones y avenidas torrenciales atendidas\npor el DAGRD, 2005–2018",
     "Fuente: elaboración propia a partir de Secretaría de Salud de Medellín (2021), Tabla 14, con registros del DAGRD;\náreas de comunas y corregimientos de la Alcaldía de Medellín.",
     "Figura_8_5_7_mapa_inundaciones_avenidas_dagrd_2005_2018.png")
draw(s2, Y2, "Inundaciones atendidas por el DAGRD,\n2021–2025",
     "Fuente: elaboración propia a partir del histórico de emergencias de SIRMED (Alcaldía de Medellín, 2026);\náreas de comunas y corregimientos de la Alcaldía de Medellín.",
     "Figura_8_5_8_mapa_inundaciones_sirmed_2021_2025.png")
