# -*- coding: utf-8 -*-
"""Annual and monthly SIRMED series (2021-2026) for rain- and fire-related incident types; territory ranking of landslides."""
from osgeo import gdal  # noqa: F401
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40)
d = pd.read_csv("ev85/sirmed_emergencias_2004_2026.csv", dtype={"Evento_id": int}, low_memory=False)
d["fecha"] = pd.to_datetime(d["fecha_registro"])
d["year"] = d["fecha"].dt.year
d["month"] = d["fecha"].dt.month
print("pre-2021 records:", int((d["year"] < 2021).sum()), "| 2021+:", int((d["year"] >= 2021).sum()))
print("pre-2021 tipo_incidente:", d.loc[d["year"] < 2021, "tipo_incidente"].value_counts(dropna=False).head(6).to_dict())
KEEP = ["Movimiento en masa", "Inundaciones", "Incendio forestal", "Quemas vía pública", "Desplome de árbol"]
t = d[d["year"] >= 2021].pivot_table(index="year", columns="tipo_incidente", values="Evento_id", aggfunc="count").fillna(0).astype(int)[KEEP]
print(t.to_string())
# same months (Jan-Sep 24) for comparability of the partial year 2026
d["jan_sep"] = d["fecha"].dt.dayofyear <= pd.Timestamp("2026-09-25").dayofyear
ts = d[(d["year"] >= 2021) & d["jan_sep"]].pivot_table(index="year", columns="tipo_incidente", values="Evento_id", aggfunc="count").fillna(0).astype(int)[KEEP]
print("\nJan 1 - Sep 25 only:\n", ts.to_string())
tot = d[d["year"] >= 2021].groupby("year").size()
print("\nall incident types per year:", tot.to_dict())
print("\nmass movements by subtype 'tipo_incidente_fenomeno' (non-null):", d.loc[(d["tipo_incidente"] == "Movimiento en masa"), "tipo_incidente_fenomeno"].value_counts(dropna=False).to_dict())
mm = d[(d["tipo_incidente"] == "Movimiento en masa") & (d["year"] >= 2021)]
print("mm records:", len(mm), "| deaths:", int(mm["numero_fallecidos"].sum()), "| injured:", int(mm["numero_lesionados"].sum()))
fl = d[(d["tipo_incidente"] == "Inundaciones") & (d["year"] >= 2021)]
print("floods records:", len(fl), "| deaths:", int(fl["numero_fallecidos"].sum()), "| injured:", int(fl["numero_lesionados"].sum()))
ff = d[(d["tipo_incidente"] == "Incendio forestal") & (d["year"] >= 2021)]
print("forest fires records:", len(ff))
print("deaths all types by type:", d.groupby("tipo_incidente")["numero_fallecidos"].sum().loc[lambda s: s > 0].to_dict())

# monthly mass movements (2021-2025)
mo = mm[mm["year"] <= 2025].groupby("month").size()
print("\nmm by month 2021-2025:", mo.to_dict(), "| share Apr-Jun + Sep-Nov: %.1f %%" % (100 * mo.loc[[4, 5, 6, 9, 10, 11]].sum() / mo.sum()))
mo_f = ff[ff["year"] <= 2025].groupby("month").size()
print("forest fires by month 2021-2025:", mo_f.to_dict())

# territory ranking of landslides 2021-2025 vs DAGRD 2005-2018 and vs hazard share
mm5 = mm[mm["year"] <= 2025].copy()
mm5["cod"] = mm5["comuna"].str.extract(r"Comuna (\d+)")[0]
by = mm5.dropna(subset=["cod"]).groupby("cod").size()
by.index = by.index.astype(int).astype(str).str.zfill(2)
dag = pd.read_csv("ev85/dagrd_movimientos_masa_por_territorio_2005_2018.csv", dtype={"cod": str})
dag = dag.set_index("cod")
common = [c for c in by.index if c in dag.index and int(c) < 50]
cmp = pd.DataFrame({"sirmed_2021_25": by.loc[common], "dagrd_2005_18": dag.loc[common, "eventos"], "territorio": dag.loc[common, "territorio"]})
print("\nSpearman SIRMED 2021-25 vs DAGRD 2005-18 (comunas):", round(spearmanr(cmp["sirmed_2021_25"], cmp["dagrd_2005_18"])[0], 2), "n =", len(cmp))
cmp["share_sirmed"] = 100 * cmp["sirmed_2021_25"] / by.loc[[c for c in by.index if int(c) < 50]].sum()
print(cmp.sort_values("sirmed_2021_25", ascending=False).round(1).to_string())
print("comunas w/o code (corregimientos etc.):", mm5[mm5["cod"].isna()]["comuna"].value_counts().head(8).to_dict())
