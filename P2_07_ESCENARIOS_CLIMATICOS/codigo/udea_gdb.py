# -*- coding: utf-8 -*-
"""Lectura de los ráster de índices extremos de la geodatabase de la UdeA (contrato 4600105139 de 2025, copia local de la entrega a la Alcaldía)
sobre las celdas de 0,25° (~27,6 km) que tocan el Distrito de Medellín. Escenario SSP3-7.0, 2021-2050, cuatro modelos con mejor desempeño."""
from common import *
from matplotlib.colors import TwoSlopeNorm
import re
GDB = P2 + r"\udea_gdb\C4600105139_2025_CCMED.gdb"
with rasterio.open(GDB) as s: subs = {sd.split(":")[-1]: sd for sd in s.subdatasets}
names = [n for n in subs if n.startswith("AMN_") and "ssp370" in n]
MODELS = {"BCC_CSM2_MR": "BCC-CSM2-MR", "CanESM5": "CanESM5", "KACE_1_0_G": "KACE-1-0-G", "MPI_ESM1_2_HR": "MPI-ESM1-2-HR"}
rows = []
for n in names:
    m = re.match(r"AMN_(TX95p|TN95p|5WSDI|R95p|R99p|RX1day|INT|CWD)_(.+?)_ssp370_(?:95p_)?(DJF|MAM|JJA|SON|cambios)_?(?:2021_2050)?(?:_anual)?$", n)
    if not m: print("sin parsear:", n); continue
    idx, mod, per = m.group(1), m.group(2), m.group(3)
    with rasterio.open(subs[n]) as r:
        a = r.read(1, masked=True).astype(float); tr = r.transform
        touched = rasterize([mapping(BOUND)], out_shape=a.shape, transform=tr, fill=0, default_value=1, dtype="uint8", all_touched=True).astype(bool)
        v = a[touched]
        rows.append(dict(indice=idx, modelo=MODELS.get(mod, mod), periodo=per, celdas=int(touched.sum()), media=float(np.ma.mean(v)), min=float(np.ma.min(v)), max=float(np.ma.max(v)), valores=[float(x) for x in v.filled(np.nan)]))
        if "n_celdas" not in globals(): n_celdas = int(touched.sum()); GRID = (a.shape, tr, r.bounds)
print("celdas que tocan el Distrito:", n_celdas, "| rejilla", GRID[0], "| bounds", [round(b) for b in GRID[2]])
json.dump(rows, open(os.path.join(P2, "udea_gdb_values.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
tab = collections.defaultdict(dict)
for r in rows: tab[(r["indice"], r["periodo"])][r["modelo"]] = r["media"]
for k in sorted(tab): print(k, {m: round(v, 1) for m, v in tab[k].items()})

# ---------------------------------------------------------------- figura 1: calor
MODS = list(MODELS.values()); COL = dict(zip(MODS, ["#1f77b4", "#d95f02", "#1b9e77", "#7b3294"]))
SEAS = ["DJF", "MAM", "JJA", "SON"]; SEAS_L = ["dic–feb", "mar–may", "jun–ago", "sep–nov"]
fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.9), constrained_layout=True)
for ax, idx, tit, unit in zip(axes, ("TX95p", "TN95p", "5WSDI"), ("Días cálidos (TX95p)", "Noches cálidas (TN95p)", "Días en rachas de calor (WSDI)"), ("% de los días del trimestre", "% de los días del trimestre", "días acumulados en las celdas")):
    for j, mod in enumerate(MODS):
        ys = [tab[(idx, s)][mod] for s in SEAS]
        ax.plot(range(4), ys, "o-", color=COL[mod], ms=4, lw=1.1, label=mod)
    if idx != "5WSDI": ax.axhline(5, color="#6b7280", lw=0.8, ls="--"); ax.text(3.05, 5.5, "5 % de referencia", fontsize=5.8, color="#6b7280", ha="right")
    ax.set_xticks(range(4)); ax.set_xticklabels(SEAS_L, fontsize=6.2); ax.tick_params(axis="y", labelsize=6.2); ax.set_title(tit, fontsize=8); ax.set_ylabel(unit, fontsize=6.4); ax.grid(color="#e5e7eb", lw=0.4)
    ax.yaxis.set_major_formatter(ES_FMT)
axes[0].legend(fontsize=5.8, frameon=False, loc="upper left", ncol=1)
fig.suptitle("Calor extremo proyectado en las celdas de Medellín, 2021–2050, SSP3-7.0 (cuatro modelos)", fontsize=8.8)
fig.supxlabel("Fuente: elaboración propia a partir de la geodatabase de Universidad de Antioquia (2026), ráster AMN_TX95p, AMN_TN95p y AMN_5WSDI. Media de las celdas que tocan el Distrito.", fontsize=5.8, color="#444444")
save(fig, "U1_calor_modelos.png")

# ---------------------------------------------------------------- figura 2: lluvia extrema (cambio anual por modelo)
fig, axes = plt.subplots(1, 5, figsize=(7.4, 2.8), constrained_layout=True)
spec = [("RX1day", "Lluvia máxima\nen un día (mm)"), ("R95p", "Lluvia de días\nmuy lluviosos (mm)"), ("R99p", "Lluvia de días extremos\n(mm)"), ("INT", "Intensidad media de\ndías húmedos (mm/día)"), ("CWD", "Racha máxima de\ndías húmedos (días)")]
for ax, (idx, tit) in zip(axes, spec):
    for j, mod in enumerate(MODS):
        v = tab[(idx, "cambios")][mod]; ax.plot([j], [v], "o", color=COL[mod], ms=6)
    ax.axhline(0, color="#374151", lw=0.8); ax.set_xticks(range(4)); ax.set_xticklabels(["BCC", "Can", "KACE", "MPI"], fontsize=6.2); ax.tick_params(axis="y", labelsize=6.2)
    ax.set_title(tit, fontsize=7.3); ax.grid(axis="y", color="#e5e7eb", lw=0.4); ax.yaxis.set_major_formatter(ES_FMT)
    lo, hi = ax.get_ylim(); ax.set_ylim(min(lo, -0.1 * hi), max(hi, 0.1 * abs(lo)))
fig.suptitle("Cambio anual proyectado de la lluvia extrema en las celdas de Medellín, 2021–2050 frente a 1981–2010, SSP3-7.0", fontsize=8.4)
fig.supxlabel("Fuente: elaboración propia a partir de la geodatabase de Universidad de Antioquia (2026), ráster AMN_*_cambios_2021_2050_anual. BCC = BCC-CSM2-MR; Can = CanESM5; MPI = MPI-ESM1-2-HR.", fontsize=5.6, color="#444444")
save(fig, "U2_lluvia_modelos.png")

# ---------------------------------------------------------------- figura 3: mapa regional R95p (cuatro modelos) con Medellín
shape_hw, tr_g, bnds = GRID
fig, axes = plt.subplots(1, 4, figsize=(7.4, 2.9), constrained_layout=True)
vals = {}
for mod, nm in MODELS.items():
    n = f"AMN_R95p_{mod}_ssp370_cambios_2021_2050_anual"
    with rasterio.open(subs[n]) as r: vals[nm] = r.read(1, masked=True).astype(float)
lim = max(abs(float(np.percentile(np.ma.compressed(v), 2))) for v in vals.values()); lim = max(lim, max(abs(float(np.percentile(np.ma.compressed(v), 98))) for v in vals.values()))
ext = (bnds[0], bnds[2], bnds[1], bnds[3])
cx, cy = (XMIN + XMAX) / 2, (YMIN + YMAX) / 2
for ax, (nm, v) in zip(axes, vals.items()):
    im = ax.imshow(np.ma.masked_invalid(v), extent=ext, cmap="RdBu", norm=TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim), interpolation="nearest")
    for pg in (BOUND.geoms if hasattr(BOUND, "geoms") else [BOUND]): ax.plot(*pg.exterior.xy, color="#111111", lw=1.0)
    ax.plot(cx, cy, "k*", ms=5)
    ax.set_title(nm, fontsize=7.6, pad=2); ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
cb = fig.colorbar(im, ax=axes, orientation="horizontal", fraction=0.06, pad=0.03, shrink=0.6); cb.ax.tick_params(labelsize=6); cb.set_label("Cambio de la lluvia de los días muy lluviosos, R95p (mm por año)", fontsize=6.4); cb.ax.xaxis.set_major_formatter(ES_FMT)
fig.suptitle("Cambio proyectado de la lluvia de días muy lluviosos en Antioquia, 2021–2050, SSP3-7.0 (celdas de 0,25°)", fontsize=8.4)
fig.supxlabel("Fuente: elaboración propia a partir de la geodatabase de Universidad de Antioquia (2026), ráster AMN_R95p_*_cambios_2021_2050_anual. Estrella y contorno negro: Distrito de Medellín.", fontsize=5.8, color="#444444")
save(fig, "U3_mapa_R95p_modelos.png")

# resumen numérico para el texto
res = {}
for idx in ("TX95p", "TN95p", "5WSDI"):
    res[idx] = {mod: {s: round(tab[(idx, s)][mod], 1) for s in SEAS} for mod in MODS}
for idx in ("RX1day", "R95p", "R99p", "INT", "CWD"):
    res[idx] = {mod: round(tab[(idx, "cambios")][mod], 2) for mod in MODS}
json.dump(res, open(os.path.join(P2, "udea_gdb_resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False)[:1500])
