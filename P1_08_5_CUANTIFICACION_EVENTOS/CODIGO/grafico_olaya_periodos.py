# -*- coding: utf-8 -*-
"""Dot-range figure: daily maximum and minimum temperature (mean per period) at the Olaya Herrera station, across
five periods -- three official IDEAM climatological normals (30-year windows, stepped 10 years) and two recent
blocks computed from the station's own quality-controlled hourly record (which only starts in December 2014, so
these are not full decades). Open markers = official normal; filled markers = station's own data.

usage: grafico_olaya_periodos.py <olaya_periodos_normal_vs_estacion.csv> <out.png>"""
from osgeo import gdal  # noqa: F401
import sys
import textwrap
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

sys.stdout.reconfigure(encoding="utf-8")
CSV, OUT = sys.argv[1:3]
T = pd.read_csv(CSV)
T = T.iloc[::-1].reset_index(drop=True)                # oldest at the bottom, most recent at the top
CMAX, CMIN = "#c0521a", "#2b6ca3"
y = range(len(T))

fig, ax = plt.subplots(figsize=(7.2, 5.6))
fig.subplots_adjust(left=0.16, right=0.945, bottom=0.40, top=0.80)
for yi, r in zip(y, T.itertuples()):
    real = r.fuente.startswith("Estación")
    ax.plot([r.tmin, r.tmax], [yi, yi], color="#9a9a9a", linewidth=1.6, zorder=2)
    for val, c in ((r.tmax, CMAX), (r.tmin, CMIN)):
        ax.scatter(val, yi, s=95 if real else 78, color=c if real else "white", edgecolor=c, linewidth=1.8, zorder=4,
                   marker="o")
    ax.text(r.tmax + 0.16, yi, f"{r.tmax:.1f}", va="center", ha="left", fontsize=8.2, color=CMAX, fontweight="bold" if real else "normal")
    ax.text(r.tmin - 0.16, yi, f"{r.tmin:.1f}", va="center", ha="right", fontsize=8.2, color=CMIN, fontweight="bold" if real else "normal")
ax.axhline(2.5, color="#bdbdbd", linewidth=0.8, linestyle=":", zorder=1)
ax.set_yticks(list(y))
ax.set_yticklabels([f"{r.periodo}" for r in T.itertuples()], fontsize=9)
ax.set_xlim(15.5, 31.2)
ax.set_ylim(-0.7, len(T) - 0.3)
ax.set_xlabel("Temperatura del aire (°C)", fontsize=9)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color="#e5e5e5", linewidth=0.6, zorder=0)
ax.set_axisbelow(True)
ax.scatter([], [], marker="o", s=95, color=CMAX, edgecolor=CMAX, label="Máxima del día")
ax.scatter([], [], marker="o", s=95, color=CMIN, edgecolor=CMIN, label="Mínima del día")
ax.scatter([], [], marker="o", s=78, facecolor="white", edgecolor="#555555", label="Normal IDEAM (30 años)")
ax.scatter([], [], marker="o", s=95, facecolor="#555555", edgecolor="#555555", label="Dato real de la estación")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.27), ncol=2, frameon=False, fontsize=7.6, columnspacing=1.3, handletextpad=0.5)
fig.suptitle("Temperatura del aire en el Aeropuerto Olaya Herrera, por periodo", fontsize=10.6, y=0.978)
NOTE = ("Los tres primeros periodos son normales climatológicas oficiales del IDEAM (ventanas de 30 años, desplazadas cada 10); entre 1971–2000 y 1991–2020 la "
        "mínima subió 0,5 °C y la máxima 0,3 °C: un aumento de +0,25 °C por década en la mínima y +0,15 °C por década en la máxima (tendencia lineal ajustada a "
        "los tres periodos). Los dos últimos son el promedio real de la propia estación, con dato horario validado; el registro abierto solo llega hasta diciembre "
        "de 2014, por lo que 2015–2020 no es una década completa y no se puede tabular 1991–2010 ni décadas anteriores con dato propio. 2021–2026: hasta el 25 de "
        "septiembre; mezcla meses de las tres fases de El Niño y La Niña en proporciones distintas a las de los periodos anteriores, por lo que su comparación con "
        "las normales no aísla el efecto del cambio climático del de la fase de El Niño y La Niña. Fuente: elaboración propia a partir de IDEAM (s. f.-b, s. f.-c, s. f.-d).")
fig.text(0.5, 0.225, chr(10).join(textwrap.wrap(NOTE, 128)), ha="center", va="top", fontsize=6.1, color="#444444", linespacing=1.45)
fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT)
