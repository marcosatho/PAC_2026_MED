# -*- coding: utf-8 -*-
"""Build a Word file (text + embedded figures + references) from the markdown draft of numerals 8.1.3, 8.1.4,
8.1.5 and 8.1.8. The package is built on top of the master deliverable so styles (Heading 3/4, Normal, theme) match
and pasted content keeps the master's look. Comments, old media and track-changes are dropped.

usage: build_docx_8_1.py <draft.md> <figures_dir> <master.docx> <out.docx>"""
import re
import sys
import zipfile
import datetime
from xml.sax.saxutils import escape
from PIL import Image

MD, FIGDIR, MASTER, OUT = sys.argv[1:5]

TEXT_W_IN = 6.0          # master: Letter, 1.25 in side margins
WIDTH_IN = {"Figura_8_1_3_1": 5.6, "Figura_8_1_4_1": 5.6, "Figura_8_1_5_1": 5.6,
            "Figura_8_1_5_2": 6.0, "Figura_8_1_8_1": 6.0,
            "Figura_8_1_7_1": 6.0, "Figura_8_1_7_2": 5.6, "Figura_8_1_7_3": 5.6,
            "Figura_8_1_9_1": 6.0, "Figura_8_1_9_2": 5.6, "Figura_8_1_9_3": 5.6}
WIDTH_IN.update({"Figura_8_5_1": 6.0, "Figura_8_5_2": 6.0, "Figura_8_5_3": 6.0, "Figura_8_5_4": 6.0, "Figura_8_5_5": 5.6, "Figura_8_5_6": 6.0, "Figura_8_5_7": 5.6, "Figura_8_5_8": 5.6})
EMU = 914400

src = zipfile.ZipFile(MASTER)
doc_xml = src.read("word/document.xml").decode("utf-8-sig")
root_open = re.search(r"<w:document [^>]*>", doc_xml).group(0)
sect = re.findall(r"<w:sectPr.*?</w:sectPr>", doc_xml, flags=re.S)[-1]
sect = re.sub(r"<w:(header|footer)Reference[^>]*/>", "", sect)


def runs(text, italic=False, bold=False, size=None, highlight=False):
    """Split *italic* markdown spans into runs."""
    out = []
    for i, part in enumerate(re.split(r"\*([^*]+)\*", text)):
        if not part:
            continue
        it = italic or (i % 2 == 1)
        rpr = ""
        if bold: rpr += "<w:b/><w:bCs/>"
        if it: rpr += "<w:i/><w:iCs/>"
        if size: rpr += '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (size, size)
        if highlight: rpr += '<w:highlight w:val="yellow"/>'
        out.append('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % ("<w:rPr>%s</w:rPr>" % rpr if rpr else "", escape(part)))
    return "".join(out)


def para(inner, ppr=""):
    return "<w:p>%s%s</w:p>" % ("<w:pPr>%s</w:pPr>" % ppr if ppr else "", inner)


images = []      # (rId, filename, bytes)


def picture(fname, caption_text):
    key = fname[:14]
    w_in = WIDTH_IN.get(fname[:12], WIDTH_IN.get(key, TEXT_W_IN))
    im = Image.open(f"{FIGDIR}/{fname}")
    cx = int(w_in * EMU)
    cy = int(cx * im.size[1] / im.size[0])
    rid = "rIdFig%d" % (len(images) + 1)
    images.append((rid, fname, open(f"{FIGDIR}/{fname}", "rb").read()))
    n = len(images)
    alt = escape(re.sub(r"\s+", " ", caption_text))
    drawing = (
        '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/>'
        '<wp:docPr id="%d" name="Figura %d" descr="%s"/><wp:cNvGraphicFramePr>'
        '<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
        '</wp:cNvGraphicFramePr><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr>'
        '<pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="%s"/>'
        '<a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        '<a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
        '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
    ) % (cx, cy, 900 + n, n, alt, 900 + n, escape(fname), rid, cx, cy)
    return para(drawing, '<w:keepNext/><w:spacing w:before="120" w:after="60"/><w:jc w:val="center"/>')


def caption(text):
    text = text.strip().strip("*")
    m = re.match(r"(Figura \d+\.)(.*)", text, flags=re.S)
    inner = runs(m.group(1), bold=True, size=18) + runs(m.group(2), size=18)
    return para(inner, '<w:spacing w:before="0" w:after="240" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/>')


def table(rows):
    """rows: list of cell lists; first row is the header, a row starting with 'Total' is bold."""
    ncol = len(rows[0])
    widths = [2300] + [int((8640 - 2300) / (ncol - 1))] * (ncol - 1)
    borders = "".join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="8C8C8C"/>' % b
                      for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
    out = ['<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders>'
           '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="70" w:type="dxa"/><w:right w:w="70" w:type="dxa"/>'
           '</w:tblCellMar></w:tblPr>' % borders]
    out.append("<w:tblGrid>%s</w:tblGrid>" % "".join('<w:gridCol w:w="%d"/>' % w for w in widths))
    for ri, row in enumerate(rows):
        is_head = ri == 0
        is_total = row[0].strip().lower() == "total"
        cells = []
        for ci, c in enumerate(row):
            shade = '<w:shd w:val="clear" w:color="auto" w:fill="D9E1F2"/>' if is_head else ""
            jc = "left" if ci == 0 else "center"
            kn = "" if ri == len(rows) - 1 else "<w:keepNext/>"
            inner = para(runs(c.strip(), bold=is_head or is_total, size=16 if is_head else 17),
                         kn + '<w:spacing w:before="30" w:after="30" w:line="240" w:lineRule="auto"/><w:jc w:val="%s"/>' % jc)
            cells.append('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>'
                         % (widths[ci], shade, inner))
        trpr = "<w:trPr>%s</w:trPr>" % ("<w:tblHeader/>" if is_head else "")
        out.append("<w:tr>%s%s</w:tr>" % (trpr, "".join(cells)))
    out.append("</w:tbl>")
    return "".join(out)


def table_caption(text):
    m = re.match(r"(Tabla \d+\.)(.*)", text.strip(), flags=re.S)
    return para(runs(m.group(1), bold=True, size=18) + runs(m.group(2), size=18),
                '<w:keepNext/><w:spacing w:before="200" w:after="80" w:line="240" w:lineRule="auto"/>')


lines = open(MD, encoding="utf-8").read().split("\n")
body, i, in_refs = [], 0, False
while i < len(lines):
    ln = lines[i].rstrip()
    if not ln.strip():
        i += 1
        continue
    if ln.startswith("### "):
        body.append(para(runs(ln[4:]), '<w:pStyle w:val="Heading4"/>'))
    elif ln.startswith("## "):
        in_refs = ln[3:].strip() == "Referencias"
        body.append(para(runs(ln[3:]), '<w:pStyle w:val="Heading3"/>'))
    elif ln.startswith("[FIGURA"):
        fname = re.search(r"—\s*(\S+\.png)\]", ln).group(1)
        cap = lines[i + 1]
        body.append(picture(fname, cap.strip().strip("*")))
        body.append(caption(cap))
        i += 1
    elif in_refs:
        body.append(para(runs(ln), '<w:spacing w:after="120"/><w:ind w:left="720" w:hanging="720"/>'))
    elif re.match(r"Tabla \d+\.", ln):
        body.append(table_caption(ln))
    elif ln.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            cells = [c for c in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r"\s*-+\s*", c) for c in cells):
                rows.append(cells)
            i += 1
        body.append(table(rows))
        continue
    elif ln.startswith("Fuente:"):
        body.append(para(runs(ln, size=18), '<w:spacing w:before="60" w:after="240" w:line="240" w:lineRule="auto"/>'))
    elif ln.startswith("- "):
        body.append(para(runs(ln[2:]), '<w:pStyle w:val="ListBullet"/>'))
    elif ln.startswith("[POR COMPLETAR"):
        body.append(para(runs(ln, highlight=True)))
    else:
        body.append(para(runs(ln)))
    i += 1

new_doc = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + root_open + "<w:body>" + "".join(body) + sect + "</w:body></w:document>"

# --- package -----------------------------------------------------------------------------------------------
KEEP_RELS = ("/styles", "/settings", "/webSettings", "/fontTable", "/theme", "/numbering")
rels_src = src.read("word/_rels/document.xml.rels").decode("utf-8-sig")
kept = [r for r in re.findall(r"<Relationship [^>]*/>", rels_src) if any(k in re.search(r'Type="([^"]+)"', r).group(1) for k in KEEP_RELS)
        and "stylesWithEffects" not in r]
img_rels = ['<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/%s"/>' % (rid, fn)
            for rid, fn, _ in images]
new_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(kept) + "".join(img_rels) + "</Relationships>")

kept_parts = {"word/styles.xml", "word/settings.xml", "word/webSettings.xml", "word/fontTable.xml", "word/theme/theme1.xml", "word/numbering.xml"}
ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/>'
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
      '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
      '<Override PartName="/word/webSettings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.webSettings+xml"/>'
      '<Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>'
      '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
      '<Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
      '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>')
root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
             '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>')
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>PAC 2026 - Numeral 8.5: cuantificación de los eventos (borrador)</dc:title>'
        '<dc:creator>Marcos Arango</dc:creator><dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
        '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified></cp:coreProperties>') % (now, now)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ct)
    z.writestr("_rels/.rels", root_rels)
    z.writestr("docProps/core.xml", core)
    z.writestr("word/document.xml", new_doc)
    z.writestr("word/_rels/document.xml.rels", new_rels)
    for part in kept_parts:
        data = src.read(part)
        if part == "word/settings.xml":
            txt = data.decode("utf-8-sig")
            txt = re.sub(r"<w:trackRevisions\s*/>", "", txt)             # no track changes in the new file
            txt = re.sub(r"<w:rsids>.*?</w:rsids>", "", txt, flags=re.S)
            data = txt.encode("utf-8")
        z.writestr(part, data)
    for _, fn, data in images:
        z.writestr("word/media/" + fn, data)

print("saved", OUT, "| paragraphs:", len(body), "| figures:", len(images))
