# -*- coding: utf-8 -*-
"""Solo lectura: dominios de valores codificados de la gdb del DAP (p. ej. tipo_sistema 1..5) para rotular los mapas."""
import os, json, sys
from osgeo import gdal, ogr
gdal.UseExceptions()
sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
ds = gdal.OpenEx(os.path.join(AQUI, "gdb", "mj_rev_pot_2025_med.gdb"), gdal.OF_VECTOR)
out = {}
doms = {}
for dn in ds.GetFieldDomainNames() or []:
    d = ds.GetFieldDomain(dn)
    try:
        doms[dn] = {str(k): v for k, v in d.GetEnumeration().items()} if hasattr(d.GetEnumeration(), "items") else {str(k): v for k, v in d.GetEnumeration()}
    except Exception as e:
        doms[dn] = str(e)[:60]
for i in range(ds.GetLayerCount()):
    lyr = ds.GetLayerByIndex(i)
    nm = lyr.GetName()
    if nm.startswith("T_"):
        continue
    ld = lyr.GetLayerDefn()
    for j in range(ld.GetFieldCount()):
        fd = ld.GetFieldDefn(j)
        dn = fd.GetDomainName()
        if dn:
            out.setdefault(nm, {})[fd.GetName()] = dn
json.dump(dict(dominios=doms, campos=out), open(os.path.join(AQUI, "dominios.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(doms), "dominios;", sum(len(v) for v in out.values()), "campos con dominio en", len(out), "capas")
for nm in ("gu_spc_corred_tte_pasajeros", "gu_spc_equipamiento"):
    print(nm, out.get(nm))
