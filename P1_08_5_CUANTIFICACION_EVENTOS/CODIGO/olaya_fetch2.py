# -*- coding: utf-8 -*-
"""Second pass for the max/min hourly series (the paged query ordered by date timed out): one request per year, no ordering.
Same station (0027015330), same columns; see olaya_fetch.py."""
import sys, json, time, urllib.parse, urllib.request
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
BASE = "https://www.datos.gov.co/resource/%s.json"
JOBS = {"tmax_ccvq-rp9s": "ccvq-rp9s", "tmin_afdg-3zpb": "afdg-3zpb"}
for name, ds in JOBS.items():
    rows = []
    for y in range(2014, 2027):
        where = "codigoestacion='0027015330' AND fechaobservacion between '%d-01-01T00:00:00' and '%d-12-31T23:59:59'" % (y, y)
        q = urllib.parse.urlencode({"$select": "fechaobservacion,valorobservado,codigosensor,descripcionsensor,nombreestacion", "$where": where, "$limit": 50000})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(BASE % ds + "?" + q, timeout=240) as r:
                    page = json.loads(r.read().decode("utf-8"))
                break
            except Exception as e:
                print("  retry", name, y, attempt, e); time.sleep(5)
        else:
            print("  FAILED", name, y); continue
        print(name, y, len(page))
        rows += page
    df = pd.DataFrame(rows)
    df.to_csv(f"ev85/olaya/olaya_{name}.csv", index=False, encoding="utf-8")
    print("saved", name, len(df), df["fechaobservacion"].min(), df["fechaobservacion"].max())
