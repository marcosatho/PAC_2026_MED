# -*- coding: utf-8 -*-
"""Lista todas las capas del servidor de mapas de la Alcaldía de Medellín (ArcGIS REST) para buscar datos de medidas."""
import json, sys, os, urllib.request, urllib.parse, csv
from concurrent.futures import ThreadPoolExecutor

ROOT = "https://www.medellin.gov.co/servidormapas/rest/services"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
OUT = os.path.dirname(os.path.abspath(__file__))


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            err = str(e)
    return {"error": err}


root = get(ROOT + "?f=json")
folders = root.get("folders", [])
print("carpetas:", len(folders), flush=True)


def lista_carpeta(f):
    d = get("%s/%s?f=json" % (ROOT, f))
    return f, d.get("services", [])


servicios = []
with ThreadPoolExecutor(8) as ex:
    for f, sv in ex.map(lista_carpeta, folders):
        for s in sv:
            servicios.append((f, s["name"].split("/")[-1], s["type"]))
print("servicios:", len(servicios), flush=True)


def capas(t):
    f, n, ty = t
    if ty not in ("MapServer", "FeatureServer"):
        return []
    d = get("%s/%s/%s/%s?f=json" % (ROOT, f, n, ty))
    filas = []
    desc = (d.get("serviceDescription") or d.get("description") or "").replace("\n", " ")[:300]
    for l in d.get("layers", []) or []:
        filas.append({"carpeta": f, "servicio": n, "tipo": ty, "id": l["id"], "capa": l["name"], "geom": l.get("geometryType", ""), "descripcion_servicio": desc})
    return filas


filas = []
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(capas, servicios):
        filas += r
print("capas:", len(filas), flush=True)
with open(os.path.join(OUT, "capas_servidor_alcaldia.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["carpeta", "servicio", "tipo", "id", "capa", "geom", "descripcion_servicio"])
    w.writeheader(); w.writerows(filas)
json.dump(servicios, open(os.path.join(OUT, "servicios_alcaldia.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("listo")
