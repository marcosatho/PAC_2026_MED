# -*- coding: utf-8 -*-
"""Share of land in high / medium / low mass-movement hazard by corregimiento (rural soil) and comuna (urban soil).
Data: basic hazard study (EBA, Universidad EAFIT for DAP, 2026), Table 94 (rural soil by corregimiento) and
Table 99 (urban soil by comuna). Areas in hectares: (high, medium, low)."""
import sys
import matplotlib.pyplot as plt

OUT = sys.argv[1]
C_LOW, C_MED, C_HIGH = "#fecc5c", "#fd8d3c", "#bd0026"

corregimientos = {   # Table 94
    "San Sebastián de Palmitas": (3046.21, 1056.58, 1531.76),
    "San Cristóbal": (2347.68, 936.80, 1123.01),
    "Altavista": (1604.23, 707.75, 290.37),
    "San Antonio de Prado": (2669.63, 1491.70, 1391.27),
    "Santa Elena": (2371.82, 596.20, 3647.24),
}
comunas = {          # Table 99
    "1 Popular": (150.06, 58.98, 100.76),
    "2 Santa Cruz": (36.75, 20.37, 162.44),
    "3 Manrique": (244.80, 22.93, 241.89),
    "4 Aranjuez": (28.17, 12.75, 447.41),
    "5 Castilla": (10.34, 8.10, 587.96),
    "6 Doce de Octubre": (19.16, 18.83, 346.99),
    "7 Robledo": (216.78, 71.12, 658.13),
    "8 Villa Hermosa": (186.31, 87.30, 298.09),
    "9 Buenos Aires": (56.55, 13.74, 534.98),
    "10 La Candelaria": (2.92, 0.08, 733.08),
    "11 Laureles Estadio": (3.54, 7.97, 728.75),
    "12 La América": (5.05, 4.11, 388.16),
    "13 San Javier": (112.38, 63.69, 308.85),
    "14 El Poblado": (76.32, 40.28, 1324.83),
    "15 Guayabal": (1.09, 5.90, 721.85),
    "16 Belén": (58.88, 31.77, 794.98),
}


def pct(v):
    t = sum(v)
    return [100 * x / t for x in v]


def es(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")


def sort_desc(d):
    return sorted(d.items(), key=lambda kv: -(pct(kv[1])[0] + pct(kv[1])[1]))


groups = [("Corregimientos (suelo rural)", sort_desc(corregimientos)), ("Comunas (suelo urbano)", sort_desc(comunas))]

fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.4), sharex=True,
                         gridspec_kw={"height_ratios": [len(corregimientos) + 1.1, len(comunas) + 1.1], "hspace": 0.16})
fig.subplots_adjust(left=0.235, right=0.90, bottom=0.135, top=0.905)
for ax, (title, items) in zip(axes, groups):
    n = len(items)
    for i, (name, v) in enumerate(items):
        a, m, b = pct(v)
        y = n - 1 - i
        ax.barh(y, a, color=C_HIGH, height=0.72, zorder=3)
        ax.barh(y, m, left=a, color=C_MED, height=0.72, zorder=3)
        ax.barh(y, b, left=a + m, color=C_LOW, height=0.72, zorder=3)
        ax.text(100.8, y, es(a + m) + " %", va="center", ha="left", fontsize=7.6, color="#222222")
    ax.set_yticks(range(n))
    ax.set_yticklabels([nm for nm, _ in items][::-1], fontsize=8)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xlim(0, 100)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#d8d8d8", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=9.2, fontweight="bold", pad=3, x=-0.235)
axes[1].set_xlabel("Porcentaje del suelo (%)", fontsize=8.6)
axes[1].tick_params(axis="x", labelsize=8)
axes[0].text(100.8, 1.03, "Alta +\nmedia", transform=axes[0].get_xaxis_transform(), ha="left", va="bottom",
             fontsize=7.4, color="#222222", linespacing=1.0)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (C_HIGH, C_MED, C_LOW)]
fig.legend(handles, ["Amenaza alta", "Amenaza media", "Amenaza baja"], loc="upper center", ncol=3, frameon=False,
           fontsize=8.3, bbox_to_anchor=(0.56, 0.995))
fig.text(0.5, 0.05, "Fuente: elaboración propia a partir de Departamento Administrativo de Planeación (2026a), "
         "estudio básico de amenaza (Universidad EAFIT), Tablas 94 y 99.", ha="center", fontsize=6.3, color="#444444")
fig.text(0.5, 0.018, "Ordenados por la suma de amenaza alta y media. Corregimientos: suelo rural (Tabla 94); "
         "comunas: suelo urbano (Tabla 99).", ha="center", fontsize=6.3, color="#444444")
fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT)
