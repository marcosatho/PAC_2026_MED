# -*- coding: utf-8 -*-
"""Une los datos de la fase 1 (mapa_datos.json) con los de medidas (medidas_datos.json) y agrega el identificador de cada barrio."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(os.path.dirname(D), "medidas2")
d = json.load(open(os.path.join(D, "mapa_datos.json"), encoding="utf-8"))
m = json.load(open(os.path.join(M, "medidas_datos.json"), encoding="utf-8"))
feats = d["bar_geo"]["features"]
assert len(feats) == len(m["bid_order"]), (len(feats), len(m["bid_order"]))
for f, b, c in zip(feats, m["bid_order"], m["cod_order"]):
    assert f["properties"]["codigo"] == c, (f["properties"]["codigo"], c)
    f["properties"]["bid"] = b
d["med"] = m["med"]
out = os.path.join(D, "mapa_datos_v2.json")
json.dump(d, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("mapa_datos_v2.json:", round(os.path.getsize(out) / 1048576, 2), "MB")
