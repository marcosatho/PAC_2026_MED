# -*- coding: utf-8 -*-
import csv, re, sys, os, collections
D = os.path.dirname(os.path.abspath(__file__))
pat = re.compile(sys.argv[1], re.I)
excl = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
g = collections.OrderedDict()
for r in csv.DictReader(open(os.path.join(D, "capas_servidor_alcaldia.csv"), encoding="utf-8-sig")):
    txt = r["capa"] + " " + r["servicio"]
    if pat.search(txt) and not (excl and excl.search(txt)):
        g.setdefault((r["carpeta"], r["servicio"], r["descripcion_servicio"][:110]), []).append("%s:%s%s" % (r["id"], r["capa"], {"esriGeometryPolygon": "[pol]", "esriGeometryPolyline": "[lin]", "esriGeometryPoint": "[pto]", "": ""}.get(r["geom"], "[" + r["geom"][-6:] + "]")))
for k, v in g.items():
    print("## %s/%s — %s" % (k[0], k[1], k[2]))
    print("   " + " | ".join(v[:40]) + (" ..." if len(v) > 40 else ""))
print(len(g), "servicios")
