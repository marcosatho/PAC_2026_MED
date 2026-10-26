# -*- coding: utf-8 -*-
"""Exporta las piezas exactas de la multiamenaza (producto de las clases baja=1, media=2, alta=3 de deslizamientos, inundación y avenidas torrenciales)
en EPSG:9377. Misma lógica de datos_mapa.py (bloque «multiamenaza»); aquí se guarda la capa completa, sin simplificar."""
import os, numpy as np, geopandas as gpd, rasterio
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.ops import unary_union

D = os.path.dirname(os.path.abspath(__file__))
BASE = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
RES = BASE + r"\00_RESPALDO_PAC_2026_Referencias_7.1_8.1_8.5_8.6"
LIM = BASE + r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910"
OUT = os.path.join(D, "multiamenaza_piezas.gpkg")

com = gpd.read_file(LIM + r"\comunas_corregimientos_4326.geojson").to_crs(9377)
distrito = unary_union(com.geometry)

def clases_gpkg(path):
    g = gpd.read_file(path).to_crs(9377)
    return {r["clase"]: r.geometry.intersection(distrito) for _, r in g.iterrows()}

haz = {"inu": clases_gpkg(RES + r"\8.1_datos_pot2026_amenaza_inundacion_9377.gpkg"),
       "tor": clases_gpkg(RES + r"\8.1_datos_pot2026_amenaza_avenidas_torrenciales_9377.gpkg")}
with rasterio.open(RES + r"\8.1_datos_pot2026_amenaza_movimientos_masa_clase_9377.tif") as r:
    a = r.read(1); tr = r.transform
mm = {}
for k, nombre in ((1, "alta"), (2, "media"), (3, "baja")):
    polys = [shape(s) for s, v in shapes(a, mask=(a == k), transform=tr, connectivity=4)]
    mm[nombre] = unary_union(polys).intersection(distrito)
mm_v = {1: mm["baja"], 2: mm["media"], 3: mm["alta"]}

def clases_v(g):
    alta = g["alta"]
    media = g["media"].difference(alta)
    return {1: distrito.difference(unary_union([media, alta])), 2: media, 3: alta}
Bc, Cc = clases_v(haz["inu"]), clases_v(haz["tor"])
filas = []
for b in (1, 2, 3):
    for c in (1, 2, 3):
        Q = Bc[b].intersection(Cc[c])
        if Q.is_empty:
            continue
        for a_ in (1, 2, 3):
            P = mm_v[a_].intersection(Q)
            if P.geom_type not in ("Polygon", "MultiPolygon"):
                P = unary_union([g_ for g_ in getattr(P, "geoms", []) if g_.geom_type in ("Polygon", "MultiPolygon")])
            if P.is_empty or P.area < 1:
                continue
            filas.append({"clase_deslizamientos": a_, "clase_inundacion": b, "clase_torrenciales": c, "indice": a_ * b * c, "ha": P.area / 1e4, "geometry": P})
g = gpd.GeoDataFrame(filas, crs=9377).sort_values(["indice", "clase_deslizamientos", "clase_inundacion"]).reset_index(drop=True)
g["pct_distrito"] = g["ha"] / (distrito.area / 1e4) * 100
g.to_file(OUT, layer="multiamenaza_piezas", driver="GPKG")
print("piezas:", len(g), "| cubierto / Distrito:", round(g["ha"].sum() / (distrito.area / 1e4), 4), "| guardado:", OUT)
print(g.groupby("indice")["ha"].sum().round(0).to_dict())
