# -*- coding: utf-8 -*-
"""ENSO phases with the NOAA episode definition.

ONI = 3-month running mean of the Niño-3.4 anomaly, assigned to the central month (previous + current + next month).
An El Niño (La Niña) EPISODE = at least 5 consecutive months with ONI >= +0.5 (<= -0.5). Months above the threshold that are
not part of a 5-month run stay 'neutro'.  A run that is still open at the end of the published series and has fewer than 5 months
is 'provisional' (drawn as El Niño*/La Niña*).

Functions are imported by the figure and workbook scripts; run directly to list the episodes."""
import numpy as np
import pandas as pd


def load_oni(path):
    o = pd.read_csv(path, header=0, names=["date", "oni"], parse_dates=["date"])
    o = o[o["oni"] > -99].copy()
    o["ym"] = o["date"].dt.to_period("M")
    return o.set_index("ym")["oni"]


def classify(oni, months=None, min_run=5, thr=0.5):
    """Return a DataFrame indexed by month with columns oni, fase and run_len (fase in La Niña, El Niño, neutro, *_prov, sin dato)."""
    idx = months if months is not None else oni.index
    full = pd.period_range(min(oni.index.min(), idx.min()), max(oni.index.max(), idx.max()), freq="M")
    s = oni.reindex(full)
    sign = pd.Series(0, index=full)
    sign[s >= thr] = 1
    sign[s <= -thr] = -1
    fase = pd.Series("neutro", index=full, dtype=object)
    last_obs = oni.index.max()
    i = 0
    n = len(full)
    runlen = pd.Series(0, index=full)
    while i < n:
        if sign.iloc[i] == 0:
            i += 1
            continue
        j = i
        while j + 1 < n and sign.iloc[j + 1] == sign.iloc[i]:
            j += 1
        L = j - i + 1
        runlen.iloc[i:j + 1] = L
        name = "El Niño" if sign.iloc[i] == 1 else "La Niña"
        if L >= min_run:
            fase.iloc[i:j + 1] = name
        elif full[j] == last_obs:                        # open run at the end of the published series
            fase.iloc[i:j + 1] = name + "*"
        i = j + 1
    fase[s.isna() & (full > last_obs)] = "sin dato"
    out = pd.DataFrame({"oni": s, "fase": fase, "run": runlen})
    return out.loc[idx]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    o = load_oni(sys.argv[1])
    c = classify(o, pd.period_range("2004-01", "2026-07", freq="M"))
    # list episodes
    ep = []
    cur = None
    for p, r in c.iterrows():
        f = r["fase"]
        if f in ("El Niño", "La Niña", "El Niño*", "La Niña*"):
            if cur and cur[0] == f and cur[2] + 1 == p.ordinal:
                cur[2] = p.ordinal; cur[3] = p
            else:
                if cur: ep.append(cur)
                cur = [f, p, p.ordinal, p]
        else:
            if cur: ep.append(cur); cur = None
    if cur: ep.append(cur)
    for f, a, _, b in ep:
        print(f, a, "->", b, "(", (b - a).n + 1, "months )")
