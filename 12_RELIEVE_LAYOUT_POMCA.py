"""Versiones editoriales del relieve con la composicion usada en mapas POMCA."""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import BoundaryNorm, LightSource, ListedColormap
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter


DRIVE_ROOT = Path(
    r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución"
    r"\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA"
    r"\P1_Caracterizacion_Socioeconomica_Ambiental"
    r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE"
)
PROCESS_ROOT = DRIVE_ROOT / "09_RELIEVE_DTM_LIDAR"
DATA_DIR = PROCESS_ROOT / "02_DATOS_PREPARADOS"
OUTPUT_DIR = PROCESS_ROOT / "04_FIGURAS" / "publicacion_carta"

LOCAL_LIMITS = Path(__file__).resolve().parent / "P1_07_1_CLIMA_RELIEVE" / "03_DATOS_PREPARADOS" / "20260910"
DRIVE_LIMITS = DRIVE_ROOT / "03_DATOS_PREPARADOS" / "20260910"
LIMITS_DIR = LOCAL_LIMITS if LOCAL_LIMITS.exists() else DRIVE_LIMITS

DTM = DATA_DIR / "DTM_Medellin_2021_10m_EPSG9377.tif"
SLOPE = DATA_DIR / "pendiente_Medellin_2021_10m_EPSG9377.tif"
MUNICIPAL_LIMIT = LIMITS_DIR / "limite_medellin_4326.geojson"
POLITICAL_LIMITS = LIMITS_DIR / "comunas_corregimientos_4326.geojson"


def read_raster(path: Path):
    with rasterio.open(path) as src:
        values = src.read(1).astype("float32")
        values[values == src.nodata] = np.nan
        bounds = src.bounds
        transform = src.transform
    extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)
    return values, extent, transform


def interval_label(low: float, high: float, unit: str = "") -> str:
    suffix = f" {unit}" if unit else ""
    return f"{low:,.0f} – {high:,.0f}{suffix}".replace(",", ".")


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
    scale_m = 5_000
    start_x = (xmin + xmax) / 2 - scale_m / 2
    start_y = ymin + (ymax - ymin) * 0.045
    ax.plot([start_x, start_x + scale_m], [start_y, start_y], color="black", lw=2.4, zorder=10)
    ax.text(
        start_x + scale_m / 2,
        start_y + (ymax - ymin) * 0.016,
        "5 km",
        ha="center",
        fontsize=9,
        zorder=10,
    )


def add_legend(ax, interval_handles, title):
    handles = list(interval_handles)
    handles.extend(
        [
            plt.Line2D([0], [0], color="#252525", lw=0.7, label="Comunas y corregimientos"),
            plt.Line2D([0], [0], color="#bd1f36", lw=2, label="Límite municipal"),
        ]
    )
    ax.legend(
        handles=handles,
        title=title,
        loc="upper center",
        bbox_to_anchor=(0.61, 0.985),
        ncol=2,
        fontsize=7.7,
        title_fontsize=8.6,
        framealpha=0.94,
        borderpad=0.55,
        labelspacing=0.35,
        columnspacing=0.9,
        handletextpad=0.55,
    )


def save_figure(fig, basename: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    png = OUTPUT_DIR / f"{basename}.png"
    pdf = OUTPUT_DIR / f"{basename}.pdf"
    fig.savefig(png, dpi=300, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(png)
    print(pdf)


def elevation_map(elevation, extent, transform, divisions, boundary):
    breaks = np.arange(1_100, 3_351, 250, dtype=float)
    colors = plt.get_cmap("terrain")(np.linspace(0.08, 0.95, len(breaks) - 1))
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(breaks, cmap.N)
    valid = elevation[np.isfinite(elevation)]
    filled = np.where(np.isfinite(elevation), elevation, np.nanmedian(valid))
    shade = LightSource(azdeg=315, altdeg=40).hillshade(filled, vert_exag=1.2, dx=10, dy=10)
    shade = np.ma.array(shade, mask=~np.isfinite(elevation))

    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)
    ax.imshow(np.ma.masked_invalid(elevation), extent=extent, origin="upper", cmap=cmap, norm=norm)
    ax.imshow(shade, extent=extent, origin="upper", cmap="gray", alpha=0.25)

    left, right, bottom, top = extent
    xs = np.linspace(left + 5, right - 5, elevation.shape[1])
    ys = np.linspace(top - 5, bottom + 5, elevation.shape[0])
    levels = np.arange(1_200, 3_201, 200)
    contours = ax.contour(xs, ys, np.ma.masked_invalid(elevation), levels=levels,
                          colors="#303030", linewidths=0.35, alpha=0.62)
    ax.clabel(contours, levels[::2], inline=True, fontsize=5.7, fmt="%d m")

    divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.88, zorder=4)
    boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.8, zorder=5)
    decorate_axis(ax, extent)
    ax.set_title("Elevación del terreno\nDTM LiDAR 2021", fontsize=14.2, pad=9)

    present = []
    for i in range(len(breaks) - 1):
        if np.any((valid >= breaks[i]) & (valid < breaks[i + 1])):
            present.append(Patch(facecolor=colors[i], edgecolor="#555", linewidth=0.35,
                                 label=interval_label(breaks[i], breaks[i + 1] - 1)))
    add_legend(ax, present, "Intervalos (m s. n. m.)")
    fig.text(
        0.5, 0.012,
        "Fuente: Alcaldía de Medellín — DTM-LiDAR 2021, 1 m (AeroEstudios). Elaboración propia.",
        ha="center", fontsize=7.3, color="#444444",
    )
    save_figure(fig, "elevacion_medellin_DTM_2021_carta_v2")


def slope_map(slope, extent, divisions, boundary):
    breaks = np.array([0, 5, 15, 30, 45, 90], dtype=float)
    labels = ["0 – 5°", "5 – 15°", "15 – 30°", "30 – 45°", "> 45°"]
    colors = plt.get_cmap("YlOrBr")(np.linspace(0.10, 0.92, len(labels)))
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(breaks, cmap.N)
    valid = slope[np.isfinite(slope)]

    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.17, top=0.87)
    ax.imshow(np.ma.masked_invalid(slope), extent=extent, origin="upper", cmap=cmap,
              norm=norm, interpolation="nearest")
    divisions.boundary.plot(ax=ax, color="#252525", linewidth=0.42, alpha=0.88, zorder=3)
    boundary.boundary.plot(ax=ax, color="#bd1f36", linewidth=1.8, zorder=4)
    decorate_axis(ax, extent)
    ax.set_title("Pendiente del terreno\nDTM LiDAR 2021", fontsize=14.2, pad=9)

    present = []
    for i, label in enumerate(labels):
        if np.any((valid >= breaks[i]) & (valid < breaks[i + 1])):
            present.append(Patch(facecolor=colors[i], edgecolor="#555", linewidth=0.35, label=label))
    add_legend(ax, present, "Intervalos (grados)")
    fig.text(
        0.5, 0.012,
        "Fuente: Alcaldía de Medellín — DTM-LiDAR 2021, 1 m (AeroEstudios). Elaboración propia.",
        ha="center", fontsize=7.3, color="#444444",
    )
    save_figure(fig, "pendiente_medellin_DTM_2021_carta_v2")


def main():
    elevation, elevation_extent, elevation_transform = read_raster(DTM)
    slope, slope_extent, _ = read_raster(SLOPE)
    divisions = gpd.read_file(POLITICAL_LIMITS).to_crs(9377)
    boundary = gpd.read_file(MUNICIPAL_LIMIT).to_crs(9377)
    elevation_map(elevation, elevation_extent, elevation_transform, divisions, boundary)
    slope_map(slope, slope_extent, divisions, boundary)


if __name__ == "__main__":
    main()
