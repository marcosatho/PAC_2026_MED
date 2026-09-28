# -*- coding: utf-8 -*-
"""Numbers quoted in the 8.5 draft: DAGRD fires by territory 2016-2018, flood series, UNGRD climate totals, Geohazards 2020s."""
from osgeo import gdal  # noqa: F401
import json
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)
EV = "ev85"
d = pd.read_csv(f"{EV}/dagrd_eventos_por_territorio_2005_2018.csv", dtype={"cod": str})
f = d[(d["amenaza"] == "incendio de cobertura vegetal") & ~d["territorio_raw"].str.startswith("Total")]
by = f.groupby(["cod", "territorio"])["eventos"].sum().reset_index().sort_values("eventos", ascending=False)
by["corr"] = by["cod"].astype(int) >= 50
tot_rows = by["eventos"].sum()
print("fires 2016-2018 sum of rows:", tot_rows, "| printed totals sum:", 536 + 214 + 226)
print(by.assign(share_rows=(100 * by["eventos"] / tot_rows).round(1)).to_string())
print("corregimientos share of rows: %.1f %%" % (100 * by.loc[by["corr"], "eventos"].sum() / tot_rows))
print("top 3 territories:", by.head(3)[["territorio", "eventos"]].values.tolist())

# floods and torrential floods
tot = d[d["territorio_raw"].str.startswith("Total")].pivot_table(index="anio", columns="amenaza", values="eventos", aggfunc="sum")
fl = tot["inundación y avenida torrencial"]
print("\nfloods total", int(fl.sum()), "| one every %.1f days" % (5113 / fl.sum()), "| max", fl.idxmax(), int(fl.max()), "| per day in max year %.2f" % (fl.max() / 366))
print("mean 2006-2011: %.0f | mean 2015-2018: %.0f" % (fl.loc[2006:2011].mean(), fl.loc[2015:2018].mean()))
fd = d[(d["amenaza"] == "inundación y avenida torrencial") & ~d["territorio_raw"].str.startswith("Total")]
b2 = fd.groupby("territorio")["eventos"].sum().sort_values(ascending=False)
print("floods by territory top 6:", b2.head(6).to_dict(), "| share top 4: %.1f %%" % (100 * b2.head(4).sum() / b2.sum()))

# UNGRD climate totals (deduplicated)
u = pd.DataFrame(json.load(open(f"{EV}/ungrd_medellin_raw.json", encoding="utf-8")))
u = u.drop_duplicates()
for c in ["fallecidos", "heridos", "personas", "viviendas_destruidas", "viviendas_averiadas", "hectareas"]:
    u[c] = pd.to_numeric(u[c], errors="coerce")
clim = u[u["evento"].isin(["MOVIMIENTO EN MASA", "INUNDACION", "CRECIENTE SUBITA", "AVENIDA TORRENCIAL", "INCENDIO DE COBERTURA VEGETAL", "VENDAVAL", "AMENAZAS CONCATENADAS O COMPLEJAS"])]
print("\nUNGRD 2019-2022 climate events:", len(clim), "| deaths", int(clim["fallecidos"].sum()), "| injured", int(clim["heridos"].sum()),
      "| people affected", int(clim["personas"].sum()), "| homes destroyed", int(clim["viviendas_destruidas"].sum()), "| homes damaged", int(clim["viviendas_averiadas"].sum()))
water = clim[clim["evento"].isin(["INUNDACION", "CRECIENTE SUBITA", "AVENIDA TORRENCIAL"])]
print("UNGRD floods+torrential+flash:", len(water), "| deaths", int(water["fallecidos"].sum()), "| people", int(water["personas"].sum()),
      "| homes damaged", int(water["viviendas_averiadas"].sum()), "| destroyed", int(water["viviendas_destruidas"].sum()))
mmv = clim[clim["evento"] == "MOVIMIENTO EN MASA"]
print("UNGRD mass movements:", len(mmv), "| deaths", int(mmv["fallecidos"].sum()), "| homes destroyed", int(mmv["viviendas_destruidas"].sum()), "| damaged", int(mmv["viviendas_averiadas"].sum()))

# Geohazards 2020s and biggest recent events
g = pd.read_csv(f"{EV}/geohazards_medellin_limpio.csv")
g = g[~g["dup_same_day_110m"]].copy()
g["fatalities"] = g["fatalities_verified"]
g20 = g[g["year"] >= 2020]
print("\nGeohazards 2020-2026 records:", len(g20), "| 2021+2022:", int(g20["year"].isin([2021, 2022]).sum()), "(%.0f %%)" % (100 * g20["year"].isin([2021, 2022]).mean()))
print("Geohazards 2010s records:", int(((g["year"] >= 2010) & (g["year"] <= 2019)).sum()))
print(g[(g["year"] >= 2000) & (g["fatalities"] >= 5)][["date", "fatalities", "type_es", "site", "county", "source"]].to_string())
print("\nrecent events with deaths (2015+):")
print(g[(g["year"] >= 2015) & (g["fatalities"] > 0)][["date", "fatalities", "type_es", "site", "county", "source"]].to_string())
