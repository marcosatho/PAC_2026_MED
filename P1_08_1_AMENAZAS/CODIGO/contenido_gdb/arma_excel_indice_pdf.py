# -*- coding: utf-8 -*-
"""Arma el Excel de resumen del contenido de la geodatabase del POT 2026, la lámina índice (16:9) y el PDF con todas las láminas.
Corre después de mapas_contenido_gdb_pot2026.py. Solo lee la tabla de trazabilidad y los PNG de los mapas."""
import os, re, sys, json, collections
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAPAS_OUT", os.path.join(AQUI, "salida"))
TRAZ = os.path.join(AQUI, "Trazabilidad_capas_POT2026_vs_2014_v2.xlsx")
XLSX = os.path.join(OUT, "Contenido_geodatabase_POT2026_resumen.xlsx")
src = open(os.path.join(AQUI, "mapas_contenido_gdb_pot2026.py"), encoding="utf-8").read()

# ---------------------------------------------------------------- datos de la tabla de trazabilidad
rows = list(openpyxl.load_workbook(TRAZ, read_only=True)["Capas"].iter_rows(values_only=True))
H, filas = rows[0], rows[1:]
capas = {r[1]: r for r in filas}

# ---------------------------------------------------------------- mapas: título, capas que dibuja
partes = re.split(r'@mapa\("(\d\d)", "([^"]+)"\)', src)
MAPAS = {}
for i in range(1, len(partes), 3):
    num, nombre, cuerpo = partes[i], partes[i + 1], partes[i + 2]
    t = re.search(r'lienzo\(\d, "([^"]+)", "([^"]+)"', cuerpo)
    cs = set(re.findall(r'G\("([^"]+)"\)', cuerpo))
    MAPAS[num] = dict(nombre=nombre, titulo=t.group(1), grupo=t.group(2).replace("Grupo ", "").replace(" de la geodatabase", ""), capas=cs)
MAPAS["10"]["capas"] |= {"gur_ar_amenaza_inundaciones", "gur_ar_amenaza_avtorrenciales", "gur_ar_amenaza_mov_masa"}
MAPAS["11"]["capas"] |= {"gur_ar_riesgo_inundaciones", "gur_ar_riesgo_avtorrenciales", "gur_ar_riesgo_mov_masa"}
capa_mapa = collections.defaultdict(list)
for num, m in MAPAS.items():
    for c in m["capas"]:
        capa_mapa[c].append(num)
sin = [c for c in capas if c not in capa_mapa]
print("capas sin mapa:", sin)

# ---------------------------------------------------------------- clases de origen
def clase(t):
    t = str(t)
    if t.startswith("2014 (Acuerdo") or t.startswith("2014–2016"):
        return "Acuerdo 48 de 2014"
    if t.startswith("Mixta") or t.startswith("Ajuste"):
        return "Acuerdo 48 con ajustes o elementos nuevos"
    if t.startswith("Inventario"):
        return "Inventario 2024–2026"
    if t.startswith("2026") or t.startswith("2025–2026"):
        return "Revisión 2025–2026"
    return "Instrumentos complementarios"
CLASES = ["Acuerdo 48 de 2014", "Acuerdo 48 con ajustes o elementos nuevos", "Inventario 2024–2026", "Revisión 2025–2026", "Instrumentos complementarios"]
COL = {"Acuerdo 48 de 2014": "#4c78a8", "Acuerdo 48 con ajustes o elementos nuevos": "#9ecae1", "Inventario 2024–2026": "#59a14f", "Revisión 2025–2026": "#e15759", "Instrumentos complementarios": "#b07aa1"}

GRUPOS = collections.OrderedDict([
    ("a_DivisionAdministrativa", ("División administrativa", "Comunas, corregimientos, barrios y veredas.")),
    ("b_NormadelSuelo", ("Norma del suelo", "Clasificación del suelo, estructura ecológica, suelo de protección, áreas de actividad, centralidades, tratamientos urbanísticos y patrimonio cultural.")),
    ("c_AmenazayRiesgo", ("Amenaza y riesgo", "Amenaza y riesgo por inundación, avenidas torrenciales y movimientos en masa, y áreas con condición de amenaza.")),
    ("d_SistemasGenerales", ("Sistemas generales", "Vías y transporte, espacio público, equipamientos y servicios públicos: acueducto, alcantarillado, energía, gas, alumbrado, telecomunicaciones y aseo.")),
    ("e_PlanificacionComplementaria", ("Planificación complementaria", "Instrumentos de planificación de segundo y tercer nivel (macroproyectos, planes parciales, planes maestros, unidades rurales).")),
    ("f_SubsistemaFinanciacion", ("Subsistema de financiación", "Zonas generadoras y receptoras de derechos adicionales y zonas de desarrollo orientado al transporte.")),
])
est = collections.OrderedDict()
for g in GRUPOS:
    rs = [r for r in filas if r[0] == g]
    est[g] = dict(n=len(rs), elem=sum(int(r[3]) for r in rs), cl=collections.Counter(clase(r[4]) for r in rs),
                  mapas=sorted({m for r in rs for m in capa_mapa[r[1]]}))
for g, d in est.items():
    print(g, d["n"], d["elem"], dict(d["cl"]), d["mapas"])

# ---------------------------------------------------------------- Excel
wb = openpyxl.Workbook()
AZ, GR, RJ = PatternFill("solid", fgColor="1F4E78"), PatternFill("solid", fgColor="595959"), PatternFill("solid", fgColor="7F1D1D")
TEAL = PatternFill("solid", fgColor="0F766E")


def hoja(nombre, cab, datos, anchos, fills, primera=False):
    ws = wb.active if primera else wb.create_sheet()
    ws.title = nombre
    ws.append(cab)
    for c, f in zip(ws[1], fills):
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = f
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for d in datos:
        ws.append(list(d))
    for i, w in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 36
    return ws


tot_c, tot_e = sum(d["n"] for d in est.values()), sum(d["elem"] for d in est.values())
res = []
for g, (tema, que) in GRUPOS.items():
    d = est[g]
    res.append((g, tema, que, d["n"], d["elem"], "; ".join(f"{k}: {v}" for k, v in sorted(d["cl"].items(), key=lambda kv: -kv[1])), ", ".join(d["mapas"])))
res.append(("Total", "", "", tot_c, tot_e, "; ".join(f"{k}: {sum(d['cl'][k] for d in est.values())}" for k in CLASES if sum(d['cl'][k] for d in est.values())), "01 a 23"))
hoja("Resumen por grupo", ["[Datos de la gdb] Grupo (feature dataset)", "[Cálculo PAC] Tema", "[Cálculo PAC] Qué contiene", "[Datos de la gdb] Capas",
                           "[Datos de la gdb] Elementos", "[Cálculo PAC] Origen propuesto (n.º de capas)", "[Cálculo PAC] Mapas"],
     res, [30, 26, 70, 9, 12, 70, 14], [GR, RJ, RJ, GR, GR, RJ, RJ], primera=True)

cap = []
for r in filas:
    ms = capa_mapa[r[1]]
    cap.append((r[0], r[1], r[26], r[18], r[2], int(r[3]), clase(r[4]), str(r[4]), ", ".join(ms), ", ".join(MAPAS[m]["nombre"] + ".png" for m in ms)))
hoja("Capas (82)", ["[Datos de la gdb] Grupo", "[Datos de la gdb] Capa", "[Metadata XML de la gdb] Título (texto del DAP)", "[Diccionario DAP] Descripción (texto literal del DAP)",
                    "[Datos de la gdb] Geometría", "[Datos de la gdb] Elementos", "[Cálculo PAC] Origen propuesto (resumido)", "[Cálculo PAC] Origen propuesto (detalle de la tabla de trazabilidad)",
                    "[Cálculo PAC] Mapa n.º", "[Cálculo PAC] Archivo del mapa"],
     cap, [26, 34, 34, 90, 14, 11, 32, 40, 9, 46], [GR, GR, TEAL, AZ, GR, GR, RJ, RJ, RJ, RJ])

mp = [(n, m["nombre"] + ".png", m["titulo"], m["grupo"], len(m["capas"]), ", ".join(sorted(m["capas"]))) for n, m in sorted(MAPAS.items())]
hoja("Mapas", ["N.º", "Archivo", "Título", "Grupo de la gdb", "Capas", "Capas que dibuja"], mp, [6, 44, 70, 28, 8, 120], [RJ] * 6)

leeme = [
    ("Qué es", "Resumen del contenido de la geodatabase de la propuesta de revisión del POT 2026 que envió el Departamento Administrativo de Planeación (DAP): 82 capas de datos en 6 grupos (más 328 capas de errores topológicos, que no se resumen aquí)."),
    ("Advertencia del DAP", "El DAP aclara en su correo que no todas las capas integran la revisión de mediano plazo (algunas son ajustes parciales o se mantienen como en la revisión de largo plazo) y que la información aún no está protocolizada: es susceptible de cambios hasta su aprobación oficial. Toda cifra o mapa que salga de esta geodatabase debe declararse como «propuesta de revisión del POT 2026, aún no protocolizada»."),
    ("Qué es del DAP y qué es nuestro", "Los encabezados indican el origen: [Diccionario DAP] y [Metadata XML de la gdb] son texto literal del DAP, sin resumir; [Datos de la gdb] se lee de las capas; [Cálculo PAC] es lo único que escribimos o calculamos nosotros (tema, qué contiene por grupo, origen propuesto y número de mapa)."),
    ("Origen propuesto", "El DAP no declara qué capa es de 2014 y cuál de 2026. La columna es una inferencia nuestra a partir de las fechas de las capas, de su metadata y del diccionario (ver la tabla Trazabilidad_capas_POT2026_vs_2014_v2.xlsx, con las evidencias de cada capa). La fecha del diccionario es la de documentación del campo, no la del dato."),
    ("Mapas", "Los 23 mapas (carpeta de imágenes y PDF) siguen el orden de los grupos de la geodatabase y el estilo de los mapas del Producto 1; los ejes están en km (MAGNA-SIRGAS / Origen Nacional). Los datos pesados de la geodatabase quedan en Drive."),
    ("Fecha", "Análisis del 2026-10-20 (geodatabase recibida del DAP; análisis de trazabilidad del 2026-10-18). Preparado por Marcos Arango Tamayo (ITM) con apoyo de Claude."),
]
ws = wb.create_sheet("Léame")
for k, v in leeme:
    ws.append([k, v])
ws.column_dimensions["A"].width = 30
ws.column_dimensions["B"].width = 140
for row in ws.iter_rows():
    row[0].font = Font(bold=True)
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")
wb.move_sheet("Léame", offset=-3)
# detalle del origen propuesto con las categorías originales de la tabla de trazabilidad (suman 82)
ws_res = wb["Resumen por grupo"]
ws_res.append([])
ws_res.append(["Origen propuesto (detalle de la tabla de trazabilidad del 18-oct)", "N.º de capas"])
for c in ws_res[ws_res.max_row]:
    c.font = Font(bold=True)
det = collections.Counter(str(r[4]).split(" (")[0].split(":")[0] if str(r[4]).startswith(("Mixta", "2014 (", "2026 (")) else str(r[4]) for r in filas)
orden = collections.Counter()
for r in filas:
    t = str(r[4])
    k = ("2014 (Acuerdo 48)" if t.startswith("2014 (") else "Mixta: 2014 + elementos sin fecha o con ajustes" if t.startswith("Mixta") else "2026 (revisión)" if t.startswith("2026 (")
         else "2025–2026 (revisión: norma propuesta o ajustada)" if t.startswith("2025–2026") else "Inventario 2024–2026 (redes, equipamientos y patrimonio)" if t.startswith("Inventario")
         else "Instrumentos complementarios" if t.startswith("Instrumentos") else "Ajuste de la norma de 2014 en la revisión (metadata 2024)" if t.startswith("Ajuste")
         else "2014–2016 (probable Acuerdo 48; sin fecha en la capa ni en el diccionario)")
    orden[k] += 1
for k, v in sorted(orden.items(), key=lambda kv: -kv[1]):
    ws_res.append([k, v])
ws_res.append(["Total", sum(orden.values())])
wb.save(XLSX)
print("xlsx ok:", XLSX)

# ---------------------------------------------------------------- lámina índice 16:9
fig = plt.figure(figsize=(16, 9))
fig.text(0.5, 0.992, "Propuesta de revisión del POT 2026, información aún no protocolizada", ha="center", va="top", fontsize=10.5, style="italic", color="#7f1d1d")
fig.text(0.045, 0.955, "Contenido de la geodatabase del POT 2026", ha="left", va="top", fontsize=24, weight="bold", color="#111827")
fig.text(0.045, 0.9, f"{tot_c} capas de datos en 6 grupos y {tot_e:,} elementos".replace(",", ".") + " · enviada por el Departamento Administrativo de Planeación (DAP)", ha="left", va="top", fontsize=12.5, color="#4b5563")
ax = fig.add_axes([0.045, 0.2, 0.93, 0.62])
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.text(0.0, 1.0, "GRUPO DE LA GEODATABASE", fontsize=9, color="#6b7280", weight="bold", va="top")
ax.text(0.40, 1.0, "CAPAS · ELEMENTOS", fontsize=9, color="#6b7280", weight="bold", va="top")
ax.text(0.545, 1.0, "ORIGEN PROPUESTO (n.º de capas)", fontsize=9, color="#6b7280", weight="bold", va="top")
ax.text(0.93, 1.0, "MAPAS", fontsize=9, color="#6b7280", weight="bold", va="top", ha="center")
ax.plot([0, 1], [0.965, 0.965], color="#d1d5db", lw=0.8)
alto = 0.155
y = 0.94
maxn = max(d["n"] for d in est.values())
for g, (tema, que) in GRUPOS.items():
    d = est[g]
    ax.text(0.0, y, tema, fontsize=14, weight="bold", va="top", color="#111827")
    import textwrap
    ax.text(0.0, y - 0.04, "\n".join(textwrap.wrap(que, 62)), fontsize=9.3, va="top", color="#374151", linespacing=1.25)
    ax.text(0.40, y - 0.004, f"{d['n']} capas", fontsize=12, va="top", color="#111827", weight="bold")
    ax.text(0.40, y - 0.045, f"{d['elem']:,} elementos".replace(",", "."), fontsize=10, va="top", color="#4b5563")
    x = 0.545
    ancho = 0.34
    for k in CLASES:
        n = d["cl"].get(k, 0)
        if n:
            w = ancho * n / d["n"]
            ax.add_patch(Rectangle((x, y - 0.045), w, 0.04, facecolor=COL[k], edgecolor="white", linewidth=1))
            if w > 0.02:
                ax.text(x + w / 2, y - 0.025, str(n), ha="center", va="center", fontsize=9, color="white", weight="bold")
            x += w
    ax.text(0.93, y - 0.004, ", ".join(d["mapas"]) if len(d["mapas"]) < 5 else f"{d['mapas'][0]} a {d['mapas'][-1]}", fontsize=11, va="top", ha="center", color="#111827", weight="bold")
    ax.plot([0, 1], [y - alto + 0.02, y - alto + 0.02], color="#e5e7eb", lw=0.6)
    y -= alto
# leyenda de origen
lx = 0.045
for k in CLASES:
    fig.patches.append(Rectangle((lx, 0.135), 0.012, 0.022, transform=fig.transFigure, facecolor=COL[k], edgecolor="none"))
    fig.text(lx + 0.016, 0.1455, k, fontsize=9, va="center", color="#1f2937")
    lx += 0.016 + 0.0059 * len(k) + 0.03
fig.text(0.045, 0.085, "El origen propuesto es una inferencia nuestra a partir de las fechas de las capas, su metadata y el diccionario del DAP; el DAP no lo declara. El ancho de cada barra es la proporción de capas del grupo. "
         "Las 7 capas de amenaza y riesgo tienen origen propuesto en 2026;\nla mayoría de las de servicios públicos (redes, antenas, luminarias), en el inventario 2024–2026; la división administrativa, la clasificación del suelo y la estructura ecológica, en el Acuerdo 48 de 2014.",
         fontsize=9.3, color="#374151", va="top", linespacing=1.4)
fig.text(0.5, 0.012, "Fuente: elaboración propia con la geodatabase de la propuesta de revisión del POT 2026 (DAP, 2026; aún no protocolizada).", ha="center", va="bottom", fontsize=7.8, color="#444444")
idx = os.path.join(OUT, "00_indice_contenido_geodatabase.png")
fig.savefig(idx, dpi=150, facecolor="white")
plt.close(fig)
print("indice ok")

# ---------------------------------------------------------------- PDF con todas las láminas
paginas = [idx] + [os.path.join(OUT, m["nombre"] + ".png") for _, m in sorted(MAPAS.items())]
imgs = [Image.open(p).convert("RGB") for p in paginas if os.path.exists(p)]
faltan = [p for p in paginas if not os.path.exists(p)]
pdf = os.path.join(OUT, "Mapas_contenido_geodatabase_POT2026.pdf")
imgs[0].save(pdf, "PDF", save_all=True, append_images=imgs[1:], resolution=150)
print("pdf ok:", len(imgs), "páginas; faltan:", faltan)
