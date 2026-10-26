# -*- coding: utf-8 -*-
"""Etapa A de la v2: estadísticas por barrio/vereda (332 polígonos oficiales) de amenaza, arbolado, verde, obras, monitoreo y alerta temprana.
Todo en EPSG:9377 (sistema nativo de las capas); solo se agrega de píxel o polígono a barrio (intersección exacta, sin remuestreo)."""
import glob, json, os, sys, warnings
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.features import shapes
from shapely.geometry import shape
warnings.filterwarnings("ignore")

D = os.path.dirname(os.path.abspath(__file__))
DM = os.path.join(D, "datos_medidas")
BASE = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
RES = BASE + r"\00_RESPALDO_PAC_2026_Referencias_7.1_8.1_8.5_8.6"
LIM = BASE + r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910"


def cargar(n):
    fs = sorted(glob.glob(os.path.join(DM, n, "*.geojson")))
    g = pd.concat([gpd.read_file(f) for f in fs], ignore_index=True)
    g = gpd.GeoDataFrame(g, geometry="geometry", crs=9377)
    g = g[g.geometry.notna() & ~g.geometry.is_empty].copy()
    g["geometry"] = g.geometry.make_valid()
    if g.geom_type.isin(["Polygon", "MultiPolygon", "GeometryCollection"]).any():   # polígonos: quitar líneas y puntos sueltos que deja la corrección de geometrías
        from shapely.ops import unary_union
        def poli(x):
            if x.geom_type in ("Polygon", "MultiPolygon"):
                return x
            ps = [y for y in getattr(x, "geoms", []) if y.geom_type in ("Polygon", "MultiPolygon")]
            return unary_union(ps) if ps else None
        g["geometry"] = g.geometry.map(poli)
        g = g[g.geometry.notna() & ~g.geometry.is_empty].copy()
    return g


# ---------- barrios ----------
bar = gpd.read_file(LIM + r"\barrios_veredas_4326.geojson").to_crs(9377)
bar["codigo"] = bar["codigo"].astype(str)
bar["bid"] = bar["objectid"].astype(int)
bar["comuna"] = bar["limitecomunacorregimientoid"].astype(str)
bar["ha"] = bar.geometry.area / 1e4
bar["urbano"] = bar["comuna"].map(lambda c: c.isdigit() and int(c) <= 16)
print("barrios:", len(bar), "| códigos repetidos:", int(bar["codigo"].duplicated().sum()), "| urbanos:", int(bar["urbano"].sum()), flush=True)
B = bar[["bid", "geometry"]]
S = bar[["bid", "codigo", "nombre", "comuna", "ha", "urbano"]].copy().set_index("bid")


def sumar(df, clave, valor, col):
    return df.groupby(clave)[valor].sum().reindex(S.index).fillna(0).rename(col)


HC = os.path.join(D, "haz_barrios_cache.csv")   # las intersecciones de amenaza tardan; se guardan para repetir el resto sin recalcularlas
if os.path.exists(HC):
    c_ = pd.read_csv(HC).set_index("bid")
    for col in c_.columns:
        S[col] = c_[col]
    print("amenazas leídas del caché", flush=True)
else:
    # ---------- amenaza por barrio (intersección vectorial exacta) ----------
    def clases_gpkg(path):
        g = gpd.read_file(path).to_crs(9377)
        return g[["clase", "geometry"]]


    inu = clases_gpkg(RES + r"\8.1_datos_pot2026_amenaza_inundacion_9377.gpkg")
    tor = clases_gpkg(RES + r"\8.1_datos_pot2026_amenaza_avenidas_torrenciales_9377.gpkg")
    with rasterio.open(RES + r"\8.1_datos_pot2026_amenaza_movimientos_masa_clase_9377.tif") as r:
        a = r.read(1); tr = r.transform
    nombres = {1: "alta", 2: "media", 3: "baja"}
    polys = [{"clase": nombres[int(v)], "geometry": shape(s)} for s, v in shapes(a, mask=np.isin(a, [1, 2, 3]), transform=tr, connectivity=4) if int(v) in nombres]
    mm = gpd.GeoDataFrame(polys, crs=9377)
    print("polígonos de deslizamientos:", len(mm), flush=True)
    for nom, g in (("mm", mm), ("inu", inu), ("tor", tor)):
        g = g.copy(); g["geometry"] = g.geometry.make_valid()
        ov = gpd.overlay(g, B, how="intersection", keep_geom_type=True)
        ov["ha"] = ov.geometry.area / 1e4
        t = ov.groupby(["bid", "clase"])["ha"].sum().unstack(fill_value=0).reindex(S.index).fillna(0)
        for c in ("alta", "media", "baja"):
            S[f"{nom}_{c}_ha"] = t[c] if c in t.columns else 0.0
        print("amenaza", nom, "listo", flush=True)

    # ---------- incendios ----------
    inc = cargar("incendios")
    ov = gpd.overlay(inc[["magnitud", "geometry"]], B, how="intersection", keep_geom_type=True)
    ov["ha"] = ov.geometry.area / 1e4
    t = ov.groupby(["bid", "magnitud"])["ha"].sum().unstack(fill_value=0).reindex(S.index).fillna(0)
    for c, k in (("Alta", "alta"), ("Media", "media"), ("Baja", "baja")):
        S[f"inc_{k}_ha"] = t[c] if c in t.columns else 0.0
    print("incendios listo", flush=True)

    S[[c for c in S.columns if c.split("_")[0] in ("mm", "inu", "tor", "inc") and c.endswith("_ha")]].to_csv(HC)

# ---------- temperatura de superficie por barrio (ya calculada en la fase 1) ----------
lb = pd.read_csv(RES + r"\8.1_datos_LST_norm_por_barrio.csv", dtype={"codigo": str}, encoding="utf-8-sig").drop_duplicates("codigo").set_index("codigo")
S["lst_n"] = S["codigo"].map(lambda c: float(lb.loc[c, "median"]) if c in lb.index else np.nan)

# ---------- árbol urbano ----------
if os.path.isdir(os.path.join(DM, "arboles")) and glob.glob(os.path.join(DM, "arboles", "*.geojson")):
    ar = cargar("arboles")
    n0 = len(ar); ar = ar.drop_duplicates("objectid")
    print("árboles descargados:", n0, "| sin repetidos:", len(ar), flush=True)
    j = gpd.sjoin(ar[["s_estado_arbol", "tipoarbol", "geometry"]], B, how="inner", predicate="within")
    S["arboles"] = j.groupby("bid").size().reindex(S.index).fillna(0)
    for k, est in (("sanos", "Individuo Sano"), ("muertos", "Individuo Muerto"), ("enfermos", "Individuo Enfermo")):
        S[f"arb_{k}"] = j[j["s_estado_arbol"] == est].groupby("bid").size().reindex(S.index).fillna(0)
    print("árboles dentro de barrios:", int(S["arboles"].sum()), flush=True)
else:
    print("SIN árboles", flush=True)

# ---------- espacios verdes urbanos (recorte exacto a cada barrio) ----------
if glob.glob(os.path.join(DM, "evu", "*.geojson")):
    ev = cargar("evu")
    n0 = len(ev); ev = ev.drop_duplicates("objectid")
    print("EVU descargados:", n0, "| sin repetidos:", len(ev), flush=True)
    ov = gpd.overlay(ev[["cobertura", "categoria_msu", "cubierta_verde", "propiedad", "geometry"]], B, how="intersection", keep_geom_type=True)
    ov["ha"] = ov.geometry.area / 1e4
    S["evu_ha"] = sumar(ov, "bid", "ha", "evu_ha")
    for k, c in (("arboles", "Arboles"), ("arbustos", "Arbustos"), ("pasto", "GramaPasto"), ("jardin", "Jardin")):
        S[f"evu_{k}_ha"] = sumar(ov[ov["cobertura"] == c], "bid", "ha", f"evu_{k}_ha")
    S["evu_publico_ha"] = sumar(ov[ov["propiedad"].astype(str).str.contains("ublic", case=False, na=False)], "bid", "ha", "evu_publico_ha")
    # polígonos con cubierta verde, completos, para dibujarlos en el mapa (los que tocan algún barrio)
    tz = ev[ev["cubierta_verde"] == "Si"]
    tz = tz[tz.index.isin(gpd.sjoin(tz[["geometry"]], B, predicate="intersects").index)]
    tz[["categoria_msu", "geometry"]].to_file(os.path.join(D, "techos_evu.gpkg"), driver="GPKG")
    te = ov[ov["cubierta_verde"] == "Si"]
    S["techos_n"] = te.groupby("bid").size().reindex(S.index).fillna(0)
    S["techos_ha"] = sumar(te, "bid", "ha", "techos_ha")
    print("EVU listo", flush=True)
else:
    print("SIN EVU", flush=True)

# ---------- zonas verdes con potencial verde ----------
zp = cargar("zv_potencial")
c = zp.copy(); c["geometry"] = c.geometry.centroid
j = gpd.sjoin(c[["geometry"]], B, how="inner", predicate="within")
S["pot_n"] = j.groupby("bid").size().reindex(S.index).fillna(0)
zp["ha"] = zp.geometry.area / 1e4
zz = zp.join(j["bid"])
S["pot_ha"] = zz.groupby("bid")["ha"].sum().reindex(S.index).fillna(0)

# ---------- obras de mitigación, monitoreo, estudios, alerta temprana ----------
ob = cargar("obras")
if len(ob) < 131:   # un registro viene sin geometría: se ubica con las coordenadas nacionales del propio registro
    crudo = pd.concat([gpd.read_file(f) for f in sorted(glob.glob(os.path.join(DM, "obras", "*.geojson")))], ignore_index=True)
    falta = crudo[crudo.geometry.isna() | crudo.geometry.is_empty]
    print("obras sin geometría:", len(falta), falta[["nombre_barrio_vereda", "x_origen_nacional", "y_origen_nacional", "obra_ejecutada"]].to_string(), flush=True)
    ok = falta[falta["x_origen_nacional"].notna()]
    if len(ok):
        pts = gpd.GeoDataFrame(ok.drop(columns="geometry"), geometry=gpd.points_from_xy(ok["x_origen_nacional"], ok["y_origen_nacional"]), crs=9377)
        ob = pd.concat([ob, pts], ignore_index=True); ob = gpd.GeoDataFrame(ob, geometry="geometry", crs=9377)
S["obras"] = gpd.sjoin(ob[["geometry"]], B, predicate="within").groupby("bid").size().reindex(S.index).fillna(0)
mo = cargar("monit")
S["monit"] = gpd.sjoin(mo[["geometry"]], B, predicate="within").groupby("bid").size().reindex(S.index).fillna(0)
S["monit_activos"] = gpd.sjoin(mo[mo["estado"] == "Activo"][["geometry"]], B, predicate="within").groupby("bid").size().reindex(S.index).fillna(0)
es = cargar("estudios")
S["estudios"] = gpd.sjoin(es[["geometry"]], B, predicate="intersects").groupby("bid").size().reindex(S.index).fillna(0)
for nom in ("alarmas", "sensores", "encuentro"):
    g = cargar(nom)
    S[nom] = gpd.sjoin(g[["geometry"]], B, predicate="within").groupby("bid").size().reindex(S.index).fillna(0)
ru = cargar("rutas")
S["rutas"] = gpd.sjoin(ru[["geometry"]], B, predicate="intersects").groupby("bid").size().reindex(S.index).fillna(0)
S["sat_total"] = S[["alarmas", "sensores", "encuentro", "rutas"]].sum(axis=1)

# ---------- porcentajes ----------
for nom in ("mm", "inu", "tor"):
    for c in ("alta", "media", "baja"):
        S[f"{nom}_{c}"] = (S[f"{nom}_{c}_ha"] / S["ha"] * 100).round(2)
S = S.reset_index()
out = os.path.join(D, "barrios_stats.csv")
S.to_csv(out, index=False, encoding="utf-8-sig")
print("guardado:", out, S.shape, flush=True)
print(S[["ha", "mm_alta", "inu_alta", "tor_alta", "tor_alta_ha", "lst_n"] + [c for c in ("arboles", "evu_ha", "obras", "monit", "sat_total") if c in S.columns]].describe().round(2).to_string(), flush=True)
