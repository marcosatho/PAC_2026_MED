# -*- coding: utf-8 -*-
"""Figures for numeral 8.5 from the DAGRD event tables (PASCCM Tomo I, Tablas 13-14, 2005-2018).

Figura_8_5_1: reported landslide events and flood / torrential-flood events per year, La Niña years highlighted.
Figura_8_5_2: landslide events 2005-2018 by comuna and corregimiento: total, and per square kilometre.

usage: grafico_eventos_dagrd.py <dagrd_long.csv> <oni.csv> <limites.gpkg> <out_dir>"""
from osgeo import gdal  # noqa: F401
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.stats import spearmanr
from enso_episodes import load_oni, classify

sys.stdout.reconfigure(encoding="utf-8")
CSV, ONI, GPKG, OUT = sys.argv[1:5]
d = pd.read_csv(CSV, dtype={"cod": str})
d["anio"] = d["anio"].astype(int)

# ---- La Niña years: at least 6 months of the year with ONI <= -0.5 ---------------------------------------------
_c = classify(load_oni(ONI), pd.period_range("2005-01", "2018-12", freq="M"))
_n = _c[_c["fase"] == "La Niña"].groupby(_c[_c["fase"] == "La Niña"].index.year).size()
NINA = sorted(int(y) for y, n in _n.items() if n >= 6)
print("La Niña years (>= 6 months inside a La Niña episode):", NINA)

tot = d[d["territorio_raw"].str.startswith("Total")].pivot_table(index="anio", columns="amenaza", values="eventos", aggfunc="sum")
mm = tot["movimiento en masa"].astype(int)
fl = tot["inundación y avenida torrencial"].astype(int)
years = list(range(2005, 2019))
print("mm total 2005-2018:", int(mm.sum()), "| per day: %.1f" % (mm.sum() / 5113), "| floods total:", int(fl.sum()))
print("mm per day 2008: %.1f | 2015: %.1f | 2011: %.1f" % (mm[2008] / 366, mm[2015] / 365, mm[2011] / 365))
print("top mm years:", mm.sort_values(ascending=False).head(5).to_dict(), "| top flood years:", fl.sort_values(ascending=False).head(4).to_dict())
share_nina = mm[NINA].sum() / mm.sum()
print("mm events in La Niña years: %.1f %% of total (%d of 14 years)" % (100 * share_nina, len(NINA)))
print("mean mm per year: La Niña %.0f | others %.0f" % (mm[NINA].mean(), mm.drop(NINA).mean()))
print("floods: mean La Niña %.0f | others %.0f | 2006-2011 mean %.0f | 2015-2018 mean %.0f" % (
    fl[NINA].mean(), fl.drop(NINA).mean(), fl.loc[2006:2011].mean(), fl.loc[2015:2018].mean()))

# ---- Figure 1: two stacked panels ------------------------------------------------------------------------------
C_MM, C_MM_D = "#e0b27c", "#a1622f"        # landslides: light / dark (La Niña)
C_FL, C_FL_D = "#9ecae1", "#2b83ba"        # floods: light / dark
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 6.0), sharex=True, gridspec_kw={"hspace": 0.34})
fig.subplots_adjust(left=0.115, right=0.975, bottom=0.185, top=0.89)


def bars(ax, series, c_light, c_dark, ymax, label_fs=7.4):
    cols = [c_dark if y in NINA else c_light for y in years]
    b = ax.bar([str(y) for y in years], [series[y] for y in years], color=cols, width=0.72, zorder=3)
    for y, r in zip(years, b):
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + ymax * 0.015, f"{series[y]:,}".replace(",", "."), ha="center", va="bottom", fontsize=label_fs)
    ax.set_ylim(0, ymax)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#d8d8d8", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=8)


bars(a1, mm, C_MM, C_MM_D, 5500)
a1.set_title("Movimientos en masa", fontsize=9.6, loc="left")
a1.set_ylabel("Eventos reportados", fontsize=8.6)
a1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", ".")))
a1.text(0.99, 0.90, "2008: 13 eventos por día", transform=a1.transAxes, ha="right", va="top", fontsize=7.6, color="#444444")
bars(a2, fl, C_FL, C_FL_D, 380)
a2.set_title("Inundaciones y avenidas torrenciales", fontsize=9.6, loc="left")
a2.set_ylabel("Eventos reportados", fontsize=8.6)
a2.legend(handles=[Patch(color="#5a5a5a", label="Año con La Niña (6 meses o más)"), Patch(color="#bdbdbd", label="Otros años")],
          loc="upper right", frameon=False, fontsize=7.6, bbox_to_anchor=(1.0, 1.02))
fig.suptitle("Emergencias por lluvia atendidas por el DAGRD en Medellín, 2005–2018", fontsize=10.6, y=0.965)
fig.text(0.5, 0.075, "Fuente: elaboración propia a partir de Secretaría de Salud de Medellín (2021), Tablas 13 y 14, con registros del DAGRD.\n"
         "Años con La Niña: al menos seis meses dentro de un episodio de La Niña (índice oceánico de El Niño de la NOAA en −0,5 o menos, cinco meses seguidos o más).",
         ha="center", fontsize=6.3, color="#444444", linespacing=1.6)
fig.savefig(f"{OUT}/Figura_8_5_1_eventos_dagrd_por_anio.png", dpi=300, facecolor="white")
plt.close(fig)

# ---- Figure 2: by territory (total + per km2) -----------------------------------------------------------------
div = gpd.read_file(GPKG, layer="comunas_corregimientos")
div["cod"] = div["codigo"].astype(str)
area_km2 = (div.set_index("cod")["st_area(shape)"] / 1e6).to_dict()
t = d[(d["amenaza"] == "movimiento en masa") & ~d["territorio_raw"].str.startswith("Total")]
by = t.groupby(["cod", "territorio"])["eventos"].sum().reset_index()
by["cod"] = by["cod"].astype(str).str.zfill(2)
by["km2"] = by["cod"].map(area_km2)
by["dens"] = by["eventos"] / by["km2"]
by["tipo"] = np.where(by["cod"].astype(int) >= 50, "corr", "com")
by = by.sort_values("eventos", ascending=False).reset_index(drop=True)
TOT = by["eventos"].sum()
print("\ntotal:", TOT, "(should equal", int(mm.sum()), ")")
print(by.assign(share=lambda x: 100 * x["eventos"] / TOT).round(1).to_string())
top4 = by.head(4)
print("top4:", top4["territorio"].tolist(), "share %.1f %%" % (100 * top4["eventos"].sum() / TOT))
print("top6 share: %.1f %%" % (100 * by.head(6)["eventos"].sum() / TOT))

# correlation with EBA hazard (share of urban soil in high+medium), Table 99, comunas only
EBA = {"01": (150.06, 58.98, 100.76), "02": (36.75, 20.37, 162.44), "03": (244.80, 22.93, 241.89), "04": (28.17, 12.75, 447.41),
       "05": (10.34, 8.10, 587.96), "06": (19.16, 18.83, 346.99), "07": (216.78, 71.12, 658.13), "08": (186.31, 87.30, 298.09),
       "09": (56.55, 13.74, 534.98), "10": (2.92, 0.08, 733.08), "11": (3.54, 7.97, 728.75), "12": (5.05, 4.11, 388.16),
       "13": (112.38, 63.69, 308.85), "14": (76.32, 40.28, 1324.83), "15": (1.09, 5.90, 721.85), "16": (58.88, 31.77, 794.98)}
hz = {k: 100 * (v[0] + v[1]) / sum(v) for k, v in EBA.items()}
c = by[by["tipo"] == "com"].copy()
c["haz"] = c["cod"].map(hz)
r_tot = spearmanr(c["eventos"], c["haz"])[0]
r_den = spearmanr(c["dens"], c["haz"])[0]
print("\nSpearman comunas (n=%d): events vs hazard share %.2f | events per km2 vs hazard share %.2f" % (len(c), r_tot, r_den))
print(c[["territorio", "eventos", "dens", "haz"]].sort_values("dens", ascending=False).round(1).to_string())

fig, (b1, b2) = plt.subplots(1, 2, figsize=(7.2, 6.4), sharey=True, gridspec_kw={"wspace": 0.10, "width_ratios": [1, 1]})
fig.subplots_adjust(left=0.235, right=0.975, bottom=0.165, top=0.885)
n = len(by)
col = {"com": "#a1622f", "corr": "#d9b99b"}
for i, r in by.iterrows():
    y = n - 1 - i
    b1.barh(y, r["eventos"], color=col[r["tipo"]], height=0.72, zorder=3)
    b1.text(r["eventos"] + 60, y, f"{int(r['eventos']):,}".replace(",", "."), va="center", fontsize=7.2)
b1.set_yticks(range(n))
b1.set_yticklabels(by["territorio"].str.replace("San Sebastián de Palmitas", "San Sebastián de Palmitas")[::-1], fontsize=7.6)
b1.set_xlim(0, 6400)
b1.set_title("Total 2005–2018", fontsize=9, loc="left")
b1.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", ".")))
by2 = by.sort_values("eventos", ascending=False)
for i, r in by.iterrows():
    y = n - 1 - i
    b2.barh(y, r["dens"], color=col[r["tipo"]], height=0.72, zorder=3)
    b2.text(r["dens"] + 22, y, f"{r['dens']:,.0f}".replace(",", "."), va="center", fontsize=7.2)
b2.set_xlim(0, 1500)
b2.set_title("Por kilómetro cuadrado", fontsize=9, loc="left")
b2.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", ".")))
for ax in (b1, b2):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", labelsize=7.6)
    ax.grid(axis="x", color="#d8d8d8", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(-0.6, n - 0.4)
b1.set_xlabel("Eventos reportados", fontsize=8.4)
b2.set_xlabel("Eventos por km²", fontsize=8.4)
b2.legend(handles=[Patch(color=col["com"], label="Comunas"), Patch(color=col["corr"], label="Corregimientos")],
          loc="lower right", frameon=False, fontsize=7.6)
fig.suptitle("Movimientos en masa atendidos por el DAGRD, por comuna y corregimiento", fontsize=10.2, y=0.965)
fig.text(0.5, 0.035, "Fuente: elaboración propia a partir de Secretaría de Salud de Medellín (2021), Tabla 13, con registros del DAGRD; áreas de\n"
         "comunas y corregimientos de la Alcaldía de Medellín. Ordenados por número total de eventos.",
         ha="center", fontsize=6.3, color="#444444", linespacing=1.6)
fig.savefig(f"{OUT}/Figura_8_5_2_movimientos_masa_dagrd_por_territorio.png", dpi=300, facecolor="white")
by.to_csv(f"{OUT}/../dagrd_movimientos_masa_por_territorio_2005_2018.csv", index=False, encoding="utf-8-sig")
print("saved figures")
