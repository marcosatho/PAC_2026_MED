"""Prepara y visualiza el DTM LiDAR oficial de Medellin (2021).

El archivo fuente se conserva intacto. El script fuerza EPSG:6257, reproyecta
una copia de trabajo a EPSG:9377 con resolucion de 10 m, recorta al limite
municipal y genera una figura hipsometrica con sombreado y curvas de nivel.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import BoundaryNorm, LightSource
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.mask import mask
from rasterio.vrt import WarpedVRT
from rasterio.warp import calculate_default_transform


DRIVE_ROOT = Path(
    r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución"
    r"\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA"
    r"\P1_Caracterizacion_Socioeconomica_Ambiental"
    r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE"
)

PROCESS_ROOT = DRIVE_ROOT / "09_RELIEVE_DTM_LIDAR"
DRIVE_SOURCE_TIF = (
    PROCESS_ROOT
    / "01_DATOS_ORIGINALES"
    / "DTM_2021_1M"
    / "MDT1_05001_20210501_modelo completo origen Medellin.TIF"
)
LOCAL_SOURCE_TIF = Path(
    r"C:\Users\marco\Downloads\DTM_2021_1M_OPERATIVO"
    r"\MDT1_05001_20210501_modelo completo origen Medellin.TIF"
)
SOURCE_TIF = LOCAL_SOURCE_TIF if LOCAL_SOURCE_TIF.exists() else DRIVE_SOURCE_TIF

LOCAL_LIMITS_ROOT = Path(__file__).resolve().parent / "P1_07_1_CLIMA_RELIEVE" / "03_DATOS_PREPARADOS" / "20260910"
DRIVE_LIMITS_ROOT = DRIVE_ROOT / "03_DATOS_PREPARADOS" / "20260910"
LIMITS_ROOT = LOCAL_LIMITS_ROOT if LOCAL_LIMITS_ROOT.exists() else DRIVE_LIMITS_ROOT
MUNICIPAL_LIMIT = LIMITS_ROOT / "limite_medellin_4326.geojson"
POLITICAL_LIMITS = LIMITS_ROOT / "comunas_corregimientos_4326.geojson"

PREPARED_DIR = PROCESS_ROOT / "02_DATOS_PREPARADOS"
FIGURES_DIR = PROCESS_ROOT / "04_FIGURAS"
OUTPUT_TIF = PREPARED_DIR / "DTM_Medellin_2021_10m_EPSG9377.tif"
OUTPUT_FIGURE = FIGURES_DIR / "relieve_hipsometrico_medellin_DTM_2021.png"
SLOPE_TIF = PREPARED_DIR / "pendiente_Medellin_2021_10m_EPSG9377.tif"
SLOPE_FIGURE = FIGURES_DIR / "pendiente_medellin_DTM_2021.png"

SOURCE_CRS = CRS.from_epsg(6257)
TARGET_CRS = CRS.from_epsg(9377)
TARGET_RESOLUTION = 10.0


def add_scale_bar(ax: plt.Axes, length_m: float = 5_000) -> None:
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    x0 = xmin + 0.08 * (xmax - xmin)
    y0 = ymin + 0.055 * (ymax - ymin)
    ax.plot([x0, x0 + length_m], [y0, y0], color="black", lw=3, solid_capstyle="butt")
    ax.text(x0 + length_m / 2, y0 + 0.012 * (ymax - ymin), "5 km", ha="center", va="bottom", fontsize=9)


def add_north_arrow(ax: plt.Axes) -> None:
    ax.annotate(
        "N",
        xy=(0.94, 0.94),
        xytext=(0.94, 0.84),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=12,
        arrowprops={"arrowstyle": "->", "lw": 1.4, "color": "black"},
    )


def main() -> None:
    PREPARED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    municipality = gpd.read_file(MUNICIPAL_LIMIT).to_crs(TARGET_CRS)
    political = gpd.read_file(POLITICAL_LIMITS).to_crs(TARGET_CRS)
    shapes = [geom.__geo_interface__ for geom in municipality.geometry]

    with rasterio.open(SOURCE_TIF) as src:
        # El GeoTIFF declara un LOCAL_CS; los metadatos oficiales identifican
        # el sistema como MAGNA-SIRGAS / Medellin urban grid (EPSG:6257).
        target_transform, target_width, target_height = calculate_default_transform(
            SOURCE_CRS,
            TARGET_CRS,
            src.width,
            src.height,
            *src.bounds,
            resolution=TARGET_RESOLUTION,
        )
        with WarpedVRT(
            src,
            src_crs=SOURCE_CRS,
            crs=TARGET_CRS,
            transform=target_transform,
            width=target_width,
            height=target_height,
            resampling=Resampling.bilinear,
            nodata=-32767.0,
        ) as vrt:
            data, transform = mask(vrt, shapes, crop=True, filled=True, nodata=-32767.0)
            elevation = data[0].astype("float32")
            elevation[elevation == -32767.0] = np.nan

            profile = vrt.profile.copy()
            profile.update(
                driver="GTiff",
                width=elevation.shape[1],
                height=elevation.shape[0],
                transform=transform,
                count=1,
                dtype="float32",
                nodata=-32767.0,
                compress="DEFLATE",
                predictor=3,
                tiled=True,
                blockxsize=256,
                blockysize=256,
            )

    with rasterio.open(OUTPUT_TIF, "w", **profile) as dst:
        dst.write(np.where(np.isfinite(elevation), elevation, -32767.0), 1)
        dst.update_tags(
            source="Alcaldia de Medellin - DTM LiDAR 2021, 1 m",
            source_crs="EPSG:6257",
            processing="Reproyeccion bilinear a EPSG:9377, resolucion 10 m y recorte municipal",
        )

    grad_y, grad_x = np.gradient(elevation, TARGET_RESOLUTION, TARGET_RESOLUTION)
    slope = np.degrees(np.arctan(np.hypot(grad_x, grad_y))).astype("float32")
    slope[~np.isfinite(elevation)] = np.nan
    with rasterio.open(SLOPE_TIF, "w", **profile) as dst:
        dst.write(np.where(np.isfinite(slope), slope, -32767.0), 1)
        dst.update_tags(
            source="Pendiente derivada del DTM LiDAR Medellin 2021",
            units="degrees",
            processing="Gradiente 3x3 sobre DTM reproyectado a EPSG:9377, resolucion 10 m",
        )

    valid = elevation[np.isfinite(elevation)]
    vmin = float(np.floor(np.nanpercentile(valid, 1) / 100) * 100)
    vmax = float(np.ceil(np.nanpercentile(valid, 99) / 100) * 100)
    contour_min = int(np.ceil(np.nanmin(valid) / 100) * 100)
    contour_max = int(np.floor(np.nanmax(valid) / 100) * 100)
    contour_levels = np.arange(contour_min, contour_max + 1, 100)

    left = transform.c
    top = transform.f
    right = left + transform.a * elevation.shape[1]
    bottom = top + transform.e * elevation.shape[0]
    extent = [left, right, bottom, top]

    masked = np.ma.masked_invalid(elevation)
    filled = np.where(np.isfinite(elevation), elevation, np.nanmedian(valid))
    hillshade = LightSource(azdeg=315, altdeg=40).hillshade(
        filled,
        vert_exag=1.2,
        dx=TARGET_RESOLUTION,
        dy=TARGET_RESOLUTION,
    )
    hillshade = np.ma.array(hillshade, mask=~np.isfinite(elevation))

    fig, ax = plt.subplots(figsize=(8.1, 9.2), constrained_layout=False)
    image = ax.imshow(
        masked,
        extent=extent,
        origin="upper",
        cmap="terrain",
        vmin=vmin,
        vmax=vmax,
        interpolation="bilinear",
        zorder=1,
    )
    ax.imshow(
        hillshade,
        extent=extent,
        origin="upper",
        cmap="gray",
        alpha=0.30,
        interpolation="bilinear",
        zorder=2,
    )

    xs = np.linspace(left + TARGET_RESOLUTION / 2, right - TARGET_RESOLUTION / 2, elevation.shape[1])
    ys = np.linspace(top - TARGET_RESOLUTION / 2, bottom + TARGET_RESOLUTION / 2, elevation.shape[0])
    contours = ax.contour(
        xs,
        ys,
        masked,
        levels=contour_levels,
        colors="#303030",
        linewidths=0.35,
        alpha=0.60,
        zorder=3,
    )
    ax.clabel(contours, contour_levels[::2], inline=True, fontsize=6, fmt="%d m")

    political.boundary.plot(ax=ax, color="#202020", linewidth=0.45, alpha=0.75, zorder=4)
    municipality.boundary.plot(ax=ax, color="#c51b36", linewidth=1.7, zorder=5)

    minx, miny, maxx, maxy = municipality.total_bounds
    pad_x = (maxx - minx) * 0.025
    pad_y = (maxy - miny) * 0.025
    ax.set_xlim(minx - pad_x, maxx + pad_x)
    ax.set_ylim(miny - pad_y, maxy + pad_y)
    ax.set_aspect("equal")

    ax.set_title(
        "Relieve de Medellín\nModelo Digital del Terreno LiDAR 2021",
        fontsize=15,
        pad=16,
    )
    ax.set_xlabel("Este (m) — MAGNA-SIRGAS / Origen Nacional")
    ax.set_ylabel("Norte (m) — MAGNA-SIRGAS / Origen Nacional")
    ax.grid(color="#808080", linewidth=0.35, alpha=0.30)
    add_scale_bar(ax)
    add_north_arrow(ax)

    cax = inset_axes(ax, width="3.3%", height="38%", loc="upper right", borderpad=2.7)
    colorbar = fig.colorbar(image, cax=cax)
    colorbar.set_label("Elevación (m s. n. m.)", fontsize=9)
    colorbar.ax.tick_params(labelsize=8)

    fig.subplots_adjust(left=0.10, right=0.96, top=0.90, bottom=0.11)
    fig.text(
        0.5,
        0.035,
        "Fuente: Alcaldía de Medellín — DTM-LiDAR 2021, 1 m (AeroEstudios). "
        "Elaboración propia. Derivado cartográfico a 10 m.",
        ha="center",
        va="bottom",
        fontsize=8,
    )
    fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    slope_breaks = np.array([0, 5, 15, 30, 45, 90], dtype=float)
    slope_labels = ["0–5°", "5–15°", "15–30°", "30–45°", ">45°"]
    slope_cmap = plt.get_cmap("YlOrBr", len(slope_labels))
    slope_norm = BoundaryNorm(slope_breaks, slope_cmap.N)
    fig, ax = plt.subplots(figsize=(8.1, 9.2), constrained_layout=False)
    slope_img = ax.imshow(
        np.ma.masked_invalid(slope),
        extent=extent,
        origin="upper",
        cmap=slope_cmap,
        norm=slope_norm,
        interpolation="nearest",
        zorder=1,
    )
    ax.imshow(hillshade, extent=extent, origin="upper", cmap="gray", alpha=0.17, zorder=2)
    political.boundary.plot(ax=ax, color="#202020", linewidth=0.45, alpha=0.72, zorder=3)
    municipality.boundary.plot(ax=ax, color="#c51b36", linewidth=1.7, zorder=4)
    ax.set_xlim(minx - pad_x, maxx + pad_x)
    ax.set_ylim(miny - pad_y, maxy + pad_y)
    ax.set_aspect("equal")
    ax.set_title("Pendiente del terreno en Medellín\nDTM LiDAR 2021", fontsize=15, pad=16)
    ax.set_xlabel("Este (m) — MAGNA-SIRGAS / Origen Nacional")
    ax.set_ylabel("Norte (m) — MAGNA-SIRGAS / Origen Nacional")
    ax.grid(color="#808080", linewidth=0.35, alpha=0.30)
    add_scale_bar(ax)
    add_north_arrow(ax)
    cax = inset_axes(ax, width="3.3%", height="34%", loc="upper right", borderpad=2.7)
    colorbar = fig.colorbar(slope_img, cax=cax, ticks=(slope_breaks[:-1] + slope_breaks[1:]) / 2)
    colorbar.ax.set_yticklabels(slope_labels)
    colorbar.set_label("Pendiente (grados)", fontsize=9)
    colorbar.ax.tick_params(labelsize=8)
    fig.subplots_adjust(left=0.10, right=0.96, top=0.90, bottom=0.11)
    fig.text(
        0.5,
        0.035,
        "Fuente: Alcaldía de Medellín — DTM-LiDAR 2021, 1 m (AeroEstudios). "
        "Elaboración propia. Pendiente derivada a 10 m.",
        ha="center", va="bottom", fontsize=8,
    )
    fig.savefig(SLOPE_FIGURE, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"DTM preparado: {OUTPUT_TIF}")
    print(f"Figura: {OUTPUT_FIGURE}")
    print(f"Pendiente: {SLOPE_TIF}")
    print(f"Figura de pendiente: {SLOPE_FIGURE}")
    print(f"Elevacion municipal minima: {np.nanmin(valid):.2f} m")
    print(f"Elevacion municipal maxima: {np.nanmax(valid):.2f} m")
    print(f"Elevacion municipal media: {np.nanmean(valid):.2f} m")


if __name__ == "__main__":
    main()
