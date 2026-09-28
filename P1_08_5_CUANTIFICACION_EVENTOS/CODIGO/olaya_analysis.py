# -*- coding: utf-8 -*-
"""Daily and monthly air-temperature series of the IDEAM station Aeropuerto Olaya Herrera (27015330, Medellin, 1,490 m), 2014-12 to 2026-09.

Inputs (pulled from datos.gov.co by olaya_fetch.py): hourly mean (sbwg-7ju4, sensor 0068), hourly maximum (ccvq-rp9s), hourly minimum (afdg-3zpb).
Quality control: physical range, duplicated stamps dropped, a day is valid with >= 18 distinct hours; a month is valid with >= 24 valid days.
Reference: IDEAM climatological normals 1991-2020 of the same station (datos.gov.co nsz2-kzcq): monthly mean of the daily maximum / minimum / mean.
ENSO phase of each month: NOAA episode rule (enso_episodes.classify); months after the last published index are labelled 'El Nino*' (author's assumption).

usage: olaya_analysis.py <out_dir>   (writes olaya_diaria.csv, olaya_mensual.csv, prints the statistics quoted in the text)"""
from osgeo import gdal  # noqa: F401
import sys
import numpy as np
import pandas as pd
from enso_episodes import load_oni, classify

sys.stdout.reconfigure(encoding="utf-8")
OUT = sys.argv[1]
SRC = "ev85/olaya/olaya_%s.csv"
RANGE = {"tmean_sbwg-7ju4": (8, 38), "tmax_ccvq-rp9s": (10, 40), "tmin_afdg-3zpb": (5, 30)}
NORM = {  # IDEAM normals 1991-2020, Aeropuerto Olaya Herrera, Jan..Dec
    "tmax": [27.8, 28.3, 28.1, 27.7, 27.9, 28.4, 28.6, 28.7, 28.1, 27.3, 27.1, 27.3],
    "tmin": [17.5, 17.8, 18.0, 17.9, 17.9, 17.7, 17.5, 17.6, 17.5, 17.4, 17.6, 17.6],
    "tmean": [23.0, 23.3, 23.1, 22.8, 23.0, 23.7, 24.0, 23.9, 23.2, 22.2, 22.0, 22.5]}


def load(name, lo, hi):
    d = pd.read_csv(SRC % name)
    d["t"] = pd.to_datetime(d["fechaobservacion"])
    d["v"] = pd.to_numeric(d["valorobservado"], errors="coerce")
    d["year"] = d["t"].dt.year
    n0 = d.groupby("year").size()
    d = d[d["v"].between(lo, hi)].drop_duplicates(subset=["t"], keep="first").copy()
    d["day"] = d["t"].dt.floor("D")
    d["hour"] = d["t"].dt.floor("h")
    return d, n0


# hourly mean = reference to validate the sensors of maximum and minimum (from 2024 they contain spikes to 45 C and false minima near 0 C)
mh, n_m = load("tmean_sbwg-7ju4", 8, 38)
ref = mh.groupby("hour")["v"].mean()
# spike filter on the hourly mean itself: drop hours that differ by more than 6 C from the median of the 5 surrounding hours
r = ref.reindex(pd.date_range(ref.index.min(), ref.index.max(), freq="h"))
med = r.rolling(5, center=True, min_periods=3).median()
bad_ref = (r - med).abs() > 6
ref = r[~bad_ref].dropna()
print(f"hourly mean: {len(ref)} valid hours ({int(bad_ref.sum())} spikes dropped)")
qc_rows = []


def daily_ext(name, how, lo, hi, sign):
    d, n0 = load(name, lo, hi)
    d["ref"] = d["hour"].map(ref)
    diff = sign * (d["v"] - d["ref"])                  # tmax: v - mean (>= 0); tmin: mean - v  ->  sign = -1 gives mean - v ... handled below
    has_ref = d["ref"].notna()
    ok = has_ref & diff.between(-1.0, 4.5)
    n_norefs = int((~has_ref).sum())
    keep = d[ok].copy()
    q = pd.DataFrame({"raw": n0, "in_range_unique": d.groupby("year").size(), "kept": keep.groupby("year").size()}).fillna(0).astype(int)
    q["variable"] = how
    qc_rows.append(q.reset_index())
    print(f"{name}: raw {int(n0.sum())} | in physical range & unique {len(d)} | no hourly-mean reference {n_norefs} | kept {len(keep)}")
    g = keep.groupby("day")
    out = pd.DataFrame({how: g["v"].agg("max" if how == "tmax" else "min"), "n_h": g["hour"].nunique()})
    return out[out["n_h"] >= 18]


dx = daily_ext("tmax_ccvq-rp9s", "tmax", 12, 36.5, +1)
dn = daily_ext("tmin_afdg-3zpb", "tmin", 12, 32, -1)
g = ref.groupby(ref.index.floor("D"))
dm = pd.DataFrame({"tmean": g.mean(), "n_h": g.size()})
dm = dm[dm["n_h"] >= 18]
print(f"valid days: tmax {len(dx)} | tmin {len(dn)} | tmean {len(dm)}")
pd.concat(qc_rows).to_csv(f"{OUT}/olaya_control_calidad_por_anio.csv", index=False, encoding="utf-8-sig")
D = dx[["tmax"]].join(dn[["tmin"]], how="outer").join(dm[["tmean"]], how="outer")
D.index.name = "date"
# consistency: daily max must not be below the daily mean or the daily min
inc = D[(D["tmax"] < D["tmean"]) | (D["tmax"] < D["tmin"])]
print("inconsistent days (tmax < tmean or < tmin):", len(inc))
D.loc[inc.index, ["tmax"]] = np.nan
D.to_csv(f"{OUT}/olaya_diaria.csv", encoding="utf-8-sig")
D["ym"] = D.index.to_period("M")
D["year"] = D.index.year

# ---- coverage
cov = D.groupby("year")[["tmax", "tmin", "tmean"]].count()
print("\nvalid days per year:\n", cov.to_string())

# ---- distribution and records of the daily maximum
tx = D["tmax"].dropna()
print("\ndaily Tmax quantiles:", {q: round(float(tx.quantile(q)), 1) for q in (0.05, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99)}, "| max", tx.max(), tx.idxmax().date())
print("top 12 days:", [(str(i.date()), v) for i, v in tx.sort_values(ascending=False).head(12).items()])
tn = D["tmin"].dropna()
print("daily Tmin: lowest", tn.min(), tn.idxmin().date(), "| highest", tn.max(), tn.idxmax().date())

# ---- monthly table
idx = pd.period_range("2014-12", "2026-09", freq="M")
M = pd.DataFrame(index=idx)
for v in ("tmax", "tmin", "tmean"):
    g = D.groupby("ym")[v]
    M[v] = g.mean()
    M[f"n_{v}"] = g.count()
    M.loc[M[f"n_{v}"] < 24, v] = np.nan
for thr in (28, 29, 30, 31):
    M[f"d{thr}"] = D.assign(f=(D["tmax"] > thr).where(D["tmax"].notna())).groupby("ym")["f"].sum()
M.loc[M["tmax"].isna(), [f"d{t}" for t in (28, 29, 30, 31)]] = np.nan
for v in ("tmax", "tmin", "tmean"):
    M[f"anom_{v}"] = M[v] - np.array([NORM[v][p.month - 1] for p in M.index])
oni = load_oni("oni_actualizado_2026-09-27.csv")
cl = classify(oni, idx)
cl.loc[cl["fase"] == "sin dato", "fase"] = "El Niño*"
M["fase"] = cl["fase"].replace({"neutro": "Neutro"})
M["oni"] = cl["oni"]
M.rename_axis("mes").reset_index().assign(mes=lambda x: x["mes"].astype(str)).to_csv(f"{OUT}/olaya_mensual.csv", index=False, encoding="utf-8-sig")

pd.set_option("display.width", 220)
print("\nmonthly anomalies vs 1991-2020 normals (deg C): mean by phase")
print(M.groupby("fase")[["anom_tmax", "anom_tmin", "anom_tmean", "d28", "d29", "d30"]].agg(["mean", "count"]).round(2).to_string())
print("\nphase counts:", M["fase"].value_counts().to_dict())

# ---- annual (complete years) and Jan-Sep comparison
A = pd.DataFrame({"tmax": M.groupby(M.index.year)["tmax"].mean(), "tmin": M.groupby(M.index.year)["tmin"].mean(), "tmean": M.groupby(M.index.year)["tmean"].mean(),
                  "n_mes": M.groupby(M.index.year)["tmax"].count(), "d28": M.groupby(M.index.year)["d28"].sum(), "d29": M.groupby(M.index.year)["d29"].sum(),
                  "d30": M.groupby(M.index.year)["d30"].sum(), "anom_tmax": M.groupby(M.index.year)["anom_tmax"].mean(), "anom_tmin": M.groupby(M.index.year)["anom_tmin"].mean(),
                  "anom_tmean": M.groupby(M.index.year)["anom_tmean"].mean()})
print("\nannual (valid months only):\n", A.round(2).to_string())
js = M[M.index.month <= 9]
S = pd.DataFrame({"n_mes": js.groupby(js.index.year)["tmax"].count(), "d28": js.groupby(js.index.year)["d28"].sum(), "d29": js.groupby(js.index.year)["d29"].sum(),
                  "d30": js.groupby(js.index.year)["d30"].sum(), "anom_tmax": js.groupby(js.index.year)["anom_tmax"].mean(), "anom_tmin": js.groupby(js.index.year)["anom_tmin"].mean(),
                  "anom_tmean": js.groupby(js.index.year)["anom_tmean"].mean()})
print("\nJan-Sep only:\n", S.round(2).to_string())
print("\nmonths with data:", int(M["tmax"].notna().sum()), "of", len(M))
