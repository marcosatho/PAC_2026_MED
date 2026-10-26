# -*- coding: utf-8 -*-
"""Flujograma de la información, figura de escalas espaciales y composiciones de capturas de pantalla de los PDF de los estudios."""
import sys
sys.argv = [sys.argv[0]]
from common import *
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import textwrap, pymupdf
from PIL import Image

# =============================================================== F1: flujograma
fig = plt.figure(figsize=(7.4, 7.2)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 96); ax.axis("off")
def box(x, y, w, h, title, body="", fc="#ffffff", ec="#374151", tfs=7.0, bfs=5.9, wrap=44, tcol="#111827", lw=0.9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.8", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h - 0.9, title, ha="center", va="top", fontsize=tfs, fontweight="bold", color=tcol)
    if body:
        lines = []
        for para in body.split("\n"): lines += textwrap.wrap(para, wrap) or [""]
        ax.text(x + 1.3, y + h - 3.8, "\n".join(lines), ha="left", va="top", fontsize=bfs, color="#1f2937", linespacing=1.27)
def arrow(x0, y0, x1, y1, color="#6b7280", lw=1.1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, color=color, lw=lw, shrinkA=0, shrinkB=0))
def band(y, h, text, fc):
    ax.add_patch(Rectangle((0.4, y), 99.2, h, fc=fc, ec="none", alpha=0.6, zorder=0)); ax.text(1.4, y + h - 0.9, text, fontsize=6.2, color="#374151", va="top", fontweight="bold")

band(78, 17.5, "1. ACUERDOS GLOBALES (IPCC)", "#e0f2fe")
band(44, 33, "2. LOS TRES ESTUDIOS", "#fef3c7")
band(24, 19, "3. LO QUE ENTREGA CADA UNO", "#dcfce7")
band(0.5, 23, "4. USO EN EL PAC", "#f3e8ff")

box(2, 79.5, 29.5, 11.5, "Emisiones y sociedad futuras", "AR5 (2013): trayectorias de concentración RCP 2.6, 4.5, 6.0 y 8.5.\nAR6 (2021): trayectorias socioeconómicas compartidas (SSP).", wrap=42)
box(35.2, 79.5, 29.5, 11.5, "Modelos climáticos globales", "Simulan atmósfera, océano y superficie en celdas de 100 a 250 km. Se agrupan en CMIP5 (RCP) y CMIP6 (SSP).", wrap=42)
box(68.5, 79.5, 29.5, 11.5, "Escenarios que usan los estudios", "SIATA: RCP 4.5 (CMIP5). UdeA e IDEAM: SSP1-2.6, 2-4.5, 3-7.0 y 5-8.5 (CMIP6).", wrap=42)
arrow(31.5, 85, 35.2, 85); arrow(64.7, 85, 68.5, 85)

cols = [(2, "#ede9fe", "SIATA (2019)", "Convenio 4600082037 de 2019, para el DAGRD y el AMVA.\nEscenario: RCP 4.5.\nModelo: CCSM4 (CMIP5), celdas de 104 × 138 km.\nReducción de escala: dinámica con el modelo regional WRF, tres dominios anidados de 12, 3 y 1 km.\nReferencia: radar de Santa Elena y estaciones.\nPeriodos: 1990–2000, 2030–2040 y 2040–2050; un año climatológico por década."),
        (35.2, "#fee2e2", "Universidad de Antioquia (2026)", "Contrato 4600105139 de 2025, para la Secretaría de Medio Ambiente.\nEscenarios: SSP1-2.6, 2-4.5, 3-7.0 y 5-8.5, y HighresFuture (parecido a SSP5-8.5).\nModelos: 19 del conjunto NEX-GDDP-CMIP6 (NASA) y 7 de alta resolución (HighResMIP).\nReducción de escala: estadística, celdas de 0,25° (~28 km).\nReferencia: CHIRTS y CHIRPS v2.\nPeriodos: 2021–2050 y 2071–2100, frente a 1981–2010."),
        (68.5, "#dcfce7", "IDEAM (2024)", "Cuarta Comunicación Nacional de Cambio Climático.\nEscenarios: SSP1-2.6, 2-4.5, 3-7.0 y 5-8.5.\nModelos: 25 del conjunto NEX-GDDP-CMIP6, ponderados por su correlación con lo observado.\nReducción de escala: estadística (Delta Q-Q) sobre el «cubo de datos» de 10 × 10 km.\nReferencia: 1753 estaciones, CHIRPS, MERRA, CHIRTS y ERA5.\nPeriodos: 2021–2040 a 2081–2100, frente a 1981–2010.")]
for x, fc, t, b in cols: box(x, 45.5, 29.5, 28.5, t, b, fc=fc, wrap=43)
arrow(29, 79.5, 29, 74.3); arrow(50, 79.5, 50, 74.3); arrow(83.2, 79.5, 83.2, 74.3)

ents = [(2, "#ede9fe", "Mapas de 1 km del Distrito", "Temperatura y lluvia medias, lluvia horaria extrema, días con más de 29 y 30 °C, evapotranspiración, índices de lluvia detonante y susceptibilidad a incendios."),
        (35.2, "#fee2e2", "Índices de extremos (ETCCDI)", "Días y noches cálidos, rachas de calor, lluvia máxima en un día, rachas secas y húmedas, sequía (SPI) y eventos compuestos. Cuatro celdas cubren Medellín."),
        (68.5, "#dcfce7", "Siete variables medias", "Precipitación, temperatura media, máxima y mínima, humedad relativa, viento y radiación, por año, trimestre y mes. Píxeles de 10 km.")]
for x, fc, t, b in ents: box(x, 25.5, 29.5, 14, t, b, fc=fc, wrap=44)
for x in (29, 50, 83.2): arrow(x, 45.5, x, 39.8)

box(2, 10.5, 29.5, 10, "Amenazas climáticas", "Calor extremo, lluvias intensas (movimientos en masa, avenidas torrenciales, inundaciones), sequía e incendios.", wrap=44)
box(35.2, 10.5, 29.5, 10, "Riesgo climático del Distrito", "Amenaza, exposición y vulnerabilidad por comuna y corregimiento (P1).", wrap=44)
box(68.5, 10.5, 29.5, 10, "Trayectorias del PAC", "Escenarios que sustentan medidas, metas y brechas (P2).", wrap=44)
arrow(31.5, 15.5, 35.2, 15.5); arrow(64.7, 15.5, 68.5, 15.5)
arrow(29, 25.5, 29, 20.8, color="#9ca3af", lw=0.8)
ax.text(50, 7.0, "Los tres estudios no son comparables celda a celda: cambian el escenario, los modelos, la escala y el periodo de referencia.", ha="center", fontsize=6.2, style="italic", color="#4b5563")
ax.text(50, 3.0, "Fuente: elaboración propia a partir de SIATA (2019), Universidad de Antioquia (2026a) e Ideam (2024).", ha="center", fontsize=5.8, color="#444444")
fig.savefig(os.path.join(FIG, "F1_flujograma.png"), dpi=250, facecolor="white"); plt.close(fig); print("F1 ok")

# =============================================================== F2: escalas espaciales sobre el Distrito
fig, ax = plt.subplots(figsize=(7.2, 5.3), constrained_layout=True)
ux0, uy0, uc = 4500847, 2555564, 27634.408
xlo, xhi, ylo, yhi = 4690000, 4760000, 2212000, 2282000
for k in range(0, 16):
    for m in range(0, 17):
        x0 = ux0 + k * uc; y0 = uy0 - (m + 1) * uc
        if x0 + uc >= xlo and x0 <= xhi and y0 + uc >= ylo and y0 <= yhi:
            ax.add_patch(Rectangle((x0, y0), uc, uc, fc="none", ec="#b91c1c", lw=1.6, zorder=3))
a, tr = load9377(os.path.join(SIATA, "2_Temper_media", "Temper_1990-01.tif")); ext = extent(a, tr)
xs = np.arange(ext[0], ext[1] + 1, abs(tr.a)); ys = np.arange(ext[3], ext[2] - 1, -abs(tr.e))
for x in xs:
    if xlo <= x <= xhi: ax.plot([x, x], [max(ylo, ext[2]), min(yhi, ext[3])], color="#a78bfa", lw=0.35, zorder=2)
for y in ys:
    if ylo <= y <= yhi: ax.plot([max(xlo, ext[0]), min(xhi, ext[1])], [y, y], color="#a78bfa", lw=0.35, zorder=2)
ax.add_patch(Rectangle((xlo + 3000, yhi - 13000), 10000, 10000, fc="#bbf7d0", ec="#15803d", lw=1.5, zorder=3, alpha=0.85)); ax.text(xlo + 8000, yhi - 8000, "10 km", ha="center", va="center", fontsize=7, color="#14532d", fontweight="bold")
ax.text(xlo + 14500, yhi - 8000, "píxel del IDEAM (2024):\ntamaño de referencia", fontsize=6.4, va="center", color="#14532d")
for pg in (BOUND.geoms if hasattr(BOUND, "geoms") else [BOUND]):
    ax.fill(*pg.exterior.xy, fc="#fde68a", ec="#111827", lw=1.3, alpha=0.9, zorder=4)
ax.set_xlim(xlo, xhi); ax.set_ylim(ylo, yhi); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
area = BOUND.area / 1e6
ax.text(xlo + 1500, ylo + 2500, f"Distrito de Medellín: {area:.0f} km²\nSIATA (2019): ~1 km, unas 450 celdas (violeta)\nIDEAM (2024): 10 km, unos {area/100:.0f} píxeles de 100 km²\nUdeA (2026): 0,25° (~28 km), 4 celdas (rojo)", fontsize=6.6, va="bottom", color="#111827", bbox=dict(fc="white", ec="#9ca3af", boxstyle="round,pad=0.35", alpha=0.95), zorder=10)
ax.annotate("N", xy=(0.95, 0.97), xytext=(0.95, 0.88), xycoords="axes fraction", ha="center", fontsize=8, arrowprops={"arrowstyle": "->", "lw": 0.9})
ax.plot([xhi - 15000, xhi - 5000], [ylo + 2500] * 2, color="black", lw=2); ax.text(xhi - 10000, ylo + 3300, "10 km", ha="center", fontsize=6.4)
ax.set_title("Escala de cada estudio sobre el Distrito de Medellín", fontsize=9)
fig.supxlabel("Fuente: elaboración propia a partir de SIATA (2019), Universidad de Antioquia (2026a, 2026b, p. 204) e Ideam (2024, pp. 22 y 31).\nLa malla del IDEAM no está publicada en el documento; se muestra solo su tamaño.", fontsize=5.7, color="#444444")
save(fig, "F2_escalas.png")

# =============================================================== U4: capturas de los diagramas de cajas de la UdeA para el Valle de Aburrá
imgs = [("udea_box_p111_1.png", "Fig. 59. Días cálidos (TX95p)"), ("udea_box_p112_1.png", "Fig. 60. Noches cálidas (TN95p)"), ("udea_box_p112_2.png", "Fig. 61. Rachas de calor (WSDI)"),
        ("udea_box_p113_1.png", "Fig. 62. Intensidad de sequía (SPI)"), ("udea_box_p114_1.png", "Fig. 63. Lluvia máxima en un día (RX1day)"), ("udea_box_p114_2.png", "Fig. 64. Lluvia de días muy lluviosos (R95p)")]
fig, axes = plt.subplots(2, 3, figsize=(7.4, 4.6), constrained_layout=True)
for ax, (fn, tit) in zip(axes.ravel(), imgs):
    ax.imshow(Image.open(os.path.join(P2, "img", fn))); ax.axis("off"); ax.set_title(tit, fontsize=6.6, pad=2)
fig.suptitle("Cambios proyectados 2021–2050 en el dominio del Valle de Aburrá por escenario (capturas del estudio de la UdeA)", fontsize=8)
fig.supxlabel("Fuente: capturas de Universidad de Antioquia (2026a, pp. 111-114), figuras 59 a 64. Cada caja resume las celdas del dominio\n(5,5–7° N; 76–75° O) para SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5 y HighresFuture.", fontsize=5.6, color="#444444")
save(fig, "U4_cajas_Valle_de_Aburra.png")

# =============================================================== U5: captura de la figura 21 (WSDI, corto plazo)
doc = pymupdf.open(r"C:\Users\marco\Downloads\Bibliografia_P1_PDF\UdeA_2026a_Escenarios_cambio_climatico_CCMED.pdf")
pg = doc[68]; rect = pymupdf.Rect(70, 112, 560, 670); pix = pg.get_pixmap(dpi=170, clip=rect); pix.save(os.path.join(FIG, "U5_captura_fig21_WSDI.png")); print("U5", pix.width, pix.height)
print("OK")
