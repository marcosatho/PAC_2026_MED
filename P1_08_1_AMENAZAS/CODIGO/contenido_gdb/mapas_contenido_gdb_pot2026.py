# -*- coding: utf-8 -*-
"""Mapas de panorama del contenido de la geodatabase del POT 2026 (DAP): una lámina 16:9 por tema, en el orden de los
grupos de la geodatabase (a. división administrativa, b. norma del suelo, c. amenaza y riesgo, d. sistemas generales,
e. planificación complementaria, f. financiación). Mismo estilo que los mapas del P1 (fondo gris claro, límite municipal en rojo,
comunas y corregimientos, ejes en km, regla de 5 km alineada con las marcas, nota de «no protocolizada»).

Entradas: pickles de las capas (cache_capas.py lee la geodatabase recibida del DAP; no se modifica) y la tabla de trazabilidad
Trazabilidad_capas_POT2026_vs_2014_v2.xlsx. Uso: python mapas_contenido_gdb_pot2026.py   (env MAPAS_ONLY=01,05 para rehacer algunos)"""
import os, sys, json, textwrap, warnings, functools
import numpy as np
import pandas as pd
import geopandas as gpd
import openpyxl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator

warnings.filterwarnings("ignore")
AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("MAPAS_CACHE", os.path.join(AQUI, "cache"))
OUT = os.environ.get("MAPAS_OUT", os.path.join(AQUI, "salida"))
TRAZ = os.environ.get("MAPAS_TRAZ", os.path.join(AQUI, "Trazabilidad_capas_POT2026_vs_2014_v2.xlsx"))
LIM = os.environ.get("MAPAS_LIM", (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA"
                                   r"\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE"
                                   r"\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg"))
ONLY = [s for s in os.environ.get("MAPAS_ONLY", "").split(",") if s]
os.makedirs(OUT, exist_ok=True)

STATS = json.load(open(os.environ.get("MAPAS_STATS", 'G:\\Mi unidad\\2.Consultoria\\01_PAC_MEDELLIN_2026\\2.Ejecución\\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\\P1_Caracterizacion_Socioeconomica_Ambiental\\02_DOCUMENTOS_EN_ELABORACION\\08_1_AMENAZAS\\05_POT2026_AMENAZAS_OFICIAL_V2\\03_FIGURAS\\estadisticas_mapas_v2.json'), encoding="utf-8"))
NOTA = "Propuesta de revisión del POT 2026, información aún no protocolizada"
FUENTE = ("Fuente: elaboración propia con la geodatabase de la propuesta de revisión del POT 2026 (Departamento Administrativo de Planeación [DAP], 2026; "
          "aún no protocolizada). Los ejes están en km (MAGNA-SIRGAS / Origen Nacional). El «origen propuesto» de cada capa (2014, 2026, inventario…) es una inferencia nuestra "
          "a partir de las fechas de la geodatabase; el DAP no lo declara.")
DIVISIONS = gpd.read_file(LIM, layer="comunas_corregimientos")
BOUNDARY = gpd.read_file(LIM, layer="limite_medellin")
BPOLY = BOUNDARY.geometry.iloc[0]
import shapely
shapely.prepare(BPOLY)   # acelera intersects() con capas de cientos de miles de tramos
BOUNDS = BOUNDARY.total_bounds
DISTRICT_HA = BPOLY.area / 1e4
DIV_B = DIVISIONS.boundary
BND_B = BOUNDARY.boundary
NAMES = {"50": "San Sebastián\nde Palmitas", "60": "San Cristóbal", "70": "Altavista", "80": "San Antonio\nde Prado", "90": "Santa Elena"}

# ---------------------------------------------------------------- trazabilidad (columna de la tabla del 18-oct)
TAG = {"2014 (Acuerdo 48)": "2014", "Inventario 2024–2026": "inventario 2024–26", "Mixta": "mixta", "2026 (revisión)": "2026",
       "2025–2026": "norma propuesta 2025–26", "Instrumentos": "fecha propia", "Ajuste de la norma": "ajuste de la norma 2014", "2014–2016": "2014–16 (probable)"}
TRAZA = {}
_ws = openpyxl.load_workbook(TRAZ, read_only=True)["Capas"]
for _i, _r in enumerate(_ws.iter_rows(values_only=True)):
    if _i == 0:
        continue
    t = str(_r[4])
    TRAZA[_r[1]] = next((v for k, v in TAG.items() if t.startswith(k)), t)
ELEM = {}
_ws = openpyxl.load_workbook(TRAZ, read_only=True)["Capas"]
for _i, _r in enumerate(_ws.iter_rows(values_only=True)):
    if _i:
        ELEM[_r[1]] = int(_r[3])


def fmt(x, dec=0):
    return f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")


@functools.lru_cache(maxsize=None)
def G(n):
    g = pd.read_pickle(os.path.join(CACHE, n + ".pkl"))
    return gpd.GeoDataFrame(g, geometry="geometry", crs=9377) if not isinstance(g, gpd.GeoDataFrame) or g.crs is None else g


def ha_clase(gdf, mask=None):
    """Hectáreas dentro del Distrito de las geometrías (unión: sin doble conteo entre polígonos superpuestos)."""
    g = gdf if mask is None else gdf[mask]
    if not len(g):
        return 0.0
    u = g.geometry.make_valid().union_all()
    return float(u.intersection(BPOLY).area / 1e4)


# ---------------------------------------------------------------- lienzo 16:9
def lienzo(n, titulo, grupo, ancho_texto=None, tick=None, subtitulos=None):
    ancho_texto = ancho_texto or {1: 0.40, 2: 0.30, 3: 0.215}[n]
    fig = plt.figure(figsize=(16, 9))
    x0, x1 = 0.045, 1 - ancho_texto - 0.025
    y0, top = 0.115, 0.855
    xmin, ymin, xmax, ymax = BOUNDS
    ar = (xmax - xmin + 1500) / (ymax - ymin + 1500)
    sub = 0.035 if subtitulos else 0
    if n == 1:
        rects = [(x0, y0, x1 - x0, top - y0)]
        fig._lec = None
    else:
        gap = 0.012
        w = (x1 - x0 - gap * (n - 1)) / n
        h = min((w * 16 / ar) / 9, top - sub - y0)
        yb = top - sub - h
        rects = [(x0 + i * (w + gap), yb, w, h) for i in range(n)]
        fig._lec = fig.add_axes([x0, 0.045, x1 - x0, max(yb - 0.115, 0.1)])
        fig._lec.axis("off")
        fig._lec.set_xlim(0, 1)
        fig._lec.set_ylim(0, 1)
    axes = [fig.add_axes(r) for r in rects]
    axp = fig.add_axes([1 - ancho_texto, 0.115, ancho_texto - 0.02, 0.775])
    axp.axis("off")
    axp.set_xlim(0, 1)
    axp.set_ylim(0, 1)
    fig.text(0.5, 0.992, NOTA, ha="center", va="top", fontsize=10.5, style="italic", color="#7f1d1d")
    fig.text(0.045, 0.955, titulo, ha="left", va="top", fontsize=21, weight="bold", color="#111827")
    fig.text(0.045, 0.905, grupo, ha="left", va="top", fontsize=11, color="#4b5563")
    pie = textwrap.fill(" ".join(FUENTE.split()), width=175)
    fig.text(0.5, 0.012, pie, ha="center", va="bottom", fontsize=7.8, color="#444444")
    step = tick or (5000 if n == 1 else 10000)
    for i, ax in enumerate(axes):
        DIVISIONS.plot(ax=ax, facecolor="#f3f3f3", edgecolor="none", zorder=1)
        if subtitulos:
            ax.set_title(subtitulos[i], fontsize=12.5, pad=5)
        _ax_setup(ax, step, primero=(i == 0), n=n)
    return fig, axes, axp, step


def _ax_setup(ax, step, primero, n):
    xmin, ymin, xmax, ymax = BOUNDS
    pad = 750
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)
    ax.set_aspect("equal", adjustable="box", anchor="C")
    ax.grid(color="#9ca3af", linewidth=0.45, alpha=0.35)
    ax.set_axisbelow(True)
    km = FuncFormatter(lambda v, _: f"{v / 1000:.0f}")
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(MultipleLocator(step))
        axis.set_major_formatter(km)
    fs = 9.5 if n == 1 else 8
    ax.tick_params(axis="both", labelsize=fs, rotation=0)
    if n == 1:
        ax.set_xlabel("Este (km) — MAGNA-SIRGAS / Origen Nacional", fontsize=10)
        ax.set_ylabel("Norte (km)", fontsize=10)
    elif primero:
        ax.set_ylabel("Norte (km)", fontsize=9)
    if n > 1 and not primero:
        ax.set_yticklabels([])


def cierre_ax(ax, step, norte=True, rotulos=True, n=1):
    DIV_B.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.9, zorder=40)
    BND_B.plot(ax=ax, color="#bd1f36", linewidth=1.6 if n == 1 else 1.2, zorder=41)
    xmin, ymin, xmax, ymax = BOUNDS
    pad = 750
    if norte:
        ax.annotate("N", xy=(0.955, 0.94), xytext=(0.955, 0.855), xycoords="axes fraction", ha="center", va="center", fontsize=11 if n == 1 else 9,
                    arrowprops={"arrowstyle": "->", "lw": 1.2, "color": "black"})
    start_x = round(((ax.get_xlim()[0] + ax.get_xlim()[1]) / 2 - step / 2) / step) * step
    start_y = ymin - pad + (ymax - ymin + 2 * pad) * 0.04
    ax.plot([start_x, start_x + step], [start_y, start_y], color="black", lw=2.4 if n == 1 else 2, zorder=60, path_effects=[pe.withStroke(linewidth=6, foreground="white")])
    ax.text(start_x + step / 2, start_y + (ymax - ymin) * (0.014 if n == 1 else 0.026), f"{step // 1000} km", ha="center", fontsize=9 if n == 1 else 7.5, zorder=60, bbox=dict(facecolor="white", edgecolor="none", pad=1.2, alpha=0.9))
    if rotulos:
        for _, r in DIVISIONS[DIVISIONS["codigo"].isin(NAMES)].iterrows():
            p = r.geometry.representative_point()
            ax.text(p.x, p.y, NAMES[r["codigo"]], ha="center", va="center", fontsize=6.6 if n == 1 else 5.2, color="#333333", style="italic", zorder=45,
                    path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])


# ---------------------------------------------------------------- panel de texto
class Panel:
    def __init__(self, ax, titulo_capas="Capas (elementos · origen propuesto)"):
        self.ax = ax
        self.lec = getattr(ax.figure, '_lec', None)
        if ax.get_position().width < 0.2:
            titulo_capas = "Capas"
        self.y = 1.0
        self.fila = 0.034
        self.cap(titulo_capas)

    def cap(self, txt):
        self.ax.text(0, self.y, txt.upper(), fontsize=9, color="#6b7280", weight="bold", va="top")
        self.ax.plot([0, 1], [self.y - 0.022, self.y - 0.022], color="#d1d5db", lw=0.8)
        self.y -= 0.042

    def capa(self, nombre, titulo, extra=None, det=True):
        n = ELEM.get(nombre)
        tag = TRAZA.get(nombre, "")
        det_txt = f"{fmt(n)} · {tag}" if (n is not None and det) else ""
        if extra:
            det_txt = extra
        self.ax.text(0, self.y, titulo, fontsize=10.5, weight="bold", va="top", color="#111827")
        self.ax.text(1, self.y - 0.002, det_txt, fontsize=8.6, va="top", ha="right", color="#6b7280")
        self.y -= self.fila + 0.002

    def fila_sw(self, tipo, color, etiqueta, detalle="", edge=None, ls="-", lw=2.0, ms=6):
        ax = self.ax
        yc = self.y - 0.011
        if tipo == "poly":
            ax.add_patch(Rectangle((0.012, yc - 0.0105), 0.05, 0.021, facecolor=color, edgecolor=edge or "#6b7280", linewidth=0.5))
        elif tipo == "line":
            ax.plot([0.012, 0.062], [yc, yc], color=color, lw=lw, ls=ls, solid_capstyle="butt")
        elif tipo == "point":
            ax.plot([0.037], [yc], marker="o", ms=ms, color=color, mec="white", mew=0.4, ls="")
        elif tipo == "tri":
            ax.plot([0.037], [yc], marker="^", ms=ms + 1, color=color, mec="white", mew=0.4, ls="")
        elif tipo == "sq":
            ax.plot([0.037], [yc], marker="s", ms=ms, color=color, mec="white", mew=0.4, ls="")
        ax.text(0.085, self.y, etiqueta, fontsize=9.8, va="top", color="#1f2937")
        if detalle:
            ax.text(1, self.y - 0.001, detalle, fontsize=8.8, va="top", ha="right", color="#6b7280")
        self.y -= self.fila

    def espacio(self, d=0.012):
        self.y -= d

    def lecturas(self, items, ancho=70):
        if self.lec is not None:
            ax = self.lec
            y = 1.0
            ax.text(0, y, "LO QUE SE VE", fontsize=9, color="#6b7280", weight="bold", va="top")
            ax.plot([0, 1], [y - 0.085, y - 0.085], color="#d1d5db", lw=0.8)
            y -= 0.16
            for it in items:
                for k, l in enumerate(textwrap.wrap(it, 150)):
                    ax.text(0.0, y, ("•  " if k == 0 else "    ") + l, fontsize=11, va="top", color="#1f2937")
                    y -= 0.105
                y -= 0.03
            return
        self.y -= 0.01
        self.cap("Lo que se ve")
        for it in items:
            lines = textwrap.wrap(it, 74 if ancho >= 60 else ancho)
            for k, l in enumerate(lines):
                self.ax.text(0.0, self.y, ("•  " if k == 0 else "    ") + l, fontsize=9.8, va="top", color="#1f2937")
                self.y -= 0.0285
            self.y -= 0.006


# ---------------------------------------------------------------- dibujo de capas
def poly(ax, gdf, color, lw=0.15, alpha=1.0, z=3, edge=None, hatch=None):
    if len(gdf):
        gdf.plot(ax=ax, facecolor=color, edgecolor=edge or color, linewidth=lw, alpha=alpha, zorder=z, hatch=hatch)


def outline(ax, gdf, color, lw=0.8, z=8, ls="-"):
    if len(gdf):
        gdf.boundary.plot(ax=ax, color=color, linewidth=lw, zorder=z, linestyle=ls)


def _en(gdf):
    return gdf[gdf.intersects(BPOLY)] if len(gdf) else gdf


def lines(ax, gdf, color, lw=0.4, z=6, ls="-", alpha=1.0):
    """Líneas recortadas al Distrito (solo para dibujar; la capa original no se toca)."""
    gdf = _en(gdf)
    if 0 < len(gdf) <= 5000:   # el recorte exacto solo en capas pequeñas; en las de cientos de miles de tramos solo se quitan los que quedan fuera
        gdf = gpd.clip(gdf, BPOLY)
        gdf = gdf[gdf.geom_type.isin(["LineString", "MultiLineString"])]
    if len(gdf):
        gdf.plot(ax=ax, color=color, linewidth=lw, zorder=z, linestyle=ls, alpha=alpha)


def pts(ax, gdf, color, s=6, z=10, marker="o", ec="white", lw=0.3):
    gdf = _en(gdf)
    if not len(gdf):
        return
    g = gdf.geometry
    g = g.where(g.geom_type == "Point", g.representative_point())
    ax.scatter(g.x, g.y, s=s, c=color, marker=marker, edgecolors=ec, linewidths=lw, zorder=z)


def guarda(fig, nombre):
    out = os.path.join(OUT, nombre)
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print("saved", out, flush=True)
    return out


def pct(ha):
    return f"{fmt(100 * ha / DISTRICT_HA, 1)} %"


MAPAS = []


def mapa(num, nombre):
    def deco(f):
        MAPAS.append((num, nombre, f))
        return f
    return deco


# ================================================================ a. DIVISIÓN ADMINISTRATIVA
@mapa("01", "01_division_administrativa")
def m01():
    fig, (ax,), axp, st = lienzo(1, "División administrativa: comunas, corregimientos, barrios y veredas", "Grupo a_DivisionAdministrativa de la geodatabase")
    com = G("limitecomunacorregimiento_2014")
    bar = G("barriovereda_2014")
    sn = com[com["codigo"].str.startswith("SN")]
    reg = com[~com["codigo"].str.startswith("SN")]
    cor = reg[reg["subtipo_comunacorregimiento"] == 2]
    urb = reg[reg["subtipo_comunacorregimiento"] == 1]
    poly(ax, urb, "#dbeafe", lw=0.2, z=3)
    poly(ax, cor, "#dcfce7", lw=0.2, z=3)
    poly(ax, sn, "#fde68a", lw=0.2, z=3)
    outline(ax, bar, "#6b7280", lw=0.25, z=5)
    outline(ax, com, "#111827", lw=1.0, z=7)
    for _, r in urb.iterrows():
        p = r.geometry.representative_point()
        ax.text(p.x, p.y, str(int(r["codigo"])), fontsize=8, ha="center", va="center", color="#1e3a8a", weight="bold", zorder=50,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")])
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("limitecomunacorregimiento_2014", "Comunas y corregimientos")
    P.fila_sw("poly", "#dbeafe", "Comunas (número en el mapa)", f"{len(urb)}")
    P.fila_sw("poly", "#dcfce7", "Corregimientos", f"{len(cor)}")
    P.fila_sw("poly", "#fde68a", "Polígonos sin nombre (SN01 y SN02)", f"{len(sn)} · {fmt(ha_clase(sn))} ha")
    P.espacio()
    P.capa("barriovereda_2014", "Barrios y veredas")
    P.fila_sw("line", "#6b7280", "Límite de barrios y veredas", lw=1)
    P.lecturas([f"{len(com)} unidades de nivel superior: {len(urb)} comunas, {len(cor)} corregimientos y {len(sn)} polígonos sin nombre (códigos SN01 y SN02); además, {len(bar)} barrios y veredas.",
                "Las dos capas conservan el sufijo _2014: son la división del Acuerdo 48 de 2014.",
                "Es la base de referencia de las demás capas: cada elemento lleva el código de su barrio o comuna."])
    return guarda(fig, "01_division_administrativa.png")


# ================================================================ b. NORMA DEL SUELO
@mapa("02", "02_clasificacion_suelo")
def m02():
    fig, (ax,), axp, st = lienzo(1, "Clasificación del suelo y centros poblados", "Grupo b_NormadelSuelo de la geodatabase")
    cs = G("g_cs_clasificacion_suelo")
    cp = G("g_cs_centros_poblados")
    clases = [("Urbano", "#e9b44c", cs["clase_suelo"] == "Urbano"),
              ("Expansión urbana", "#d1495b", cs["clase_suelo"] == "Expansión Urbana"),
              ("Rural suburbano", "#6a994e", (cs["clase_suelo"] == "Rural") & (cs["categoria_suelo"] == "Suburbano")),
              ("Rural (resto)", "#cfe1b9", (cs["clase_suelo"] == "Rural") & (cs["categoria_suelo"] != "Suburbano"))]
    stats = {}
    for lab, c, m in clases:
        poly(ax, cs[m], c, lw=0.2, z=3)
        stats[lab] = (int(m.sum()), ha_clase(cs, m))
    outline(ax, cp, "#1f2937", lw=0.9, z=9)
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("g_cs_clasificacion_suelo", "Clasificación del suelo")
    for lab, c, m in clases:
        n, ha = stats[lab]
        P.fila_sw("poly", c, lab, f"{fmt(ha)} ha · {pct(ha)}")
    P.espacio()
    P.capa("g_cs_centros_poblados", "Centros poblados")
    P.fila_sw("line", "#1f2937", "Contorno de centro poblado", lw=1.2)
    P.lecturas([f"El suelo rural suma {fmt(stats['Rural suburbano'][1] + stats['Rural (resto)'][1])} ha ({pct(stats['Rural suburbano'][1] + stats['Rural (resto)'][1])} del Distrito); el urbano, {fmt(stats['Urbano'][1])} ha ({pct(stats['Urbano'][1])}).",
                f"El suelo de expansión urbana ocupa {fmt(stats['Expansión urbana'][1])} ha en {stats['Expansión urbana'][0]} polígonos.",
                "Origen propuesto de las dos capas: Acuerdo 48 de 2014."])
    return guarda(fig, "02_clasificacion_suelo.png")


@mapa("03", "03_estructura_ecologica_areas")
def m03():
    fig, (ax,), axp, st = lienzo(1, "Estructura ecológica (1): áreas protegidas, cuencas abastecedoras y cerros", "Grupo b_NormadelSuelo de la geodatabase")
    ap = G("gur_ee_areas_protegidas")
    cu = G("gur_ee_cuencas_abastecedoras")
    co = G("gur_ee_sistema_orografico")
    hu = G("gur_ee_humedales")
    os_ = G("gur_ee_ojos_sal")
    cz = G("gur_ee_cuencas_orden_cero")
    poly(ax, co, "#c9a66b", lw=0.2, alpha=0.5, z=3)
    poly(ax, cz, "#bfdbfe", lw=0.2, alpha=0.7, z=4)
    pr = ap[ap["estructura_ecologica"] == "Estructura Ecologica Principal"]
    cm = ap[ap["estructura_ecologica"] != "Estructura Ecologica Principal"]
    poly(ax, cm, "#a6dba0", lw=0.2, alpha=0.85, z=5)
    poly(ax, pr, "#1b7837", lw=0.2, alpha=0.85, z=6)
    outline(ax, cu, "#2166ac", lw=1.0, z=9)
    poly(ax, hu, "#2b8cbe", lw=0.4, z=8)
    pts(ax, os_, "#111827", s=22, z=12, marker="D")
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gur_ee_areas_protegidas", "Áreas protegidas")
    P.fila_sw("poly", "#1b7837", "Estructura ecológica principal", f"{len(pr)}")
    P.fila_sw("poly", "#a6dba0", "Estructura ecológica complementaria", f"{len(cm)}")
    P.capa("gur_ee_cuencas_abastecedoras", "Cuencas abastecedoras")
    P.fila_sw("line", "#2166ac", "Contorno de cuenca abastecedora", lw=1.5)
    P.capa("gur_ee_sistema_orografico", "Sistema orográfico")
    P.fila_sw("poly", "#c9a66b", "Cerros y elementos orográficos")
    P.capa("gur_ee_cuencas_orden_cero", "Cuencas de orden cero")
    P.fila_sw("poly", "#bfdbfe", "Cuencas de orden cero")
    P.capa("gur_ee_humedales", "Humedales")
    P.fila_sw("poly", "#2b8cbe", "Humedales")
    P.capa("gur_ee_ojos_sal", "Ojos de sal")
    P.fila_sw("sq", "#111827", "Ojos de sal", ms=6)
    ha_ap = ha_clase(ap)
    P.lecturas([f"Las áreas protegidas cubren {fmt(ha_ap)} ha, {pct(ha_ap)} del Distrito (unión de los {len(ap)} polígonos).",
                "Origen propuesto de las seis capas: Acuerdo 48 de 2014."])
    return guarda(fig, "03_estructura_ecologica_areas.png")


@mapa("04", "04_estructura_ecologica_agua")
def m04():
    fig, (ax,), axp, st = lienzo(1, "Estructura ecológica (2): red hídrica, retiros y conectividad ecológica", "Grupo b_NormadelSuelo de la geodatabase")
    rh = G("gur_ee_redhidrica")
    rt = G("gur_ee_retiros")
    rhu = G("gur_ee_retiro_humedales")
    rc = G("gur_ee_redconectividadecologic")
    cols = [("Enlace actual", "#1b9e77"), ("Enlace proyectado", "#7fcdbb"), ("Fragmento", "#7570b3"), ("Nodo actual", "#d95f02"), ("Nodo proyectado", "#fdae6b")]
    poly(ax, rt, "#9ecae1", lw=0.15, alpha=0.8, z=3)
    poly(ax, rhu, "#6baed6", lw=0.15, alpha=0.9, z=4)
    for lab, c in cols:
        poly(ax, rc[rc["tipo"] == lab], c, lw=0.25, alpha=0.9, z=5)
    lines(ax, rh, "#2563eb", lw=0.45, z=7)
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gur_ee_redhidrica", "Red hídrica")
    P.fila_sw("line", "#2563eb", "Quebradas y ríos", lw=1.4)
    P.capa("gur_ee_retiros", "Retiros a la red hídrica")
    P.fila_sw("poly", "#9ecae1", "Franja de retiro")
    P.capa("gur_ee_retiro_humedales", "Retiros a humedales")
    P.fila_sw("poly", "#6baed6", "Franja de retiro de humedal")
    P.capa("gur_ee_redconectividadecologic", "Red de conectividad ecológica")
    for lab, c in cols:
        P.fila_sw("poly", c, lab, f"{int((rc['tipo'] == lab).sum())}")
    P.lecturas(["La red hídrica y sus retiros dibujan las quebradas que bajan de las laderas al río Medellín.",
                f"La red de conectividad suma {len(rc)} elementos; {int((rc['tipo'].str.contains('proyectad')).sum())} son proyectados.",
                "Origen propuesto de las cuatro capas: Acuerdo 48 de 2014."])
    return guarda(fig, "04_estructura_ecologica_agua.png")


@mapa("05", "05_suelo_proteccion_y_actividad_rural")
def m05():
    fig, (a1, a2), axp, st = lienzo(2, "Suelo de protección y áreas de actividad rural", "Grupo b_NormadelSuelo de la geodatabase", ancho_texto=0.30,
                                    subtitulos=["Suelo de protección", "Áreas de actividad rural"])
    sp = G("gur_sp_suelo_proteccion_union")
    ar = G("r_so_areas_actividad_rural")
    cs = [("Áreas de conservación y protección ambiental", "#1b7837", "Conservación y protección ambiental"),
          ("Áreas de protección para la producción", "#fdae61", "Protección para la producción"),
          ("Áreas de Amenaza y Riesgo", "#d7191c", "Amenaza y riesgo")]
    for k, c, _ in cs:
        poly(a1, sp[sp["categoria"] == k], c, lw=0.2, z=3)
    act = [("Forestal", "#1b7837"), ("Agropecuario", "#fdbf6f"), ("Agrícola", "#f6e27a"), ("Agroforestal", "#b2df8a"),
           ("Mixto rural 1 -  Baja", "#cab2d6"), ("Mixto rural 2 -  Media", "#a6cee3"), ("Mixto rural 3 -  Alta", "#1f78b4"), ("Minera en transición", "#6a3d9a")]
    for k, c in act:
        poly(a2, ar[ar["area_actividad"] == k], c, lw=0.2, z=3)
    cierre_ax(a1, st, n=2)
    cierre_ax(a2, st, norte=False, n=2, rotulos=False)
    P = Panel(axp)
    P.capa("gur_sp_suelo_proteccion_union", "Suelo de protección (unión)")
    for k, c, lab in cs:
        P.fila_sw("poly", c, lab, f"{fmt(ha_clase(sp, sp['categoria'] == k))} ha")
    P.espacio()
    P.capa("r_so_areas_actividad_rural", "Áreas de actividad rural")
    for k, c in act:
        P.fila_sw("poly", c, k.replace("  ", " "), f"{fmt(ha_clase(ar, ar['area_actividad'] == k))} ha")
    P.lecturas(["Origen propuesto de las dos capas: mixto (Acuerdo 48 de 2014 más elementos nuevos o sin fecha).",
                f"El suelo de protección por amenaza y riesgo es la categoría más pequeña: {fmt(ha_clase(sp, sp['categoria'] == 'Áreas de Amenaza y Riesgo'))} ha de {fmt(ha_clase(sp))} ha de suelo de protección."], ancho=52)
    return guarda(fig, "05_suelo_proteccion_y_actividad_rural.png")


@mapa("06", "06_areas_actividad_urbana")
def m06():
    fig, (ax,), axp, st = lienzo(1, "Áreas de actividad urbana", "Grupo b_NormadelSuelo de la geodatabase")
    au = G("u_so_area_actividad_urbana")
    cls = [("Área de baja mixtura de predominancia residencial", "#fee391", "Baja mixtura, predominio residencial"),
           ("Área de media mixtura de soporte barrial", "#fdae61", "Media mixtura, soporte barrial"),
           ("Área de alta mixtura de predominancia económica", "#d7301f", "Alta mixtura, predominio económico"),
           ("Área de alta mixtura en transformación", "#7a0177", "Alta mixtura en transformación"),
           ("Área dotacional", "#3182bd", "Dotacional"),
           ("Área dotacional del sistema vial", "#8c8c8c", "Dotacional del sistema vial"),
           ("Río", "#9ecae1", "Río")]
    for k, c, _ in cls:
        poly(ax, au[au["area_actividad"] == k], c, lw=0.1, z=3)
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("u_so_area_actividad_urbana", "Áreas de actividad urbana")
    tot = 0
    for k, c, lab in cls:
        m = au["area_actividad"] == k
        ha = float(au.loc[m, "area_ha"].sum())
        tot += ha
        P.fila_sw("poly", c, lab, f"{fmt(int(m.sum()))} polig. · {fmt(ha)} ha")
    P.lecturas([f"Son {fmt(len(au))} polígonos (escala de manzana) que suman {fmt(tot)} ha de suelo urbano.",
                "Origen propuesto: norma del Acuerdo 48 de 2014 ajustada en la revisión (metadata de 2024)."])
    return guarda(fig, "06_areas_actividad_urbana.png")


@mapa("07", "07_vocacion_y_centralidades")
def m07():
    fig, (a1, a2), axp, st = lienzo(2, "Áreas de vocación y subsistema de centralidades", "Grupo b_NormadelSuelo de la geodatabase", ancho_texto=0.30,
                                    subtitulos=["Áreas de vocación urbana", "Centralidades por jerarquía"])
    av = G("u_so_area_vocacion_urbana")
    ce = G("so_substema_centralidades")
    voc = [("Desarrollo Orientado al Transporte -DOT-", "#e41a1c", "Desarrollo orientado al transporte"), ("Ciencia, Tecnología e Innovación -CTeI-", "#377eb8", "Ciencia, tecnología e innovación"),
           ("Cuidado Ambiental", "#4daf4a", "Cuidado ambiental"), ("Patrimonial del ámbito nacional -PEMP-N", "#984ea3", "Patrimonial (ámbito nacional)")]
    for k, c, _ in voc:
        poly(a1, av[av["area_vocacion"] == k], c, lw=0.3, alpha=0.85, z=3)
    jer = [("Metropolitana", "#7f0000"), ("Distrital", "#d7301f"), ("Zonal", "#fc8d59"), ("Barrial", "#fdcc8a"),
           ("Corregimental", "#08519c"), ("Corregimental Intermedia", "#6baed6"), ("Veredal", "#bdd7e7")]
    for k, c in jer:
        poly(a2, ce[ce["jerarquia"] == k], c, lw=0.4, alpha=0.95, z=3)
    cierre_ax(a1, st, n=2)
    cierre_ax(a2, st, norte=False, n=2, rotulos=False)
    P = Panel(axp)
    P.capa("u_so_area_vocacion_urbana", "Áreas de vocación urbana")
    for k, c, lab in voc:
        P.fila_sw("poly", c, lab, f"{int((av['area_vocacion'] == k).sum())}")
    P.espacio()
    P.capa("so_substema_centralidades", "Subsistema de centralidades")
    for k, c in jer:
        P.fila_sw("poly", c, k, f"{int((ce['jerarquia'] == k).sum())}")
    P.lecturas([f"{int((av['area_vocacion'].str.startswith('Desarrollo')).sum())} de {len(av)} áreas de vocación son de desarrollo orientado al transporte.",
                f"Hay {len(ce)} centralidades; {int((ce['clase_suelo'] == 'Rural').sum())} están en suelo rural (veredales y corregimentales).",
                "Origen propuesto: centralidades, revisión 2025–2026; áreas de vocación, Acuerdo 48 (2014–2016, probable)."], ancho=52)
    return guarda(fig, "07_vocacion_y_centralidades.png")


@mapa("08", "08_tratamientos_urbanisticos")
def m08():
    fig, (ax,), axp, st = lienzo(1, "Tratamientos urbanísticos, aprovechamientos y obligaciones", "Grupo b_NormadelSuelo de la geodatabase")
    tr = G("ur_so_tratament_aprovch_oblig")
    cls = [("Consolidación", "#fdae61", "Consolidación"), ("Consolidación Suburbana", "#fee08b", "Consolidación suburbana"), ("Conservación", "#1a9850", "Conservación"),
           ("Renovación Urbana", "#d73027", "Renovación urbana"), ("Mejoramiento Integral", "#7b3294", "Mejoramiento integral"), ("Desarrollo", "#2c7bb6", "Desarrollo"),
           ("Áreas de Preservación de Infraestructuras y del Sistema Público y Colectivo", "#969696", "Preservación de infraestructuras y sistema público"),
           ("Generación de actividades rurales sostenibles", "#b2df8a", "Generación de actividades rurales sostenibles"),
           ("Restauración de actividades rurales", "#66c2a5", "Restauración de actividades rurales"),
           ("Transición ambiental y paisajística", "#a6761d", "Transición ambiental y paisajística")]
    for k, c, _ in cls:
        poly(ax, tr[tr["categoria_tratamiento"] == k], c, lw=0.15, z=3)
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("ur_so_tratament_aprovch_oblig", "Tratamientos (categoría)")
    for k, c, lab in cls:
        m = tr["categoria_tratamiento"] == k
        P.fila_sw("poly", c, lab, f"{int(m.sum())} polig. · {fmt(ha_clase(tr, m))} ha")
    P.lecturas([f"Son {len(tr)} polígonos en {tr['categoria_tratamiento'].nunique()} categorías de tratamiento y {tr['nivel_tratamiento'].nunique()} niveles.",
                "Cada polígono trae densidad de vivienda y altura máxima. Origen propuesto: revisión 2025–2026."], ancho=60)
    return guarda(fig, "08_tratamientos_urbanisticos.png")


@mapa("09", "09_patrimonio_cultural")
def m09():
    fig, (ax,), axp, st = lienzo(1, "Patrimonio cultural: bienes de interés cultural y zonas de influencia", "Grupo b_NormadelSuelo de la geodatabase")
    bic = G("ur_spc_bienes_interes_cultural")
    zi = G("ur_spc_zonas_influencia")
    zia = G("ur_spc_zi_arqueologicas")
    ap = G("ur_spc_bic_arqueologico_p")
    al = G("ur_spc_bic_arqueologico_l")
    aa = G("ur_spc_bic_arqueologico_a")
    li = G("ur_spc_patrimonio_licbic_p_48")
    poly(ax, zi, "#fdd0a2", lw=0.3, alpha=0.8, z=3)
    poly(ax, zia, "#c7e9c0", lw=0.3, alpha=0.9, z=3)
    lines(ax, al, "#7f2704", lw=0.8, z=6)
    poly(ax, aa, "#d9a066", lw=0.8, alpha=0.5, z=5, edge="#7f2704")
    pts(ax, li, "#9e9ac8", s=9, z=8)
    pts(ax, ap, "#7f2704", s=7, z=9)
    nac = bic[bic["ambito"] == "Nacional"]
    dis = bic[bic["ambito"] != "Nacional"]
    pts(ax, dis, "#08519c", s=14, z=11)
    pts(ax, nac, "#cb181d", s=34, z=12, marker="s")
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("ur_spc_bienes_interes_cultural", "Bienes de interés cultural")
    P.fila_sw("point", "#08519c", "Ámbito distrital", f"{len(dis)}")
    P.fila_sw("sq", "#cb181d", "Ámbito nacional", f"{len(nac)}")
    P.capa("ur_spc_zonas_influencia", "Zonas de influencia de los BIC")
    P.fila_sw("poly", "#fdd0a2", "Zona de influencia")
    P.capa("ur_spc_zi_arqueologicas", "Zonas de influencia arqueológicas")
    P.fila_sw("poly", "#c7e9c0", "Zona de influencia arqueológica")
    P.capa("ur_spc_bic_arqueologico_p", "Bienes arqueológicos (puntos, líneas, áreas)")
    P.fila_sw("point", "#7f2704", "Punto", f"{len(ap)}")
    P.fila_sw("line", "#7f2704", "Línea", f"{len(al)}", lw=1.4)
    P.fila_sw("poly", "#d9a066", "Área", f"{len(aa)}", edge="#7f2704")
    P.capa("ur_spc_patrimonio_licbic_p_48", "Listado indicativo de BIC (Acuerdo 48)")
    P.fila_sw("point", "#9e9ac8", "Bien del listado indicativo")
    P.lecturas([f"{len(bic)} bienes de interés cultural: {len(dis)} de ámbito distrital y {len(nac)} de ámbito nacional; los bienes se marcan con un punto en su centro.",
                "Origen propuesto: inventario 2024–2026; listado indicativo, Acuerdo 48."], ancho=60)
    return guarda(fig, "09_patrimonio_cultural.png")


# ================================================================ c. AMENAZA Y RIESGO
@mapa("10", "10_amenazas")
def m10():
    fig, axs, axp, st = lienzo(3, "Amenaza por inundación, avenidas torrenciales y movimientos en masa", "Grupo c_AmenazayRiesgo de la geodatabase", ancho_texto=0.20,
                               subtitulos=["Inundación", "Avenidas torrenciales", "Movimientos en masa"])
    capas = [("gur_ar_amenaza_inundaciones", 0.4), ("gur_ar_amenaza_avtorrenciales", 0.4), ("gur_ar_amenaza_mov_masa", 0.1)]
    colors = {"Baja": "#fecc5c", "Media": "#fd8d3c", "Alta": "#bd0026"}
    info = []
    for i, (ax, (nm, lw)) in enumerate(zip(axs, capas)):
        g = G(nm)
        col = "categoria" if "categoria" in g.columns else next(c for c in g.columns if "amenaza" in c.lower())
        for k in ("Baja", "Media", "Alta"):
            poly(ax, g[g[col].astype(str).str.capitalize() == k], colors[k], lw=lw, z=3)
        info.append((nm, g, col))
        cierre_ax(ax, st, norte=(i == 0), n=3, rotulos=False)
    P = Panel(axp)
    P.capa("gur_ar_amenaza_inundaciones", "Inundación", det=False)
    P.capa("gur_ar_amenaza_avtorrenciales", "Avenidas torrenciales", det=False)
    P.capa("gur_ar_amenaza_mov_masa", "Movimientos en masa", det=False)
    P.espacio()
    for k in ("Alta", "Media", "Baja"):
        P.fila_sw("poly", colors[k], k)
    ha = lambda k: STATS[k]["ha"]
    P.lecturas([f"Inundación ({fmt(ELEM['gur_ar_amenaza_inundaciones'])} polígonos): alta {fmt(ha('inundacion')['Alta'])} ha, media {fmt(ha('inundacion')['Media'])} ha y baja {fmt(ha('inundacion')['Baja'])} ha.",
                f"Avenidas torrenciales ({fmt(ELEM['gur_ar_amenaza_avtorrenciales'])} polígonos): alta {fmt(ha('avenidas_torrenciales')['Alta'])} ha, media {fmt(ha('avenidas_torrenciales')['Media'])} ha y baja {fmt(ha('avenidas_torrenciales')['Baja'])} ha.",
                f"Movimientos en masa ({fmt(ELEM['gur_ar_amenaza_mov_masa'])} polígonos): alta {fmt(ha('movimientos_masa')['Alta'])} ha ({fmt(STATS['movimientos_masa']['pct_of_district']['Alta'], 1)} % del Distrito), media {fmt(ha('movimientos_masa')['Media'])} ha y baja {fmt(ha('movimientos_masa')['Baja'])} ha.",
                "Origen propuesto: 2026, construidas con el estudio básico de amenaza; son las mismas capas del Producto 1 (numerales 8.1.3 a 8.1.5)."], ancho=36)
    return guarda(fig, "10_amenazas.png")


@mapa("11", "11_riesgo")
def m11():
    fig, axs, axp, st = lienzo(3, "Riesgo por inundación, avenidas torrenciales y movimientos en masa", "Grupo c_AmenazayRiesgo de la geodatabase", ancho_texto=0.20,
                               subtitulos=["Inundación", "Avenidas torrenciales", "Movimientos en masa"])
    capas = ["gur_ar_riesgo_inundaciones", "gur_ar_riesgo_avtorrenciales", "gur_ar_riesgo_mov_masa"]
    cls = [("Riesgo bajo", "#ffeda0"), ("Riesgo medio", "#feb24c"), ("En condición de riesgo", "#fc4e2a"), ("Alto riesgo mitigable", "#bd0026"), ("Alto riesgo no mitigable", "#4a0012")]
    for i, (ax, nm) in enumerate(zip(axs, capas)):
        g = G(nm)
        for k, c in cls:
            poly(ax, g[g["riesgo"] == k], c, lw=0.35, z=3)
        cierre_ax(ax, st, norte=(i == 0), n=3, rotulos=False)
    P = Panel(axp)
    for nm, t in zip(capas, ["Inundación", "Avenidas torrenciales", "Movimientos en masa"]):
        P.capa(nm, t, det=False)
    P.espacio()
    for k, c in cls:
        det = " / ".join(str(int((G(nm)["riesgo"] == k).sum())) for nm in capas)
        P.fila_sw("poly", c, k, det)
    rl = [f"{t} ({fmt(len(G(nm)))} polígonos): {fmt(int((G(nm)['riesgo'] == 'En condición de riesgo').sum()))} en condición de riesgo, {fmt(int((G(nm)['riesgo'] == 'Alto riesgo mitigable').sum()))} de alto riesgo mitigable y {fmt(int((G(nm)['riesgo'] == 'Alto riesgo no mitigable').sum()))} de alto riesgo no mitigable."
          for nm, t in zip(capas, ["Inundación", "Avenidas torrenciales", "Movimientos en masa"])]
    P.lecturas(rl + ["Cifras del recuadro de la derecha: polígonos de inundación / avenidas / movimientos en masa. Origen propuesto de las tres capas: 2026."], ancho=36)
    return guarda(fig, "11_riesgo.png")


@mapa("12", "12_condicion_amenaza")
def m12():
    fig, (ax,), axp, st = lienzo(1, "Áreas con condición de amenaza", "Grupo c_AmenazayRiesgo de la geodatabase")
    g = G("gur_ar_condicion_amenaza")
    fen = [("Movimientos en Masa", "#8c510a", "Movimientos en masa"), ("Avenida Torrencial", "#2166ac", "Avenidas torrenciales"), ("Inundación", "#01665e", "Inundación")]
    for k, c, _ in fen:
        poly(ax, g[g["fenomeno"] == k], c, lw=0.5, alpha=0.9, z=4)
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gur_ar_condicion_amenaza", "Áreas con condición de amenaza")
    for k, c, lab in fen:
        m = g["fenomeno"] == k
        P.fila_sw("poly", c, lab, f"{fmt(int(m.sum()))} polig. · {fmt(ha_clase(g, m))} ha")
    P.lecturas([f"{int((g['categoria'] == 'Alta').sum())} polígonos son de amenaza alta y {int((g['categoria'] == 'Media').sum())} de amenaza media.",
                "Según el DAP, son zonas de amenaza alta y media que el POT clasifica como suelo urbano, de expansión, rural suburbano o centro poblado para permitir su desarrollo (Decreto 1077 de 2015).",
                "Origen propuesto: 2026; cada polígono lleva el nombre de su barrio."], ancho=60)
    return guarda(fig, "12_condicion_amenaza.png")


# ================================================================ d. SISTEMAS GENERALES
@mapa("13", "13_vias_y_transporte_masivo")
def m13():
    fig, (ax,), axp, st = lienzo(1, "Vías y corredores de transporte de pasajeros", "Grupo d_SistemasGenerales de la geodatabase")
    vi = G("gur_spc_vias_urbanorural")
    ct = G("gu_spc_corred_tte_pasajeros")
    jer = [("Vía de primer orden nacional", "#111827", 1.6, "Vías nacionales (1.º, 2.º y 3.er orden)"), ("Vía de segundo orden nacional", "#111827", 1.6, None), ("Vía de tercer orden nacional", "#111827", 1.6, None),
           ("Autopista urbana o vía de travesía", "#7f1d1d", 1.4, "Autopista urbana o de travesía"), ("Vía arteria", "#b45309", 0.9, "Vía arteria"), ("Vía colectora", "#d97706", 0.5, "Vía colectora"),
           ("Vía primaria rural", "#4d7c0f", 0.8, "Vía primaria rural"), ("Vía secundaria rural", "#84cc16", 0.5, "Vía secundaria rural"), ("Vía férrea", "#6b7280", 1.0, None)]
    for k, c, lw, _ in jer:
        lines(ax, vi[vi["jerarquizacion_via"] == k], c, lw=lw, z=5)
    tip = {"1": ("Metro", "#00a859"), "2": ("Metrocable", "#f59e0b"), "3": ("Metroplús", "#2563eb"), "4": ("Tranvía", "#a21caf"), "5": ("Otros corredores de pasajeros", "#dc2626")}
    for code, (lab, c) in tip.items():
        sub = ct[ct["tipo_sistema"].astype(str) == code]
        lines(ax, sub[sub["estado"].astype(str) == "1"], c, lw=2.6, z=9)
        lines(ax, sub[sub["estado"].astype(str) != "1"], c, lw=2.2, z=9, ls=(0, (3, 2)))
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gur_spc_vias_urbanorural", "Vías urbano-rurales")
    seen = set()
    for k, c, lw, lab in jer:
        if lab and lab not in seen:
            seen.add(lab)
            n = int(vi["jerarquizacion_via"].isin([x[0] for x in jer if x[3] == lab or (lab.startswith("Vías nacionales") and x[0].endswith("nacional"))]).sum()) if lab.startswith("Vías nacionales") else int((vi["jerarquizacion_via"] == k).sum())
            P.fila_sw("line", c, lab, f"{n}", lw=max(lw, 1.2))
    P.capa("gu_spc_corred_tte_pasajeros", "Corredores de transporte de pasajeros")
    for code, (lab, c) in tip.items():
        sub = ct[ct["tipo_sistema"].astype(str) == code]
        P.fila_sw("line", c, lab, f"{len(sub)} tramos", lw=2.6)
    P.fila_sw("line", "#374151", "Trazo continuo: existente · discontinuo: proyectado o en ejecución", lw=2, ls=(0, (3, 2)))
    ex = int((ct["estado"].astype(str) == "1").sum())
    P.lecturas([f"De {len(ct)} tramos de transporte de pasajeros, {ex} existen y {len(ct) - ex} están proyectados o en estudio.",
                f"Las vías suman {fmt(len(vi))} elementos; {fmt(int((vi['estado'] == 'Proyectado').sum()))} son proyectadas y {fmt(int((vi['estado'] == 'Ampliación').sum()))} son ampliaciones."], ancho=62)
    return guarda(fig, "13_vias_y_transporte_masivo.png")


@mapa("14", "14_peatonal_ciclorrutas_corredores_verdes")
def m14():
    fig, (ax,), axp, st = lienzo(1, "Red peatonal, ciclorrutas y corredores verdes", "Grupo d_SistemasGenerales de la geodatabase")
    rp = G("gu_spc_red_peatonal")
    rpe = G("gu_spc_red_peatonal_estructurante")
    ci = G("gu_spc_ciclorutas")
    cv = G("gu_spc_corredores_verdes")
    poly(ax, rpe, "#fbb4b9", lw=0.2, z=3)
    lines(ax, rp, "#c51b8a", lw=0.35, z=5)
    lines(ax, cv, "#238b45", lw=1.4, z=7)
    ex = ci[ci["estado"] == "Existente"]
    pr = ci[ci["estado"] != "Existente"]
    lines(ax, pr, "#2171b5", lw=1.1, z=9, ls=(0, (3, 2)))
    lines(ax, ex, "#2171b5", lw=1.4, z=9)
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gu_spc_red_peatonal_estructurante", "Red peatonal estructurante")
    P.fila_sw("poly", "#fbb4b9", "Polígonos de la red peatonal estructurante")
    P.capa("gu_spc_red_peatonal", "Red peatonal")
    P.fila_sw("line", "#c51b8a", "Ejes de la red peatonal", lw=1.2)
    P.capa("gu_spc_ciclorutas", "Ciclorrutas")
    P.fila_sw("line", "#2171b5", "Existente", f"{len(ex)}", lw=2)
    P.fila_sw("line", "#2171b5", "Proyectada o en estudio", f"{len(pr)}", lw=2, ls=(0, (3, 2)))
    P.capa("gu_spc_corredores_verdes", "Corredores verdes")
    P.fila_sw("line", "#238b45", "Corredor verde", lw=2.2)
    P.lecturas([f"Hay {len(ex)} tramos de ciclorruta existentes y {len(pr)} proyectados o en estudio.",
                "Origen propuesto: corredores verdes y red peatonal, Acuerdo 48; ciclorrutas, inventario 2024–2026."], ancho=60)
    return guarda(fig, "14_peatonal_ciclorrutas_corredores_verdes.png")


@mapa("15", "15_espacio_publico")
def m15():
    fig, (a1, a2), axp, st = lienzo(2, "Espacio público existente y proyectado", "Grupo d_SistemasGenerales de la geodatabase", ancho_texto=0.30,
                                    subtitulos=["Existente", "Proyectado"])
    ex = G("gu_spc_espac_publico_existente")
    pr = G("gu_spc_espac_publico_proyectado")
    zv = G("gu_spc_zonverdpubl_sistmovil")
    poly(a1, zv, "#d9f0d3", lw=0.3, z=3)
    cat = [("Parque Recreativo", "#2b8cbe"), ("Ecoparque", "#1b7837"), ("Plazoleta", "#e08214"), ("Plazuela", "#e08214"), ("No Aplica", "#9e9ac8")]
    for k, c in cat:
        poly(a1, ex[ex["categoria"] == k], c, lw=0.5, z=5)
    for k, c in [("Parque Recreativo", "#2b8cbe"), ("Ecoparque", "#1b7837"), ("Mirador Panorámico", "#d73027"), ("Plazoleta", "#e08214"), ("Plaza", "#e08214"), ("Parque Cívico", "#e08214")]:
        poly(a2, pr[pr["categoria"] == k], c, lw=0.5, z=5)
    poly(a2, pr[~pr["categoria"].isin(["Parque Recreativo", "Ecoparque", "Mirador Panorámico", "Plazoleta", "Plaza", "Parque Cívico"])], "#9e9ac8", lw=0.5, z=5)
    cierre_ax(a1, st, n=2)
    cierre_ax(a2, st, norte=False, n=2, rotulos=False)
    P = Panel(axp)
    P.capa("gu_spc_espac_publico_existente", "Espacio público existente")
    for lab, c, ks in [("Parques recreativos", "#2b8cbe", ["Parque Recreativo"]), ("Ecoparques", "#1b7837", ["Ecoparque"]), ("Plazoletas y plazuelas", "#e08214", ["Plazoletas", "Plazoleta", "Plazuela"]), ("Otros (sin categoría)", "#9e9ac8", ["No Aplica"])]:
        P.fila_sw("poly", c, lab, f"{int(ex['categoria'].isin(ks).sum())}")
    P.capa("gu_spc_zonverdpubl_sistmovil", "Zonas verdes del sistema móvil")
    P.fila_sw("poly", "#d9f0d3", "Zona verde pública (solo panel izquierdo)")
    P.espacio()
    P.capa("gu_spc_espac_publico_proyectado", "Espacio público proyectado")
    for lab, c, ks in [("Ecoparques", "#1b7837", ["Ecoparque"]), ("Parques recreativos", "#2b8cbe", ["Parque Recreativo"]), ("Miradores panorámicos", "#d73027", ["Mirador Panorámico"]), ("Plazas y plazoletas", "#e08214", ["Plazoleta", "Plaza", "Parque Cívico"])]:
        P.fila_sw("poly", c, lab, f"{int(pr['categoria'].isin(ks).sum())}")
    P.lecturas([f"El proyectado ({len(pr)} elementos) es sobre todo de ecoparques: {int((pr['categoria'] == 'Ecoparque').sum())}, con {int(pr['subcategoria'].astype(str).str.contains('quebrada').sum())} de quebrada o cuerpos de agua.",
                "Origen propuesto: existente, inventario 2024–2026; proyectado, mixto (Acuerdo 48 más elementos nuevos); zonas verdes, Acuerdo 48."], ancho=52)
    return guarda(fig, "15_espacio_publico.png")


@mapa("16", "16_equipamientos")
def m16():
    fig, (ax,), axp, st = lienzo(1, "Equipamientos colectivos", "Grupo d_SistemasGenerales de la geodatabase")
    eq = G("gu_spc_equipamiento")
    t = eq["tipo_ladmpot"].astype(str)
    grp = [("Educación", "#1f77b4", ["1"]), ("Salud", "#d62728", ["3"]), ("Bienestar social", "#ff7f0e", ["4"]), ("Cultura", "#9467bd", ["2"]), ("Culto", "#8c564b", ["5"]),
           ("Deportivo y recreativo", "#2ca02c", ["6"]), ("Seguridad, defensa y justicia", "#17becf", ["7", "8"]), ("Administración pública y atención SPD", "#7f7f7f", ["12", "13"]),
           ("Infraestructura de transporte", "#bcbd22", ["31", "32"]), ("Abastecimiento y cementerios", "#e377c2", ["9", "11"])]
    for lab, c, ks in grp:
        pts(ax, eq[t.isin(ks)], c, s=11, z=8, lw=0.2)
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gu_spc_equipamiento", "Equipamientos (tipo)")
    for lab, c, ks in grp:
        P.fila_sw("point", c, lab, f"{int(t.isin(ks).sum())}")
    P.lecturas([f"{fmt(len(eq))} equipamientos; {fmt(int(t.isin(['1']).sum()))} son educativos y {fmt(int(t.isin(['6']).sum()))} deportivos y recreativos.",
                "Cada equipamiento se marca con un punto en su centro. Origen propuesto: mixto (Acuerdo 48 más elementos nuevos)."], ancho=60)
    return guarda(fig, "16_equipamientos.png")


@mapa("17", "17_acueducto")
def m17():
    fig, (ax,), axp, st = lienzo(1, "Servicio de acueducto: redes, captaciones y plantas", "Grupo d_SistemasGenerales de la geodatabase")
    per = G("gur_spc_perimetro_acueducto")
    sec = G("gur_spc_red_acdto_secundario_epm")
    pri = G("gur_spc_red_acdto_primario_epm")
    ver = G("gr_spc_red_acuedto_veredal")
    ce = G("gr_spc_captaciones_epm")
    cv = G("gr_spc_captaciones_veredales")
    pot = G("gur_spc_sistem_potabilizacion")
    pt = G("gur_spc_acuedpotable_48")
    poly(ax, per, "#e0f2fe", lw=0.3, alpha=0.7, z=2)
    lines(ax, sec, "#7dd3fc", lw=0.12, z=4)
    lines(ax, ver, "#14b8a6", lw=0.4, z=5)
    lines(ax, pri, "#1d4ed8", lw=0.55, z=6)
    pts(ax, cv, "#0f766e", s=24, z=10, marker="^")
    pts(ax, ce, "#1e3a8a", s=40, z=11, marker="^")
    pts(ax, pt, "#f59e0b", s=40, z=11, marker="s")
    pts(ax, pot, "#dc2626", s=26, z=12, marker="s")
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gur_spc_perimetro_acueducto", "Perímetro del servicio de acueducto")
    P.fila_sw("poly", "#e0f2fe", "Perímetro por circuito")
    P.capa("gur_spc_red_acdto_secundario_epm", "Red secundaria (EPM)")
    P.fila_sw("line", "#7dd3fc", "Red secundaria", lw=1.4)
    P.capa("gur_spc_red_acdto_primario_epm", "Red primaria (EPM)")
    P.fila_sw("line", "#1d4ed8", "Red primaria", lw=1.8)
    P.capa("gr_spc_red_acuedto_veredal", "Red de acueducto veredal")
    P.fila_sw("line", "#14b8a6", "Red veredal", lw=1.6)
    P.capa("gr_spc_captaciones_epm", "Captaciones de EPM")
    P.fila_sw("tri", "#1e3a8a", "Captación de EPM")
    P.capa("gr_spc_captaciones_veredales", "Captaciones veredales")
    P.fila_sw("tri", "#0f766e", "Captación veredal")
    P.capa("gur_spc_sistem_potabilizacion", "Sistemas de potabilización y almacenamiento")
    P.fila_sw("sq", "#dc2626", "Sistema de potabilización")
    P.capa("gur_spc_acuedpotable_48", "Plantas de potabilización (Acuerdo 48)")
    P.fila_sw("sq", "#f59e0b", "Planta de potabilización")
    P.lecturas([f"La red secundaria tiene {fmt(len(sec))} tramos y la primaria {fmt(len(pri))}; es inventario de EPM.",
                "Origen propuesto: redes y sistemas de potabilización, inventario 2024–2026; plantas de potabilización, Acuerdo 48."], ancho=60)
    return guarda(fig, "17_acueducto.png")


@mapa("18", "18_alcantarillado_aseo")
def m18():
    fig, (ax,), axp, st = lienzo(1, "Alcantarillado, tratamiento de aguas residuales y aseo", "Grupo d_SistemasGenerales de la geodatabase")
    al = G("gu_spc_red_alcantarill_urbano")
    per = G("gur_spc_perimetro_alcantarillad")
    pta = G("gur_spc_plant_tto_agresidual")
    ase = G("gur_spc_aseo")
    as48 = G("gur_spc_aseo_48")
    poly(ax, per, "#fde68a", lw=0.3, alpha=0.6, z=2)
    lines(ax, al, "#92400e", lw=0.12, z=5)
    pts(ax, as48, "#7c3aed", s=36, z=10, marker="s")
    pts(ax, ase, "#9333ea", s=30, z=11, marker="o")
    pts(ax, pta, "#dc2626", s=70, z=12, marker="D")
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gur_spc_perimetro_alcantarillad", "Perímetro del servicio de alcantarillado")
    P.fila_sw("poly", "#fde68a", "Perímetro")
    P.capa("gu_spc_red_alcantarill_urbano", "Red de alcantarillado urbano (EPM)")
    P.fila_sw("line", "#92400e", "Tramos de red", lw=1.4)
    P.capa("gur_spc_plant_tto_agresidual", "Plantas de tratamiento de aguas residuales")
    P.fila_sw("point", "#dc2626", "Planta de tratamiento", f"{len(pta)}", ms=7)
    P.capa("gur_spc_aseo", "Equipamientos de aseo")
    P.fila_sw("point", "#9333ea", "Equipamiento de aseo (inventario)", f"{len(ase)}")
    P.capa("gur_spc_aseo_48", "Aseo (Acuerdo 48)")
    P.fila_sw("sq", "#7c3aed", "Punto de aseo del Acuerdo 48", f"{len(as48)}")
    P.lecturas([f"La red de alcantarillado urbano tiene {fmt(len(al))} tramos, una de las cuatro capas de la geodatabase con más de 100.000 elementos (las otras: anillo de gas, luminarias y red secundaria de acueducto).",
                f"El perímetro del servicio son {len(per)} polígonos. Origen propuesto: inventario 2024–2026 de EPM."], ancho=60)
    return guarda(fig, "18_alcantarillado_aseo.png")


@mapa("19", "19_energia_y_gas")
def m19():
    fig, (a1, a2), axp, st = lienzo(2, "Energía eléctrica y gas natural", "Grupo d_SistemasGenerales de la geodatabase", ancho_texto=0.30,
                                    subtitulos=["Energía eléctrica", "Gas natural"])
    lp = G("gur_spc_linea_primaria_energia")
    rp = G("gur_spc_red_primaria_energia")
    isa = G("gur_spc_linea_trans_isa")
    to = G("gur_spc_torres_energia")
    su = G("gu_spc_subestac_energia_epm")
    si = G("gur_spc_servidumb_lin_prim_energ")
    sis = G("gur_spc_servidumbre_linea_isa")
    an = G("gu_spc_tuberia_anillo_gas")
    ar = G("gu_spc_tuberia_arteria_gas")
    pr = G("gu_spc_tuberia_primaria_gas")
    poly(a1, si, "#fde68a", lw=0.3, z=3)
    poly(a1, sis, "#fde68a", lw=0.3, z=3)
    lines(a1, rp, "#fbbf24", lw=0.2, z=4)
    lines(a1, lp, "#ea580c", lw=0.8, z=6)
    lines(a1, isa, "#7f1d1d", lw=1.6, z=7)
    pts(a1, to, "#78350f", s=8, z=9)
    poly(a1, su, "#dc2626", lw=1.0, z=10)
    pts(a1, su, "#dc2626", s=34, z=11, marker="s")
    lines(a2, an, "#c4b5fd", lw=0.1, z=4)
    lines(a2, ar, "#7c3aed", lw=0.3, z=5)
    lines(a2, pr, "#4c1d95", lw=1.0, z=6)
    cierre_ax(a1, st, n=2)
    cierre_ax(a2, st, norte=False, n=2, rotulos=False)
    P = Panel(axp)
    P.capa("gur_spc_red_primaria_energia", "Red primaria de energía")
    P.fila_sw("line", "#fbbf24", "Red primaria", lw=1.4)
    P.capa("gur_spc_linea_primaria_energia", "Líneas primarias de energía")
    P.fila_sw("line", "#ea580c", "Línea primaria", lw=1.8)
    P.capa("gur_spc_linea_trans_isa", "Transmisión ISA")
    P.fila_sw("line", "#7f1d1d", "Línea de transmisión", lw=2)
    P.capa("gur_spc_torres_energia", "Torres de energía")
    P.fila_sw("point", "#78350f", "Torre")
    P.capa("gu_spc_subestac_energia_epm", "Subestaciones")
    P.fila_sw("sq", "#dc2626", "Subestación")
    P.capa("gur_spc_servidumb_lin_prim_energ", "Servidumbres de líneas")
    P.fila_sw("poly", "#fde68a", "Franja de servidumbre")
    P.espacio()
    P.capa("gu_spc_tuberia_anillo_gas", "Tubería anillo de gas")
    P.fila_sw("line", "#c4b5fd", "Anillo", lw=1.4)
    P.capa("gu_spc_tuberia_arteria_gas", "Tubería arteria de gas")
    P.fila_sw("line", "#7c3aed", "Arteria", lw=1.6)
    P.capa("gu_spc_tuberia_primaria_gas", "Tubería primaria de gas")
    P.fila_sw("line", "#4c1d95", "Primaria", lw=2)
    P.lecturas([f"El anillo de gas tiene {fmt(len(an))} tramos y la red primaria de energía {fmt(len(rp))}: son inventarios de EPM 2024–2026.",
                "Origen propuesto de todas las capas de energía y gas: inventario 2024–2026."], ancho=52)
    return guarda(fig, "19_energia_y_gas.png")


@mapa("20", "20_alumbrado_publico")
def m20():
    fig, (ax,), axp, st = lienzo(1, "Alumbrado público: luminarias, transformadores y cuadrantes", "Grupo d_SistemasGenerales de la geodatabase")
    lu = G("gur_spc_luminarias")
    cu = G("gur_spc_cuadrantes_alumbrado")
    tr = G("gur_spc_transformador_alumbr")
    an_g = G("gu_spc_tuberia_anillo_gas")
    poly(ax, cu, "#fef9c3", lw=0.3, alpha=0.6, z=2)
    outline(ax, cu, "#a16207", lw=0.6, z=4)
    lu_d = _en(lu)
    ax.scatter(lu_d.geometry.x, lu_d.geometry.y, s=0.35, c="#d97706", linewidths=0, zorder=6, rasterized=True)
    pts(ax, tr, "#1d4ed8", s=18, z=9)
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gur_spc_cuadrantes_alumbrado", "Cuadrantes del servicio")
    P.fila_sw("poly", "#fef9c3", "Cuadrante", edge="#a16207")
    P.capa("gur_spc_luminarias", "Luminarias")
    P.fila_sw("point", "#d97706", "Luminaria", ms=4)
    P.capa("gur_spc_transformador_alumbr", "Transformadores de alumbrado")
    P.fila_sw("point", "#1d4ed8", "Transformador")
    P.lecturas([f"Son {fmt(len(lu))} luminarias: la segunda capa con más elementos de la geodatabase (la primera es el anillo de gas, con {fmt(len(an_g))}).",
                "Las luminarias dibujan la trama de calles y vías: se concentran en la zona urbana y siguen las vías de los corregimientos.",
                "Origen propuesto: inventario 2024–2026."], ancho=60)
    return guarda(fig, "20_alumbrado_publico.png")


@mapa("21", "21_telecomunicaciones_hidrocarburos")
def m21():
    fig, (ax,), axp, st = lienzo(1, "Telecomunicaciones e infraestructura de hidrocarburos", "Grupo d_SistemasGenerales de la geodatabase")
    an = G("gur_spc_cubrimiento_anten_telec")
    tdt = G("gr_spc_television_tdt_telecom")
    am = G("gur_spc_radio_am_telecom")
    fm = G("gur_spc_radio_fm_telecom")
    et = G("gur_spc_estacion_terrenas_telec")
    it = G("gur_spc_infra_telecomunicaciones")
    hi = G("gur_spc_infra_hidrocarburos")
    poly(ax, it, "#a78bfa", lw=0.8, z=4)
    poly(ax, hi, "#ef4444", lw=0.8, z=4)
    pts(ax, an, "#0ea5e9", s=7, z=6, lw=0.1)
    pts(ax, fm, "#22c55e", s=36, z=9, marker="^")
    pts(ax, am, "#f59e0b", s=36, z=9, marker="v")
    pts(ax, tdt, "#a21caf", s=44, z=10, marker="D")
    pts(ax, et, "#111827", s=44, z=10, marker="s")
    cierre_ax(ax, st)
    P = Panel(axp)
    P.capa("gur_spc_cubrimiento_anten_telec", "Antenas de telecomunicaciones")
    P.fila_sw("point", "#0ea5e9", "Antena", ms=4)
    P.capa("gr_spc_television_tdt_telecom", "Antenas de televisión TDT")
    P.fila_sw("sq", "#a21caf", "Antena TDT")
    P.capa("gur_spc_radio_fm_telecom", "Radio FM")
    P.fila_sw("tri", "#22c55e", "Antena FM")
    P.capa("gur_spc_radio_am_telecom", "Radio AM")
    P.fila_sw("tri", "#f59e0b", "Antena AM")
    P.capa("gur_spc_estacion_terrenas_telec", "Estaciones terrenas")
    P.fila_sw("sq", "#111827", "Estación terrena")
    P.capa("gur_spc_infra_telecomunicaciones", "Infraestructura de telecomunicaciones")
    P.fila_sw("poly", "#a78bfa", "Predio de infraestructura")
    P.capa("gur_spc_infra_hidrocarburos", "Infraestructura de hidrocarburos")
    P.fila_sw("poly", "#ef4444", "Predios y derechos de vía")
    P.lecturas([f"{fmt(len(an))} antenas de telecomunicaciones, además de antenas de televisión, radio AM y FM y estaciones terrenas.",
                "Origen propuesto: inventario 2024–2026."], ancho=60)
    return guarda(fig, "21_telecomunicaciones_hidrocarburos.png")


# ================================================================ e. PLANIFICACIÓN COMPLEMENTARIA
@mapa("22", "22_instrumentos_planificacion")
def m22():
    fig, (a1, a2), axp, st = lienzo(2, "Instrumentos de planificación complementaria", "Grupo e_PlanificacionComplementaria de la geodatabase", ancho_texto=0.30,
                                    subtitulos=["Segundo nivel", "Tercer nivel"])
    s2 = G("sget_splc_instrum_segundonivel")
    s3 = G("sget_splc_instrum_tercer_nivel")
    c2 = [("Macroproyecto - MP", "#e41a1c", "Macroproyectos"), ("Plan Urbano Integral del Ámbito Ladera - PUIAL", "#377eb8", "Plan urbano integral de ladera"),
          ("Plan Rural Integral - PRI", "#4daf4a", "Plan rural integral"), ("Distrito Rural Campesino - DRC", "#984ea3", "Distrito rural campesino")]
    for k, c, _ in c2:
        poly(a1, s2[s2["instrument"] == k], c, lw=0.5, alpha=0.65, z=3)
    c3 = [("Plan Maestro - PM", "#1f78b4", "Planes maestros"), ("Plan parcial - PP", "#e31a1c", "Planes parciales"),
          ("Plan de legalización, regularización y mejoramiento del hábitat - PLRMH", "#ff7f00", "Legalización, regularización y mejoramiento (PLRMH)"),
          ("Unidad de Planificación Rural - UPR", "#33a02c", "Unidades de planificación rural"), ("Plan Especial de Manejo y Protección del Patrimonio - PEMP", "#6a3d9a", "Planes especiales de patrimonio (PEMP)")]
    for k, c, _ in c3:
        poly(a2, s3[s3["instrument"] == k], c, lw=0.4, alpha=0.75, z=3)
    cierre_ax(a1, st, n=2)
    cierre_ax(a2, st, norte=False, n=2, rotulos=False)
    P = Panel(axp)
    P.capa("sget_splc_instrum_segundonivel", "Instrumentos de segundo nivel")
    for k, c, lab in c2:
        P.fila_sw("poly", c, lab, f"{int((s2['instrument'] == k).sum())}")
    P.espacio()
    P.capa("sget_splc_instrum_tercer_nivel", "Instrumentos de tercer nivel")
    for k, c, lab in c3:
        P.fila_sw("poly", c, lab, f"{int((s3['instrument'] == k).sum())}")
    P.lecturas([f"{int((s3['estado'] == 'Sin Formular').sum())} de {len(s3)} instrumentos de tercer nivel están sin formular; {int((s3['estado'] == 'Adoptado').sum())} están adoptados.",
                f"En segundo nivel, {int((s2['estado'] == 'Sin Formular').sum())} de {len(s2)} están sin formular.",
                "Cada instrumento trae su acto administrativo, su fecha y su vigencia."], ancho=52)
    return guarda(fig, "22_instrumentos_planificacion.png")


# ================================================================ f. FINANCIACIÓN
@mapa("23", "23_financiacion")
def m23():
    fig, (a1, a2), axp, st = lienzo(2, "Subsistema de financiación: zonas generadoras y receptoras", "Grupo f_SubsistemaFinanciacion de la geodatabase", ancho_texto=0.30,
                                    subtitulos=["Zonas generadoras de derechos adicionales", "Zonas receptoras"])
    zg = G("u_sget_zonasgeneradoras")
    dot = G("u_so_zona_receptora_dot")
    tt = G("u_so_zona_receptora_ttmto")
    cz = [("Red de conectividad ecológica neta en suelo urbano", "#1b9e77", "Red de conectividad ecológica neta"), ("Zonas de Interés Ambiental y Espacio Público", "#7570b3", "Interés ambiental y espacio público"),
          ("Zonas de Interés Patrimonial", "#d95f02", "Interés patrimonial")]
    for k, c, _ in cz:
        poly(a1, zg[zg["tipo"] == k], c, lw=0.4, z=3)
    poly(a2, dot[dot["tipo"] == "Tipo 1"], "#e41a1c", lw=0.3, alpha=0.8, z=4)
    poly(a2, dot[dot["tipo"] != "Tipo 1"], "#ff7f00", lw=0.3, alpha=0.9, z=5)
    poly(a2, tt, "#377eb8", lw=0.3, alpha=0.55, z=3)
    cierre_ax(a1, st, n=2)
    cierre_ax(a2, st, norte=False, n=2, rotulos=False)
    P = Panel(axp)
    P.capa("u_sget_zonasgeneradoras", "Zonas generadoras")
    for k, c, lab in cz:
        P.fila_sw("poly", c, lab, f"{int((zg['tipo'] == k).sum())}")
    P.espacio()
    P.capa("u_so_zona_receptora_dot", "Zonas receptoras DOT")
    P.fila_sw("poly", "#e41a1c", "DOT tipo 1", f"{int((dot['tipo'] == 'Tipo 1').sum())}")
    P.fila_sw("poly", "#ff7f00", "DOT tipo 2", f"{int((dot['tipo'] != 'Tipo 1').sum())}")
    P.capa("u_so_zona_receptora_ttmto", "Zonas receptoras por tratamiento")
    P.fila_sw("poly", "#377eb8", "Receptora de derechos adicionales", f"{len(tt)}")
    P.lecturas([f"Las zonas receptoras DOT se concentran junto a las estaciones: {int((dot['estado'] == 'Existente').sum())} existentes, {int((dot['estado'] == 'En construcción').sum())} en construcción y {int((dot['estado'] == 'Proyectada').sum())} proyectadas.",
                "Origen propuesto: zonas receptoras, revisión 2025–2026; zonas generadoras, mixto (Acuerdo 48 más elementos nuevos)."], ancho=52)
    return guarda(fig, "23_financiacion.png")


if __name__ == "__main__":
    for num, nombre, f in MAPAS:
        if ONLY and num not in ONLY:
            continue
        try:
            f()
        except Exception as e:
            import traceback
            print("ERROR", num, nombre, repr(e)[:300], flush=True)
            traceback.print_exc()
    print("FIN")
