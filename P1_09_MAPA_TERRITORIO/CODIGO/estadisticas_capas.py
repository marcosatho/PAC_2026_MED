# -*- coding: utf-8 -*-
"""Distribuciones por campo (conteo y suma opcional) de capas candidatas del servidor de mapas de la Alcaldía."""
import json, sys, os, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = "https://www.medellin.gov.co/servidormapas/rest/services"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return {"error": str(e)}


def dist(ruta, campo, suma=None, where="1=1", maxn=14):
    stats = [{"statisticType": "count", "onStatisticField": "objectid", "outStatisticFieldName": "n"}]
    if suma:
        stats.append({"statisticType": "sum", "onStatisticField": suma, "outStatisticFieldName": "s"})
    q = {"where": where, "groupByFieldsForStatistics": campo, "outStatistics": json.dumps(stats), "f": "json"}
    d = get("%s/%s/query?%s" % (ROOT, ruta, urllib.parse.urlencode(q)))
    if "error" in d:
        return "ERROR " + str(d["error"])[:150]
    rows = [(f["attributes"].get(campo), f["attributes"].get("n"), f["attributes"].get("s")) for f in d.get("features", [])]
    rows.sort(key=lambda x: -(x[1] or 0))
    return rows[:maxn]


def dominio(ruta, campo):
    d = get("%s/%s?f=json" % (ROOT, ruta))
    for f in d.get("fields") or []:
        if f["name"] == campo and f.get("domain"):
            return {c["code"]: c["name"] for c in f["domain"].get("codedValues", [])}
    return None


tareas = json.load(open(sys.argv[1], encoding="utf-8"))


def correr(t):
    if t[0] == "dist":
        return t, dist(*t[1:])
    return t, dominio(*t[1:])


with ThreadPoolExecutor(6) as ex:
    for t, r in ex.map(correr, tareas):
        print("== %s" % (t[1:],))
        if isinstance(r, list):
            for x in r:
                print("   ", x)
        else:
            print("   ", r)
