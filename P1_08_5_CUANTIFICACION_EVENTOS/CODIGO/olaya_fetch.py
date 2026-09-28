# -*- coding: utf-8 -*-
"""Pull the IDEAM open-data temperature series of the Aeropuerto Olaya Herrera station (0027015330) from datos.gov.co (Socrata).
Only this station and only date / value / sensor columns are requested.
sbwg-7ju4: 'Temperatura Ambiente del Aire' (sensor 0068, hourly); ccvq-rp9s: 'Temperatura Maxima del Aire'; afdg-3zpb: 'Temperatura Minima del Aire'."""
import sys, json, time, urllib.parse, urllib.request
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
BASE = "https://www.datos.gov.co/resource/%s.json"
JOBS = {"tmean_sbwg-7ju4": ("sbwg-7ju4", "codigoestacion='0027015330' AND codigosensor='0068'"),
        "tmax_ccvq-rp9s": ("ccvq-rp9s", "codigoestacion='0027015330'"),
        "tmin_afdg-3zpb": ("afdg-3zpb", "codigoestacion='0027015330'")}
for name, (ds, where) in JOBS.items():
    rows, off = [], 0
    while True:
        q = urllib.parse.urlencode({"$select": "fechaobservacion,valorobservado,codigosensor,descripcionsensor,nombreestacion", "$where": where,
                                    "$order": "fechaobservacion", "$limit": 50000, "$offset": off})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(BASE % ds + "?" + q, timeout=120) as r:
                    page = json.loads(r.read().decode("utf-8"))
                break
            except Exception as e:
                print("retry", attempt, e); time.sleep(4)
        else:
            raise SystemExit("failed")
        rows += page
        print(name, "offset", off, "got", len(page))
        if len(page) < 50000:
            break
        off += 50000
    df = pd.DataFrame(rows)
    df.to_csv(f"ev85/olaya/olaya_{name}.csv", index=False, encoding="utf-8")
    print("saved", name, len(df), df["fechaobservacion"].min(), df["fechaobservacion"].max())
