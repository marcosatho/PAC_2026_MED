# -*- coding: utf-8 -*-
"""Parche de datos v3: añade la multiamenaza (baja=1, media=2, alta=3; producto de las tres) a datos_mapa.py."""
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_mapa.py")
s = open(p, encoding="utf-8").read()
if "multi_geo" in s:
    raise SystemExit("ya aplicado")

bloque = '''
# ---------- multiamenaza: partición exacta del Distrito por (clase MM, clase inundación, clase torrencial) ----------
# baja = 1, media = 2, alta = 3; «fuera de la mancha» de inundación o torrencial = 1 (elemento neutro del producto).
# Sin pasar a ráster: intersección vectorial exacta de las tres capas.
mm_v = {1: haz["mm"]["baja"], 2: haz["mm"]["media"], 3: haz["mm"]["alta"]}
def clases_v(hh):
    g = haz[hh]
    alta = g["alta"]
    media = g["media"].difference(alta)
    return {1: distrito.difference(unary_union([media, alta])), 2: media, 3: alta}
Bc, Cc = clases_v("inu"), clases_v("tor")
piezas = []
for b in (1, 2, 3):
    for c in (1, 2, 3):
        Q = Bc[b].intersection(Cc[c])
        if Q.is_empty:
            continue
        for a_ in (1, 2, 3):
            P = mm_v[a_].intersection(Q)
            if P.is_empty or P.area < 1:
                continue
            piezas.append((a_, b, c, P))
tot_area = sum(P.area for *_, P in piezas)
print("multiamenaza: piezas", len(piezas), "| cubierto / Distrito:", round(tot_area / distrito.area, 4))
dist_prod = {}
for a_, b, c, P in piezas:
    dist_prod[a_ * b * c] = dist_prod.get(a_ * b * c, 0) + P.area / 1e4
print("producto -> ha:", {k: round(v) for k, v in sorted(dist_prod.items())})
for fila, (_, t) in zip(filas, com.iterrows()):
    g = t.geometry; ar = g.area; comb = {}
    for a_, b, c, P in piezas:
        x = g.intersection(P).area / ar * 100
        if x >= 0.005:
            comb["%d-%d-%d" % (a_, b, c)] = round(x, 3)
    fila["comb"] = comb
multi_geo = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"a": a_, "b": b, "c": c, "p": a_ * b * c}, "geometry": geo4326(P, 14)} for a_, b, c, P in piezas]}
'''
key = "df = pd.DataFrame(filas)"
assert key in s
s = s.replace(key, bloque + "\n" + key, 1)

# totales del Distrito: combinaciones y producto
key2 = "print(tot)\n"
assert key2 in s
tot_code = '''tot["comb"] = {"%d-%d-%d" % (a_, b, c): round(P.area / distrito.area * 100, 3) for a_, b, c, P in piezas}
tot["multi_ha"] = {str(k): round(v, 0) for k, v in sorted(dist_prod.items())}
tot["multi_pct"] = {str(k): round(v / area_dist * 100, 2) for k, v in sorted(dist_prod.items())}
print(tot["multi_pct"])
'''
s = s.replace(key2, tot_code + key2, 1)

old = '"haz_geo": haz_geo, "bar_geo": bar_geo'
assert old in s
s = s.replace(old, '"haz_geo": haz_geo, "multi_geo": multi_geo, "bar_geo": bar_geo', 1)
old = 'for k in ("terr_geo", "bar_geo"):'
assert old in s
s = s.replace(old, 'for k in ("terr_geo", "bar_geo", "multi_geo"):', 1)
open(p, "w", encoding="utf-8").write(s)
print("parche de datos aplicado")
