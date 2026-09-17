"""Versión POMCA de temperatura con la paleta RdYlBu_r de CHELSA.

Usa el recorte ya preparado; no modifica ni sobrescribe figuras anteriores.
"""
from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(BASE / ".matplotlib"))

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib import colormaps
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter
from PIL import Image

SOURCE = BASE / "capas_climaticas_renderizadas"
OUTPUT = BASE / "recortes_medellin"
PUBLICATION = OUTPUT / "publicacion_carta"
GPKG = BASE.parent / "03_DATOS_PREPARADOS" / "20260910" / "limites_medellin_9377.gpkg"
LEGEND_JSON = SOURCE / "leyenda_servicio.json"
RASTER = OUTPUT / "23_temperatura_medellin_render.tif"


def legend_entries():
    payload = json.loads(LEGEND_JSON.read_text(encoding="utf-8"))
    for layer in payload["layers"]:
        if layer.get("layerId") != 23:
            continue
        items = []
        for item in layer["legend"]:
            symbol = Image.open(io.BytesIO(base64.b64decode(item["imageData"]))).convert("RGBA")
            r, g, b, _ = symbol.getpixel((symbol.width // 2, symbol.height // 2))
            items.append((item["label"], (r / 255, g / 255, b / 255)))
        return items
    raise RuntimeError("No se encontró la leyenda de temperatura (capa 23).")


def read_rgba():
    with rasterio.open(RASTER) as src:
        data = np.moveaxis(src.read(), 0, -1).astype(np.uint8)
        bounds = src.bounds
    data[..., 3] = np.where(data[..., 3] > 0, 255, 0).astype(np.uint8)
    return data, (bounds.left, bounds.right, bounds.bottom, bounds.top)


def recolor(rgba, original):
    old_colors = np.rint(np.asarray([color for _, color in original]) * 255).astype(np.int32)
    pixels = rgba[..., :3].astype(np.int32)
    distances = np.sum((pixels[..., None, :] - old_colors[None, None, :, :]) ** 2, axis=3)
    nearest = np.argmin(distances, axis=2)
    valid = rgba[..., 3] > 0
    present = sorted(np.unique(nearest[valid]).tolist())
    colors = colormaps["RdYlBu_r"](np.linspace(0.0, 1.0, len(original)))[:, :3]
    styled = [(item[0], tuple(color)) for item, color in zip(original, colors)]
    new_colors = np.rint(np.asarray([color for _, color in styled]) * 255).astype(np.uint8)
    result = rgba.copy()
    result[valid, :3] = new_colors[nearest[valid]]
    return result, [styled[index] for index in present]


def decorate_axis(ax, extent):
    xmin, xmax, ymin, ymax = extent
    ax.set_aspect("equal")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("Este (m) — MAGNA-SIRGAS / Origen Nacional")
    ax.set_ylabel("Norte (m)")
    ax.grid(color="#9ca3af", linewidth=0.45, alpha=0.35)
    ax.set_axisbelow(True)
    formatter = ScalarFormatter(useOffset=False)
    formatter.set_scientific(False)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.tick_params(axis="x", rotation=25)
    ax.annotate(
        "N", xy=(0.955, 0.94), xytext=(0.955, 0.84), xycoords="axes fraction",
        ha="center", va="center", fontsize=11,
        arrowprops={"arrowstyle": "->", "lw": 1.3, "color": "black"},
    )
    scale_m = 5000
    start_x = (xmin + xmax) / 2 - scale_m / 2
    start_y = ymin + (ymax - ymin) * 0.045
    ax.plot([start_x, start_x + scale_m], [start_y, start_y], color="black", lw=2.4)
    ax.text(start_x + scale_m / 2, start_y + (ymax - ymin) * 0.016, "5 km", ha="center", fontsize=9)


def main():
    original = legend_entries()
    rgba, extent = read_rgba()
    rgba, legend = recolor(rgba, original)
    divisions = gpd.read_file(GPKG, layer="barrios_veredas").to_crs(9377)
    boundary = gpd.read_file(GPKG, layer="limite_medellin").to_crs(9377)

    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)
    ax.imshow(rgba, extent=extent, origin="upper", interpolation="nearest")
    divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.9, zorder=3)
    boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.8, zorder=4)
    decorate_axis(ax, extent)
    ax.set_title("Temperatura media\nRecorte municipal con barrios y veredas", fontsize=15, pad=11)

    handles = [
        Patch(facecolor=color, edgecolor="#555", linewidth=0.35, label=label)
        for label, color in legend
    ]
    handles.extend([
        plt.Line2D([0], [0], color="#252525", lw=0.7, label="Barrios y veredas"),
        plt.Line2D([0], [0], color="#bd1f36", lw=2, label="Límite municipal"),
    ])
    ax.legend(
        handles=handles, title="Intervalos (°C)", loc="upper center",
        bbox_to_anchor=(0.67, 0.985), ncol=2, fontsize=8.3, title_fontsize=9,
        framealpha=0.94, borderpad=0.55, labelspacing=0.35,
        columnspacing=0.9, handletextpad=0.55,
    )
    fig.text(
        0.5, 0.012,
        "Fuente: POMCA río Aburrá — Área Metropolitana del Valle de Aburrá. "
        "Imagen temática clasificada.",
        ha="center", fontsize=7.3, color="#444444",
    )
    PUBLICATION.mkdir(parents=True, exist_ok=True)
    out = PUBLICATION / "23_temperatura_medellin_carta_paleta_CHELSA"
    fig.savefig(out.with_suffix(".png"), dpi=300, facecolor="white")
    fig.savefig(out.with_suffix(".pdf"), facecolor="white")
    plt.close(fig)
    print(out.with_suffix(".png"))
    print(out.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
