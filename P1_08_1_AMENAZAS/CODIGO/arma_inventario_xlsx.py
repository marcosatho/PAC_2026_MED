# -*- coding: utf-8 -*-
"""Arma el Excel de trazabilidad 2026 / 2014 de las capas de la gdb del POT (zip YDRAY) a partir de inventario_capas.json."""
import json, re, sys, os, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

J = json.load(open(sys.argv[1], encoding="utf-8"))
OUT = sys.argv[2]
dic, topo = J["dic"], J["topo"]
norm = lambda s: re.sub(r"[\s_]+", "", str(s or "")).lower()   # ignora espacios y guiones bajos (hay nombres mal escritos)


dic = {norm(v["nombre_dic"]): v for v in dic.values()}   # re-indexa con la normalización de este script
topo = {norm(k): v for k, v in topo.items()}


def fecha(s):
    """Normaliza fechas del diccionario: texto ISO, dd/mm/aaaa o número de serie de Excel."""
    s = str(s or "").strip()
    if not s:
        return ""
    if re.fullmatch(r"\d{5}", s):
        return (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(s))).isoformat()
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return s[:10]


# ---------- evidencias por capa
filas, campos_rows = [], []
for c in J["capas"]:
    k = norm(c["capa"])
    d = dic.get(k, {})
    campos_gdb = [x for x in c["campos"] if not x.lower().startswith("shape")]
    fechas_dic = sorted({fecha(x) for x in d.get("fechas", []) if fecha(x)})
    dic_min, dic_max = (fechas_dic[0], fechas_dic[-1]) if fechas_dic else ("", "")
    # campos del diccionario: fecha por campo
    dic_campos = {nm.lower(): fecha(fe) for nm, fe in d.get("campos", [])}
    gdb_lc = {x.lower() for x in campos_gdb}
    sin_doc = sorted(x for x in campos_gdb if x.lower() not in dic_campos and x.lower() not in ("objectid", "globalid"))
    solo_dic = sorted(nm for nm in dic_campos if nm not in gdb_lc)
    campos_2026 = sorted(nm for nm, fe in dic_campos.items() if fe >= "2026-01-01" and nm in gdb_lc)
    ladm = [x for x in campos_gdb if x.lower().startswith(("ladm", "_ladm"))]
    # fechas dentro de la capa
    vf = c["valores_fecha"]
    anios = {}
    for nm, x in vf.items():
        if isinstance(x, dict) and "anios" in x:
            for a, n in x["anios"].items():
                anios[a] = anios.get(a, 0) + n
    base_adop = vf.get("fecha_adopcion") or vf.get("fecha_adop") or {}
    base_act = vf.get("fecha_actualizacion") or {}
    # recuento 2014 / posteriores / nulos usando fecha_actualizacion (o adopción)
    ref = base_act if isinstance(base_act, dict) and "anios" in base_act else base_adop
    n14 = sum(n for a, n in ref.get("anios", {}).items() if int(a) <= 2014) if isinstance(ref, dict) else 0
    n25 = sum(n for a, n in ref.get("anios", {}).items() if int(a) >= 2025) if isinstance(ref, dict) else 0
    nmid = sum(n for a, n in ref.get("anios", {}).items() if 2015 <= int(a) <= 2024) if isinstance(ref, dict) else 0
    ntot = c["n"]
    # nombre y descripción
    nombre_48 = bool(re.search(r"(_48$|_48_|_2014$)", c["capa"]))
    desc = d.get("descripcion", "")
    norma = sorted(set(re.findall(r"(?:Acuerdo|Decreto|Resoluci[oó]n|Ley)\s+(?:No\.?\s*)?\d+\s+de\s+\d{4}", desc)))
    cita_48 = bool(re.search(r"Acuerdo\s+(?:No\.?\s*)?48", desc))
    # fechas de referencia declaradas en la metadata XML de la gdb (creación / publicación / revisión)
    xr = {}
    for part in c["xml"]["fecha_ref"].split("; "):
        if "=" in part:
            a_, b_ = part.split("=", 1)
            xr[a_] = b_[:10]
    xml_ini, xml_pub, xml_rev = xr.get("createDate", ""), xr.get("pubDate", ""), xr.get("reviseDate", "")
    xml_ref_txt = "; ".join(f"{a_}: {b_}" for a_, b_ in xr.items())
    es_spc = bool(re.match(r"^(gur_spc|gu_spc|gr_spc|ur_spc)_", c["capa"]))
    # ---- clasificación del CONTENIDO
    ev = []
    if ref and ref.get("no_nulos"):
        ev.append(f"fechas dentro de la capa ({ 'fecha_actualizacion' if base_act else 'fecha_adopcion'}): {n14} de {ntot} elementos ≤2014, {nmid} de 2015–2024, {n25} de 2025–2026, {ntot - n14 - nmid - n25} sin fecha")
    if nombre_48:
        ev.append("el nombre de la capa lleva el sufijo del Acuerdo 48 (2014)")
    if cita_48:
        ev.append("la descripción cita el Acuerdo 48")
    if xml_ref_txt:
        ev.append("metadata XML de la gdb: " + xml_ref_txt)
    if dic_min:
        ev.append(f"diccionario: elaboración {dic_min}" + (f" a {dic_max}" if dic_max != dic_min else ""))
    if campos_2026:
        ev.append(f"{len(campos_2026)} campo(s) documentados con fecha 2026")
    clase, conf = "", ""
    sin_fecha_pct = (ntot - ref["no_nulos"]) / ntot if ref and ref.get("no_nulos") is not None and ntot else 0
    es_instrumento = c["capa"].startswith("sget_splc_instrum")
    if es_instrumento:
        clase, conf = "Instrumentos complementarios (fecha propia de cada instrumento)", "Media"
    elif ref and ref.get("no_nulos"):
        if n25 == 0 and nmid == 0 and n14 >= 0.95 * ref["no_nulos"]:
            if sin_fecha_pct > 0.10:
                clase, conf = "Mixta: 2014 + elementos sin fecha o con ajustes", "Media"
                ev.append(f"{round(100 * sin_fecha_pct)} % de los elementos no tiene fecha: pueden ser posteriores a 2014")
            else:
                clase, conf = "2014 (Acuerdo 48)", "Alta"
        elif n25 > 0 and n14 == 0 and nmid == 0:
            clase, conf = "2026 (revisión)", "Alta"
        else:
            clase, conf = "Mixta: 2014 + elementos sin fecha o con ajustes", "Alta"
    if not clase:
        x0 = xml_ini or xml_rev
        if nombre_48:
            clase, conf = "2014 (Acuerdo 48)", "Alta"
        elif c["capa"].startswith("gur_ar_"):
            clase, conf = "2026 (revisión)", "Alta"
        elif x0 and x0 <= "2016-12-31":
            clase, conf = "2014 (Acuerdo 48)", "Media"
        elif es_spc and x0 and "2024-01-01" <= x0 <= "2026-12-31":
            clase, conf = "Inventario 2024–2026 (redes, equipamientos y patrimonio)", "Media"
        elif x0 and x0 >= "2025-01-01":
            clase, conf = "2025–2026 (revisión: norma propuesta o ajustada)", "Media"
        elif x0 and x0 >= "2024-01-01":
            clase, conf = "Ajuste de la norma de 2014 en la revisión (metadata 2024)", "Media"
        elif dic_min and dic_max and dic_max <= "2016-12-31":
            clase, conf = "2014–2016 (probable Acuerdo 48; sin fecha en la capa ni en el XML)", "Baja"
        else:
            clase, conf = "Por confirmar: sin fecha en la capa ni en el XML", "Baja"
    # casos especiales documentados
    nota = []
    if c["capa"].startswith("gur_ar_amenaza") or c["capa"] == "gur_ar_condicion_amenaza":
        nota.append("amenaza: elaborada con el estudio básico (EAFIT, 2025) y estudios de detalle; en inundación 36 polígonos (4,95 ha) conservan la zonificación del POT 2014")
    if c["capa"].startswith("gur_ar_riesgo"):
        nota.append("riesgo: diccionario 2026-02-25; delimitación con estudios de detalle adoptados por el Distrito")
    if ladm and clase.startswith("2014"):
        nota.append("contenido de 2014 con campos LADM-COL-POT agregados en 2026 (homologación)")
    if d and d.get("cantidad") and re.fullmatch(r"\d+", d["cantidad"]) and int(d["cantidad"]) != ntot:
        nota.append(f"el diccionario declara {d['cantidad']} elementos y la capa tiene {ntot}")
    if c["capa"] != d.get("nombre_dic", c["capa"]) and norm(c["capa"]) == norm(d.get("nombre_dic", "")):
        nota.append(f"nombre distinto en el diccionario: «{d['nombre_dic']}»")
    t = topo.get(k, [])
    xml = c["xml"]
    filas.append(dict(
        grupo=c["grupo"], capa=c["capa"], geom=c["geom"], n=ntot, clase=clase, conf=conf, evidencia=" | ".join(ev),
        nota=" | ".join(nota), n14=n14, nmid=nmid, n25=n25,
        nulos=(ntot - n14 - nmid - n25) if ref and ref.get("no_nulos") is not None else "",
        dic_min=dic_min, dic_max=dic_max, cantidad_dic=d.get("cantidad", ""), en_dic="Sí" if d else "No",
        descripcion=desc, normas=", ".join(norma), dependencia=d.get("dependencia", ""), correo=d.get("correo", ""),
        topologia=d.get("topologia", ""), excepciones=d.get("excepciones", ""),
        topo_n=sum(int(x["n"]) for x in t if str(x["n"]).isdigit()) if t else "", topo_regla="; ".join(sorted({x["regla"][:40] for x in t})),
        xml_crea=xml["creadate"], xml_titulo=xml["titulo"], xml_resumen=xml["resumen"], xml_creditos=xml["creditos"], xml_ref=xml_ref_txt, xml_mod=xml["moddate"], xml_prop=xml["proposito"],
        campos_gdb=len(campos_gdb), campos_sin_doc=len(sin_doc), sin_doc=", ".join(sin_doc), solo_dic=", ".join(solo_dic),
        ladm=len(ladm), campos_fecha=", ".join(c["campos_fecha"]),
        clasif_pub=", ".join(f"{a}: {b}" for a, b in d.get("clasif", {}).items() if a),
    ))
    for x in campos_gdb:
        fe = dic_campos.get(x.lower(), "")
        campos_rows.append(dict(capa=c["capa"], campo=x, en_dic="Sí" if x.lower() in dic_campos else "No", fecha_dic=fe,
                                ladm="Sí" if x.lower().startswith(("ladm", "_ladm")) else ""))
    for nm in solo_dic:
        campos_rows.append(dict(capa=c["capa"], campo=nm, en_dic="Solo en el diccionario", fecha_dic=dic_campos[nm], ladm=""))

# ---------- Excel
wb = Workbook()
HF = PatternFill("solid", fgColor="1F3A5F"); HFont = Font(bold=True, color="FFFFFF")
COLORES = {"2014 (Acuerdo 48)": "D9D9D9", "2026 (revisión)": "C6E0B4", "Mixta: 2014 + elementos sin fecha o con ajustes": "FFE699",
           "Inventario 2024–2026 (redes, equipamientos y patrimonio)": "DDEBF7",
           "2025–2026 (revisión: norma propuesta o ajustada)": "E2F0D9",
           "Ajuste de la norma de 2014 en la revisión (metadata 2024)": "FFF2CC",
           "2014–2016 (probable Acuerdo 48; sin fecha en la capa ni en el XML)": "EDEDED",
           "Instrumentos complementarios (fecha propia de cada instrumento)": "E4DFEC",
           "Por confirmar: sin fecha en la capa ni en el XML": "F8CBAD"}
thin = Side(style="thin", color="BFBFBF")


ORIGEN = {"[Diccionario DAP]": "2F5597", "[Metadata XML de la gdb]": "1F7A7A", "[Datos de la gdb]": "595959",
          "[Topologia.xlsx DAP]": "7030A0", "[Cálculo PAC]": "9C2A2A"}


def hoja(ws, cols, rows, anchos):
    ws.append([c[0] for c in cols])
    for cell in ws[1]:
        cell.fill, cell.font = HF, HFont
        for pref, col in ORIGEN.items():
            if str(cell.value).startswith(pref):
                cell.fill = PatternFill("solid", fgColor=col)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append([r[c[1]] for c in cols])
    for i, w in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[1].height = 42


# 1. LEEME
ws = wb.active; ws.title = "LEEME"
texto = [
    ("Trazabilidad 2026 / 2014 de las capas de la geodatabase del POT (revisión de mediano plazo)", True),
    ("Fecha del análisis: 2026-10-18. Preparado por Marcos Arango Tamayo (ITM) con apoyo de Claude. Solo lectura: no se modificó ningún dato recibido.", False),
    ("", False),
    ("Fuente analizada", True),
    ("Archivo YDRAY-GDB_Form_DiccTopolog.zip: geodatabase mj_rev_pot_2025_med.gdb (82 capas de datos más 328 capas de errores topológicos T_xx), diccionario de datos FO-GINF-041 y Topologia.xlsx. SHA-256 del zip: a5a80c402fb76313fb1c4d1d4ce11a573671b9e1962e8a578d4d95f1da2e0de2.", False),
    ("", False),
    ("Lo que dice el correo del Departamento Administrativo de Planeación (DAP) que acompaña el envío", True),
    ("1) No todas las capas integran la revisión de mediano plazo: algunas contienen ajustes parciales (actualización de inventarios o intervenciones ejecutadas) y otras se mantienen tal como fueron estructuradas en la revisión de largo plazo de 2014 (Acuerdo 48 de 2014).", False),
    ("2) La información aún no está protocolizada: permanece en revisión, análisis y validación por parte del Concejo Distrital de Medellín y es susceptible de cambios y ajustes hasta su aprobación oficial.", False),
    ("Consecuencia para el PAC: toda cifra o mapa que salga de esta geodatabase debe declararse como «propuesta de revisión del POT 2026, aún no protocolizada», y las capas que no cambiaron deben citarse como Acuerdo 48 de 2014.", False),
    ("", False),
    ("Cómo se asignó la trazabilidad (columna «Trazabilidad propuesta» de la hoja Capas)", True),
    ("El DAP no declara en una columna qué capa es de 2014 y cuál de 2026; esta clasificación se infiere de seis evidencias y siempre se muestran en la columna «Evidencias»: (a) fechas de adopción y de actualización dentro de los propios datos (campos fecha_adopcion / fecha_actualizacion); (b) fecha de elaboración del diccionario FO-GINF-041; (c) sufijo del nombre de la capa (_48, _2014); (d) normas citadas en la descripción; (e) campos agregados en 2026 (homologación LADM-COL-POT); (f) fechas de referencia declaradas en la metadata XML de la gdb (creación, publicación, revisión).", False),
    ("Categorías: «2014 (Acuerdo 48)»: al menos el 95 % de los elementos con fecha están fechados en 2014 o antes, ninguno en 2025–2026 y menos del 10 % sin fecha (o el nombre lleva _48 / _2014). «2026 (revisión)»: capas de amenaza y riesgo, o todas las fechas son de 2025–2026. «Mixta»: hay fechas de ambos periodos o más del 10 % de los elementos sin fecha (pueden ser posteriores a 2014). «Inventario 2025–2026»: redes de servicios públicos, equipamientos y patrimonio sin fecha dentro de la capa y con diccionario de 2025–2026; el DAP dice que algunas capas tienen actualización de inventarios. «2014–2016»: sin fecha en la capa y diccionario de 2015–2016. «Instrumentos complementarios»: cada instrumento trae su propia fecha de adopción. «Por confirmar»: sin fecha dentro de la capa y con diccionario de 2026, por lo que no se puede decir si el contenido es nuevo o de 2014.", False),
    ("Límite importante: la fecha de elaboración del diccionario describe cuándo se documentó el campo, no cuándo se produjo el dato. Por eso varias capas figuran con diccionario de 2026 pero con contenido de 2014 (los campos LADM-COL-POT se agregaron en 2026 sobre geometrías de 2014). La clasificación es una propuesta y debe confirmarse con el DAP.", False),
    ("", False),
    ("Origen de cada columna de la hoja Capas (se lee en el encabezado y en su color)", True),
    ("[Diccionario DAP] (azul): texto y fechas tomados tal cual del diccionario de datos FO-GINF-041 que envió el DAP; no se modificó ni se resumió (solo se quitaron saltos de línea sobrantes). El diccionario es un archivo Excel aparte; no está dentro de la gdb.", False),
    ("[Metadata XML de la gdb] (verde azulado): metadata que viene incrustada en la propia geodatabase (registro ArcGIS de cada capa); texto literal del DAP, sin recortar.", False),
    ("[Datos de la gdb] (gris): lo que se lee directamente de las capas (número de elementos, geometría, nombres de campos).", False),
    ("[Topologia.xlsx DAP] (morado): el resumen de excepciones topológicas que envió el DAP.", False),
    ("[Cálculo PAC] (rojo oscuro): lo único que escribimos o calculamos nosotros: trazabilidad propuesta, confianza, evidencias, notas, recuentos de elementos por rango de fechas y comparaciones entre el diccionario y la gdb.", False),
    ("", False),
    ("Hojas", True),
    ("Capas: una fila por capa con trazabilidad, evidencias, metadata declarada y calidad de la metadata. Campos: una fila por campo con su fecha en el diccionario. Calidad metadata: problemas encontrados. Resumen: conteos por categoría.", False),
]
for t, b in texto:
    ws.append([t])
    ws.cell(ws.max_row, 1).font = Font(bold=b)
    ws.cell(ws.max_row, 1).alignment = Alignment(wrap_text=True, vertical="top")
ws.column_dimensions["A"].width = 150

# 2. Capas
cols = [("[Datos de la gdb] Grupo (feature dataset)", "grupo"), ("[Datos de la gdb] Capa", "capa"), ("[Datos de la gdb] Geometría", "geom"),
        ("[Datos de la gdb] Elementos", "n"),
        ("[Cálculo PAC] Trazabilidad propuesta", "clase"), ("[Cálculo PAC] Confianza", "conf"), ("[Cálculo PAC] Evidencias", "evidencia"),
        ("[Cálculo PAC] Notas", "nota"),
        ("[Cálculo PAC] Elementos fechados ≤2014 (campos de fecha de la capa)", "n14"),
        ("[Cálculo PAC] Elementos fechados 2015–2024", "nmid"), ("[Cálculo PAC] Elementos fechados 2025–2026", "n25"),
        ("[Cálculo PAC] Elementos sin fecha", "nulos"),
        ("[Metadata XML de la gdb] Fechas de referencia (creación / publicación / revisión)", "xml_ref"),
        ("[Metadata XML de la gdb] Última modificación del registro", "xml_mod"),
        ("[Diccionario DAP] Fecha de elaboración (mín.)", "dic_min"), ("[Diccionario DAP] Fecha de elaboración (máx.)", "dic_max"),
        ("[Cálculo PAC] ¿Está en el diccionario?", "en_dic"), ("[Diccionario DAP] Elementos declarados", "cantidad_dic"),
        ("[Diccionario DAP] Descripción (texto literal del DAP)", "descripcion"),
        ("[Cálculo PAC] Normas citadas en la descripción", "normas"),
        ("[Diccionario DAP] Dependencia", "dependencia"), ("[Diccionario DAP] Contacto", "correo"),
        ("[Diccionario DAP] Topología declarada", "topologia"), ("[Diccionario DAP] Excepciones declaradas", "excepciones"),
        ("[Topologia.xlsx DAP] Excepciones topológicas", "topo_n"),
        ("[Metadata XML de la gdb] Creación del registro (ArcGIS)", "xml_crea"), ("[Metadata XML de la gdb] Título", "xml_titulo"),
        ("[Metadata XML de la gdb] Resumen (texto literal del DAP)", "xml_resumen"),
        ("[Metadata XML de la gdb] Propósito (texto literal del DAP)", "xml_prop"), ("[Metadata XML de la gdb] Créditos", "xml_creditos"),
        ("[Datos de la gdb] Campos", "campos_gdb"), ("[Cálculo PAC] Campos sin documentar", "campos_sin_doc"), ("[Cálculo PAC] Cuáles", "sin_doc"),
        ("[Cálculo PAC] Documentados pero no están en la gdb", "solo_dic"),
        ("[Datos de la gdb] Campos LADM-COL-POT", "ladm"), ("[Datos de la gdb] Campos de fecha", "campos_fecha"),
        ("[Diccionario DAP] Clasificación de publicación (campos)", "clasif_pub")]
filas.sort(key=lambda r: (r["grupo"], r["capa"]))
ws = wb.create_sheet("Capas")
hoja(ws, cols, filas, [18, 30, 14, 11, 30, 10, 70, 50, 11, 11, 11, 11, 34, 14, 12, 12, 9, 12, 70, 24, 24, 24, 9, 40, 10, 14, 24, 60, 60, 24, 8, 9, 30, 30, 8, 24, 30])
for row in ws.iter_rows(min_row=2):
    cl = row[4].value
    if cl in COLORES:
        row[4].fill = PatternFill("solid", fgColor=COLORES[cl])
    if str(row[1].value).startswith("gur_ar_"):
        for cell in row[:4]:
            cell.font = Font(bold=True)

# 3. Campos
ws = wb.create_sheet("Campos")
hoja(ws, [("Capa", "capa"), ("Campo", "campo"), ("¿Está en el diccionario?", "en_dic"), ("Fecha de elaboración del campo", "fecha_dic"), ("Campo LADM-COL-POT", "ladm")],
     sorted(campos_rows, key=lambda r: (r["capa"], r["campo"])), [34, 34, 22, 18, 12])

# 4. Calidad metadata
prob = []
for r in filas:
    for m in r["nota"].split(" | "):
        if m.startswith("el diccionario declara") or m.startswith("nombre distinto"):
            prob.append(dict(capa=r["capa"], tipo="Cantidad o nombre", detalle=m))
    if r["campos_sin_doc"]:
        prob.append(dict(capa=r["capa"], tipo="Campos sin documentar", detalle=r["sin_doc"]))
    if r["solo_dic"]:
        prob.append(dict(capa=r["capa"], tipo="Campos documentados que no existen en la capa", detalle=r["solo_dic"]))
    if not r["dic_min"]:
        prob.append(dict(capa=r["capa"], tipo="Sin fecha de elaboración en el diccionario", detalle=""))
    if r["en_dic"] == "No":
        prob.append(dict(capa=r["capa"], tipo="No está en el diccionario", detalle=""))
extras = [
    ("gur_ar_riesgo_inundaciones", "Descripción copiada", "La descripción dice «amenaza alta por avenida torrencial»; es copia de la capa de avenidas torrenciales."),
    ("gur_ar_riesgo_mov_masa", "Clasificación de publicación vacía", "El campo `fuente` no tiene clasificación de publicación en el diccionario."),
    ("Topologia.xlsx", "Capa que no existe con ese nombre", "La capa «gu_spc_vias_urbanorural» de Topologia.xlsx es gur_spc_vias_urbanorural en la gdb."),
    ("Topologia.xlsx", "Nota pendiente dentro del archivo", "Una fila dice que faltan las dos capas de servicios públicos (aseo y agua potable) y la capa de licencias de bienes de interés cultural «del 48» que van en el mapa 3; corresponden a gur_spc_aseo_48, gur_spc_acuedpotable_48 y ur_spc_patrimonio_licbic_p_48."),
    ("Diccionario", "Nombre distinto", "«sget_splc_instrum_segundo_nivel» (diccionario) frente a sget_splc_instrum_segundonivel (gdb); «g_cs_ centros_poblados» con espacio."),
    ("Diccionario", "Fechas mal formateadas", "Algunas fechas de elaboración vienen como número de serie de Excel o como texto dd/mm/aaaa; se normalizaron al leerlas."),
    ("gdb", "Nombre del archivo", "La gdb se llama mj_rev_pot_2025_med.gdb pero el diccionario es de 2026; los registros de metadata XML se crearon entre 2024-11-28 y 2026-10-14 y no equivalen a la fecha de los datos."),
    ("gur_ar_amenaza_*", "Campo `estudio` marcado como dato privado", "Si una figura o tabla cita el estudio de detalle por nombre, hay que confirmar con el DAP que puede publicarse."),
]
for a, b, c_ in extras:
    prob.append(dict(capa=a, tipo=b, detalle=c_))
ws = wb.create_sheet("Calidad metadata")
hoja(ws, [("Capa", "capa"), ("Tipo de problema", "tipo"), ("Detalle", "detalle")], prob, [38, 38, 120])

# 5. Resumen
cnt = {}
for r in filas:
    cnt.setdefault(r["clase"], []).append(r["capa"])
ws = wb.create_sheet("Resumen")
ws.append(["Trazabilidad propuesta", "N.º de capas", "Capas"])
for cell in ws[1]:
    cell.fill, cell.font = HF, HFont
for k_, v_ in sorted(cnt.items(), key=lambda x: -len(x[1])):
    ws.append([k_, len(v_), ", ".join(v_)])
    if k_ in COLORES:
        ws.cell(ws.max_row, 1).fill = PatternFill("solid", fgColor=COLORES[k_])
ws.append(["Total", sum(len(v) for v in cnt.values()), ""])
ws.cell(ws.max_row, 1).font = Font(bold=True)
ws.column_dimensions["A"].width = 52; ws.column_dimensions["B"].width = 12; ws.column_dimensions["C"].width = 150
for row in ws.iter_rows(min_row=2):
    for cell in row:
        cell.alignment = Alignment(wrap_text=True, vertical="top")
wb.move_sheet("Resumen", offset=-3)
wb.save(OUT)
print("guardado", OUT)
for k_, v_ in sorted(cnt.items(), key=lambda x: -len(x[1])):
    print(f"{len(v_):3d}  {k_}")
json.dump(filas, open(OUT.replace(".xlsx", "_filas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
