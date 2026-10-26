# -*- coding: utf-8 -*-
"""Busca en el catálogo geográfico de la Alcaldía (GeoNetwork) conjuntos de datos relacionados con medidas."""
import json, sys, urllib.request
BASE = "https://www.medellin.gov.co/giscatalogacion/srv/api/search/records/_search"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
      "Content-Type": "application/json", "Accept": "application/json"}


def buscar(q, n=30):
    body = {"from": 0, "size": n, "query": {"query_string": {"query": q}}, "_source": ["resourceTitleObject", "resourceAbstractObject", "uuid", "resourceType", "format", "link", "changeDate", "cl_status"]}
    req = urllib.request.Request(BASE, data=json.dumps(body).encode(), headers=UA, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


for q in sys.argv[1:]:
    try:
        d = buscar(q)
    except Exception as e:
        print("==", q, "ERROR", e); continue
    hits = d.get("hits", {})
    print("==", q, "| total:", hits.get("total"))
    for h in hits.get("hits", []):
        s = h["_source"]
        t = (s.get("resourceTitleObject") or {}).get("default", "")
        a = ((s.get("resourceAbstractObject") or {}).get("default", "") or "").replace("\n", " ")[:140]
        print("  -", h["_id"], "|", t, "|", a)
