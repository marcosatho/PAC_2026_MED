from __future__ import annotations

import argparse
import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from matplotlib.patches import Patch
from matplotlib.patches import PathPatch
from matplotlib.ticker import ScalarFormatter
from rasterio.mask import mask


CLASSES = {
    1: ("Af", "Tropical lluvioso", "#2166ac"),
    2: ("Am", "Tropical monzónico", "#67a9cf"),
    15: ("Cfb", "Templado, sin estación seca\ny verano templado", "#80c5cf"),
}


def geometry_clip_patch(geometry, ax) -> PathPatch:
    """Convierte un polígono o multipolígono en una máscara vectorial exacta."""
    polygons = list(geometry.geoms) if geometry.geom_type == "MultiPolygon" else [geometry]
    vertices: list[tuple[float, float]] = []
    codes: list[int] = []

    for polygon in polygons:
        for ring in [polygon.exterior, *polygon.interiors]:
            coordinates = list(ring.coords)
            vertices.extend(coordinates)
            codes.extend(
                [MplPath.MOVETO]
                + [MplPath.LINETO] * (len(coordinates) - 2)
                + [MplPath.CLOSEPOLY]
            )

    return PathPatch(
        MplPath(vertices, codes),
        transform=ax.transData,
        facecolor="none",
        edgecolor="none",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publica el mapa Köppen-Geiger de Medellín en formato carta."
    )
    parser.add_argument(
        "root",
        type=Path,
        help="Carpeta 07_1_CLIMA_RELIEVE del proyecto.",
    )
    return parser.parse_args()


def decorate_axis(ax, extent: tuple[float, float, float, float]) -> None:
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

    scale_m = 5_000
    start_x = (xmin + xmax) / 2 - scale_m / 2
    start_y = ymin + (ymax - ymin) * 0.045
    ax.plot(
        [start_x, start_x + scale_m],
        [start_y, start_y],
        color="black",
        lw=2.4,
        zorder=8,
    )
    ax.text(
        start_x + scale_m / 2,
        start_y + (ymax - ymin) * 0.016,
        "5 km",
        ha="center",
        fontsize=9,
        zorder=8,
    )


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    os.environ.setdefault("MPLCONFIGDIR", str(root / ".matplotlib"))

    snapshot = "20260910"
    gpkg = root / "03_DATOS_PREPARADOS" / snapshot / "limites_medellin_9377.gpkg"
    raster_path = (
        root
        / "03_DATOS_PREPARADOS"
        / snapshot
        / "koppen_geiger_1991_2020_medellin_9377.tif"
    )
    output = root / "04_PREVISUALIZACIONES" / "publicacion_carta"
    output.mkdir(parents=True, exist_ok=True)

    boundary = gpd.read_file(gpkg, layer="limite_medellin").to_crs(9377)
    divisions = gpd.read_file(gpkg, layer="barrios_veredas").to_crs(9377)
    divisions = gpd.clip(divisions, boundary)

    with rasterio.open(raster_path) as src:
        shapes = [geom.__geo_interface__ for geom in boundary.geometry]
        clipped, transform = mask(
            src,
            shapes,
            crop=True,
            all_touched=True,
            nodata=0,
            filled=True,
        )

    data = clipped[0]
    present = sorted(int(v) for v in np.unique(data) if int(v) in CLASSES)
    if not present:
        raise ValueError("El recorte no contiene las clases Köppen esperadas.")

    plot_data = np.full(data.shape, np.nan, dtype="float32")
    for index, code in enumerate(present):
        plot_data[data == code] = index

    colors = [CLASSES[code][2] for code in present]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(np.arange(-0.5, len(present) + 0.5, 1), cmap.N)

    xmin = transform.c
    ymax = transform.f
    xmax = xmin + data.shape[1] * transform.a
    ymin = ymax + data.shape[0] * transform.e
    extent = (xmin, xmax, ymin, ymax)

    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)

    raster_artist = ax.imshow(
        np.ma.masked_invalid(plot_data),
        extent=extent,
        origin="upper",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
        zorder=1,
    )

    # Se conservan las clases y los píxeles originales, pero su representación
    # se corta exactamente por el límite municipal. No hay interpolación ni
    # reasignación de valores en los bordes.
    municipal_geometry = boundary.geometry.union_all()
    clip_patch = geometry_clip_patch(municipal_geometry, ax)
    ax.add_patch(clip_patch)
    raster_artist.set_clip_path(clip_patch)
    divisions.boundary.plot(
        ax=ax,
        color="#252525",
        linewidth=0.42,
        alpha=0.9,
        zorder=3,
    )
    boundary.boundary.plot(
        ax=ax,
        color="#bd1f36",
        linewidth=1.8,
        zorder=4,
    )

    decorate_axis(ax, extent)
    ax.set_title(
        "Clasificación climática Köppen-Geiger\n"
        "Periodo 1991–2020 · recorte municipal con barrios y veredas",
        fontsize=15,
        pad=11,
    )

    handles = [
        Patch(
            facecolor=CLASSES[code][2],
            edgecolor="#555555",
            linewidth=0.35,
            label=f"{CLASSES[code][0]}: {CLASSES[code][1]}",
        )
        for code in present
    ]
    handles.extend(
        [
            Line2D([0], [0], color="#252525", lw=0.7, label="Barrios y veredas"),
            Line2D([0], [0], color="#bd1f36", lw=2, label="Límite municipal"),
        ]
    )
    ax.legend(
        handles=handles,
        title="Clases climáticas y límites",
        loc="upper center",
        bbox_to_anchor=(0.67, 0.985),
        ncol=1,
        fontsize=7.6,
        title_fontsize=8.6,
        framealpha=0.94,
        borderpad=0.55,
        labelspacing=0.32,
        handletextpad=0.55,
    )

    fig.text(
        0.5,
        0.012,
        "Fuente climática: Beck et al. (2023). Límites: Alcaldía de Medellín. "
        "Resolución aproximada de 1 km; no representa microclimas intraurbanos.",
        ha="center",
        fontsize=7.1,
        color="#444444",
    )

    base = output / "Koppen_Geiger_1991_2020_Medellin_carta"
    fig.savefig(base.with_suffix(".png"), dpi=300, facecolor="white")
    fig.savefig(base.with_suffix(".pdf"), facecolor="white")
    plt.close(fig)

    print(base.with_suffix(".png"))
    print(base.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
