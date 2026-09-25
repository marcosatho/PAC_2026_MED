# -*- coding: utf-8 -*-
"""Surface temperature (LST) for the Medellin district from the AMVA heat-island package (Guzman Echavarria, 2018).

Inputs (EPSG:32618, 30 m, degC): Mediana_LST.tif (median of morning Landsat 8 scenes) and Mediana_LST_norm.tif (the same
after removing the topographic bias in incident radiation).
Outputs: both rasters reprojected to EPSG:9377 (bilinear, 30 m) and clipped to the district; zonal statistics by comuna /
corregimiento and by barrio (CSV).

usage: uhi_lst_prepare.py <src_dir> <out_dir>"""
import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling

sys.stdout.reconfigure(encoding="utf-8")
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
GPKG = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
        r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg")
boundary = gpd.read_file(GPKG, layer="limite_medellin")
bpoly = boundary.geometry.iloc[0]


def prep(name):
    with rasterio.open(os.path.join(SRC, name)) as s:
        tr, w, h = calculate_default_transform(s.crs, "EPSG:9377", s.width, s.height, *s.bounds, resolution=30)
        arr = np.full((h, w), np.nan, "float32")
        reproject(rasterio.band(s, 1), arr, src_transform=s.transform, src_crs=s.crs, dst_transform=tr, dst_crs="EPSG:9377",
                  resampling=Resampling.bilinear, src_nodata=s.nodata, dst_nodata=np.nan)
    tmp = os.path.join(OUT, "_tmp.tif")
    with rasterio.open(tmp, "w", driver="GTiff", height=h, width=w, count=1, dtype="float32", crs="EPSG:9377", transform=tr, nodata=np.nan) as d:
        d.write(arr, 1)
    with rasterio.open(tmp) as s:
        img, tr2 = mask(s, [bpoly.__geo_interface__], crop=True, nodata=np.nan, all_touched=True)
    os.remove(tmp)
    out = os.path.join(OUT, name.replace(".tif", "_9377_Medellin.tif"))
    with rasterio.open(out, "w", driver="GTiff", height=img.shape[1], width=img.shape[2], count=1, dtype="float32", crs="EPSG:9377",
                       transform=tr2, nodata=np.nan, compress="lzw") as d:
        d.write(img[0], 1)
    return img[0], tr2


data = {n: prep(n) for n in ("Mediana_LST.tif", "Mediana_LST_norm.tif")}
for n, (a, tr) in data.items():
    inside = rasterize([bpoly.__geo_interface__], out_shape=a.shape, transform=tr, fill=0, default_value=1, dtype="uint8").astype(bool)
    v = a[inside & np.isfinite(a)]
    print(f"{n}: district coverage {100 * (inside & np.isfinite(a)).sum() / inside.sum():.1f} % | degC min {v.min():.1f} p5 {np.percentile(v, 5):.1f} "
          f"median {np.median(v):.1f} p95 {np.percentile(v, 95):.1f} max {v.max():.1f}")


def zonal(gdf, name_col, arr, tr):
    rows = []
    for _, r in gdf.iterrows():
        m = rasterize([r.geometry.__geo_interface__], out_shape=arr.shape, transform=tr, fill=0, default_value=1, dtype="uint8").astype(bool) & np.isfinite(arr)
        if m.sum() > 20:
            v = arr[m]
            rows.append({"codigo": r.get("codigo"), "nombre": r[name_col], "mean": v.mean(), "median": np.median(v), "p90": np.percentile(v, 90), "cells": int(m.sum())})
    return pd.DataFrame(rows)


div = gpd.read_file(GPKG, layer="comunas_corregimientos")
for n in ("Mediana_LST.tif", "Mediana_LST_norm.tif"):
    a, tr = data[n]
    z = zonal(div, "nombre", a, tr)
    z["nombre"] = z["nombre"].fillna(z["codigo"])
    z.to_csv(os.path.join(OUT, "LST_por_comuna_corregimiento_" + n.replace(".tif", "") + ".csv"), index=False, encoding="utf-8-sig")
    urban = z[z["codigo"].astype(str).str.fullmatch(r"\d{2}") & ~z["codigo"].astype(str).isin(["50", "60", "70", "80", "90"])]
    rural = z[z["codigo"].astype(str).isin(["50", "60", "70", "80", "90"])]
    print(f"\n== {n}: media por unidad (degC) | urbanas (16 comunas) media {np.average(urban['mean'], weights=urban['cells']):.1f} | "
          f"corregimientos media {np.average(rural['mean'], weights=rural['cells']):.1f}")
    print(z.sort_values("mean", ascending=False)[["nombre", "mean", "p90"]].round(1).to_string(index=False))

bar = gpd.read_file(GPKG, layer="barrios")
print("\nbarrios layer columns:", list(bar.columns)[:12], "| n =", len(bar))
a, tr = data["Mediana_LST_norm.tif"]
name_col = "nombre" if "nombre" in bar.columns else bar.columns[1]
zb = zonal(bar, name_col, a, tr)
zb.to_csv(os.path.join(OUT, "LST_norm_por_barrio.csv"), index=False, encoding="utf-8-sig")
print("barrios con dato:", len(zb), "| top 12 más calientes (LST corregida):")
print(zb.sort_values("mean", ascending=False).head(12)[["codigo", "nombre", "mean", "p90"]].round(1).to_string(index=False))
print("12 más frescos:")
print(zb.sort_values("mean").head(12)[["codigo", "nombre", "mean"]].round(1).to_string(index=False))
