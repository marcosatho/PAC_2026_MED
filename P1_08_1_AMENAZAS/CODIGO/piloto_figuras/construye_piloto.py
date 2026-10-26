# -*- coding: utf-8 -*-
"""Piloto local: copia parcial del borrador RT (capítulos 7.1 y 8.1) con las figuras en su ubicación propuesta.

No toca el original. Salida: Downloads\\Piloto_figuras_7.1_y_8.1_local.docx y un JSON con el resultado (numeración, anclas)."""
import sys, os, re, json, copy, zipfile, shutil, io
sys.stdout.reconfigure(encoding="utf-8")
from lxml import etree
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan_figuras import P

RT = r"C:\Users\marco\Downloads\PAC_P1_BORRADOR_RT.docx"
OUT = os.environ.get("PILOTO_OUT", r"C:\Users\marco\Downloads\Piloto_figuras_7.1_y_8.1_local_ejes_km.docx")
SALIDA_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "piloto_resultado.json")
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
W = "{%s}" % NS["w"]
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NSDECL = " ".join(f'xmlns:{k}="{v}"' for k, v in NS.items())
MAX_W, MAX_H = 5810250, 4480560  # EMU: ancho de las figuras del RT y alto máximo (4,9 in)

zin = zipfile.ZipFile(RT)
doc = etree.fromstring(zin.read("word/document.xml"))
body = doc.find(W + "body")
els = list(body)
txt = lambda e: "".join(t.text or "" for t in e.iter(W + "t"))

# ---------- rangos que se conservan: capítulo 7 hasta el final de 7.1 y capítulo 8 hasta el final de 8.1
def idx_heading(inicio):
    for i, e in enumerate(els):
        if e.tag == W + "p" and txt(e).startswith(inicio):
            ps = e.find(W + "pPr")
            sid = ps.find(W + "pStyle").get(W + "val") if ps is not None and ps.find(W + "pStyle") is not None else ""
            if sid.startswith("Heading") and i > 400:
                return i
    raise SystemExit("no se encontró " + inicio)

i7, i72 = idx_heading("7. Caracterización ambiental"), idx_heading("7.2 Biodiversidad")
i8, i82 = idx_heading("8. Caracterización de riesgos"), idx_heading("8.2 Exposición")
print("rangos:", (i7, i72), (i8, i82))
keep = set(range(i7, i72)) | set(range(i8, i82))

# ---------- numeración nueva: orden de aparición dentro de cada capítulo (figuras existentes y nuevas)
exist = []  # (índice, capítulo, número actual)
for i, e in enumerate(els):
    if e.tag == W + "p":
        m = re.match(r"^Figura (\d+)\.(\d+)\.", txt(e).strip())
        if m and int(m.group(1)) in (7, 8):
            exist.append((i, int(m.group(1)), int(m.group(2))))
entradas = []  # (posición ordenable, tipo, objeto)
for k, p in enumerate(P):
    cap = 7 if p["anchor"] < i72 else 8
    entradas.append((p["anchor"] + 0.5 + k * 1e-4, cap, "nueva", p))
for (i, cap, n) in exist:
    entradas.append((i - 0.25, cap, "existente", (i, n)))  # el gráfico va antes de su leyenda; la leyenda queda tras él
entradas.sort(key=lambda x: x[0])
cont = {7: 0, 8: 0}
mapa_exist = {}   # (cap, n_actual) -> n_nuevo
for pos, cap, tipo, obj in entradas:
    if tipo == "nueva" and obj["placeholder"]:
        obj["num"] = None
        continue
    cont[cap] += 1
    if tipo == "nueva":
        obj["num"] = f"{cap}.{cont[cap]}"
    else:
        mapa_exist[(cap, obj[1])] = f"{cap}.{cont[cap]}"
        obj_i = obj[0]
print("figuras existentes ->", {f"{a}.{b}": v for (a, b), v in mapa_exist.items()})

# ---------- construcción de elementos
def E(xml):
    return etree.fromstring(f"<root {NSDECL}>{xml}</root>")[0]

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def p_tag(texto):
    return E(f'<w:p><w:pPr><w:pStyle w:val="Cuerpo"/><w:keepNext/><w:spacing w:before="160" w:after="20"/></w:pPr>'
             f'<w:r><w:rPr><w:highlight w:val="yellow"/><w:sz w:val="15"/><w:szCs w:val="15"/></w:rPr><w:t xml:space="preserve">{esc(texto)}</w:t></w:r></w:p>')

def p_caption(num, cuerpo):
    return E(f'<w:p><w:pPr><w:pStyle w:val="Cuerpo"/><w:keepNext w:val="false"/></w:pPr>'
             f'<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t xml:space="preserve">Figura {num}.</w:t></w:r>'
             f'<w:r><w:t xml:space="preserve"> {esc(cuerpo)}</w:t></w:r></w:p>')

def p_pendiente(texto):
    return E(f'<w:p><w:pPr><w:pStyle w:val="Cuerpo"/></w:pPr><w:r><w:rPr><w:highlight w:val="yellow"/><w:b/></w:rPr>'
             f'<w:t xml:space="preserve">[{esc(texto)}]</w:t></w:r></w:p>')

rels = {}   # rId -> (destino, nombre)
nuevos_media = []
docpr = [900]

def p_imagen(rid, ruta, alt):
    w, h = Image.open(ruta).size
    esc_ = min(MAX_W / w, MAX_H / h)
    cx, cy = int(w * esc_), int(h * esc_)
    docpr[0] += 1
    nombre = os.path.basename(ruta)
    return E(
        f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{docpr[0]}" name="{esc(nombre)}" descr="{esc(alt)}"/>'
        f'<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
        f'<pic:nvPicPr><pic:cNvPr id="{docpr[0]}" name="{esc(nombre)}"/><pic:cNvPicPr><a:picLocks noChangeAspect="1"/></pic:cNvPicPr></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')

def sustituye_referencias(e):
    """Actualiza «Figura 7.1» / «Figura 8.1» del texto corrido (no de las leyendas) con la numeración nueva."""
    cambios = []
    for t in e.iter(W + "t"):
        if t.text and "Figura" in t.text:
            def rep(m):
                clave = (int(m.group(1)), int(m.group(2)))
                if clave in mapa_exist:
                    cambios.append(f"Figura {m.group(1)}.{m.group(2)} → Figura {mapa_exist[clave]}")
                    return "Figura " + mapa_exist[clave]
                return m.group(0)
            t.text = re.sub(r"Figura (\d+)\.(\d+)(?!\d)", rep, t.text)
    return cambios

# ---------- cuerpo nuevo
nuevo = []
nota = E('<w:p><w:pPr><w:pStyle w:val="Cuerpo"/></w:pPr><w:r><w:rPr><w:highlight w:val="yellow"/><w:b/></w:rPr><w:t xml:space="preserve">'
         'PILOTO LOCAL (18-oct-2026). Copia parcial del borrador RT con solo los numerales 7.1 y 8.1 y las figuras en su ubicación propuesta. '
         'Los textos en amarillo son marcas del piloto y se quitan en la versión final. No reemplaza al documento en línea.</w:t></w:r></w:p>')
nuevo.append(nota)
por_ancla = {}
for p in P:
    por_ancla.setdefault(p["anchor"], []).append(p)
registro = []
cont_rid = 0
refs_cambiadas = []
for i in sorted(keep):
    e = copy.deepcopy(els[i])
    # leyenda existente: nuevo número
    if e.tag == W + "p":
        m = re.match(r"^Figura (\d+)\.(\d+)\.", txt(e).strip())
        if m and int(m.group(1)) in (7, 8):
            primero = next(e.iter(W + "t"))
            primero.text = f"Figura {mapa_exist[(int(m.group(1)), int(m.group(2)))]}."
        else:
            c = sustituye_referencias(e)
            if i == 558:  # el párrafo remite al mapa de pendientes nuevo y al gráfico que ya estaba
                for t in e.iter(W + "t"):
                    if t.text and "(Figura 7.3)" in t.text:
                        t.text = t.text.replace("(Figura 7.3)", "(Figuras 7.2 y 7.3)")
                        c.append("ajuste manual: (Figura 7.3) → (Figuras 7.2 y 7.3)")
            if c:
                refs_cambiadas.append((i, c))
    nuevo.append(e)
    for p in por_ancla.get(i, []):
        if p["placeholder"]:
            nuevo.append(p_tag(f"PILOTO · figura del P1 v2 n.º {p['v2']} · sin archivo definitivo · {p['sec']}"))
            nuevo.append(p_pendiente(p["titulo"] + " " + p["fuente"]))
            registro.append(dict(k=p["k"], num="", anchor=i, estado="pendiente"))
            continue
        if not p["src"] or not os.path.exists(p["src"]):
            raise SystemExit(f"falta el archivo de {p['k']}: {p['src']}")
        cont_rid += 1
        rid = f"rIdPil{cont_rid:02d}"
        ext = os.path.splitext(p["src"])[1].lower()
        dest = f"media/piloto_fig{cont_rid:02d}{ext}"
        rels[rid] = dest
        nuevos_media.append((f"word/{dest}", p["src"]))
        nuevo.append(p_tag(f"PILOTO · figura nueva {p['num']} · P1 v2 n.º {p['v2']} · {os.path.basename(p['src'])} · {p['sec']}"))
        nuevo.append(p_imagen(rid, p["src"], p["titulo"][:200]))
        nuevo.append(p_caption(p["num"], p["titulo"] + " " + p["fuente"]))
        registro.append(dict(k=p["k"], num=p["num"], anchor=i, estado="insertada", archivo=p["src"]))

# ---------- escribir el nuevo document.xml (se conserva el sectPr final)
sect = els[-1]
assert sect.tag == W + "sectPr"
for e in list(body):
    body.remove(e)
for e in nuevo:
    body.append(e)
body.append(copy.deepcopy(sect))
doc_xml = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)

# ---------- relaciones y tipos de contenido
rels_xml = etree.fromstring(zin.read("word/_rels/document.xml.rels"))
for rid, dest in rels.items():
    etree.SubElement(rels_xml, "{%s}Relationship" % REL_NS, Id=rid, Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", Target=dest)
rels_bytes = etree.tostring(rels_xml, xml_declaration=True, encoding="UTF-8", standalone=True)
ct = zin.read("[Content_Types].xml").decode("utf-8")
assert 'Extension="png"' in ct

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename.startswith("[trash]"):
            continue  # restos de Word sin referencia (están también en el original)
        if item.filename == "word/document.xml":
            zout.writestr(item, doc_xml)
        elif item.filename == "word/_rels/document.xml.rels":
            zout.writestr(item, rels_bytes)
        else:
            zout.writestr(item, zin.read(item.filename))
    for destino, origen in nuevos_media:
        zout.write(origen, destino)
print("escrito:", OUT, round(os.path.getsize(OUT) / 1e6, 1), "MB | figuras insertadas:", sum(1 for r in registro if r["estado"] == "insertada"),
      "| pendientes:", sum(1 for r in registro if r["estado"] == "pendiente"))
print("referencias de texto actualizadas:", refs_cambiadas)
json.dump(dict(registro=registro, mapa_exist={f"{a}.{b}": v for (a, b), v in mapa_exist.items()}, refs=refs_cambiadas, i7=i7, i72=i72, i8=i8, i82=i82),
          open(SALIDA_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
