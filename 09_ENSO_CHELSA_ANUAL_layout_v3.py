"""Composiciones anuales CHELSA v2.1 según fase ENSO.

Metodología:
- ONI asignado al mes central correcto de cada trimestre móvil.
- Niño/Niña mensual confirmado por cinco o más temporadas consecutivas.
- Un año se clasifica Niño o Niña si contiene al menos cinco meses confirmados
  de esa fase y más meses de esa fase que de la opuesta; los demás son neutrales.
- Precipitación anual: suma de los 12 meses (mm/año).
- Temperatura media anual: promedio de los 12 meses (°C).

Genera una salida nueva; no sobrescribe las versiones mensuales anteriores.
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
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import array_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.ndimage import zoom

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


def load_oni():
    local = BASE / "oni.ascii.txt"
    if local.exists():
        frame = pd.read_fwf(local, skiprows=1, names=["season", "year", "total", "oni"])
    else:
        url = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
        with urlopen(url, timeout=30) as response:
            frame = pd.read_fwf(io.BytesIO(response.read()), skiprows=1,
                                names=["season", "year", "total", "oni"])
    frame = frame[(frame.year >= 1981) & (frame.year <= 2021)].copy()
    # Mes central: DJF→enero, JFM→febrero, ..., NDJ→diciembre.
    center = {name: month for month, name in enumerate(
        ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"], 1)}
    frame["month"] = frame.season.map(center)
    frame["period"] = pd.to_datetime(
        {"year": frame.year, "month": frame.month, "day": 15}
    ).dt.to_period("M")
    frame["raw_phase"] = np.select(
        [frame.oni >= 0.5, frame.oni <= -0.5], ["El Niño", "La Niña"], default="Neutral"
    )
    frame["run"] = (frame.raw_phase != frame.raw_phase.shift()).cumsum()
    run_size = frame.groupby("run").size()
    frame["phase"] = np.where(frame.run.map(run_size) >= 5, frame.raw_phase, "Neutral")
    return frame.set_index("period")["phase"]


def raster_files(variable):
    result = {}
    for file in sorted((DATA / variable).glob("*.tif")):
        match = re.search(r"_(\d{2})_(\d{4})_V", file.name)
        if match:
            result[pd.Period(f"{match.group(2)}-{match.group(1)}", freq="M")] = file
    return result


phase_month = load_oni()
paths = {variable: raster_files(variable) for variable in ("pr", "tas")}
phases = ["El Niño", "Neutral", "La Niña"]
annual = {variable: {phase: [] for phase in phases} for variable in ("pr", "tas")}
years_by_phase = {phase: [] for phase in phases}

common_periods = set(paths["pr"]) & set(paths["tas"]) & set(phase_month.index)
complete_years = [
    year for year in range(1981, 2022)
    if all(pd.Period(f"{year}-{month:02d}", freq="M") in common_periods for month in range(1, 13))
]

for year in complete_years:
    periods = [pd.Period(f"{year}-{month:02d}", freq="M") for month in range(1, 13)]
    counts = phase_month.loc[periods].value_counts()
    niño = int(counts.get("El Niño", 0))
    niña = int(counts.get("La Niña", 0))
    if niño >= 5 and niño > niña:
        year_phase = "El Niño"
    elif niña >= 5 and niña > niño:
        year_phase = "La Niña"
    else:
        year_phase = "Neutral"
    years_by_phase[year_phase].append(year)

    stacks = {}
    for variable in ("pr", "tas"):
        months = []
        for period in periods:
            with rasterio.open(paths[variable][period]) as src:
                values = src.read(1).astype("float32")
                values[values >= 65000] = np.nan
                profile = src.profile
            if variable == "tas":
                values = values * 0.1 - 273.15
            months.append(values)
        stack = np.stack(months)
        stacks[variable] = np.nansum(stack, axis=0) if variable == "pr" else np.nanmean(stack, axis=0)
    annual["pr"][year_phase].append(stacks["pr"])
    annual["tas"][year_phase].append(stacks["tas"])

composites = {
    variable: {phase: np.nanmean(np.stack(arrays), axis=0) for phase, arrays in groups.items()}
    for variable, groups in annual.items()
}

with rasterio.open(paths["pr"][pd.Period("1981-01", freq="M")]) as src:
    dst_transform, width, height = calculate_default_transform(
        src.crs, "EPSG:9377", src.width, src.height, *src.bounds, resolution=1000
    )
    src_transform = src.transform


def warp(values):
    result = np.full((height, width), np.nan, dtype="float32")
    reproject(
        values.astype("float32"), result,
        src_transform=src_transform, src_crs="EPSG:4326",
        dst_transform=dst_transform, dst_crs="EPSG:9377",
        resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan,
    )
    return result


composites = {
    variable: {phase: warp(values) for phase, values in groups.items()}
    for variable, groups in composites.items()
}


def interpolate_for_contours(values, factor=5):
    valid = np.isfinite(values).astype(float)
    numerator = zoom(np.nan_to_num(values, nan=0.0), factor, order=3)
    denominator = zoom(valid, factor, order=3)
    return np.divide(numerator, denominator, out=np.full_like(numerator, np.nan), where=denominator > 0.5)


def clip_path_from(gdf):
    paths_out = []
    for geometry in gdf.geometry:
        polygons = list(geometry.geoms) if geometry.geom_type == "MultiPolygon" else [geometry]
        for polygon in polygons:
            for ring in [polygon.exterior, *polygon.interiors]:
                xy = np.asarray(ring.coords)
                codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(xy) - 2) + [MplPath.CLOSEPOLY]
                paths_out.append(MplPath(xy, codes))
    return MplPath.make_compound_path(*paths_out)


municipal_mask = geometry_mask(
    boundary.geometry, transform=dst_transform, out_shape=(height, width), invert=True
)
limits = {
    variable: (
        np.nanmin(np.concatenate([values[municipal_mask] for values in groups.values()])),
        np.nanmax(np.concatenate([values[municipal_mask] for values in groups.values()])),
    )
    for variable, groups in composites.items()
}
clip_path = clip_path_from(boundary)
left, bottom, right, top = boundary.total_bounds
rleft, rbottom, rright, rtop = array_bounds(height, width, dst_transform)
extent = [rleft, rright, rbottom, rtop]

fig = plt.figure(figsize=(10.5, 13.2), facecolor="white")
grid = fig.add_gridspec(
    5, 2, height_ratios=[1, 1, 1, 0.075, 0.05],
    left=0.105, right=0.985, top=0.885, bottom=0.085, wspace=0.07, hspace=0.09,
)
axes = np.array([[fig.add_subplot(grid[row, col]) for col in range(2)] for row in range(3)])
cbar_axes = [fig.add_subplot(grid[4, col]) for col in range(2)]
variables = ("pr", "tas")
cmaps = {"pr": "Blues", "tas": "RdYlBu_r"}
column_titles = ["Precipitación media anual", "Temperatura media anual"]
column_units = ["CHELSA v2.1 · mm/año", "CHELSA v2.1 · °C"]
km = FuncFormatter(lambda value, position: f"{value / 1000:.0f}")
last_mappable = {}
row_centers = []

for row, phase in enumerate(phases):
    for col, variable in enumerate(variables):
        ax = axes[row, col]
        values = interpolate_for_contours(composites[variable][phase])
        lo, hi = limits[variable]
        levels = np.linspace(lo, hi, 8)
        filled = ax.contourf(values, levels=levels, extent=extent, cmap=cmaps[variable], extend="both")
        filled.set_clip_path(clip_path, transform=ax.transData)
        lines = ax.contour(values, levels=levels, extent=extent, colors="0.16", linewidths=0.55)
        lines.set_clip_path(clip_path, transform=ax.transData)
        divisions.boundary.plot(ax=ax, color="0.18", linewidth=0.30, zorder=4)
        boundary.boundary.plot(ax=ax, color="#b5122b", linewidth=1.45, zorder=5)
        ax.set_xlim(left - 800, right + 800)
        ax.set_ylim(bottom - 800, top + 800)
        ax.set_aspect("equal")
        ax.grid(True, color="0.86", linewidth=0.35)
        ax.xaxis.set_major_formatter(km)
        ax.yaxis.set_major_formatter(km)
        ax.tick_params(labelsize=8, pad=2)
        if row < 2:
            ax.tick_params(labelbottom=False)
        else:
            ax.set_xlabel("Este (km)", fontsize=9)
        if col == 0:
            ax.set_ylabel("Norte (km) · MAGNA-SIRGAS / Origen Nacional", fontsize=9)
        else:
            ax.tick_params(labelleft=False)
        if row == 0:
            ax.set_title(f"{column_titles[col]}\n{column_units[col]}", fontsize=11, pad=9)
        last_mappable[variable] = filled
    row_centers.append((axes[row, 0].get_position().y0 + axes[row, 0].get_position().y1) / 2)

for y, phase in zip(row_centers, phases):
    fig.text(
        0.035, y, f"{phase.upper()}\n{len(years_by_phase[phase])} años",
        rotation=90, ha="center", va="center", fontsize=10.5, fontweight="bold", color="0.18",
    )

for cax, variable, label in zip(
    cbar_axes, variables,
    ("Precipitación media anual (mm/año)", "Temperatura media anual (°C)"),
):
    lo, hi = limits[variable]
    colorbar = fig.colorbar(
        last_mappable[variable], cax=cax, orientation="horizontal", ticks=np.linspace(lo, hi, 8)
    )
    colorbar.set_label(label, fontsize=9, labelpad=4)
    colorbar.ax.tick_params(labelsize=8, pad=2)

fig.suptitle(
    "Precipitación y temperatura anual según fase del ENOS\nMedellín · 1981–2021",
    fontsize=15, y=0.975,
)
fig.text(
    0.545, 0.025,
    "Fuente climática: CHELSA v2.1. Fases anuales derivadas del ONI (CPC/NOAA). "
    "Límites: Alcaldía de Medellín.",
    ha="center", va="center", fontsize=8, color="0.32",
)

out = OUT / "CHELSA_ENSO_ANUAL_1981_2021_MAGNA_SIRGAS_Medellin_layout_v3.png"
fig.savefig(out, dpi=240, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("Años por fase:", years_by_phase)
print(out)
