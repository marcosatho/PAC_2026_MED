# -*- coding: utf-8 -*-
"""Prepare the Geohazards landslide/debris-flow inventory for Medellín: clean fields, flag duplicates and
default-placed points, assign comuna/corregimiento by point-in-polygon, save a tidy CSV and a point layer.

usage: geohazards_prepare.py <out_dir>"""
from osgeo import gdal  # noqa: F401  (must load before pyproj/geopandas on this install)
import json, sys
import numpy as np
import pandas as pd
import geopandas as gpd

sys.stdout.reconfigure(encoding="utf-8")
OUT = sys.argv[1]
SRC = "C:/Users/marco/Downloads/Inventario Geohazards Antioquia.json"
GPKG = (r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA"
        r"\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE"
        r"\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg")
CENTROID = (-75.56582, 6.24764)   # coordinate that 267 records share: default placement, not a real location

g = json.load(open(SRC, encoding="utf-8"))
rows = []
for f in g["features"]:
    p = dict(f["properties"])
    c = (f.get("geometry") or {}).get("coordinates") or [None, None]
    p["x"], p["y"] = c[0], c[1]
    rows.append(p)
df = pd.DataFrame(rows)
m = df[df["town"].str.contains("Medell", case=False, na=False)].copy()

m["date"] = pd.to_datetime(m["date"], errors="coerce")
m["year"] = m["date"].dt.year
m["month"] = m["date"].dt.month
m["decade"] = (m["year"] // 10) * 10
m["fatalities"] = pd.to_numeric(m["fatalities"], errors="coerce").fillna(0).astype(int)
m["losses_raw"] = pd.to_numeric(m["losses"], errors="coerce")

# Death tolls checked against independent sources (web check, 26 Sep 2026); everything else keeps the inventory value.
CORR = {("1954-07-12", 100): (74, "Media Luna: las fuentes citan entre 60 y 74 víctimas (El Colombiano; García Márquez, 1954); el inventario trae 100."),
        ("2008-05-31", 28): (27, "El Socorro: 27 fallecidos y 16 lesionados según la revista EIA (2008) y otras fuentes; el inventario trae 28.")}
m["fatalities_verified"] = m["fatalities"]
m["verificacion"] = ""
_d = m["date"].dt.strftime("%Y-%m-%d")
for (dd, orig), (val, note) in CORR.items():
    hit = (_d == dd) & (m["fatalities"] == orig)
    m.loc[hit, "fatalities_verified"] = val
    m.loc[hit, "verificacion"] = note
m.loc[(_d == "1987-09-27") & (m["fatalities"] == 500), "verificacion"] = "Villatina: cerca de 500 fallecidos (Wikipedia; El Colombiano, El Tiempo)."
m.loc[(_d == "2008-11-16") & (m["fatalities"] == 12), "verificacion"] = "Alto Verde (Cola del Zorro): 12 fallecidos (El Colombiano; Vanguardia)."
print("verified rows:", int((m["verificacion"] != "").sum()))
m["uncertainty"] = m["uncertainty"].str.strip().str.capitalize()
m["type_es"] = m["type"].map({"Landslide": "deslizamiento", "Debris Flow": "flujo de detritos"})
m["trigger_es"] = m["triggering"].map({"Rainfall": "lluvia", "Anthropic": "actividad humana", "Unknown": "sin dato"}).fillna("otro")
m["source"] = m["source"].str.strip()
m = m.drop(columns=["lat", "lng"]).rename(columns={"x": "lon", "y": "lat"})
m["lon"] = pd.to_numeric(m["lon"], errors="coerce")
m["lat"] = pd.to_numeric(m["lat"], errors="coerce")

m["default_location"] = (m["lon"].round(5) == CENTROID[0]) & (m["lat"].round(5) == CENTROID[1])
m["k_xy"] = m["date"].dt.strftime("%Y-%m-%d") + "|" + m["lon"].round(3).astype(str) + "|" + m["lat"].round(3).astype(str)
m["dup_same_day_110m"] = m.duplicated("k_xy", keep="first") & ~m["default_location"]

div = gpd.read_file(GPKG, layer="comunas_corregimientos").set_crs(9377, allow_override=True)
div["territorio"] = (div["nombre"].fillna("").str.replace("Corregimiento de ", "", regex=False)
                     .str.replace("Laureles Estadio", "Laureles-Estadio", regex=False))
div["tipo"] = np.where(div["subtipo_comunacorregimiento"].astype(str) == "2", "corregimiento", "comuna")
div["cod"] = div["codigo"]
pts = gpd.GeoDataFrame(m, geometry=gpd.points_from_xy(m["lon"], m["lat"]), crs=4326).to_crs(9377)
pts = gpd.sjoin(pts, div[["cod", "territorio", "tipo", "geometry"]], how="left", predicate="within").drop(columns="index_right")
pts.loc[pts["default_location"], ["cod", "territorio", "tipo"]] = np.nan   # default coordinate says nothing about location

print("records:", len(pts), "| range", pts["date"].min().date(), pts["date"].max().date())
print("default-location records:", int(pts["default_location"].sum()))
print("possible duplicates (same day, ~110 m):", int(pts["dup_same_day_110m"].sum()))
print("located inside a division:", int(pts["territorio"].notna().sum()), "| outside/none (not default):",
      int((pts["territorio"].isna() & ~pts["default_location"]).sum()))

keep = ["id", "date", "year", "month", "decade", "type_es", "trigger_es", "triggering_description", "fatalities", "fatalities_verified", "verificacion", "losses_raw",
        "uncertainty", "source", "site", "county", "lon", "lat", "default_location", "dup_same_day_110m", "cod", "territorio", "tipo"]
tidy = pd.DataFrame(pts[keep])
tidy["date"] = tidy["date"].dt.strftime("%Y-%m-%d")
tidy.to_csv(f"{OUT}/geohazards_medellin_limpio.csv", index=False, encoding="utf-8-sig")
pts[keep + ["geometry"]].to_file(f"{OUT}/geohazards_medellin_9377.gpkg", layer="eventos", driver="GPKG")
print("saved to", OUT)

# quick descriptive numbers (used to plan the figures)
pts["date"] = pd.to_datetime(pts["date"])
print("\nrecords per decade:\n", pts.groupby("decade").agg(n=("id", "size"), muertes=("fatalities", "sum"), lluvia=("trigger_es", lambda s: (s == "lluvia").sum())).to_string())
print("\nsince 1990 by year:\n", pts[pts["year"] >= 1990].groupby("year").size().to_string())
print("\nby territory (located only):\n", pts.groupby("territorio").agg(n=("id", "size"), muertes=("fatalities", "sum")).sort_values("n", ascending=False).to_string())
print("\nevents with deaths >= 5:\n", pts[pts["fatalities"] >= 5][["date", "fatalities", "type_es", "site", "county", "source", "uncertainty"]].sort_values("date").to_string())
