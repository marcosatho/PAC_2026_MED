# -*- coding: utf-8 -*-
"""Lectura de las clases de color de los mapas de los escenarios del IDEAM (2024) sobre el Valle de Aburrá.
Cada figura es una malla de 4 escenarios (filas) x 4 periodos (columnas) con el contorno de Colombia. Se calibra cada panel con las
coordenadas extremas del territorio continental (N 12,46; S -4,23; E -66,84; W -79,02) y se toma la clase de color dominante en una ventana
alrededor de Medellín (6,25 N; -75,57 W). Es una lectura visual de un mapa publicado, con incertidumbre de posición de ~0,2-0,3 grados."""
import sys, json, numpy as np
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image
LON_W, LON_E, LAT_N, LAT_S = -79.02, -66.84, 12.46, -4.23
MED = (-75.57, 6.25)

def groups(a):
    g = []
    for v in a:
        if g and v - g[-1][-1] <= 2: g[-1].append(v)
        else: g.append([v])
    return [(int(x[0]), int(x[-1])) for x in g]

def panels(im):
    dark = (im.sum(axis=2) < 200)
    rows = groups(np.where(dark.mean(axis=1) > 0.55)[0]); cols = groups(np.where(dark.mean(axis=0) > 0.45)[0])
    return rows, cols

def mainland_bbox(sub):
    """bounding box (x0,y0,x1,y1) del bloque continental: mayor componente conexa de píxeles no blancos (4-conectividad)"""
    nonwhite = (sub.sum(axis=2) < 740)
    h, w = nonwhite.shape
    lab = np.zeros((h, w), dtype=np.int32); n = 0; best = (0, None)
    for y in range(h):
        for x in range(w):
            if nonwhite[y, x] and lab[y, x] == 0:
                n += 1; stack = [(y, x)]; lab[y, x] = n; pts = []
                while stack:
                    cy, cx = stack.pop(); pts.append((cy, cx))
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and nonwhite[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = n; stack.append((ny, nx))
                if len(pts) > best[0]: best = (len(pts), pts)
    ys = [p[0] for p in best[1]]; xs = [p[1] for p in best[1]]
    return min(xs), min(ys), max(xs), max(ys), best[0]

def classify_window(sub, bbox, lon, lat, half_deg, palette):
    x0, y0, x1, y1, _ = bbox
    px = lambda lo: x0 + (lo - LON_W) / (LON_E - LON_W) * (x1 - x0)
    py = lambda la: y0 + (LAT_N - la) / (LAT_N - LAT_S) * (y1 - y0)
    xa, xb = int(round(px(lon - half_deg))), int(round(px(lon + half_deg)))
    ya, yb = int(round(py(lat + half_deg))), int(round(py(lat - half_deg)))
    ya0, xa0 = max(ya, 0), max(xa, 0)
    block = sub[ya0:yb + 1, xa0:xb + 1]
    # se descartan los píxeles pegados a líneas oscuras (límites departamentales), que mezclan el color con negro
    dk = (sub.max(axis=2) < 80)
    near = np.zeros(dk.shape, bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near |= np.roll(np.roll(dk, dy, axis=0), dx, axis=1)
    keep = ~near[ya0:yb + 1, xa0:xb + 1]
    win = block[keep]
    cnt = {}
    for rgb in win:
        c = min(palette, key=lambda k: sum((int(a) - int(b)) ** 2 for a, b in zip(k, rgb)))
        d = sum((int(a) - int(b)) ** 2 for a, b in zip(c, rgb)) ** .5
        if d < 30: cnt[palette[c]] = cnt.get(palette[c], 0) + 1
    tot = sum(cnt.values())
    return {k: round(v / tot, 2) for k, v in sorted(cnt.items(), key=lambda t: -t[1])} if tot else {}, (xa, ya, xb, yb)

def legend_from_page(page_png, spec):
    a = np.array(Image.open(page_png).convert("RGB"))
    return a

HALF = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
if __name__ == "__main__":
    name, palette_file = sys.argv[1], sys.argv[2]
    pal = {tuple(k): v for k, v in json.load(open(palette_file, encoding="utf-8"))}
    im = np.array(Image.open(f"img/ideam4_fig_{name}.png").convert("RGB")).astype(int)
    rows, cols = panels(im)
    # filas de datos: entre líneas consecutivas (excluyendo encabezado y borde inferior); columnas de datos
    ry = [rows[i][1] + 1 for i in range(1, 5)]; ry_end = [rows[i][0] for i in range(2, 6)]
    cx = [cols[i][1] + 1 for i in range(1, 5)]; cx_end = [cols[i][0] for i in range(2, 6)]
    out = {}
    for i, ssp in enumerate(("SSP1-2.6", "SSP2-4.5", "SSP3-7.0", "SSP5-8.5")):
        for j, per in enumerate(("2021-2040", "2041-2060", "2061-2080", "2081-2100")):
            sub = im[ry[i]:ry_end[i], cx[j]:cx_end[j]]
            bb = mainland_bbox(sub)
            res, win = classify_window(sub, bb, MED[0], MED[1], HALF, pal)
            out[f"{ssp}|{per}"] = {"clases": res, "bbox": bb[:4], "ventana": win}
            print(ssp, per, res, "bbox", bb)
    json.dump(out, open(f"ideam_{name}_medellin_h{int(HALF*100)}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
