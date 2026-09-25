# -*- coding: utf-8 -*-
"""Build georeferenced hazard layers (EPSG:9377) from the POT 2026 cartography plates (Cartografia 1).

Plate 06 (floods) and plate 07 (torrential floods) store the hazard zones as vector paths with the
legend colours, so polygons are recovered exactly. Plate 05 (mass movements) is a raster picture
inside the PDF; its class raster is produced by extract_plate.py.
Output classes are made disjoint (high > medium > low) and clipped to the district boundary.
Validation: class areas are compared with the areas published in the basic hazard study (EBA)."""
import sys
from osgeo import ogr  # noqa: F401  (import before shapely/scipy stacks)
import geopandas as gpd
import extract_plate as ep
import extract_vector as ev

OUT = sys.argv[1] if len(sys.argv) > 1 else "prep"

PLATES = {
    "inundacion": dict(page=5, colors={(1.0, 0.0, 0.0): "alta", (1.0, 0.83, 0.5): "media", (0.69, 0.88, 0.0): "baja"},
                       eba_ha={"alta": 575, "media": 195, "baja": 364}),
    "avenidas_torrenciales": dict(page=6, colors={(0.0, 0.15, 0.45): "alta", (0.0, 0.44, 1.0): "media", (0.75, 0.91, 1.0): "baja"},
                                  eba_ha={"alta": 587, "media": 207, "baja": 169}),
}

boundary = ep.read_boundary()
for name, cfg in PLATES.items():
    polys, _ = ev.extract(cfg["page"], cfg["colors"])
    alta = polys["alta"].intersection(boundary)
    media = polys["media"].intersection(boundary).difference(alta)
    baja = polys["baja"].intersection(boundary).difference(alta).difference(media)
    gdf = gpd.GeoDataFrame({"clase": ["alta", "media", "baja"], "geometry": [alta, media, baja]}, crs="EPSG:9377")
    gdf["area_ha"] = (gdf.area / 1e4).round(1)
    gdf["area_ha_eba"] = gdf["clase"].map(cfg["eba_ha"])
    path = f"{OUT}/pot2026_amenaza_{name}_9377.gpkg"
    gdf.to_file(path, layer=f"amenaza_{name}", driver="GPKG")
    print(name, "->", path)
    print(gdf[["clase", "area_ha", "area_ha_eba"]].to_string(index=False))
