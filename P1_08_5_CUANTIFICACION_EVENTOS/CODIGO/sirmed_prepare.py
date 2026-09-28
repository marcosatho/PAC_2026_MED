# -*- coding: utf-8 -*-
"""Merge the yearly SIRMED 'Histórico de Emergencias' layer (capas/range, layer=emergencias), 2004-2026, remove repeated
events, cross-check against the manual CSV download and print annual counts by incident type.

usage: sirmed_prepare.py <api_dir> <manual_csv> <out_dir>"""
from osgeo import gdal  # noqa: F401
import glob
import json
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40)
API, MAN, OUT = sys.argv[1:4]
rows = []
for f in sorted(glob.glob(f"{API}/emergencias_*.json")):
    j = json.load(open(f, encoding="utf-8"))
    data = (j.get("capa") or {}).get("data") or []
    for r in data:
        r["_file_year"] = int(f.split("_")[-1].split(".")[0])
    rows += data
    print(f.split("/")[-1], len(data))
d = pd.DataFrame(rows)
print("\nraw rows:", len(d), "| columns:", d.columns.tolist())
d["fecha"] = pd.to_datetime(d["fecha_registro"], errors="coerce")
print("bad dates:", int(d["fecha"].isna().sum()), "| range:", d["fecha"].min(), "->", d["fecha"].max())
dup = d.duplicated("Evento_id", keep="first")
print("repeated Evento_id:", int(dup.sum()))
d = d[~dup].copy()
d["year"] = d["fecha"].dt.year
d["numero_fallecidos"] = pd.to_numeric(d["numero_fallecidos"], errors="coerce").fillna(0).astype(int)
d["numero_lesionados"] = pd.to_numeric(d["numero_lesionados"], errors="coerce").fillna(0).astype(int)
print("unique events:", len(d))

# cross-check with the manual CSV (22 months)
m = pd.read_csv(glob.glob(MAN)[0], encoding="utf-8-sig", low_memory=False)
m["fecha"] = pd.to_datetime(m["fecha_registro"])
win = d[(d["fecha"] >= m["fecha"].min()) & (d["fecha"] <= m["fecha"].max())]
print("\nmanual CSV rows:", len(m), "| API rows in the same window:", len(win), "| ids only in manual:", len(set(m["Evento_id"]) - set(win["Evento_id"])),
      "| ids only in API:", len(set(win["Evento_id"]) - set(m["Evento_id"])))

print("\nannual counts by incident type (all types):")
t = d.pivot_table(index="year", columns="tipo_incidente", values="Evento_id", aggfunc="count").fillna(0).astype(int)
print(t.to_string())
print("\nannual totals:", d.groupby("year").size().to_dict())
print("deaths by year:", d.groupby("year")["numero_fallecidos"].sum().to_dict())
d.drop(columns=["fecha"]).to_csv(f"{OUT}/sirmed_emergencias_2004_2026.csv", index=False, encoding="utf-8-sig")
print("saved", f"{OUT}/sirmed_emergencias_2004_2026.csv")
