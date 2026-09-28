# -*- coding: utf-8 -*-
"""Territorial distribution of SIRMED floods and forest fires (2021-2025) and comparison with UdeA fires and DAGRD tables."""
from osgeo import gdal  # noqa: F401
import sys
import pandas as pd
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)
d = pd.read_csv("ev85/sirmed_emergencias_2004_2026.csv", dtype={"Evento_id": int}, low_memory=False)
d["year"] = pd.to_datetime(d["fecha_registro"]).dt.year
d["terr"] = (d["comuna"].str.replace(r"^Comuna \d+ ", "", regex=True).str.replace("Corregimiento de ", "", regex=False)
             .str.replace("Laureles Estadio", "Laureles-Estadio", regex=False))
w = d[(d["year"].between(2021, 2025))]


def top(tipo, n=10):
    s = w[w["tipo_incidente"] == tipo].groupby("terr").size().sort_values(ascending=False)
    return s, (100 * s / s.sum()).round(1)


for tipo in ("Incendio forestal", "Inundaciones"):
    s, sh = top(tipo)
    print(f"\n{tipo} 2021-2025: total {int(s.sum())}")
    print(pd.DataFrame({"n": s, "%": sh}).head(10).to_string())
    if tipo == "Incendio forestal":
        corr = ["San Antonio de Prado", "San Cristóbal", "Altavista", "Santa Elena", "San Sebastián de Palmitas", "Palmitas"]
        print("share in the 5 corregimientos: %.1f %%" % (100 * s[s.index.isin(corr)].sum() / s.sum()))
        print("San Cristóbal + Altavista + Santa Elena: %.1f %%" % (100 * s[s.index.isin(["San Cristóbal", "Altavista", "Santa Elena"])].sum() / s.sum()))
dag = pd.read_csv("ev85/dagrd_eventos_por_territorio_2005_2018.csv", dtype={"cod": str})
fl = dag[(dag["amenaza"] == "inundación y avenida torrencial") & ~dag["territorio_raw"].str.startswith("Total")].groupby("territorio")["eventos"].sum()
s, _ = top("Inundaciones")
c = pd.concat([s.rename("sirmed_2021_25"), fl.rename("dagrd_2005_18")], axis=1).dropna()
print("\nfloods: Spearman SIRMED 2021-25 vs DAGRD 2005-18 (n=%d): %.2f" % (len(c), spearmanr(c.iloc[:, 0], c.iloc[:, 1])[0]))
fire16 = dag[(dag["amenaza"] == "incendio de cobertura vegetal") & ~dag["territorio_raw"].str.startswith("Total")].groupby("territorio")["eventos"].sum()
sf, _ = top("Incendio forestal")
c2 = pd.concat([sf.rename("sirmed_2021_25"), fire16.rename("dagrd_2016_18")], axis=1).dropna()
print("fires: Spearman SIRMED 2021-25 vs DAGRD 2016-18 (n=%d): %.2f" % (len(c2), spearmanr(c2.iloc[:, 0], c2.iloc[:, 1])[0]))
UDEA = {"San Cristóbal": 572, "Altavista": 275, "Santa Elena": 261, "Robledo": 51, "San Javier": 45, "Villa Hermosa": 43, "Manrique": 31}
u = pd.Series(UDEA)
c3 = pd.concat([sf.rename("sirmed"), u.rename("udea")], axis=1).dropna()
print("fires: SIRMED vs UdeA on the 7 territories with UdeA counts: Spearman %.2f" % spearmanr(c3["sirmed"], c3["udea"])[0])
print(c3.to_string())
