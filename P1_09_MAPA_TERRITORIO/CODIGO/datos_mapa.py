# -*- coding: utf-8 -*-
"""Etapa 1: prepara los datos de la página «Mapa del territorio» (pestaña 6 del tablero del Producto 9).
Entradas: capas de amenaza POT 2026 (vectorizadas de las láminas en PDF), límites oficiales, LST, y la base del tablero.
Salida: mapa_datos.json (todo en WGS84 y redondeado para web)."""
import json, re, sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union

BASE = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
RES = BASE + r"\00_RESPALDO_PAC_2026_Referencias_7.1_8.1_8.5_8.6"
LIM = BASE + r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910"
TABLERO = r"C:\Users\marco\Downloads\Producto9_tablero_base_variables_PAC_v1.html"
OUT = r"C:\Users\marco\AppData\Local\Temp\claude\G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude\446a2666-30c7-4c61-98e1-c82458a0665f\scratchpad\mapa\mapa_datos.json"
TOL_W = {"inu": 12, "tor": 12, "mm": 16}   # m, simplificación solo para la web (las áreas se calculan sin simplificar)
TOL_B = 6


def rnd(x, n=5):
    if isinstance(x, (list, tuple)):
        return [rnd(i, n) for i in x]
    return round(x, n)


def geo4326(geom9377, tol):
    g = gpd.GeoSeries([geom9377.simplify(tol, preserve_topology=True)], crs=9377).to_crs(4326).iloc[0]
    m = mapping(g)
    return {"type": m["type"], "coordinates": rnd(m["coordinates"])}


# ---------- límites ----------
com = gpd.read_file(LIM + r"\comunas_corregimientos_4326.geojson").to_crs(9377)
com["codigo"] = com["codigo"].astype(str)
print(com[["codigo", "nombre", "identificacion"]].to_string())
distrito = unary_union(com.geometry)
area_dist = distrito.area / 1e4  # ha

# ---------- amenazas ----------
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
haz["mm"] = mm
print({h: {c: round(g.area / 1e4, 1) for c, g in d.items()} for h, d in haz.items()}, "ha; distrito", round(area_dist, 0))

# ---------- tabla por territorio ----------
def tipo(cod):
    if cod.isdigit():
        n = int(cod)
        return "Comuna" if n <= 16 else "Corregimiento"
    return "Sin nombre"

lst_raw = pd.read_csv(RES + r"\8.1_datos_LST_por_comuna_corregimiento_Mediana_LST.csv", dtype={"codigo": str}, encoding="utf-8-sig")
lst_nor = pd.read_csv(RES + r"\8.1_datos_LST_por_comuna_corregimiento_Mediana_LST_norm.csv", dtype={"codigo": str}, encoding="utf-8-sig")
raw = lst_raw.set_index("codigo"); nor = lst_nor.set_index("codigo")

filas = []
for _, t in com.iterrows():
    cod = t["codigo"]; g = t.geometry; ar = g.area
    f = {"codigo": cod, "nombre": (re.sub(r"^Corregimiento de ", "", t["nombre"]).strip() if isinstance(t["nombre"], str) else "") or ("Sin nombre " + cod), "tipo": tipo(cod), "km2": round(ar / 1e6, 2)}
    for h in ("mm", "inu", "tor"):
        for c in ("alta", "media", "baja"):
            f[f"{h}_{c}"] = round(g.intersection(haz[h][c]).area / ar * 100, 1)
    f["lst"] = round(float(raw.loc[cod, "median"]), 1) if cod in raw.index else None
    f["lst_n"] = round(float(nor.loc[cod, "median"]), 1) if cod in nor.index else None
    f["cells"] = int(raw.loc[cod, "cells"]) if cod in raw.index else 0
    filas.append(f)

# ---------- multiamenaza: partición exacta del Distrito por (clase MM, clase inundación, clase torrencial) ----------
# baja = 1, media = 2, alta = 3; «fuera de la mancha» de inundación o torrencial = 1 (elemento neutro del producto).
# Sin pasar a ráster: intersección vectorial exacta de las tres capas.
mm_v = {1: haz["mm"]["baja"], 2: haz["mm"]["media"], 3: haz["mm"]["alta"]}
def clases_v(hh):
    g = haz[hh]
    alta = g["alta"]
    media = g["media"].difference(alta)
    return {1: distrito.difference(unary_union([media, alta])), 2: media, 3: alta}
Bc, Cc = clases_v("inu"), clases_v("tor")
piezas = []
for b in (1, 2, 3):
    for c in (1, 2, 3):
        Q = Bc[b].intersection(Cc[c])
        if Q.is_empty:
            continue
        for a_ in (1, 2, 3):
            P = mm_v[a_].intersection(Q)
            if P.geom_type not in ("Polygon", "MultiPolygon"):   # la intersección puede traer líneas o puntos sueltos
                P = unary_union([g_ for g_ in getattr(P, "geoms", []) if g_.geom_type in ("Polygon", "MultiPolygon")])
            if P.is_empty or P.area < 1:
                continue
            piezas.append((a_, b, c, P))
tot_area = sum(P.area for *_, P in piezas)
print("multiamenaza: piezas", len(piezas), "| cubierto / Distrito:", round(tot_area / distrito.area, 4))
dist_prod = {}
for a_, b, c, P in piezas:
    dist_prod[a_ * b * c] = dist_prod.get(a_ * b * c, 0) + P.area / 1e4
print("producto -> ha:", {k: round(v) for k, v in sorted(dist_prod.items())})
for fila, (_, t) in zip(filas, com.iterrows()):
    g = t.geometry; ar = g.area; comb = {}
    for a_, b, c, P in piezas:
        x = g.intersection(P).area / ar * 100
        if x >= 0.005:
            comb["%d-%d-%d" % (a_, b, c)] = round(x, 3)
    fila["comb"] = comb
multi_geo = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"a": a_, "b": b, "c": c, "p": a_ * b * c}, "geometry": geo4326(P, 14)} for a_, b, c, P in piezas if (b > 1 or c > 1) and not P.simplify(14, preserve_topology=True).is_empty]}
# Para la web solo se guardan las piezas dentro de las manchas de inundación o torrencial (b>1 o c>1); donde b=c=1 el índice
# es la clase de deslizamientos (1, 2, 3) y la página lo pinta con la capa de deslizamientos ya incluida (ahorra ~4 MB).

df = pd.DataFrame(filas)
print(df[["codigo", "nombre", "tipo", "km2", "mm_alta", "inu_alta", "tor_alta", "lst", "lst_n"]].to_string())

# ---------- totales del Distrito y contraste urbano-rural ----------
tot = {"km2": round(area_dist / 100, 1)}
for h in ("mm", "inu", "tor"):
    for c in ("alta", "media", "baja"):
        tot[f"{h}_{c}"] = round(haz[h][c].area / 1e4 / area_dist * 100, 1)
        tot[f"{h}_{c}_ha"] = round(haz[h][c].area / 1e4, 0)

def prom(col, tp):
    d = df[(df["tipo"] == tp) & df[col].notna()]
    return round(float(np.average(d[col], weights=d["cells"])), 1)

tot["lst_com"], tot["lst_cor"] = prom("lst", "Comuna"), prom("lst", "Corregimiento")
tot["lstn_com"], tot["lstn_cor"] = prom("lst_n", "Comuna"), prom("lst_n", "Corregimiento")
tot["comb"] = {"%d-%d-%d" % (a_, b, c): round(P.area / distrito.area * 100, 3) for a_, b, c, P in piezas}
tot["multi_ha"] = {str(k): round(v, 0) for k, v in sorted(dist_prod.items())}
tot["multi_pct"] = {str(k): round(v / area_dist * 100, 2) for k, v in sorted(dist_prod.items())}
print(tot["multi_pct"])
print(tot)

# ---------- geometrías para la web ----------
terr_geo = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"codigo": t["codigo"]}, "geometry": geo4326(t.geometry, 4)} for _, t in com.iterrows()]}
haz_geo = {}
for h in ("mm", "inu", "tor"):
    feats = []
    for c in ("baja", "media", "alta"):
        feats.append({"type": "Feature", "properties": {"clase": c}, "geometry": geo4326(haz[h][c], TOL_W[h])})
    haz_geo[h] = {"type": "FeatureCollection", "features": feats}

bar = gpd.read_file(LIM + r"\barrios_veredas_4326.geojson").to_crs(9377)
bar["codigo"] = bar["codigo"].astype(str)
lb = pd.read_csv(RES + r"\8.1_datos_LST_norm_por_barrio.csv", dtype={"codigo": str}, encoding="utf-8-sig").set_index("codigo")
nb = 0; feats = []
for _, b in bar.iterrows():
    cod = b["codigo"]
    if cod in lb.index:
        nb += 1; v = round(float(lb.loc[cod, "median"]), 1)
    else:
        v = None
    feats.append({"type": "Feature", "properties": {"codigo": cod, "nombre": (b["nombre"].strip() if isinstance(b["nombre"], str) else ""), "lst_n": v}, "geometry": geo4326(b.geometry, TOL_B)})
print("barrios con LST:", nb, "de", len(bar))
bar_geo = {"type": "FeatureCollection", "features": feats}
vals = [f["properties"]["lst_n"] for f in feats if f["properties"]["lst_n"] is not None]
print("LST barrios rango", min(vals), max(vals), "p5/p95", np.percentile(vals, [5, 95]).round(1))

# ---------- foto de la base de variables (tablero) ----------
h = open(TABLERO, encoding="utf-8").read()
s = re.search(r"<script[^>]*>(.*?)</script>", h, re.S).group(1)
D, _ = json.JSONDecoder().raw_decode(s[s.index("const D=") + 8:])
V = {v[0]: v for v in D["vars"]}
bl = {b["id"]: b for b in D["bloques"]}
pat = {"A1": r"inundaci|anegamiento", "A2": r"movimiento en masa|deslizamiento|remoci", "A4": r"torrencial|creciente|avenida", "A5": r"temperatura|calor|isla"}
snap = []
for bid in ("A1", "A2", "A4", "A5"):
    vs = [V[a[0]] for a in D["asign"] if a[1] == bid]
    fino = [v for v in vs if re.search(r"omuna|orregimiento|arrio", v[8])]
    est = [v for v in vs if "stación" in v[8]]
    espec = [v for v in vs if re.search(pat[bid], v[4], re.I)]
    snap.append({"id": bid, "nombre": bl[bid]["nombre"], "asig": len(vs), "comuna": len(fino), "estacion": len(est),
                 "municipio_ciudad": len(vs) - len(fino) - len(est), "especificas": len(espec),
                 "ejemplos": [v[4][:70] for v in espec[:3]]})
print(json.dumps(snap, ensure_ascii=False)[:900])
resumen = {"vars": len(D["vars"]), "ubicadas": sum(1 for v in D["vars"] if v[11] == "Ubicada"), "bloques": len(D["bloques"]), "asign": len(D["asign"])}

out = {"terr": df.drop(columns=[]).to_dict("records"), "tot": tot, "terr_geo": terr_geo, "haz_geo": haz_geo, "multi_geo": multi_geo, "bar_geo": bar_geo, "snap": snap, "tablero": resumen}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
import os
print("mapa_datos.json:", round(os.path.getsize(OUT) / 1048576, 2), "MB")
for k in ("terr_geo", "bar_geo", "multi_geo"):
    print(k, round(len(json.dumps(out[k], separators=(",", ":"))) / 1048576, 2), "MB")
for k, v in haz_geo.items():
    print(k, round(len(json.dumps(v, separators=(",", ":"))) / 1048576, 2), "MB")
