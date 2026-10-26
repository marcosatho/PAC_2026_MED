# -*- coding: utf-8 -*-
"""Corre un script de mapas sin modificarlo y pasa los ejes de coordenadas planas de metros a kilómetros.

Uso:  python corre_en_km.py <script.py> [argumentos del script ...]
Entorno: KM_OUT = carpeta donde se guardan las figuras (se les agrega el sufijo _km); nada se escribe en la carpeta original.

Qué hace: al guardar cada figura (Figure.savefig) busca los ejes cuyos límites caen en las coordenadas de Medellín (MAGNA-SIRGAS / Origen
Nacional: Este ≈ 4.700.000 m, Norte ≈ 2.250.000 m), les pone marcas cada 5 km (10 km si el panel es angosto), rótulos en km sin rotar y cambia
«(m)» por «(km)» en los títulos de los ejes. La geometría no cambia."""
import os, sys, runpy
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MultipleLocator

SALIDA = os.environ["KM_OUT"]
os.makedirs(SALIDA, exist_ok=True)
_original = Figure.savefig
_formato = FuncFormatter(lambda v, _: f"{v / 1000:.0f}")


def a_km(fig):
    for ax in fig.axes:
        try:
            x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
        except Exception:
            continue
        if not (4.0e6 < min(x0, x1) < 5.0e6 and 2.0e6 < min(y0, y1) < 2.6e6):
            continue
        ancho_in = ax.get_position().width * fig.get_figwidth()
        paso = 5000 if ancho_in >= 3.6 else 10000
        for eje in (ax.xaxis, ax.yaxis):
            eje.set_major_locator(MultipleLocator(paso))
            eje.set_major_formatter(_formato)
        ax.tick_params(axis="both", rotation=0)
        for rotulo in (ax.xaxis.label, ax.yaxis.label):
            t = rotulo.get_text()
            if "(m)" in t:
                rotulo.set_text(t.replace("(m)", "(km)"))
        alinea_regla(ax)


def alinea_regla(ax):
    """Mueve la regla de 5 km (y su rótulo «5 km») para que empiece en una marca de 5 km (p. ej. 4710) y termine en la siguiente (4715)."""
    for linea in ax.lines:
        xd, yd = linea.get_xdata(), linea.get_ydata()
        if len(xd) == 2 and abs(abs(xd[1] - xd[0]) - 5000) < 1 and abs(yd[1] - yd[0]) < 1e-6:
            inicio = min(xd)
            dx = round(inicio / 5000) * 5000 - inicio
            linea.set_xdata([xd[0] + dx, xd[1] + dx])
            centro = inicio + 2500
            for t in ax.texts:
                if t.get_text().strip() == "5 km" and abs(t.get_position()[0] - centro) < 3000:
                    t.set_x(t.get_position()[0] + dx)


def savefig(self, fname, *args, **kwargs):
    if isinstance(fname, (str, os.PathLike)):
        a_km(self)
        base, ext = os.path.splitext(os.path.basename(str(fname)))
        fname = os.path.join(SALIDA, f"{base}_km{ext}")
        print("km ->", fname)
    return _original(self, fname, *args, **kwargs)


Figure.savefig = savefig
script = sys.argv[1]
sys.argv = [script] + sys.argv[2:]
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
runpy.run_path(script, run_name="__main__")
