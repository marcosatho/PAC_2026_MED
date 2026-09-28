# -*- coding: utf-8 -*-
"""Update the monthly ONI series: keep the PSL file up to 2024-12 and take 2025-01..2026-07 from the official CPC table
(oni.ascii.txt, read on 2026-09-27). CPC gives 3-month seasons; each season is assigned to its centre month (DJF -> January)."""
import pandas as pd
CPC = {  # season, year, ONI (NOAA CPC table as read on 2026-09-27)
    ("DJF", 2025): -0.46, ("JFM", 2025): -0.22, ("FMA", 2025): -0.08, ("MAM", 2025): 0.02, ("AMJ", 2025): -0.04, ("MJJ", 2025): -0.02,
    ("JJA", 2025): -0.11, ("JAS", 2025): -0.26, ("ASO", 2025): -0.43, ("SON", 2025): -0.57, ("OND", 2025): -0.61, ("NDJ", 2025): -0.60,
    ("DJF", 2026): -0.39, ("JFM", 2026): -0.21, ("FMA", 2026): 0.11, ("MAM", 2026): 0.46, ("AMJ", 2026): 0.95, ("MJJ", 2026): 1.39, ("JJA", 2026): 1.80}
ORDER = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]
centre = {s: i + 2 for i, s in enumerate(ORDER)}          # DJF -> month 1 (Jan) ... NDJ -> month 12 (Dec); index i -> month i+1
centre = {s: i + 1 for i, s in enumerate(ORDER)}
old = pd.read_csv("C:/Users/marco/Downloads/oni.csv", header=0, names=["date", "oni"], parse_dates=["date"])
old = old[(old["oni"] > -99) & (old["date"] < "2025-01-01")]
new = pd.DataFrame([{"date": pd.Timestamp(year=y, month=centre[s], day=1), "oni": v} for (s, y), v in CPC.items()])
new = new.sort_values("date")
cmp = pd.read_csv("C:/Users/marco/Downloads/oni.csv", header=0, names=["date", "oni"], parse_dates=["date"]).merge(new, on="date", suffixes=("_psl", "_cpc"))
cmp["same_class"] = (cmp["oni_psl"].apply(lambda v: -1 if v <= -0.5 else (1 if v >= 0.5 else 0)) == cmp["oni_cpc"].apply(lambda v: -1 if v <= -0.5 else (1 if v >= 0.5 else 0)))
print(cmp.round(2).to_string())
print("same ENSO class in all overlapping months:", bool(cmp["same_class"].all()))
out = pd.concat([old.assign(fuente="NOAA PSL (archivo descargado el 22 may 2026)"), new.assign(fuente="NOAA CPC oni.ascii.txt (consultado el 27 sep 2026)")])
out[["date", "oni"]].to_csv("oni_actualizado_2026-09-27.csv", index=False, header=["Date", "ONI"], date_format="%Y-%m-%d")
out.to_csv("oni_actualizado_2026-09-27_con_fuente.csv", index=False, header=["Date", "ONI", "fuente"], date_format="%Y-%m-%d")
print("last rows:"); print(out.tail(5).to_string())
