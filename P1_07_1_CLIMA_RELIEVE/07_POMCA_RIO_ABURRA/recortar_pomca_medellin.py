from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(BASE / ".matplotlib"))

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter
from osgeo import gdal
from PIL import Image


SOURCE = BASE / "capas_climaticas_renderizadas"
OUTPUT = BASE / "recortes_medellin"
PUBLICATION = OUTPUT / "publicacion_carta"
GPKG = BASE.parent / "03_DATOS_PREPARADOS" / "20260910" / "limites_medellin_9377.gpkg"
LEGEND_JSON = SOURCE / "leyenda_servicio.json"

LAYERS = {
    22: {
        "slug": "evapotranspiracion",
        "title": "Evapotranspiración anual",
        "units": "mm/año",
        "palette": "GnBu",
        "palette_min": 0.38,
    },
    23: {
        "slug": "temperatura",
        "title": "Temperatura media",
        "units": "°C",
    },
    24: {
        "slug": "precipitacion",
        "title": "Precipitación media anual",
        "units": "mm/año",
        "palette": "Blues",
        "palette_min": 0.38,
    },
}


def warp_to_medellin(layer_id: int, slug: str) -> Path:
    source = SOURCE / f"{layer_id}_{slug}_pomca_render.png"
    target = OUTPUT / f"{layer_id}_{slug}_medellin_render.tif"
    options = gdal.WarpOptions(
        format="GTiff",
        srcSRS="EPSG:21897",
        dstSRS="EPSG:9377",
        cutlineDSName=str(GPKG),
        cutlineLayer="limite_medellin",
        cropToCutline=True,
        dstAlpha=True,
        resampleAlg="near",
        creationOptions=["COMPRESS=DEFLATE", "TILED=YES"],
    )
    result = gdal.Warp(str(target), str(source), options=options)
    if result is None:
        raise RuntimeError(f"No fue posible recortar {source.name}")
    result = None
    return target


def read_rgba(path: Path):
    dataset = gdal.Open(str(path))
    data = np.moveaxis(dataset.ReadAsArray(), 0, -1).astype(np.uint8)
    transform = dataset.GetGeoTransform()
    xmin = transform[0]
    ymax = transform[3]
    xmax = xmin + dataset.RasterXSize * transform[1]
    ymin = ymax + dataset.RasterYSize * transform[5]
    # El servicio entrega colores semitransparentes. Se hacen opacos dentro
    # del polígono para que coincidan visualmente con la paleta publicada.
    data[..., 3] = np.where(data[..., 3] > 0, 255, 0).astype(np.uint8)
    return data, (xmin, xmax, ymin, ymax)


def legend_entries():
    payload = json.loads(LEGEND_JSON.read_text(encoding="utf-8"))
    entries = {}
    for layer in payload["layers"]:
        layer_id = layer.get("layerId")
        if layer_id not in LAYERS:
            continue
        items = []
        for item in layer["legend"]:
            symbol = Image.open(io.BytesIO(base64.b64decode(item["imageData"]))).convert("RGBA")
            r, g, b, _ = symbol.getpixel((symbol.width // 2, symbol.height // 2))
            items.append((item["label"], (r / 255, g / 255, b / 255)))
        entries[layer_id] = items
    return entries


def apply_requested_palettes(original_legends):
    """Construye paletas truncadas y conserva la escala térmica original."""
    styled = {}
    for layer_id, items in original_legends.items():
        palette_name = LAYERS[layer_id].get("palette")
        if palette_name is None:
            styled[layer_id] = items
            continue
        positions = np.linspace(LAYERS[layer_id]["palette_min"], 0.95, len(items))
        colors = colormaps[palette_name](positions)[:, :3]
        styled[layer_id] = [(item[0], tuple(color)) for item, color in zip(items, colors)]
    return styled


def classify_pixels(rgba, layer_id, original_legends):
    """Asigna cada píxel visible a la clase publicada más cercana."""
    old_colors = np.rint(
        np.asarray([color for _, color in original_legends[layer_id]]) * 255
    ).astype(np.int32)
    pixels = rgba[..., :3].astype(np.int32)
    distances = np.sum((pixels[..., None, :] - old_colors[None, None, :, :]) ** 2, axis=3)
    nearest_class = np.argmin(distances, axis=2)
    valid = rgba[..., 3] > 0
    return nearest_class, valid


def recolor_classes(rgba, layer_id, original_legends, styled_legends):
    """Sustituye colores y devuelve las clases realmente presentes en Medellín."""
    nearest_class, valid = classify_pixels(rgba, layer_id, original_legends)
    present = sorted(np.unique(nearest_class[valid]).tolist())
    if LAYERS[layer_id].get("palette") is None:
        return rgba, present
    recolored = rgba.copy()
    new_colors = np.rint(
        np.asarray([color for _, color in styled_legends[layer_id]]) * 255
    ).astype(np.uint8)
    recolored[valid, :3] = new_colors[nearest_class[valid]]
    return recolored, present


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
        "N",
        xy=(0.955, 0.94),
        xytext=(0.955, 0.84),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=11,
        arrowprops={"arrowstyle": "->", "lw": 1.3, "color": "black"},
    )

    scale_m = 5000
    start_x = (xmin + xmax) / 2 - scale_m / 2
    start_y = ymin + (ymax - ymin) * 0.045
    ax.plot([start_x, start_x + scale_m], [start_y, start_y], color="black", lw=2.4)
    ax.text(start_x + scale_m / 2, start_y + (ymax - ymin) * 0.016, "5 km", ha="center", fontsize=9)


def add_map(ax, rgba, extent, divisions, boundary, layer_id, legends, legend=True):
    ax.imshow(rgba, extent=extent, origin="upper", interpolation="nearest")
    divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.9, zorder=3)
    boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.8, zorder=4)
    decorate_axis(ax, extent)
    ax.set_title(
        f"{LAYERS[layer_id]['title']}\nRecorte municipal con barrios y veredas",
        fontsize=15,
        pad=11,
    )
    if legend:
        handles = [Patch(facecolor=color, edgecolor="#555", linewidth=0.35, label=label)
                   for label, color in legends[layer_id]]
        handles.extend([
            plt.Line2D([0], [0], color="#252525", lw=0.7, label="Barrios y veredas"),
            plt.Line2D([0], [0], color="#bd1f36", lw=2, label="Límite municipal"),
        ])
        ax.legend(
            handles=handles,
            title=f"Intervalos ({LAYERS[layer_id]['units']})",
            loc="upper center",
            bbox_to_anchor=(0.67, 0.985),
            ncol=2,
            fontsize=8.3,
            title_fontsize=9,
            framealpha=0.94,
            borderpad=0.55,
            labelspacing=0.35,
            columnspacing=0.9,
            handletextpad=0.55,
        )


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    PUBLICATION.mkdir(parents=True, exist_ok=True)
    original_legends = legend_entries()
    legends = apply_requested_palettes(original_legends)
    divisions = gpd.read_file(GPKG, layer="barrios_veredas").to_crs(9377)
    boundary = gpd.read_file(GPKG, layer="limite_medellin").to_crs(9377)

    prepared = {}
    for layer_id, meta in LAYERS.items():
        raster_path = warp_to_medellin(layer_id, meta["slug"])
        rgba, extent = read_rgba(raster_path)
        rgba, present = recolor_classes(rgba, layer_id, original_legends, legends)
        map_legends = dict(legends)
        map_legends[layer_id] = [legends[layer_id][index] for index in present]
        prepared[layer_id] = (rgba, extent)

        fig, ax = plt.subplots(figsize=(11, 9))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.88)
        add_map(ax, rgba, extent, divisions, boundary, layer_id, map_legends)
        fig.text(
            0.5,
            0.025,
            "Fuente: POMCA río Aburrá — Área Metropolitana del Valle de Aburrá. "
            "Imagen temática clasificada; no contiene valores ráster continuos.",
            ha="center",
            fontsize=8.5,
            color="#444444",
        )
        fig.savefig(OUTPUT / f"{layer_id}_{meta['slug']}_medellin_barrios.png", dpi=180, facecolor="white")
        plt.close(fig)
        print(OUTPUT / f"{layer_id}_{meta['slug']}_medellin_barrios.png")

        # Versión dimensionada para insertarse al ancho útil de una página
        # carta vertical (7,2 × 6,6 pulgadas), sin reescalado agresivo en Word.
        fig, ax = plt.subplots(figsize=(7.2, 6.6))
        fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)
        add_map(ax, rgba, extent, divisions, boundary, layer_id, map_legends)
        fig.text(
            0.5,
            0.012,
            "Fuente: POMCA río Aburrá — Área Metropolitana del Valle de Aburrá. "
            "Imagen temática clasificada.",
            ha="center",
            fontsize=7.3,
            color="#444444",
        )
        publication_base = PUBLICATION / f"{layer_id}_{meta['slug']}_medellin_carta"
        fig.savefig(publication_base.with_suffix(".png"), dpi=300, facecolor="white")
        fig.savefig(publication_base.with_suffix(".pdf"), facecolor="white")
        plt.close(fig)
        print(publication_base.with_suffix(".png"))
        print(publication_base.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
