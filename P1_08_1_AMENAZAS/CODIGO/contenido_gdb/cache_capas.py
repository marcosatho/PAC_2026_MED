# -*- coding: utf-8 -*-
"""Solo lectura: lee las 82 capas de datos de la geodatabase del DAP (zip en Drive), las guarda en pickles locales (scratchpad)
y escribe un resumen de campos y valores para escoger cómo colorear cada mapa. No modifica nada del zip."""
import os, sys, json, time, warnings
import pandas as pd
import geopandas as gpd
import pyogrio
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")

ZIP = None  # el zip no se lee directamente: ver LEEME (se descomprime la carpeta mj_rev_pot_2025_med.gdb en la subcarpeta gdb)
GDB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gdb", "mj_rev_pot_2025_med.gdb")
AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(AQUI, "cache")
os.makedirs(CACHE, exist_ok=True)

capas = pyogrio.list_layers(GDB)
nombres = [n for n, g in capas if not n.startswith("T_") and not n.startswith("GDB_") and n.lower() != "topologia"]
print("capas en la gdb:", len(capas), "| de datos:", len(nombres))
solo = [s for s in os.environ.get("SOLO", "").split(",") if s]
resumen = {}
for n in nombres:
    if solo and n not in solo:
        continue
    t0 = time.time()
    try:
        gdf = pyogrio.read_dataframe(GDB, layer=n, force_2d=True)
    except Exception as e:
        print("ERROR", n, str(e)[:100]); continue
    crs = gdf.crs.to_epsg() if gdf.crs else None
    gdf.to_pickle(os.path.join(CACHE, n + ".pkl"))
    info = dict(n=len(gdf), crs=crs, geom=str(gdf.geom_type.value_counts().to_dict()), cols=[c for c in gdf.columns if c != "geometry"])
    cat = {}
    for c in info["cols"]:
        s = gdf[c]
        if s.dtype == object and 1 < s.nunique() <= 14:
            cat[c] = {str(k): int(v) for k, v in s.value_counts().head(14).items()}
    info["cat"] = cat
    resumen[n] = info
    print(f"{n:38s} {len(gdf):>7d} crs={crs} {time.time() - t0:5.1f}s")
json.dump(resumen, open(os.path.join(AQUI, "resumen_campos%s.json" % ("_" + "_".join(solo) if solo else "")), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("FIN")
