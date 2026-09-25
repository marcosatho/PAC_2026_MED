# -*- coding: utf-8 -*-
"""Dengue cases per year in Medellin, 2000-2018.
Data transcribed from the table under Figure 42 of the Health Adaptation Plan (Secretaria de Salud de Medellin, 2021, p. 200),
built from the municipal health secretariat surveillance data (2018). 2018 covers epidemiological weeks 1-52.
Cross-check with the text of the plan: 2010 and 2016 are the largest epidemics (15,894 and 18,003 cases); 2013-2015 rise from
2,478 to 3,945 cases. Incidence rates are not plotted: the table's rates for 2008 and 2009 (7.9 and 17.2 per 100,000) are not
consistent with the case counts (733 and 831), so only counts are used.

usage: grafico_dengue_medellin.py <out_png>"""
import sys
import matplotlib.pyplot as plt

OUT = sys.argv[1]
cases = {2000: 140, 2001: 307, 2002: 1327, 2003: 3004, 2004: 700, 2005: 658, 2006: 1233, 2007: 2479, 2008: 733, 2009: 831,
         2010: 15894, 2011: 843, 2012: 779, 2013: 2478, 2014: 3375, 2015: 3945, 2016: 18003, 2017: 2250, 2018: 1324}
epidemic = {2003, 2007, 2010, 2016}


def miles(n):
    return f"{n:,}".replace(",", ".")


fig, ax = plt.subplots(figsize=(7.2, 4.1))
fig.subplots_adjust(left=0.115, right=0.98, bottom=0.2, top=0.86)
years = list(cases)
colors = ["#bd0026" if y in epidemic else "#fd8d3c" for y in years]
bars = ax.bar([str(y) for y in years], [cases[y] for y in years], color=colors, width=0.72, zorder=3)
for y, b in zip(years, bars):
    if y in epidemic:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 250, miles(cases[y]), ha="center", va="bottom", fontsize=7.6, fontweight="bold")
ax.set_ylim(0, 20500)
ax.set_yticks(range(0, 20001, 5000))
ax.set_yticklabels([miles(v) for v in range(0, 20001, 5000)], fontsize=8)
ax.set_ylabel("Casos de dengue al año", fontsize=8.6)
ax.tick_params(axis="x", labelsize=7, rotation=0, pad=2)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#d8d8d8", linewidth=0.6, zorder=0)
ax.set_axisbelow(True)
ax.legend([plt.Rectangle((0, 0), 1, 1, color="#bd0026"), plt.Rectangle((0, 0), 1, 1, color="#fd8d3c")], ["Año de epidemia", "Otros años"],
          loc="upper left", frameon=False, fontsize=8)
ax.annotate("En 2016: casi 50\ncasos por día", xy=(15.68, 11000), xycoords="data", xytext=(0.7, 0.5), textcoords="axes fraction", ha="center", va="center",
            fontsize=8, color="#444444", arrowprops={"arrowstyle": "-\x3e", "lw": 0.9, "color": "#666666", "shrinkA": 2, "shrinkB": 0})
ax.set_title("Casos de dengue por año en Medellín, 2000–2018", fontsize=12.2, pad=8)
fig.text(0.5, 0.045, "Fuente: elaboración propia a partir de Secretaría de Salud de Medellín (2021), con datos de vigilancia de la Secretaría de Salud (2018).",
         ha="center", fontsize=6.3, color="#444444")
fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT, "| total 2000-2018:", sum(cases.values()), "| 2016 per day: %.1f" % (cases[2016] / 366))
