# -*- coding: utf-8 -*-
"""Figura_8_5_3: landslides, floods and forest fires attended by the DAGRD per MONTH, 2021-2026 (SIRMED emergencies layer),
coloured by the ENSO phase of each month (NOAA ONI: La Niña <= -0.5, El Niño >= +0.5).
Months without a published ONI (April-September 2026) are drawn as 'El Niño*' under the assumption that the event develops
under NOAA's definition (author's instruction).  September 2026 is partial (to 25 September).

usage: grafico_sirmed_2021_2026.py <sirmed_csv> <oni.csv> <out_dir> [<monthly_csv_out>]"""
from osgeo import gdal  # noqa: F401
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from enso_episodes import load_oni, classify

sys.stdout.reconfigure(encoding="utf-8")
CSV, ONI, OUT = sys.argv[1:4]
MONTHLY_OUT = sys.argv[4] if len(sys.argv) > 4 else None
d = pd.read_csv(CSV, low_memory=False)
d["ym"] = pd.to_datetime(d["fecha_registro"]).dt.to_period("M")
oni = load_oni(ONI)
idx = pd.period_range("2021-01", "2026-09", freq="M")
TYPES = [("Movimiento en masa", "Movimientos en masa"), ("Inundaciones", "Inundaciones"), ("Incendio forestal", "Incendios forestales")]
M = pd.DataFrame(index=idx)
for tipo, _ in TYPES:
    M[tipo] = d[d["tipo_incidente"] == tipo].groupby("ym").size().reindex(idx).fillna(0).astype(int)
cl = classify(oni, idx)
cl.loc[cl["fase"] == "sin dato", "fase"] = "El Niño*"      # author's assumption for the months without published index
M["oni"] = cl["oni"]
M["fase"] = cl["fase"].replace({"neutro": "Neutro"})
print(M["fase"].value_counts().to_dict())
print("provisional months (El Niño*):", M[M["fase"] == "El Niño*"].index.astype(str).tolist())
if MONTHLY_OUT:
    M.rename_axis("mes").reset_index().assign(mes=lambda x: x["mes"].astype(str)).to_csv(MONTHLY_OUT, index=False, encoding="utf-8-sig")

C = {"La Niña": "#3182bd", "Neutro": "#bdbdbd", "El Niño": "#d94801", "El Niño*": "#fdae6b"}
fig, axes = plt.subplots(3, 1, figsize=(7.2, 7.8), sharex=True, gridspec_kw={"hspace": 0.34})
fig.subplots_adjust(left=0.105, right=0.985, bottom=0.185, top=0.905)
x = np.arange(len(idx))
years = sorted({p.year for p in idx})
for ax, (tipo, title) in zip(axes, TYPES):
    ymax = M[tipo].max() * 1.32
    for xi, p in zip(x, idx):
        ph = M.loc[p, "fase"]
        star = ph == "El Niño*"
        ax.bar(xi, M.loc[p, tipo], width=0.82, color=C[ph], edgecolor="#d94801" if star else "none", linewidth=0.5,
               hatch="////" if star else None, zorder=3)
    for y in years:
        pos = [i for i, p in enumerate(idx) if p.year == y]
        if y != years[0]:
            ax.axvline(pos[0] - 0.5, color="#9a9a9a", linewidth=0.6, linestyle=":", zorder=1)
        tot = int(M.loc[[p for p in idx if p.year == y], tipo].sum())
        ax.text((pos[0] + pos[-1]) / 2, ymax * 0.965, f"{y}: {tot}", ha="center", va="top", fontsize=7.4, color="#333333")
    ax.set_ylim(0, ymax)
    ax.set_xlim(-0.8, len(idx) - 0.2)
    ax.set_title(title, fontsize=9.4, loc="left")
    ax.set_ylabel("Eventos por mes", fontsize=8.4)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e0e0e0", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)
mids = [np.mean([i for i, p in enumerate(idx) if p.year == y]) for y in years]
axes[2].set_xticks(mids)
axes[2].set_xticklabels([str(y) for y in years], fontsize=8)
axes[0].legend(handles=[Patch(color=C["La Niña"], label="La Niña"), Patch(color=C["Neutro"], label="Neutro"), Patch(color=C["El Niño"], label="El Niño"),
                        Patch(facecolor=C["El Niño*"], edgecolor="#d94801", hatch="////", label="El Niño* (en formación)")],
               loc="upper center", bbox_to_anchor=(0.5, 1.30), ncol=4, frameon=False, fontsize=7.4, columnspacing=1.2, handlelength=1.4)
fig.suptitle("Emergencias atendidas por el DAGRD en Medellín, por mes, 2021–2026", fontsize=10.6, y=0.985)
import textwrap
NOTE = ("Sobre cada año: total de eventos del año. Fase de cada mes según el índice oceánico de El Niño de la NOAA (promedio de tres meses): hay El Niño o "
        "La Niña cuando el índice se mantiene en +0,5 o más, o en −0,5 o menos, durante al menos cinco meses seguidos. * Mayo a septiembre de 2026: el episodio "
        "aún no completa los cinco meses (mayo a julio ya superan +0,5; agosto y septiembre no tienen índice publicado); se clasifican como El Niño bajo el "
        "supuesto de que se desarrolle según la definición de la NOAA. Septiembre, hasta el 25. "
        "Fuente: elaboración propia a partir del histórico de emergencias de SIRMED (Alcaldía de Medellín, 2026) y NOAA (s. f.).")
fig.text(0.5, 0.095, chr(10).join(textwrap.wrap(NOTE, 135)), ha="center", va="top", fontsize=6.3, color="#444444", linespacing=1.5)
fig.savefig(f"{OUT}/Figura_8_5_3_emergencias_sirmed_2021_2026.png", dpi=300, facecolor="white")
print("saved")
