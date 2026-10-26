# -*- coding: utf-8 -*-
"""Vista previa en HTML del piloto (texto resumido, figuras en su sitio) para revisar la ubicación sin Word."""
import sys, os, re, zipfile, html
from lxml import etree
sys.stdout.reconfigure(encoding="utf-8")
DOCX = os.environ.get("PILOTO_OUT", r"C:\Users\marco\Downloads\Piloto_figuras_7.1_y_8.1_local_ejes_km.docx")
CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vista")
os.makedirs(CARPETA, exist_ok=True)
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
W = "{%s}" % NS["w"]
z = zipfile.ZipFile(DOCX)
doc = etree.fromstring(z.read("word/document.xml"))
rels = etree.fromstring(z.read("word/_rels/document.xml.rels"))
rid2t = {r.get("Id"): r.get("Target") for r in rels}
for n in z.namelist():
    if n.startswith("word/media/"):
        destino = os.path.join(CARPETA, os.path.basename(n))
        open(destino, "wb").write(z.read(n))
estilo_head = {}
sty = etree.fromstring(z.read("word/styles.xml"))
for s in sty.iter(W + "style"):
    nm = s.find(W + "name")
    estilo_head[s.get(W + "styleId")] = nm.get(W + "val") if nm is not None else ""

partes = {"7": [], "8": []}
cap = "7"
for e in doc.find(W + "body"):
    if e.tag == W + "tbl":
        partes[cap].append('<div class="tabla">[tabla del RT]</div>'); continue
    if e.tag != W + "p":
        continue
    t = "".join(x.text or "" for x in e.iter(W + "t"))
    ps = e.find(W + "pPr")
    sid = ps.find(W + "pStyle").get(W + "val") if ps is not None and ps.find(W + "pStyle") is not None else ""
    nombre = estilo_head.get(sid, "")
    imgs = e.findall(".//a:blip", NS)
    if re.match(r"^8\. Caracterización", t):
        cap = "8"
    out = partes[cap]
    hl = e.find(".//w:highlight", NS) is not None
    if imgs:
        for b in imgs:
            f = os.path.basename(rid2t[b.get("{%s}embed" % NS["r"])])
            out.append(f'<div class="fig"><img src="{f}"></div>')
    elif nombre.startswith("Heading"):
        nivel = {"Heading 1": 1, "Heading 2": 2, "Heading 3": 3, "Heading 4": 4}.get(nombre, 4)
        out.append(f"<h{nivel + 1}>{html.escape(t)}</h{nivel + 1}>")
    elif hl:
        out.append(f'<div class="tag">{html.escape(t)}</div>')
    elif re.match(r"^(Figura|Tabla) \d+\.\d+\.", t.strip()):
        m = re.match(r"^((?:Figura|Tabla) \d+\.\d+\.)(.*)$", t.strip(), re.S)
        out.append(f'<div class="leyenda"><b>{html.escape(m.group(1))}</b>{html.escape(m.group(2)[:330])}{"…" if len(m.group(2)) > 330 else ""}</div>')
    elif t.strip():
        resumen = t.strip()
        out.append(f'<p>{html.escape(resumen[:230])}{"…" if len(resumen) > 230 else ""}</p>')

CSS = """body{font-family:Segoe UI,Arial,sans-serif;font-size:13px;margin:18px 40px;max-width:1000px;color:#222}
h2,h3,h4,h5{margin:14px 0 4px} h3{color:#1f3a5f} h5{color:#555;font-size:12px}
p{margin:3px 0;color:#444} .fig{text-align:center;margin:4px 0 0} .fig img{max-width:420px;max-height:340px;border:1px solid #ccc}
.leyenda{font-size:12px;margin:2px 0 8px;padding:3px 8px;border-left:3px solid #7f1d1d;background:#faf5f5}
.tag{background:#fff200;font-size:10.5px;display:inline-block;padding:1px 6px;margin-top:8px} .tabla{color:#888;font-style:italic}"""
for k, titulo in (("7", "Piloto 7.1: dónde irían las figuras (vista previa)"), ("8", "Piloto 8.1: dónde irían las figuras (vista previa)")):
    open(os.path.join(CARPETA, f"vista_{k}.html"), "w", encoding="utf-8").write(
        f"<!doctype html><html lang='es'><meta charset='utf-8'><title>{titulo}</title><style>{CSS}</style><body><h1 style='font-size:18px'>{titulo}</h1>"
        "<div style='font-size:11px;color:#777'>Texto del RT resumido (230 caracteres por párrafo); las figuras están reducidas.</div>" + "\n".join(partes[k]) + "</body></html>")
print("ok", {k: len(v) for k, v in partes.items()})
