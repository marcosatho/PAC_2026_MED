"""Versión alternativa de composición gráfica ENSO-CHELSA.

Conserva el procesamiento de 07_ENSO_CHELSA_MAGNA_SIRGAS.py y cambia
únicamente la organización visual: una barra de color por variable,
encabezados por columna y fases en el margen izquierdo. No sobrescribe v1.
"""
from pathlib import Path
import io
import re
from urllib.request import urlopen

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.ticker import FuncFormatter
from scipy.ndimage import zoom, distance_transform_edt
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import array_bounds, from_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling


BASE = Path(__file__).resolve().parent
ROOT = BASE / "P1_07_1_CLIMA_RELIEVE" / "08_CHELSA"
DATA = ROOT / "02_DATOS"
OUT = ROOT / "04_PREVISUALIZACIONES"
OUT.mkdir(parents=True, exist_ok=True)

boundary = gpd.read_file(
    ROOT.parent / "03_DATOS_PREPARADOS" / "20260910" / "limite_medellin_4326.geojson"
).to_crs(9377)
divisions = gpd.read_file(
    ROOT.parent / "03_DATOS_PREPARADOS" / "20260910" / "comunas_corregimientos_4326.geojson"
).to_crs(9377)
divisions = gpd.clip(divisions, boundary)

# ONI CPC. Esta versión conserva la asignación temporal de la figura anterior
# para que el ejercicio compare solamente el diseño. La corrección del desfase
# mensual se hará en la siguiente versión metodológica.
oni_url = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
oni_file = BASE / "oni.ascii.txt"
if oni_file.exists():
    oni = pd.read_fwf(oni_file, skiprows=1, names=["season", "year", "total", "oni"])
else:
    with urlopen(oni_url, timeout=30) as response:
        oni = pd.read_fwf(io.BytesIO(response.read()), skiprows=1,
                          names=["season", "year", "total", "oni"])

oni = oni[(oni.year >= 1981) & (oni.year <= 2021)].copy()
center_month = {
    "DJF": 2, "JFM": 3, "FMA": 4, "MAM": 5, "AMJ": 6, "MJJ": 7,
    "JJA": 8, "JAS": 9, "ASO": 10, "SON": 11, "OND": 12, "NDJ": 1,
}
oni["month"] = oni.season.map(center_month)
oni["date"] = pd.to_datetime(dict(year=oni.year, month=oni.month, day=15))
oni["raw_phase"] = np.select(
    [oni.oni >= 0.5, oni.oni <= -0.5], ["El Niño", "La Niña"], default="Neutral"
)
oni["run"] = (oni.raw_phase != oni.raw_phase.shift()).cumsum()
run_size = oni.groupby("run").size()
oni["phase"] = np.where(oni.run.map(run_size) >= 5, oni.raw_phase, "Neutral")
phase_month = oni.set_index(oni.date.dt.to_period("M"))["phase"]


def files(variable):
    rows = []
    for file in sorted((DATA / variable).glob("*.tif")):
        match = re.search(r"_(\d{2})_(\d{4})_V", file.name)
        if match:
            rows.append((pd.Period(f"{match.group(2)}-{match.group(1)}", freq="M"), file))
    return dict(rows)


paths = {"pr": files("pr"), "tas": files("tas")}
periods = sorted(set(paths["pr"]) & set(paths["tas"]) & set(phase_month.index))
phases = ["El Niño", "Neutral", "La Niña"]

with rasterio.open(paths["pr"][periods[0]]) as src:
    transform, width, height = calculate_default_transform(
        src.crs, "EPSG:9377", src.width, src.height, *src.bounds, resolution=1000
    )
    src_transform = src.transform


def warp(array):
    array = np.where(array >= 65000, np.nan, array).astype("float32")
    out = np.full((height, width), np.nan, dtype="float32")
    reproject(
        array, out,
        src_transform=src_transform, src_crs="EPSG:4326",
        dst_transform=transform, dst_crs="EPSG:9377",
        resampling=Resampling.bilinear,
        src_nodata=np.nan, dst_nodata=np.nan,
    )
    return out


means = {variable: {phase: [] for phase in phases} for variable in ("pr", "tas")}
for period in periods:
    phase = phase_month.loc[period]
    for variable in ("pr", "tas"):
        with rasterio.open(paths[variable][period]) as src:
            array = src.read(1).astype("float32")
            array[array >= 65000] = np.nan
        if variable == "tas":
            array = array * 0.1 - 273.15
        means[variable][phase].append(array)

means = {
    variable: {
        phase: warp(np.nanmean(np.stack(arrays), axis=0))
        for phase, arrays in phase_arrays.items()
    }
    for variable, phase_arrays in means.items()
}


def fill_nearest(array):
    good = np.isfinite(array)
    if good.all():
        return array
    _, indices = distance_transform_edt(~good, return_indices=True)
    out = array.copy()
    out[~good] = array[tuple(indices[:, ~good])]
    return out


means = {
    variable: {phase: fill_nearest(array) for phase, array in phase_arrays.items()}
    for variable, phase_arrays in means.items()
}

municipal_mask = geometry_mask(
    boundary.geometry, transform=transform, out_shape=(height, width), invert=True
)


def interpolate_grid(array, factor=5):
    valid = np.isfinite(array).astype(float)
    values = np.nan_to_num(array, nan=0.0)
    numerator = zoom(values, factor, order=3)
    denominator = zoom(valid, factor, order=3)
    return np.divide(
        numerator, denominator,
        out=np.full_like(numerator, np.nan), where=denominator > 0.05,
    )


def municipality_clip_path(gdf):
    paths_out = []
    for geometry in gdf.geometry:
        polygons = list(geometry.geoms) if geometry.geom_type == "MultiPolygon" else [geometry]
        for polygon in polygons:
            for ring in [polygon.exterior, *polygon.interiors]:
                xy = np.asarray(ring.coords)
                codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(xy) - 2) + [MplPath.CLOSEPOLY]
                paths_out.append(MplPath(xy, codes))
    return MplPath.make_compound_path(*paths_out)


clip_path = municipality_clip_path(boundary)
limits = {
    variable: (
        np.nanmin(np.concatenate([array[municipal_mask] for array in phase_arrays.values()])),
        np.nanmax(np.concatenate([array[municipal_mask] for array in phase_arrays.values()])),
    )
    for variable, phase_arrays in means.items()
}

rbottom, rleft = None, None
rbounds = array_bounds(height, width, transform)
rleft, rbottom, rright, rtop = rbounds
extent = [rleft, rright, rbottom, rtop]
left, bottom, right, top = boundary.total_bounds

# ---------------------------------------------------------------------------
# Diseño v2: dos columnas, tres fases y una barra horizontal por variable.
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(10.5, 13.2), facecolor="white")
grid = fig.add_gridspec(
    5, 2,
    height_ratios=[1, 1, 1, 0.075, 0.05],
    left=0.105, right=0.985, top=0.885, bottom=0.085,
    wspace=0.07, hspace=0.09,
)
axes = np.array([[fig.add_subplot(grid[row, col]) for col in range(2)] for row in range(3)])
cbar_axes = [fig.add_subplot(grid[4, col]) for col in range(2)]

column_titles = ["Precipitación media mensual", "Temperatura media"]
column_subtitles = ["CHELSA v2.1 · mm/mes", "CHELSA v2.1 · °C"]
cmaps = {"pr": "Blues", "tas": "RdYlBu_r"}
variables = ("pr", "tas")
last_mappables = {}
phase_centers = []
km_formatter = FuncFormatter(lambda value, position: f"{value / 1000:.0f}")

for row, phase in enumerate(phases):
    for col, variable in enumerate(variables):
        ax = axes[row, col]
        lo, hi = limits[variable]
        levels = np.linspace(lo, hi, 8)
        interpolated = interpolate_grid(means[variable][phase])
        interpolated = np.where(
            np.isfinite(interpolated), interpolated, np.nanmean(means[variable][phase])
        )

        filled = ax.contourf(
            interpolated, levels=levels, extent=extent,
            cmap=cmaps[variable], extend="both",
        )
        filled.set_clip_path(clip_path, transform=ax.transData)
        contours = ax.contour(
            interpolated, levels=levels, extent=extent,
            colors="0.16", linewidths=0.55, alpha=0.9,
        )
        contours.set_clip_path(clip_path, transform=ax.transData)
        divisions.boundary.plot(ax=ax, color="0.18", linewidth=0.30, zorder=4)
        boundary.boundary.plot(ax=ax, color="#b5122b", linewidth=1.45, zorder=5)

        ax.set_xlim(left - 800, right + 800)
        ax.set_ylim(bottom - 800, top + 800)
        ax.set_aspect("equal")
        ax.grid(True, color="0.86", linewidth=0.35, zorder=0)
        ax.tick_params(labelsize=8, pad=2)
        ax.xaxis.set_major_formatter(km_formatter)
        ax.yaxis.set_major_formatter(km_formatter)

        if row < 2:
            ax.tick_params(labelbottom=False)
        else:
            ax.set_xlabel("Este (km)", fontsize=9, labelpad=4)
        if col == 0:
            ax.set_ylabel("Norte (km) · MAGNA-SIRGAS / Origen Nacional", fontsize=9)
        else:
            ax.tick_params(labelleft=False)

        if row == 0:
            ax.set_title(
                f"{column_titles[col]}\n{column_subtitles[col]}",
                fontsize=11, pad=9,
            )
        last_mappables[variable] = filled

    phase_centers.append((axes[row, 0].get_position().y0 + axes[row, 0].get_position().y1) / 2)

for y, phase in zip(phase_centers, phases):
    fig.text(
        0.035, y, phase.upper(), rotation=90,
        ha="center", va="center", fontsize=11, fontweight="bold", color="0.18",
    )

for cax, variable, label in zip(
    cbar_axes,
    variables,
    ("Precipitación media mensual (mm/mes)", "Temperatura media (°C)"),
):
    lo, hi = limits[variable]
    ticks = np.linspace(lo, hi, 8)
    colorbar = fig.colorbar(
        last_mappables[variable], cax=cax, orientation="horizontal", ticks=ticks
    )
    colorbar.set_label(label, fontsize=9, labelpad=4)
    colorbar.ax.tick_params(labelsize=8, pad=2)

fig.suptitle(
    "Precipitación y temperatura según fase del ENOS\nMedellín · 1981–2021",
    fontsize=15, y=0.975,
)
fig.text(
    0.545, 0.025,
    "Fuente climática: CHELSA v2.1. Fases definidas con ONI (CPC/NOAA). "
    "Límites: Alcaldía de Medellín.",
    ha="center", va="center", fontsize=8, color="0.32",
)

out = OUT / "CHELSA_ENSO_1981_2021_MAGNA_SIRGAS_Medellin_layout_v2.png"
fig.savefig(out, dpi=240, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(out)
