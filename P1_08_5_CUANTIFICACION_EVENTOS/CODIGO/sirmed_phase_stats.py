# -*- coding: utf-8 -*-
"""SIRMED monthly counts by ENSO phase using the NOAA episode rule (>= 5 consecutive months)."""
from osgeo import gdal  # noqa: F401
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from enso_episodes import load_oni, classify

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)
d = pd.read_csv("ev85/sirmed_emergencias_2004_2026.csv", low_memory=False)
d["ym"] = pd.to_datetime(d["fecha_registro"]).dt.to_period("M")
oni = load_oni("oni_actualizado_2026-09-27.csv")
idx = pd.period_range("2021-01", "2026-09", freq="M")
c = classify(oni, idx)
c.loc[c["fase"] == "sin dato", "fase"] = "El Niño*"          # author's assumption for Aug-Sep 2026
M = c.copy()
for k, t in {"mm": "Movimiento en masa", "inund": "Inundaciones", "fuego": "Incendio forestal"}.items():
    M[k] = d[d["tipo_incidente"] == t].groupby("ym").size().reindex(idx).fillna(0)
print(M["fase"].value_counts().to_dict())
print("\nphase by year:"); print(M.groupby([M.index.year, "fase"]).size().unstack(fill_value=0).to_string())
obs = M[~M["fase"].str.endswith("*")]
print("\nmeans per phase (months with an established phase):")
print(obs.groupby("fase")[["mm", "inund", "fuego"]].agg(["mean", "size"]).round(1).to_string())
print("\nwindow 2021-01..2025-12 only:")
w = obs.loc[:"2025-12"]
print(w.groupby("fase")[["mm", "inund", "fuego"]].agg(["mean", "size"]).round(1).to_string())
print("\nprovisional months:", M[M["fase"].str.endswith("*")][["oni", "mm", "inund", "fuego"]].to_string())
print("fires May-Sep 2026:", int(M.loc["2026-05":"2026-09", "fuego"].sum()))
# Fig-1 check: months in La Niña episodes per year, 2005-2018
c2 = classify(oni, pd.period_range("2005-01", "2018-12", freq="M"))
print("\nLa Niña months per year (episode rule):", c2[c2["fase"] == "La Niña"].groupby(c2[c2["fase"] == "La Niña"].index.year).size().to_dict())
