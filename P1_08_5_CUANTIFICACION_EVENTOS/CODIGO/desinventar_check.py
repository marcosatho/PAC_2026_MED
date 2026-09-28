# -*- coding: utf-8 -*-
"""Cross-check DesInventar (Medellín) against Geohazards on major landslide events and decade deaths; describe its loss coverage."""
from osgeo import gdal  # noqa: F401
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 90)
d = pd.read_pickle("ev85/desinventar/desinventar_medellin.pkl")
big = d[d["muertos"] >= 15].sort_values("fecha")
print(big[["serial", "evento", "fecha", "muertos", "viv_destruidas", "lugar"]].to_string())
ls = d[d["evento"].isin(["LANDSLIDE", "SPATE"])].copy()
ls["decada"] = (ls["anio"] // 10) * 10
g = pd.read_csv("ev85/geohazards_medellin_limpio.csv")
g = g[~g["dup_same_day_110m"]]
gd = g.groupby((g["year"] // 10) * 10).agg(geohaz_registros=("id", "size"), geohaz_muertos=("fatalities_verified", "sum"))
dd = ls.groupby("decada").agg(desinv_registros=("serial", "size"), desinv_muertos=("muertos", "sum"))
print(pd.concat([dd, gd], axis=1).fillna(0).astype(int).to_string())
print("\nloss coverage: records with local-currency loss by decade:", d[d["perdidas_cop"] > 0].groupby((d["anio"] // 10) * 10).size().to_dict())
print("last year with a loss value:", int(d.loc[(d["perdidas_cop"] > 0) | (d["perdidas_usd"] > 0), "anio"].max()))
print("records 1997-2017:", int((d["anio"] >= 1997).sum()), "| with any loss value:", int(((d["anio"] >= 1997) & ((d["perdidas_cop"] > 0) | (d["perdidas_usd"] > 0))).sum()))
big_loss = d[d["perdidas_cop"] > 1e9][["serial", "evento", "fecha", "perdidas_cop", "comentarios"]]
print(big_loss.to_string())
print("\ndeaths in DesInventar 2005-2017 (all events):", int(d[d["anio"].between(2005, 2017)]["muertos"].sum()), "| Geohazards 2005-2017:", int(g[g["year"].between(2005, 2017)]["fatalities_verified"].sum()))
