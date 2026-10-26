# -*- coding: utf-8 -*-
"""Version 2 of the POT 2026 hazard layers: official vector polygons instead of the PDF-plate reconstruction (v1).

Input : file geodatabase mj_rev_pot_2025_med.gdb (zip YDRAY-GDB_Form_DiccTopolog.zip, DAP Medellín; EPSG:9377).
Output: one GeoPackage with the three hazard layers (EPSG:9377), geometries repaired with make_valid, native geometry
        (no regridding, no simplification), plus a JSON with counts and areas per class for traceability.

Usage: python prepare_pot2026_hazard_layers_v2.py <input.zip> <output_dir>
v1 files (pot2026_amenaza_*_9377.gpkg/.tif) are NOT touched."""
import sys, json, hashlib, datetime
import geopandas as gpd
from shapely import make_valid
from shapely.geometry import MultiPolygon, Polygon, GeometryCollection

import os
# Paths with spaces/accents break the QGIS .bat launcher when passed as arguments, so they may come from the environment.
ZIP = sys.argv[1] if len(sys.argv) > 1 else os.environ["V2_ZIP"]
OUT = sys.argv[2] if len(sys.argv) > 2 else os.environ["V2_OUT"]
GDB = f"/vsizip/{ZIP.replace(chr(92), '/')}/mj_rev_pot_2025_med.gdb"
LAYERS = {  # output layer -> layer in the official gdb
    "amenaza_inundacion": "gur_ar_amenaza_inundaciones",
    "amenaza_avenidas_torrenciales": "gur_ar_amenaza_avtorrenciales",
    "amenaza_movimientos_masa": "gur_ar_amenaza_mov_masa",
}
KEEP = ["categoria", "fenomeno", "descripcion", "categoria_proteccion", "subcategoria_proteccion", "estudio", "fuente"]


def polygons_only(geom):
    """make_valid can return a GeometryCollection; keep only the polygonal parts."""
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    parts = [g for g in getattr(geom, "geoms", []) if g.geom_type in ("Polygon", "MultiPolygon")]
    flat = []
    for p in parts:
        flat.extend(p.geoms if p.geom_type == "MultiPolygon" else [p])
    return MultiPolygon(flat) if flat else geom


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


report = {"input_zip": ZIP, "input_sha256": sha256(ZIP), "gdb": "mj_rev_pot_2025_med.gdb",
          "prepared_on": datetime.date.today().isoformat(), "layers": {}}
gpkg = f"{OUT}/pot2026_amenazas_oficial_v2_9377.gpkg"
first = True
for out_name, src in LAYERS.items():
    gdf = gpd.read_file(GDB, layer=src, engine="pyogrio")
    assert gdf.crs.to_epsg() == 9377, gdf.crs
    n = len(gdf)
    invalid = ~gdf.geometry.is_valid
    gdf["reparada"] = invalid.astype(int)
    gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].apply(lambda g: polygons_only(make_valid(g)))
    gdf["objectid_orig"] = range(1, n + 1)
    gdf["area_ha"] = gdf.geometry.area / 1e4
    gdf = gdf[KEEP + ["objectid_orig", "area_ha", "reparada", "geometry"]]
    assert gdf.geometry.is_valid.all()
    gdf.to_file(gpkg, layer=out_name, driver="GPKG", mode="w" if first else "a", engine="pyogrio")
    first = False
    by = gdf.groupby("categoria")["area_ha"].agg(["count", "sum"]).round(2)
    report["layers"][out_name] = {
        "source_layer": src, "polygons": n, "repaired": int(invalid.sum()),
        "total_ha": round(float(gdf["area_ha"].sum()), 2),
        "by_category": {k: {"polygons": int(v["count"]), "ha": float(v["sum"])} for k, v in by.iterrows()},
        "by_fuente": gdf["fuente"].value_counts().to_dict(),
    }
    print(out_name, n, "polygons;", int(invalid.sum()), "repaired;", by.to_dict("index"))
report["output_gpkg"] = gpkg
with open(f"{OUT}/pot2026_amenazas_oficial_v2_resumen.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("saved", gpkg)
