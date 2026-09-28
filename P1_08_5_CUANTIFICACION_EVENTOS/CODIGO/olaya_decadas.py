# -*- coding: utf-8 -*-
"""Change over time at the Olaya Herrera station: official IDEAM 30-year normals (three periods, stepped 10 years)
plus the actual station record split into ~decade blocks, as far as data allows (hourly record starts Dec 2014)."""
import sys
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)

# ---- official normals (IDEAM, datos.gov.co nsz2-kzcq), station 27015330
NORM = {"1971-2000": {"tmax": 27.6, "tmin": 17.2, "tmean": 22.8},
        "1981-2010": {"tmax": 27.9, "tmin": 17.4, "tmean": 22.5},
        "1991-2020": {"tmax": 27.9, "tmin": 17.7, "tmean": 23.1}}
years = {"1971-2000": 1985.5, "1981-2010": 1995.5, "1991-2020": 2005.5}
for v in ("tmax", "tmin", "tmean"):
    y = np.array(list(years.values())); z = np.array([NORM[p][v] for p in NORM])
    slope = np.polyfit(y, z, 1)[0]
    print(f"linear trend across the three official normals, {v}: {slope*10:+.2f} °C/decade (endpoints: {z[-1]-z[0]:+.2f} over {y[-1]-y[0]:.0f} years)")

# ---- station record, quality-controlled daily series
D = pd.read_csv("ev85/olaya/olaya_diaria.csv", parse_dates=["date"]).set_index("date")
print("\nstation daily record:", D.index.min().date(), "to", D.index.max().date())


def block(lo, hi, label):
    d = D.loc[lo:hi]
    tmean_mm = ((d["tmax"] + d["tmin"]) / 2)          # IDEAM's normal "media" = daily (max+min)/2, NOT the all-hours average
    row = {"periodo": label, "tmax": d["tmax"].mean(), "n_tmax": d["tmax"].count(),
           "tmin": d["tmin"].mean(), "n_tmin": d["tmin"].count(),
           "tmean_hourly": d["tmean"].mean(), "tmean": tmean_mm.mean(), "n_tmean": tmean_mm.count(),
           "years_span": (pd.Timestamp(hi) - pd.Timestamp(lo)).days / 365.25}
    return row


rows = [block("2015-01-01", "2020-12-31", "2015-2020"), block("2021-01-01", "2026-09-25", "2021-2026*")]
S = pd.DataFrame(rows).set_index("periodo")
S["oscilacion"] = S["tmax"] - S["tmin"]
print("\nstation blocks:\n", S.round(2).to_string())

print("\n--- combined table (official normals + station blocks) ---")
rows2 = []
for p, v in NORM.items():
    rows2.append({"periodo": p, "fuente": "Normal IDEAM (30 años)", "tmax": v["tmax"], "tmin": v["tmin"], "tmean": v["tmean"], "oscilacion": v["tmax"] - v["tmin"]})
for p, r in S.iterrows():
    rows2.append({"periodo": p, "fuente": "Estación (dato real)", "tmax": r["tmax"], "tmin": r["tmin"], "tmean": r["tmean"], "oscilacion": r["oscilacion"]})
T = pd.DataFrame(rows2)
print(T.round(2).to_string(index=False))
T.to_csv("ev85/olaya/olaya_periodos_normal_vs_estacion.csv", index=False, encoding="utf-8-sig")

print("\nchange 1971-2000 -> 2021-2026*: tmax %+.2f | tmin %+.2f | tmean %+.2f" % (
    S.loc["2021-2026*", "tmax"] - NORM["1971-2000"]["tmax"], S.loc["2021-2026*", "tmin"] - NORM["1971-2000"]["tmin"],
    S.loc["2021-2026*", "tmean"] - NORM["1971-2000"]["tmean"]))
print("change 1991-2020 (normal) -> 2021-2026* (station): tmax %+.2f | tmin %+.2f" % (
    S.loc["2021-2026*", "tmax"] - NORM["1991-2020"]["tmax"], S.loc["2021-2026*", "tmin"] - NORM["1991-2020"]["tmin"]))

# ENSO composition of the two station blocks (so the reader knows they are not phase-balanced)
M = pd.read_csv("ev85/olaya/olaya_mensual.csv")
M["p"] = pd.PeriodIndex(M["mes"], freq="M")
for lo, hi, lbl in [("2015-01", "2020-12", "2015-2020"), ("2021-01", "2026-09", "2021-2026*")]:
    sub = M[(M["p"] >= pd.Period(lo, "M")) & (M["p"] <= pd.Period(hi, "M"))]
    print(lbl, "meses por fase:", sub["fase"].value_counts().to_dict())
