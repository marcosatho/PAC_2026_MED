# -*- coding: utf-8 -*-
"""Validated vegetation fires in Medellin, 23 Jan 2018 - 30 Apr 2025: by year and by territory.
Data: Universidad de Antioquia (2026b), sections V (interannual variability) and VIII (corregimientos and comunas).
Total inventory: 1,357 fires (98 % recorded in situ by SIATA). 'Rest' is the difference to the total."""
import sys
import matplotlib.pyplot as plt

OUT = sys.argv[1]
C_CORR, C_COM, C_REST = "#bd0026", "#fd8d3c", "#c9c9c9"

years = {2018: 134, 2019: 364, 2020: 296, 2021: 133, 2022: 70, 2023: 177, 2024: 165, 2025: 18}
territories = [   # (name, count, kind)
    ("San Cristóbal", 572, "corr"), ("Altavista", 275, "corr"), ("Santa Elena", 261, "corr"),
    ("Robledo", 51, "com"), ("San Javier", 45, "com"), ("Villa Hermosa", 43, "com"), ("Manrique", 31, "com"),
]
TOTAL = 1357
assert sum(years.values()) == TOTAL
rest = TOTAL - sum(c for _, c, _ in territories)
territories.append(("Demás comunas y\ncorregimientos", rest, "rest"))
top3 = sum(c for _, c, k in territories if k == "corr")
print("rest =", rest, "| top-3 corregimientos share = %.1f %%" % (100 * top3 / TOTAL))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 4.0), gridspec_kw={"width_ratios": [1.15, 1.0], "wspace": 0.6})
fig.subplots_adjust(left=0.085, right=0.975, bottom=0.27, top=0.82)

# (a) by year
xs = list(years)
bars = a1.bar([str(x) for x in xs], [years[x] for x in xs], color="#fd8d3c", width=0.72, zorder=3)
bars[-1].set_facecolor("white")
bars[-1].set_edgecolor("#fd8d3c")
bars[-1].set_hatch("////")
for x, b in zip(xs, bars):
    a1.text(b.get_x() + b.get_width() / 2, b.get_height() + 8, str(years[x]), ha="center", va="bottom", fontsize=7.6)
a1.set_ylim(0, 420)
a1.set_ylabel("Incendios validados", fontsize=8.6)
a1.tick_params(axis="x", labelsize=6.8, rotation=0, pad=2)
a1.tick_params(axis="y", labelsize=8)
a1.spines[["top", "right"]].set_visible(False)
a1.grid(axis="y", color="#d8d8d8", linewidth=0.6, zorder=0)
a1.set_axisbelow(True)
a1.set_title("Por año", fontsize=9.6, loc="left")
a1.text(0.99, 0.94, "2025: enero a abril", transform=a1.transAxes, ha="right", va="top", fontsize=7, color="#555555")

# (b) by territory
n = len(territories)
colors = {"corr": C_CORR, "com": C_COM, "rest": C_REST}
for i, (nm, c, k) in enumerate(territories):
    y = n - 1 - i
    a2.barh(y, c, color=colors[k], height=0.7, zorder=3)
    a2.text(c + 8, y, str(c), va="center", ha="left", fontsize=7.6)
a2.set_yticks(range(n))
a2.set_yticklabels([t[0] for t in territories][::-1], fontsize=8)
a2.set_ylim(-0.6, n - 0.4)
a2.set_xlim(0, 680)
a2.spines[["top", "right", "left"]].set_visible(False)
a2.tick_params(axis="y", length=0)
a2.tick_params(axis="x", labelsize=8)
a2.grid(axis="x", color="#d8d8d8", linewidth=0.6, zorder=0)
a2.set_axisbelow(True)
a2.set_xlabel("Incendios validados", fontsize=8.6)
a2.set_title("Por territorio", fontsize=9.6, loc="left", x=-0.42)
a2.legend([plt.Rectangle((0, 0), 1, 1, color=C_CORR), plt.Rectangle((0, 0), 1, 1, color=C_COM)],
          ["Corregimientos", "Comunas"], loc="lower right", frameon=False, fontsize=7.6, bbox_to_anchor=(1.0, 0.16))
a2.text(0.98, 0.5, "Los tres corregimientos\nsuman el %s %%" % f"{100 * top3 / TOTAL:.1f}".replace(".", ","),
        transform=a2.transAxes, ha="right", va="center", fontsize=7.4, color="#444444")

fig.suptitle("Incendios de cobertura vegetal en Medellín, enero de 2018 a abril de 2025 (1.357 eventos)", fontsize=10.6, y=0.965)
fig.text(0.5, 0.115, "Fuente: elaboración propia a partir de Universidad de Antioquia (2026b), secciones V y VIII.",
         ha="center", fontsize=6.3, color="#444444")
fig.text(0.5, 0.075, "Incendios validados en coberturas vegetales (98 % registrados por SIATA); 2025 incluye solo hasta el 30 de abril.",
         ha="center", fontsize=6.3, color="#444444")
fig.text(0.5, 0.035, "«Demás comunas y corregimientos» se obtiene por diferencia con el total; el informe indica que cada uno "
         "registró 24 eventos o menos.", ha="center", fontsize=6.3, color="#444444")
fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT)
