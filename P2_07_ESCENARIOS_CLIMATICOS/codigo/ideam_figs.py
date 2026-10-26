# -*- coding: utf-8 -*-
"""Figuras de los escenarios del IDEAM (2024) y de la ficha departamental de 2015, a partir de los PDF ya descargados (sin datos nuevos)."""
import sys
sys.argv = [sys.argv[0]]
from common import *
import re, warnings
from PIL import Image, ImageDraw
import pymupdf
import ideam_maps as IM

SSP = ["SSP1-2.6", "SSP2-4.5", "SSP3-7.0", "SSP5-8.5"]; PER = ["2021-2040", "2041-2060", "2061-2080", "2081-2100"]
CS = {"SSP1-2.6": "#009E73", "SSP2-4.5": "#0072B2", "SSP3-7.0": "#E69F00", "SSP5-8.5": "#CC3311"}

# ---------------------------------------------------------------- 1) figura 4.5 del IDEAM anotada con Medellín
def annotate(name, out, title_note):
    im = Image.open(f"{P2}\\img\\ideam4_fig_{name}.png").convert("RGB")
    arr = np.array(im).astype(int)
    rows, cols = IM.panels(arr)
    ry = [rows[i][1] + 1 for i in range(1, 5)]; ry_end = [rows[i][0] for i in range(2, 6)]
    cx = [cols[i][1] + 1 for i in range(1, 5)]; cx_end = [cols[i][0] for i in range(2, 6)]
    big = im.resize((im.width * 2, im.height * 2), Image.LANCZOS); d = ImageDraw.Draw(big)
    for i in range(4):
        for j in range(4):
            sub = arr[ry[i]:ry_end[i], cx[j]:cx_end[j]]
            x0, y0, x1, y1, _ = IM.mainland_bbox(sub)
            px = x0 + (IM.MED[0] - IM.LON_W) / (IM.LON_E - IM.LON_W) * (x1 - x0)
            py = y0 + (IM.LAT_N - IM.MED[1]) / (IM.LAT_N - IM.LAT_S) * (y1 - y0)
            X, Y = (cx[j] + px) * 2, (ry[i] + py) * 2
            d.ellipse([X - 7, Y - 7, X + 7, Y + 7], outline=(0, 0, 0), width=3); d.ellipse([X - 4, Y - 4, X + 4, Y + 4], outline=(255, 255, 255), width=2)
    big.save(os.path.join(FIG, out)); print("anotada", out, big.size)

annotate("tmed", "I1_tmed_anotada.png", "")
annotate("precip", "I2_precip_anotada.png", "")

# ---------------------------------------------------------------- 2) clases de color en Medellín → rangos
def parse(lbl):
    sign = 1 if lbl.startswith("aumento") else -1
    nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:,\d+)?", lbl.replace(".", ","))]
    if ">" in lbl: lo, hi = nums[0], nums[0] * 1.15
    else: lo, hi = nums[0], nums[1]
    return (lo, hi) if sign > 0 else (-hi, -lo)

VARS = [("precip", "Precipitación anual (%)"), ("tmed", "Temperatura media (°C)"), ("tmax", "Temperatura máxima (°C)"), ("tmin", "Temperatura mínima (°C)"),
        ("hr", "Humedad relativa (puntos %)"), ("viento", "Velocidad del viento (m/s)"), ("rad", "Radiación global (W/m²)")]
TABLE = {}
fig, axes = plt.subplots(2, 4, figsize=(7.4, 4.9), constrained_layout=True)
for ax, (v, tit) in zip(axes.ravel(), VARS):
    data = json.load(open(f"{P2}\\ideam_{v}_medellin_h15.json", encoding="utf-8"))
    for si, s in enumerate(SSP):
        for pi, pr in enumerate(PER):
            cl = data[f"{s}|{pr}"]["clases"]
            if not cl: continue
            keep = {k: w for k, w in cl.items() if w >= 0.15} or cl
            lo = min(parse(k)[0] for k in keep); hi = max(parse(k)[1] for k in keep)
            mid = sum(w * (parse(k)[0] + parse(k)[1]) / 2 for k, w in cl.items()) / sum(cl.values())
            x = pi + (si - 1.5) * 0.17
            ax.plot([x, x], [lo, hi], color=CS[s], lw=2.2, solid_capstyle="butt", alpha=0.85); ax.plot([x], [mid], "o", color=CS[s], ms=3.2, mec="white", mew=0.4)
            TABLE[f"{v}|{s}|{pr}"] = dict(lo=lo, hi=hi, mid=mid, clases=cl)
    ax.axhline(0, color="#374151", lw=0.6); ax.set_xticks(range(4)); ax.set_xticklabels(["2021\n2040", "2041\n2060", "2061\n2080", "2081\n2100"], fontsize=5.6)
    ax.tick_params(axis="y", labelsize=6); ax.set_title(tit, fontsize=7.3); ax.grid(axis="y", color="#e5e7eb", lw=0.4); ax.yaxis.set_major_formatter(ES_FMT)
ax = axes.ravel()[-1]; ax.axis("off")
for si, s in enumerate(SSP): ax.plot([], [], color=CS[s], lw=3, label=s)
ax.legend(loc="center", fontsize=7, frameon=False, title="Escenario", title_fontsize=7.5)
ax.text(0.5, 0.06, "Barra: clases de color con al menos\n15 % del área de la ventana;\npunto: promedio ponderado", transform=ax.transAxes, ha="center", fontsize=5.8, color="#374151")
fig.suptitle("Cambio proyectado por el IDEAM (2024) sobre Medellín frente a 1981–2010, por escenario y periodo", fontsize=8.6)
fig.supxlabel("Fuente: elaboración propia a partir de Ideam (2024, figuras 4.2 a 4.8), lectura de las clases de color en una ventana de ±0,15° alrededor de Medellín.", fontsize=5.7, color="#444444")
save(fig, "I3_clases_Medellin.png")
json.dump(TABLE, open(f"{P2}\\ideam_medellin_tabla.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- 3) ficha departamental de Antioquia (2015), página 24 del PDF
doc = pymupdf.open(r"C:\Users\marco\Downloads\undp-co-escenarioscambioclima_departamental-2015.pdf")
pg = doc[23]; pix = pg.get_pixmap(dpi=170); out = os.path.join(FIG, "I4_ficha_Antioquia_2015.png"); pix.save(out); print("ficha", pix.width, pix.height, pg.rect)

# ---------------------------------------------------------------- 4) comparación de temperatura media entre estudios
SI = json.load(open(f"{P2}\\siata_stats.json", encoding="utf-8"))
fig, ax = plt.subplots(figsize=(7.2, 4.1), constrained_layout=True)
# IDEAM 2024 (Medellín)
for si, s in enumerate(SSP):
    xs, los, his, mids = [], [], [], []
    for pi, pr in enumerate(PER):
        t = TABLE[f"tmed|{s}|{pr}"]; yc = int(pr[:4]) + 10
        ax.plot([yc + (si - 1.5) * 1.6] * 2, [t["lo"], t["hi"]], color=CS[s], lw=3.2, solid_capstyle="butt", alpha=0.9, zorder=3)
        xs.append(yc + (si - 1.5) * 1.6); mids.append(t["mid"])
    ax.plot(xs, mids, "-", color=CS[s], lw=0.8, alpha=0.7, zorder=2)
# IDEAM 2015 (Antioquia, promedio departamental, ensamble de cuatro RCP)
yrs15 = [2025, 2055, 2085]; d15 = [0.8, 1.4, 2.2]
ax.plot(yrs15, d15, "s--", color="#4b5563", ms=5, lw=1, label="IDEAM 2015, Antioquia (ensamble RCP, vs 1976–2005)", zorder=4)
# SIATA 2019 (Distrito, RCP 4.5; valor de la media y de las celdas del casco urbano)
ys = [2035, 2045]; ds = [SI["dT_2030"]["media"], SI["dT_2040"]["media"]]
ax.errorbar(ys, ds, yerr=[[SI["dT_2030"]["media"] - SI["dT_2030"]["min"], SI["dT_2040"]["media"] - SI["dT_2040"]["min"]], [SI["dT_2030"]["max"] - SI["dT_2030"]["media"], SI["dT_2040"]["max"] - SI["dT_2040"]["media"]]], fmt="D", color="#7c3aed", ms=5, capsize=3, lw=1.2, label="SIATA 2019, Distrito (RCP 4.5, vs 1990–2000; barra: mín.–máx. de celdas)", zorder=5)
ax.set_xlim(2015, 2102); ax.set_ylim(0, 5.6); ax.set_xlabel("Centro del periodo", fontsize=7.5); ax.set_ylabel("Cambio de la temperatura media anual (°C)", fontsize=7.5)
ax.tick_params(labelsize=7); ax.grid(color="#e5e7eb", lw=0.5); ax.yaxis.set_major_formatter(ES_FMT)
for si, s in enumerate(SSP): ax.plot([], [], color=CS[s], lw=3, label=f"IDEAM 2024, Medellín, {s} (vs 1981–2010)")
ax.legend(fontsize=6.2, frameon=False, loc="upper left")
ax.set_title("Cambio proyectado de la temperatura media: tres estudios sobre Medellín y Antioquia", fontsize=9)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019; ráster 2_Temper_media), IDEAM et al. (2015, p. 24) e Ideam (2024, figura 4.5). La UdeA (2026a) no entrega temperatura media.", fontsize=5.8, color="#444444")
save(fig, "C1_comparacion_temperatura.png")

# ---------------------------------------------------------------- 5) comparación de precipitación media
fig, ax = plt.subplots(figsize=(7.2, 3.8), constrained_layout=True)
for si, s in enumerate(SSP):
    xs, mids = [], []
    for pi, pr in enumerate(PER):
        t = TABLE[f"precip|{s}|{pr}"]; yc = int(pr[:4]) + 10
        ax.plot([yc + (si - 1.5) * 1.6] * 2, [t["lo"], t["hi"]], color=CS[s], lw=3.2, solid_capstyle="butt", alpha=0.9, zorder=3); xs.append(yc + (si - 1.5) * 1.6); mids.append(t["mid"])
    ax.plot(xs, mids, "-", color=CS[s], lw=0.8, alpha=0.7)
ax.plot(yrs15, [4.88, 6.91, 9.30], "s--", color="#4b5563", ms=5, lw=1, label="IDEAM 2015, Antioquia (ensamble RCP, vs 1976–2005)", zorder=4)
ax.plot([2045], [(SI["hidrico"]["Promedio_dia_RAIN_cambio.tif"]["media"] - 1) * 100], "D", mfc="white", mec="#7c3aed", mew=1.4, ms=6, label="SIATA 2019, lluvia diaria media (cociente 2040–2050; un solo año simulado)", zorder=5)
ax.axhline(0, color="#374151", lw=0.8); ax.set_xlim(2015, 2102); ax.set_ylim(-20, 55)
ax.set_xlabel("Centro del periodo", fontsize=7.5); ax.set_ylabel("Cambio de la precipitación anual (%)", fontsize=7.5); ax.tick_params(labelsize=7); ax.grid(color="#e5e7eb", lw=0.5); ax.yaxis.set_major_formatter(ES_FMT)
for si, s in enumerate(SSP): ax.plot([], [], color=CS[s], lw=3, label=f"IDEAM 2024, Medellín, {s} (vs 1981–2010)")
ax.legend(fontsize=6.2, frameon=False, loc="upper left")
ax.set_title("Cambio proyectado de la precipitación media: los estudios no coinciden en la magnitud", fontsize=9)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019; ráster 12_RAIN_ETR), IDEAM et al. (2015, p. 24) e Ideam (2024, figura 4.2). La UdeA (2026a) reporta aumentos moderados de la lluvia total, sin cifras para Medellín.", fontsize=5.6, color="#444444")
save(fig, "C2_comparacion_precipitacion.png")
print("OK")
