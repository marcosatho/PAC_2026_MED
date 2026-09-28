# -*- coding: utf-8 -*-
"""Figures for numeral 8.5 from the Geohazards landslide / debris-flow inventory (Medellín records).

Figura_8_5_4: records and deaths per decade, 1920s-2020s (probable duplicates removed).
Figura_8_5_5: map of located records (default-placed points excluded), size by deaths, colour by period.

usage: figuras_geohazards_medellin.py <geohazards_medellin_9377.gpkg> <limites.gpkg> <out_dir>"""
from osgeo import gdal  # noqa: F401
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.ticker import ScalarFormatter

sys.stdout.reconfigure(encoding="utf-8")
EV, LIM, OUT = sys.argv[1:4]
ev = gpd.read_file(EV, layer="eventos").set_crs(9377, allow_override=True)
ev["date"] = pd.to_datetime(ev["date"])
n_all = len(ev)
ev = ev[~ev["dup_same_day_110m"]].copy()
ev["fatalities"] = ev["fatalities_verified"]
print("records:", n_all, "| after removing probable duplicates:", len(ev))

# ---- decade series ------------------------------------------------------------------------------------------
ev["decade"] = (ev["year"] // 10) * 10
dec = ev.groupby("decade").agg(n=("id", "size"), deaths=("fatalities", "sum"),
                               rain=("trigger_es", lambda s: int((s == "lluvia").sum())),
                               ev_deaths=("fatalities", lambda s: int((s > 0).sum())))
print(dec.to_string())
early = dec.loc[dec.index < 1920]
dec = dec.loc[dec.index >= 1920]
print("before 1920:", early.to_dict("list"))
print("since 2000 rain-tagged share: %.1f %%" % (100 * (ev.loc[ev["year"] >= 2000, "trigger_es"] == "lluvia").mean()))
print("events with deaths (all):", int((ev["fatalities"] > 0).sum()), "| deaths total:", int(ev["fatalities"].sum()))
print("events with >= 5 deaths:", int((ev["fatalities"] >= 5).sum()), "| share of deaths in the two largest:",
      "%.1f %%" % (100 * ev["fatalities"].nlargest(2).sum() / ev["fatalities"].sum()))
since2000 = ev[ev["year"] >= 2000]
print("since 2000: records", len(since2000), "| deaths", int(since2000["fatalities"].sum()), "| events with deaths", int((since2000["fatalities"] > 0).sum()))
print("2000s/2010s/2020s deaths:", dec.loc[[2000, 2010, 2020], "deaths"].to_dict())
# months (rain seasons)
mm = ev.groupby("month").size()
print("records by month:", mm.to_dict())
print("share Apr-Jun + Sep-Nov: %.1f %%" % (100 * mm.loc[[4, 5, 6, 9, 10, 11]].sum() / mm.sum()))

C_N, C_D = "#a1622f", "#bd0026"
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 6.0), sharex=True, gridspec_kw={"hspace": 0.34})
fig.subplots_adjust(left=0.115, right=0.975, bottom=0.185, top=0.89)
labels = [f"{d}s" if d < 2020 else "2020–\n2026" for d in dec.index]
x = np.arange(len(dec))
b1 = a1.bar(x, dec["n"], color="#e0b27c", width=0.7, zorder=3)
for xi, v in zip(x, dec["n"]):
    a1.text(xi, v + 8, str(int(v)), ha="center", va="bottom", fontsize=7.6)
a1.set_ylim(0, 430)
a1.set_ylabel("Registros", fontsize=8.6)
a1.set_title("Deslizamientos y flujos de detritos registrados", fontsize=9.6, loc="left")
b2 = a2.bar(x, dec["deaths"], color=C_D, width=0.7, zorder=3)
for xi, v in zip(x, dec["deaths"]):
    a2.text(xi, v + 12, str(int(v)), ha="center", va="bottom", fontsize=7.6)
a2.set_ylim(0, 720)
a2.set_ylabel("Personas fallecidas", fontsize=8.6)
a2.set_title("Personas fallecidas", fontsize=9.6, loc="left")
i80 = list(dec.index).index(1980)
a2.annotate("Villatina, 1987:\n500 personas", xy=(i80, 593), xytext=(i80 + 1.35, 560), fontsize=7.4, ha="left", va="center",
            arrowprops={"arrowstyle": "-", "lw": 0.8, "color": "#444444"})
i50 = list(dec.index).index(1950)
a2.annotate("Media Luna, 1954:\ncerca de 70 personas", xy=(i50, 160), xytext=(i50 - 0.1, 320), fontsize=7.4, ha="center", va="center",
            arrowprops={"arrowstyle": "-", "lw": 0.8, "color": "#444444"})
a2.set_xticks(x)
a2.set_xticklabels(labels, fontsize=8)
for ax in (a1, a2):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#d8d8d8", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=8)
fig.suptitle("Eventos por movimientos en masa en Medellín, por década", fontsize=10.6, y=0.965)
fig.text(0.5, 0.06, "Fuente: elaboración propia a partir del inventario de movimientos en masa de Geohazards (Medellín, %s registros).\n"
         "No se muestran los dos registros anteriores a 1920." % f"{len(ev):,}".replace(",", "."), ha="center", fontsize=6.3, color="#444444", linespacing=1.6)
fig.savefig(f"{OUT}/Figura_8_5_4_geohazards_registros_y_muertes_por_decada.png", dpi=300, facecolor="white")
plt.close(fig)

# ---- map ------------------------------------------------------------------------------------------------------
divisions = gpd.read_file(LIM, layer="comunas_corregimientos").set_crs(9377, allow_override=True)
boundary = gpd.read_file(LIM, layer="limite_medellin").set_crs(9377, allow_override=True)
pts = ev[ev["territorio"].notna()].copy()
print("\nlocated points:", len(pts), "of", len(ev), "| default-placed:", int(ev["default_location"].sum()))
fig, ax = plt.subplots(figsize=(7.2, 6.6))
fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)
divisions.plot(ax=ax, facecolor="#f3f3f3", edgecolor="none", zorder=1)
divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.9, zorder=4)
boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.8, zorder=5)
old = pts[pts["year"] < 2000]
new = pts[pts["year"] >= 2000]


def size(f):
    return np.where(f >= 5, 60, np.where(f >= 1, 22, 7))


ax.scatter(old.geometry.x, old.geometry.y, s=size(old["fatalities"]), c="#7f7f7f", alpha=0.55, edgecolors="white", linewidths=0.25, zorder=6)
ax.scatter(new.geometry.x, new.geometry.y, s=size(new["fatalities"]), c="#e6550d", alpha=0.7, edgecolors="white", linewidths=0.25, zorder=7)
for nm, (yr, lbl, dx, dy) in {"Villatina": (1987, "Villatina 1987\n(500 fallecidos)", 2200, 800),
                              "Media Luna": (1954, "Media Luna 1954\n(cerca de 70 fallecidos)", 300, -2400)}.items():
    r = pts[(pts["year"] == yr) & (pts["fatalities"] >= 50)]
    if len(r):
        p = r.geometry.iloc[0]
        ax.annotate(lbl, xy=(p.x, p.y), xytext=(p.x + dx, p.y + dy), fontsize=7, ha="left", va="center", zorder=9,
                    arrowprops={"arrowstyle": "-", "lw": 0.7, "color": "#222222"},
                    path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    else:
        print("annotation target not located:", nm, yr)
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
NAMES = {"50": "San Sebastián\nde Palmitas", "60": "San Cristóbal", "70": "Altavista", "80": "San Antonio\nde Prado", "90": "Santa Elena"}
for _, r in divisions[divisions["codigo"].isin(NAMES)].iterrows():
    p = r.geometry.representative_point()
    dy = 3000 if r["codigo"] == "90" else 0
    ax.text(p.x, p.y + dy, NAMES[r["codigo"]], ha="center", va="center", fontsize=6.3, color="#333333", style="italic", zorder=6,
            path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
h = [plt.scatter([], [], s=7, c="#7f7f7f", alpha=0.7, label="Hasta 1999"),
     plt.scatter([], [], s=7, c="#e6550d", alpha=0.8, label="2000 en adelante"),
     plt.scatter([], [], s=7, c="#bbbbbb", label="Sin fallecidos registrados"),
     plt.scatter([], [], s=22, c="#bbbbbb", label="1 a 4 fallecidos"),
     plt.scatter([], [], s=60, c="#bbbbbb", label="5 o más fallecidos")]
ax.legend(handles=h, title="Registros de deslizamientos\ny flujos de detritos", loc="upper right", bbox_to_anchor=(0.985, 0.985),
          fontsize=7.4, title_fontsize=8.2, framealpha=0.94, borderpad=0.55, labelspacing=0.4, handletextpad=0.55).set_zorder(20)
ax.set_title("Deslizamientos y flujos de detritos registrados\nDistrito de Medellín", fontsize=14.2, pad=9)
fig.text(0.5, 0.012, "Fuente: elaboración propia a partir del inventario de movimientos en masa de Geohazards (%s registros con ubicación\n"
         "de %s; se excluyen los registros sin coordenada propia del evento)." % (f"{len(pts):,}".replace(",", "."), f"{len(ev):,}".replace(",", ".")), ha="center", fontsize=6.0, color="#444444")
fig.savefig(f"{OUT}/Figura_8_5_5_mapa_registros_geohazards.png", dpi=300, facecolor="white")
print("saved")
