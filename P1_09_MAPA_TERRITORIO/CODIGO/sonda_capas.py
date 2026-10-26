# -*- coding: utf-8 -*-
"""Sonda de capas candidatas: cuenta registros, campos y una muestra (sin geometría)."""
import json, sys, os, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ROOT = "https://www.medellin.gov.co/servidormapas/rest/services"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
D = os.path.dirname(os.path.abspath(__file__))


def get(url, tries=2):
    err = ""
    for _ in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            err = str(e)
    return {"error": err}


def sonda(p):
    base = "%s/%s" % (ROOT, p)
    meta = get(base + "?f=json")
    cnt = get(base + "/query?where=1%3D1&returnCountOnly=true&f=json")
    smp = get(base + "/query?where=1%3D1&outFields=*&returnGeometry=false&resultRecordCount=2&f=json")
    campos = [f["name"] for f in (meta.get("fields") or [])][:40]
    ej = [f.get("attributes") for f in (smp.get("features") or [])][:2]
    ext = meta.get("extent") or {}
    return {"ruta": p, "nombre": meta.get("name"), "geom": meta.get("geometryType"), "n": cnt.get("count", cnt.get("error")),
            "campos": campos, "ejemplo": ej, "desc": (meta.get("description") or "")[:200], "ult_edicion": (meta.get("editingInfo") or {}).get("lastEditDate"),
            "scale": [meta.get("minScale"), meta.get("maxScale")], "error": meta.get("error")}


rutas = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip() and not l.startswith("#")]
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(sonda, rutas))
json.dump(res, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
for r in res:
    print("%s | %s | %s | n=%s" % (r["ruta"], r["nombre"], (r["geom"] or "")[-8:], r["n"]))
    print("   campos:", ", ".join(r["campos"])[:300])
    if r["ejemplo"]:
        print("   ej:", json.dumps(r["ejemplo"][0], ensure_ascii=False, default=str)[:420])
