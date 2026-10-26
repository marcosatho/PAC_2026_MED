# -*- coding: utf-8 -*-
"""Descarga (lectura pública) de las capas de medidas del servidor de mapas de la Alcaldía, en EPSG:9377 (su sistema nativo).
Cada capa queda como GeoJSON paginado en una carpeta propia; no se transforma ni remuestrea nada."""
import json, os, sys, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

ROOT = "https://www.medellin.gov.co/servidormapas/rest/services/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
# caja del Distrito en EPSG:9377 (de los barrios) con 1 km de margen
ENV = "4698250,2238700,4727600,2264200"

CAPAS = {
    "arboles": ("ambiente_dllo_sost/VC_Gestion_Ambiental/MapServer/0", "objectid,s_estado_arbol,tipoarbol,municipio", "municipio LIKE 'MEDELL%'", True, 1000),
    "evu": ("ambiente_dllo_sost/VA_SistemaArbolUrbano_Base/MapServer/5", "objectid,categoria_msu,cobertura,cubierta_verde,sistema_pmepvu,propiedad,narb_aprox,area_ha", "1=1", True, 2000),
    "zv_potencial": ("ambiente_dllo_sost/VC_Rec_Natural_Renovable/MapServer/4", "objectid,tipologia,categoria,cober_dom,potencial_verde,cubierta_verde", "potencial_verde='Si'", False, 2000),
    "obras": ("ambiente_dllo_sost/VM_DAGRD/MapServer/3", "*", "1=1", False, 2000),
    "monit": ("ambiente_dllo_sost/VM_DAGRD/MapServer/8", "*", "1=1", False, 2000),
    "estudios": ("ambiente_dllo_sost/VM_DAGRD/MapServer/2", "objectid,titulo,tipo_estudio,anio,estado,nombre_comuna_corr,nombre_barrio_vereda", "1=1", False, 2000),
    "alarmas": ("ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer/6", "*", "1=1", False, 2000),
    "sensores": ("ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer/12", "*", "1=1", False, 2000),
    "encuentro": ("ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer/10", "*", "1=1", False, 2000),
    "rutas": ("ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer/11", "*", "1=1", False, 2000),
    "ecoparques": ("ambiente_dllo_sost/VC_Gestion_Ambiental/MapServer/2", "objectid,nombre,quebrada_asociada,subcategoria,accion", "1=1", False, 2000),
    "corredores": ("vivienda_ciudad_terri/VC_Dllo_Territorial_Planificado/MapServer/3", "objectid,actuacion,tramo,nombre", "1=1", False, 2000),
    "incendios": ("ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer/8", "*", "1=1", False, 2000),
}
SOLO = sys.argv[2:] or list(CAPAS)


def peticion(url, datos, tries=4):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode(datos).encode(), headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:
            err = e; time.sleep(2 + 3 * i)
    raise RuntimeError("falló %s: %s" % (url, err))


def campo_oid(ruta):
    j = json.loads(peticion(ROOT + ruta + "?f=json", {}))
    for f in j.get("fields") or []:
        if f.get("type") == "esriFieldTypeOID":
            return f["name"]
    return "objectid"


def base(where, campos, con_caja, extra=None, oid="objectid"):
    d = {"where": where, "outFields": campos, "f": "geojson", "outSR": "9377", "geometryPrecision": "1", "orderByFields": oid}
    if con_caja:
        d.update({"geometry": ENV, "geometryType": "esriGeometryEnvelope", "inSR": "9377", "spatialRel": "esriSpatialRelIntersects"})
    if extra:
        d.update(extra)
    return d


def bajar(nombre):
    ruta, campos, where, caja, maxrec = CAPAS[nombre]
    url = ROOT + ruta + "/query"
    carpeta = os.path.join(OUT, nombre); os.makedirs(carpeta, exist_ok=True)
    oid = campo_oid(ruta)
    dc = base(where, oid, caja, {"returnCountOnly": "true", "f": "json"}, oid); dc.pop("orderByFields", None)
    cnt = json.loads(peticion(url, dc))
    n = cnt["count"]; print(nombre, "registros:", n, flush=True)
    offs = list(range(0, n, maxrec))

    def pagina(o):
        f = os.path.join(carpeta, "p%07d.geojson" % o)
        if os.path.exists(f) and os.path.getsize(f) > 0:
            return o
        for intento in range(8):
            b = peticion(url, base(where, campos, caja, {"resultOffset": str(o), "resultRecordCount": str(maxrec)}, oid))
            j = json.loads(b)
            if "features" in j:
                open(f, "wb").write(b)
                return o
            print("   reintento", nombre, o, str(j)[:120], flush=True)
            time.sleep(15 + 10 * intento)
        raise RuntimeError("página sin features: %s %s" % (nombre, str(j)[:200]))

    with ThreadPoolExecutor(3) as ex:
        for i, _ in enumerate(ex.map(pagina, offs)):
            if i % 20 == 0:
                print("  ", nombre, i + 1, "/", len(offs), flush=True)
    print(nombre, "listo", flush=True)


for k in SOLO:
    bajar(k)
print("TODO LISTO", flush=True)
