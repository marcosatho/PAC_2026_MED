# -*- coding: utf-8 -*-
"""Arma los datos del paquete del Producto 9 en una carpeta de preparación: tablas (CSV y Excel), capas SIG (GeoPackage, EPSG:9377) y copias de las entradas del proyecto."""
import glob, json, os, shutil, sys, warnings
import numpy as np, pandas as pd, geopandas as gpd
warnings.filterwarnings("ignore")

D = os.path.dirname(os.path.abspath(__file__))
DM = os.path.join(D, "datos_medidas")
OUT = os.path.join(D, "paquete_p9")
A, B, C = (os.path.join(OUT, "02_DATOS", n) for n in ("A_tablas", "B_capas_SIG", "C_entradas_del_proyecto"))
for p in (A, B, C):
    os.makedirs(p, exist_ok=True)

BASE = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental"
RES = BASE + r"\00_RESPALDO_PAC_2026_Referencias_7.1_8.1_8.5_8.6"
LIM = BASE + r"\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910"
FECHA = "2026-10-08"

def cargar(n):
    fs = sorted(glob.glob(os.path.join(DM, n, "*.geojson")))
    g = pd.concat([gpd.read_file(f) for f in fs], ignore_index=True)
    g = gpd.GeoDataFrame(g, geometry="geometry", crs=9377)
    if "objectid" in g.columns:
        g = g.drop_duplicates("objectid")
    return g

# ---------- tablas por barrio y vereda ----------
S = pd.read_csv(os.path.join(D, "barrios_indicadores.csv"), dtype={"codigo": str, "comuna": str}, encoding="utf-8-sig")
S["urbano"] = S["urbano"].astype(bool)
for f in ("f_calor", "f_ladera", "f_alerta"):
    S[f] = S[f].astype(bool)
d1 = json.load(open(os.path.join(os.path.dirname(D), "mapa", "mapa_datos.json"), encoding="utf-8"))
nom = {t["codigo"]: t["nombre"] for t in d1["terr"]}
S.insert(4, "comuna_nombre", S["comuna"].map(nom))
S.to_csv(os.path.join(A, "P9_barrios_veredas_indicadores_v2.csv"), index=False, encoding="utf-8-sig")
marcas = []
for k, f, txt in (("calor", "f_calor", "Calor alto y poco arbolado"), ("ladera", "f_ladera", "Deslizamiento alto sin obra ni monitoreo"), ("alerta", "f_alerta", "Avenida torrencial alta sin alerta temprana")):
    t = S[S[f]][["bid", "codigo", "nombre", "comuna", "comuna_nombre", "ha", "lst_n", "copa_pct", "arb_ha", "mm_alta", "tor_alta_ha", "obras", "monit", "sat_total"]].copy()
    t.insert(0, "brecha", txt)
    marcas.append(t)
pd.concat(marcas).to_csv(os.path.join(A, "P9_brechas_barrios_marcados_v2.csv"), index=False, encoding="utf-8-sig")

# ---------- tabla por comuna y corregimiento (misma lógica de la página) ----------
d2 = json.load(open(os.path.join(os.path.dirname(D), "mapa", "mapa_datos_v2.json"), encoding="utf-8"))
MV = [1, 2, 3, 4, 6, 8, 9, 12, 18, 27]
filas = []
for t in d2["terr"]:
    by = {v: 0.0 for v in MV}; s = 0.0
    for k, x in (t.get("comb") or {}).items():
        p = int(np.prod([int(i) for i in k.split("-")])); by[p] += x; s += x
    if s > 0:
        by = {v: by[v] / s * 100 for v in MV}
    acc, med = 0.0, None
    for v in MV:
        acc += by[v]
        if acc >= 50:
            med = v; break
    r = {k: v for k, v in t.items() if k != "comb"}
    r.update(d2["med"]["terr"].get(t["codigo"], {}))
    r["multiamenaza_mediana"] = med
    r["multiamenaza_ge4_pct"] = round(sum(by[v] for v in MV if v >= 4), 2)
    for v in MV:
        r["multiamenaza_%d_pct" % v] = round(by[v], 2)
    filas.append(r)
T = pd.DataFrame(filas)
T.to_csv(os.path.join(A, "P9_comunas_corregimientos_indicadores_v2.csv"), index=False, encoding="utf-8-sig")

# ---------- capas derivadas (GeoPackage, EPSG:9377) ----------
bar = gpd.read_file(LIM + r"\barrios_veredas_4326.geojson").to_crs(9377)
bar["bid"] = bar["objectid"].astype(int)
gb = bar[["bid", "geometry"]].merge(S, on="bid")
gb.to_file(os.path.join(B, "P9_capas_derivadas_9377.gpkg"), layer="barrios_veredas_indicadores", driver="GPKG")
com = gpd.read_file(LIM + r"\comunas_corregimientos_4326.geojson").to_crs(9377)
com["codigo"] = com["codigo"].astype(str)
gc = com[["codigo", "geometry"]].merge(T, on="codigo")
gc.to_file(os.path.join(B, "P9_capas_derivadas_9377.gpkg"), layer="comunas_corregimientos_indicadores", driver="GPKG")
mp = os.path.join(D, "multiamenaza_piezas.gpkg")
if os.path.exists(mp):
    gpd.read_file(mp).to_file(os.path.join(B, "P9_capas_derivadas_9377.gpkg"), layer="multiamenaza_piezas", driver="GPKG")
    print("multiamenaza incluida")
else:
    print("SIN multiamenaza_piezas.gpkg")

# ---------- capas del servidor de mapas de la Alcaldía, tal como se descargaron ----------
srv = os.path.join(B, "P9_capas_servidor_alcaldia_%s_9377.gpkg" % FECHA)
if os.path.exists(srv):
    os.remove(srv)
capas = [("amenaza_incendios_forestales", "incendios"), ("obras_mitigacion", "obras"), ("monitoreo_geotecnico", "monit"), ("estudios_y_disenos", "estudios"),
         ("alarmas_SAT", "alarmas"), ("sensores_nivel_SAT", "sensores"), ("puntos_encuentro", "encuentro"), ("rutas_evacuacion", "rutas"),
         ("zonas_verdes_potencial_verde", "zv_potencial"), ("ecoparques", "ecoparques"), ("corredores_verdes_POT2014", "corredores")]
for lay, n in capas:
    g = cargar(n)
    g.to_file(srv, layer=lay, driver="GPKG")
    print(lay, len(g), flush=True)
tz = gpd.read_file(os.path.join(D, "techos_evu.gpkg"))
tz.to_file(srv, layer="techos_verdes_cubierta_verde_EVU2019", driver="GPKG")
print("techos", len(tz), flush=True)

# ---------- árboles y espacios verdes (capas grandes, cada una en su archivo) ----------
ar = cargar("arboles")
ar.to_file(os.path.join(B, "P9_arboles_medellin_%s_9377.gpkg" % FECHA), layer="arboles", driver="GPKG")
print("árboles", len(ar), flush=True)
ev = cargar("evu")
ev.to_file(os.path.join(B, "P9_espacios_verdes_urbanos_2019_9377.gpkg"), layer="espacios_verdes_urbanos", driver="GPKG")
print("EVU", len(ev), flush=True)

# ---------- copias de las entradas del proyecto (ya están en el Drive del P1) ----------
for src, dst in [(RES + r"\8.1_datos_pot2026_amenaza_inundacion_9377.gpkg", "POT2026_amenaza_inundacion_9377.gpkg"),
                 (RES + r"\8.1_datos_pot2026_amenaza_avenidas_torrenciales_9377.gpkg", "POT2026_amenaza_avenidas_torrenciales_9377.gpkg"),
                 (RES + r"\8.1_datos_pot2026_amenaza_movimientos_masa_clase_9377.tif", "POT2026_amenaza_movimientos_masa_clase_9377.tif"),
                 (RES + r"\8.1_datos_LST_por_comuna_corregimiento_Mediana_LST.csv", "LST_por_comuna_corregimiento_mediana.csv"),
                 (RES + r"\8.1_datos_LST_por_comuna_corregimiento_Mediana_LST_norm.csv", "LST_por_comuna_corregimiento_mediana_sin_pendiente.csv"),
                 (RES + r"\8.1_datos_LST_norm_por_barrio.csv", "LST_por_barrio_mediana_sin_pendiente.csv"),
                 (LIM + r"\comunas_corregimientos_4326.geojson", "limites_comunas_corregimientos_4326.geojson"),
                 (LIM + r"\barrios_veredas_4326.geojson", "limites_barrios_veredas_4326.geojson")]:
    shutil.copy2(src, os.path.join(C, dst))
print("entradas copiadas")
for p in (A, B, C):
    for f in sorted(os.listdir(p)):
        print("  %-80s %8.1f MB" % (os.path.relpath(os.path.join(p, f), OUT), os.path.getsize(os.path.join(p, f)) / 1048576))
print("columnas barrios:", list(S.columns))
print("columnas comunas:", list(T.columns))
