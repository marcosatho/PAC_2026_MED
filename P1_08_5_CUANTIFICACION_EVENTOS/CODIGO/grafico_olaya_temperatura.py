# -*- coding: utf-8 -*-
"""Air temperature at the IDEAM station Aeropuerto Olaya Herrera (Medellin), month by month, 2015-2026, coloured by the ENSO phase of each month.

Panel a: anomaly of the monthly mean of the daily maximum vs the IDEAM 1991-2020 normal of the station.
Panel b: days per month with a daily maximum above 29 C.
Panel c: anomaly of the monthly mean of the daily minimum vs the same normal.
A month is drawn only with >= 24 valid days (missing months: small grey tick on the baseline).
ENSO phase: NOAA episode rule; months after the last published index are 'El Nino*' (author's assumption).

usage: grafico_olaya_temperatura.py <olaya_mensual.csv> <out.png>"""
from osgeo import gdal  # noqa: F401
import sys
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

sys.stdout.reconfigure(encoding="utf-8")
CSV, OUT = sys.argv[1:3]
M = pd.read_csv(CSV)
M["p"] = pd.PeriodIndex(M["mes"], freq="M")
M = M[M["p"] >= pd.Period("2015-01", "M")].reset_index(drop=True)
C = {"La Niña": "#3182bd", "Neutro": "#bdbdbd", "El Niño": "#d94801", "El Niño*": "#fdae6b"}
x = np.arange(len(M))
years = sorted({p.year for p in M["p"]})
comma = lambda v, _: f"{v:+.1f}".replace(".", ",").replace("-", "−") if abs(v) > 1e-9 else "0"

fig, axes = plt.subplots(3, 1, figsize=(7.2, 7.6), sharex=True, gridspec_kw={"hspace": 0.34})
fig.subplots_adjust(left=0.105, right=0.985, bottom=0.165, top=0.905)
PANELS = [("anom_tmax", "Máxima del día: anomalía del promedio mensual (°C)", (-2.4, 3.6), True),
          ("d29", "Días al mes con máxima superior a 29 °C", (0, 33), False),
          ("anom_tmin", "Mínima del día: anomalía del promedio mensual (°C)", (-1.4, 2.0), True)]
for ax, (col, title, ylim, is_anom) in zip(axes, PANELS):
    for xi, r in M.iterrows():
        v = r[col]
        if pd.isna(v):
            ax.plot(xi, 0, marker="|", color="#9a9a9a", markersize=3.2, zorder=4)
            continue
        star = r["fase"] == "El Niño*"
        ax.bar(xi, v, width=0.82, color=C[r["fase"]], edgecolor="#d94801" if star else "none", linewidth=0.5, hatch="////" if star else None, zorder=3)
    for y in years[1:]:
        first = M.index[M["p"] == pd.Period(f"{y}-01", "M")][0]
        ax.axvline(first - 0.5, color="#9a9a9a", linewidth=0.6, linestyle=":", zorder=1)
    if is_anom:
        ax.axhline(0, color="#555555", linewidth=0.7, zorder=2)
        ax.yaxis.set_major_formatter(FuncFormatter(comma))
    ax.set_ylim(*ylim)
    ax.set_xlim(-0.8, len(M) - 0.2)
    ax.set_title(title, fontsize=9.2, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e0e0e0", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)
mids = [np.mean(M.index[[p.year == y for p in M["p"]]]) for y in years]
axes[2].set_xticks(mids)
axes[2].set_xticklabels([str(y) for y in years], fontsize=8)
axes[0].legend(handles=[Patch(color=C["La Niña"], label="La Niña"), Patch(color=C["Neutro"], label="Neutro"), Patch(color=C["El Niño"], label="El Niño"),
                        Patch(facecolor=C["El Niño*"], edgecolor="#d94801", hatch="////", label="El Niño* (en formación)")],
               loc="upper center", bbox_to_anchor=(0.5, 1.36), ncol=4, frameon=False, fontsize=7.4, columnspacing=1.2, handlelength=1.4)
fig.suptitle("Temperatura del aire en el Aeropuerto Olaya Herrera, Medellín, 2015–2026", fontsize=10.6, y=0.985)
NOTE = ("Anomalía: diferencia con el promedio de 1991–2020 de la misma estación. Fase de cada mes según el índice oceánico de El Niño de la NOAA (promedio de tres "
        "meses): hay El Niño o La Niña cuando el índice se mantiene en +0,5 o más, o en −0,5 o menos, durante al menos cinco meses seguidos. * Mayo a septiembre de "
        "2026: se clasifican como El Niño bajo el supuesto de que el episodio se desarrolle según esa definición. Marca gris: mes sin al menos 24 días con dato válido. "
        "Septiembre de 2026, hasta el 25. Fuente: elaboración propia a partir de IDEAM (s. f.-a, s. f.-b, s. f.-c) y NOAA (s. f.).")
fig.text(0.5, 0.098, chr(10).join(textwrap.wrap(NOTE, 135)), ha="center", va="top", fontsize=6.3, color="#444444", linespacing=1.5)
fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT)
