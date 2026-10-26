# -*- coding: utf-8 -*-
"""Mapas y cifras del Distrito de Medellín a partir de los ráster de soporte del estudio DAGRD-SIATA (2019), ya guardados en el Drive.
Malla nativa ~1 km (WRF), reproyectada a EPSG:9377 con vecino más cercano (sin inventar detalle). Diseño limpio, sin coordenadas en los ejes."""
from common import *
from matplotlib.colors import TwoSlopeNorm
OUT = {}
def p(sub, name): return os.path.join(SIATA, sub, name)
MES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
lab = {1990: "1990–2000", 2030: "2030–2040", 2040: "2040–2050"}
def newfig(w, h): return plt.figure(figsize=(w, h), constrained_layout=True)
def gridaxes(fig, nr, nc):
    return fig.subplots(nr, nc, squeeze=False)

# ---------------------------------------------------------------- temperatura y precipitación mensuales
T, P = {}, {}
for yr in (1990, 2030, 2040):
    ts, ps = [], []
    for m in range(1, 13):
        a, tr = load9377(p("2_Temper_media", f"Temper_{yr}-{m:02d}.tif"), kelvin=True); ts.append(a)
        b, _ = load9377(p("1_Precip_media", f"Precip_{yr}-{m:02d}.tif")); ps.append(b)
    T[yr], P[yr] = np.stack(ts), np.stack(ps)
inside = inside_mask(T[1990][0].shape, tr)
OUT["celdas_distrito_1km"] = int(inside.sum())
Tm = {y: np.nanmean(T[y], axis=0) for y in T}; Pa = {y: np.nansum(P[y], axis=0) for y in P}
for y in T:
    v = Tm[y][inside]; OUT[f"T_{y}"] = dict(media=float(np.nanmean(v)), min=float(np.nanmin(v)), max=float(np.nanmax(v)))
    v = Pa[y][inside]; OUT[f"P_{y}"] = dict(media=float(np.nanmean(v)), min=float(np.nanmin(v)), max=float(np.nanmax(v)))
for y in (2030, 2040):
    d = (Tm[y] - Tm[1990])[inside]; OUT[f"dT_{y}"] = dict(media=float(np.nanmean(d)), min=float(np.nanmin(d)), max=float(np.nanmax(d)))
    OUT[f"dP_{y}"] = dict(media_ratio=float((np.nanmean(Pa[y][inside]) / np.nanmean(Pa[1990][inside]) - 1) * 100))
OUT["ciclo_T"] = {y: [float(np.nanmean(T[y][m][inside])) for m in range(12)] for y in T}
OUT["ciclo_P"] = {y: [float(np.nanmean(P[y][m][inside])) for m in range(12)] for y in P}
# urbano: celdas con T media 1990 >= 19 °C (casco urbano del valle)
urb = inside & (Tm[1990] >= 19)
OUT["urbano_celdas"] = int(urb.sum()); OUT["dT_urbano"] = {y: float(np.nanmean((Tm[y] - Tm[1990])[urb])) for y in (2030, 2040)}; OUT["T1990_urbano"] = float(np.nanmean(Tm[1990][urb]))

fig = newfig(7.4, 3.7); axes = gridaxes(fig, 1, 3)[0]
im0 = district_panel(axes[0], Tm[1990], tr, "YlOrRd", 10, 22, f"1990–2000\nmedia del Distrito {es(OUT['T_1990']['media'])} °C")
hcbar(fig, axes[0], im0, "Temperatura media anual (°C)")
dmax = max(OUT["dT_2030"]["max"], OUT["dT_2040"]["max"]); dmin = min(OUT["dT_2030"]["min"], OUT["dT_2040"]["min"])
for ax, y in zip(axes[1:], (2030, 2040)):
    im = district_panel(ax, Tm[y] - Tm[1990], tr, "OrRd", round(dmin - 0.02, 2), round(dmax + 0.02, 2), f"{lab[y]} menos 1990–2000\nmedia {es(OUT[f'dT_{y}']['media'], 2, True)} °C")
hcbar(fig, axes[1:], im, "Cambio de la temperatura media anual (°C)", shrink=0.8)
north_scale(axes[2], 5)
fig.suptitle("Temperatura media anual simulada en el Distrito de Medellín (RCP 4.5, CCSM4 reducido a 1 km)", fontsize=9.2)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019), ráster 2_Temper_media (media de 12 meses; kelvin convertido a °C).", fontsize=6, color="#444444")
save(fig, "S1_temperatura_media.png")

fig = newfig(7.2, 2.6); axes = gridaxes(fig, 1, 2)[0]
col = {1990: "#4b5563", 2030: "#f59e0b", 2040: "#b91c1c"}
for y in (1990, 2030, 2040):
    axes[0].plot(range(12), OUT["ciclo_T"][y], color=col[y], marker="o", ms=3, lw=1.3, label=lab[y]); axes[1].plot(range(12), OUT["ciclo_P"][y], color=col[y], marker="o", ms=3, lw=1.3, label=lab[y])
for ax, t, yl in zip(axes, ("Temperatura media mensual", "Precipitación mensual simulada"), ("°C", "mm por mes")):
    ax.set_xticks(range(12)); ax.set_xticklabels(MES, fontsize=6.3); ax.tick_params(axis="y", labelsize=6.3); ax.set_title(t, fontsize=8.3); ax.set_ylabel(yl, fontsize=7); ax.grid(color="#d1d5db", lw=0.4); ax.yaxis.set_major_formatter(ES_FMT)
axes[0].legend(fontsize=6.3, frameon=False, loc="lower right")
fig.suptitle("Ciclo anual simulado, promedio del Distrito de Medellín (RCP 4.5)", fontsize=9)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019), ráster 1_Precip_media y 2_Temper_media.\nUn solo año climatológico simulado por década.", fontsize=6, color="#444444")
save(fig, "S3_ciclo_anual.png")

# ---------------------------------------------------------------- días calurosos
DAYS = {}
fig = newfig(7.2, 5.6); axes = gridaxes(fig, 2, 3)
for r, thr in enumerate((29, 30)):
    arrs = {}
    for yr in (1990, 2030, 2040):
        a, trd = load9377(p("4_Num_dias_Tmax", f"Temp_{yr}_Num_DiasTmaxh_Umbral_{thr}.tif")); a, ins = fill_district_gaps(a, trd); arrs[yr] = a
        v = a[ins]; DAYS[f"{thr}_{yr}"] = dict(media=float(np.nanmean(v)), max=float(np.nanmax(v)), area_ge1=float((v >= 1).mean() * 100), area_ge10=float((v >= 10).mean() * 100), area_ge30=float((v >= 30).mean() * 100), area_ge90=float((v >= 90).mean() * 100), celdas=int(ins.sum()))
    vmax = max(np.nanmax(arrs[y][inside_mask(arrs[y].shape, trd)]) for y in arrs)
    for c, yr in enumerate((1990, 2030, 2040)):
        im = district_panel(axes[r][c], arrs[yr], trd, "YlOrRd", 0, vmax, f"{lab[yr]}\nmedia {DAYS[f'{thr}_{yr}']['media']:.0f}; máx. {DAYS[f'{thr}_{yr}']['max']:.0f} d/año")
    hcbar(fig, axes[r].tolist(), im, f"Días al año con temperatura máxima horaria superior a {thr} °C", shrink=0.5, pad=0.02, fraction=0.04)
north_scale(axes[0][2], 5)
fig.suptitle("Días al año con calor fuerte en el Distrito de Medellín (RCP 4.5)", fontsize=9.4)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019), ráster 4_Num_dias_Tmax. Cada fila conserva su propia escala de color.", fontsize=6, color="#444444")
save(fig, "S4_dias_calurosos.png"); OUT["dias"] = DAYS

# ---------------------------------------------------------------- precipitación extrema (cambio frente a 1990)
EXT = {}
fig = newfig(5.6, 5.4); axes = gridaxes(fig, 2, 2)
for r, pc in enumerate((90, 95)):
    base, trp = load9377(p("3_Precip_extrema", f"PPT_1990_Percentil_{pc}.tif")); base, ins = fill_district_gaps(base, trp)
    EXT[f"P{pc}_1990"] = float(np.nanmean(base[ins])); vals = {}
    for yr in (2030, 2040):
        a, _ = load9377(p("3_Precip_extrema", f"PPT_{yr}_Percentil_{pc}.tif")); a, _ = fill_district_gaps(a, trp)
        vals[yr] = (a / base - 1) * 100; EXT[f"P{pc}_{yr}"] = float(np.nanmean(a[ins])); EXT[f"dP{pc}_{yr}"] = dict(media=float(np.nanmean(vals[yr][ins])), min=float(np.nanmin(vals[yr][ins])), max=float(np.nanmax(vals[yr][ins])), frac_pos=float((vals[yr][ins] > 0).mean() * 100))
    lim = max(abs(np.nanpercentile(vals[y][ins], q)) for y in vals for q in (2, 98)); norm = TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim)
    for c, yr in enumerate((2030, 2040)):
        im = district_panel(axes[r][c], vals[yr], trp, "RdBu", None, None, f"Percentil {pc}, {lab[yr]}\nmedia {es(EXT[f'dP{pc}_{yr}']['media'], 1, True)} %; aumenta en {EXT[f'dP{pc}_{yr}']['frac_pos']:.0f} % del área", norm=norm)
    hcbar(fig, axes[r].tolist(), im, "Cambio frente a 1990–2000 (%)", shrink=0.7, pad=0.02, fraction=0.05)
north_scale(axes[0][1], 5)
fig.suptitle("Cambio en la lluvia horaria extrema, Distrito de Medellín (RCP 4.5)\nazul: aumenta; rojo: disminuye", fontsize=9)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019), ráster 3_Precip_extrema (lluvia horaria con más de 0,5 mm/h).", fontsize=6, color="#444444")
save(fig, "S5_precip_extrema_cambio.png"); OUT["extrema"] = EXT

# ---------------------------------------------------------------- balance hídrico (malla de 3 km)
names = [("11_T2_ETP", "Promedio_dia_T2_cambio.tif", "Temperatura del aire a 2 m\n(cambio en °C)", "OrRd", None),
         ("11_T2_ETP", "Promedio_dia_ETP_cambio.tif", "Evapotranspiración potencial\n(cociente 2040–2050 / 1990–2000)", "PuOr_r", 1.0),
         ("12_RAIN_ETR", "Promedio_dia_ETR_cambio.tif", "Evapotranspiración real\n(cociente 2040–2050 / 1990–2000)", "PuOr_r", 1.0),
         ("12_RAIN_ETR", "Promedio_dia_RAIN_cambio.tif", "Lluvia media diaria\n(cociente 2040–2050 / 1990–2000)", "BrBG", 1.0)]
HID = {}
fig = newfig(6.4, 6.2); axes = gridaxes(fig, 2, 2)
for ax, (sub, f, title, cmap, ctr) in zip(axes.ravel(), names):
    a, tr3 = load9377(p(sub, f)); ext = extent(a, tr3); ins3 = inside_mask(a.shape, tr3); v = a[ins3]
    HID[f] = dict(media=float(np.nanmean(v)), min=float(np.nanmin(v)), max=float(np.nanmax(v)), celdas=int(np.isfinite(v).sum()), dominio_media=float(np.nanmean(a)), dominio_min=float(np.nanmin(a)), dominio_max=float(np.nanmax(a)))
    if ctr is None: im = ax.imshow(np.ma.masked_invalid(a), extent=ext, cmap=cmap, vmin=np.nanmin(a), vmax=np.nanmax(a))
    else:
        half = max(abs(np.nanpercentile(a, 1) - ctr), abs(np.nanpercentile(a, 99) - ctr), 0.05)
        im = ax.imshow(np.ma.masked_invalid(a), extent=ext, cmap=cmap, norm=TwoSlopeNorm(vmin=ctr - half, vcenter=ctr, vmax=ctr + half))
    for pg in (BOUND.geoms if hasattr(BOUND, "geoms") else [BOUND]): ax.plot(*pg.exterior.xy, color="#111111", lw=1.1)
    ax.set_title(title, fontsize=8, pad=3); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    hcbar(fig, ax, im, "", shrink=0.8, pad=0.02, fraction=0.045)
fig.suptitle("Balance hídrico simulado en la región de Medellín hacia 2040–2050 (RCP 4.5, malla de 3 km)\ncontorno negro: Distrito", fontsize=8.8)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019), ráster 11_T2_ETP y 12_RAIN_ETR.\nUn solo año climatológico por década: el patrón de la lluvia es ruidoso.", fontsize=6, color="#444444")
save(fig, "S6_balance_hidrico.png"); OUT["hidrico"] = HID
ins3 = inside_mask(a.shape, tr3)
def mean3(sub, f): x, _ = load9377(p(sub, f)); return float(np.nanmean(x[ins3]))
OUT["hidrico_abs"] = {"ETP_mm_dia": [mean3("11_T2_ETP", "Promedio_dia_ETP_1990.tif"), mean3("11_T2_ETP", "Promedio_dia_ETP_2040.tif")],
                      "ETR_mm_dia": [mean3("12_RAIN_ETR", "Promedio_dia_ETR_1990.tif"), mean3("12_RAIN_ETR", "Promedio_dia_ETR_2040.tif")],
                      "RAIN_mm_dia": [mean3("12_RAIN_ETR", "Promedio_dia_RAIN_1990.tif"), mean3("12_RAIN_ETR", "Promedio_dia_RAIN_2040.tif")],
                      "T2_C": [mean3("11_T2_ETP", "Promedio_dia_T2_1990.tif"), mean3("11_T2_ETP", "Promedio_dia_T2_2040.tif")]}

# ---------------------------------------------------------------- indicadores de amenaza
HAZ = {}
specs = [("8_IndiceRiesgo", "Cambio_IndiceRiesgo_R90_2040.tif", "Lluvia y deslizamientos, índice R90\ncambio 2040–2050 menos 1990–2000", "RdBu_r", "dif"),
         ("8_IndiceRiesgo", "Cambio_IndiceRiesgo_R95_2040.tif", "Lluvia y deslizamientos, índice R95\ncambio 2040–2050 menos 1990–2000", "RdBu_r", "dif"),
         ("6_RTI", "7d_Cambio_RTI90_2040.tif", "Lluvia y avenidas torrenciales, RTI90 de 7 días\ncociente 2040–2050 / 1990–2000", "RdBu_r", "ratio"),
         ("7_Probabilidad_excedencia", "Probabilidad_Pmayor_75mm_2040.tif", "Probabilidad de que la lluvia de 3 días\nsupere 75 mm, 2040–2050", "Blues", "abs")]
fig = newfig(6.2, 6.0); axes = gridaxes(fig, 2, 2)
for ax, (sub, f, title, cmap, kind) in zip(axes.ravel(), specs):
    a, trh = load9377(p(sub, f)); a, ins = fill_district_gaps(a, trh); v = a[ins]
    HAZ[f] = dict(media=float(np.nanmean(v)), min=float(np.nanmin(v)), max=float(np.nanmax(v)), frac_aumenta=(float(((v > 1) if kind == "ratio" else (v > 0)).mean() * 100) if kind != "abs" else None), celdas=int(ins.sum()))
    if kind == "dif":
        lim = max(abs(np.nanpercentile(v, 2)), abs(np.nanpercentile(v, 98))); im = district_panel(ax, a, trh, cmap, None, None, title, norm=TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim))
    elif kind == "ratio":
        lim = max(abs(np.nanpercentile(v, 2) - 1), abs(np.nanpercentile(v, 98) - 1)); im = district_panel(ax, a, trh, cmap, None, None, title, norm=TwoSlopeNorm(vmin=1 - lim, vcenter=1, vmax=1 + lim))
    else: im = district_panel(ax, a, trh, cmap, 0, float(np.nanmax(v)), title)
    hcbar(fig, ax, im, "", shrink=0.8, pad=0.02, fraction=0.045)
north_scale(axes[0][1], 5)
fig.suptitle("Indicadores de lluvia detonante de amenazas, Distrito de Medellín (RCP 4.5, malla de 1 km)\nrojo: aumenta; azul: disminuye (salvo el panel de probabilidad)", fontsize=8.8)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019), ráster 8_IndiceRiesgo, 6_RTI y 7_Probabilidad_excedencia.\nNo son mapas de zonificación de amenaza.", fontsize=6, color="#444444")
save(fig, "S7_indicadores_amenaza.png"); OUT["amenaza"] = HAZ

# ---------------------------------------------------------------- incendios
FIRE = {}
fig = newfig(6.2, 6.0); axes = gridaxes(fig, 2, 2)
for r, (mes, m3) in enumerate((("Ene", "enero"), ("Jul", "julio"))):
    base, trf = load9377(p("5_Susc_Incendios", f"S_Incendio_1990_{mes}.tif"), resolution=60); base, ins = fill_district_gaps(base, trf, n=1)
    ch, _ = load9377(p("5_Susc_Incendios", f"S_Incendio_cambio_2040_{mes}.tif"), resolution=60); ch, _ = fill_district_gaps(ch, trf, n=1)
    vb, vc = base[ins], ch[ins]
    FIRE[mes] = dict(base_media=float(np.nanmean(vb)), cambio_media=float(np.nanmean(vc)), cambio_p95=float(np.nanpercentile(vc, 95)), frac_aumenta=float((vc > 0.02).mean() * 100), frac_disminuye=float((vc < -0.02).mean() * 100), max_base=float(np.nanmax(vb)))
    im0 = district_panel(axes[r][0], base, trf, "YlOrRd", 0, float(np.nanpercentile(vb, 99.5)), f"Susceptibilidad en {m3}, 1990–2000\nmedia del Distrito {es(FIRE[mes]['base_media'], 2)}")
    lim = max(abs(np.nanpercentile(vc, 1)), abs(np.nanpercentile(vc, 99)), 0.05)
    im1 = district_panel(axes[r][1], ch, trf, "RdBu_r", None, None, f"Cambio en {m3}, 2040–2050 menos 1990–2000\naumenta en {FIRE[mes]['frac_aumenta']:.0f} % del área", norm=TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim))
    hcbar(fig, axes[r][0], im0, "", shrink=0.8, pad=0.02, fraction=0.045); hcbar(fig, axes[r][1], im1, "", shrink=0.8, pad=0.02, fraction=0.045)
north_scale(axes[0][1], 5)
fig.suptitle("Susceptibilidad a incendios de cobertura vegetal, Distrito de Medellín\nRCP 4.5, modelo bayesiano del SIATA, celdas de 60 m (índice de 0 a 1)", fontsize=8.8)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019), ráster 5_Susc_Incendios. Las coberturas y la cercanía urbana se mantienen fijas.", fontsize=6, color="#444444")
save(fig, "S8_incendios.png"); OUT["incendios"] = FIRE

json.dump(OUT, open(os.path.join(P2, "siata_stats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: OUT[k] for k in ("dT_urbano", "T1990_urbano", "urbano_celdas", "dP_2030", "dP_2040")}, ensure_ascii=False))
print("OK")
