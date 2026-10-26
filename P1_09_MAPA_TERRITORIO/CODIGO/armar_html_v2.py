# -*- coding: utf-8 -*-
"""Etapa 2: arma el HTML final (plantilla + Leaflet 1.9.4 + datos)."""
import os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\marco\Downloads\Producto9_mapa_territorio_PAC_v2.html"

def leaflet(nombre):
    ruta = os.path.join(D, nombre)
    if not os.path.exists(ruta):
        url = "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/" + nombre
        subprocess.run(["curl", "-sSL", "-m", "60", "-o", ruta, url], check=True)
    return open(ruta, encoding="utf-8").read()

css, js = leaflet("leaflet.css"), leaflet("leaflet.js")
js = js.replace("</script>", "<\\/script>")
datos = open(os.path.join(D, "mapa_datos_v2.json"), encoding="utf-8").read()
datos = datos.replace("</", "<\\/")
html = open(os.path.join(D, "plantilla.html"), encoding="utf-8").read()
html = html.replace("__LEAFLET_CSS__", css).replace("__LEAFLET_JS__", js).replace("__DATA_JSON__", datos)
open(OUT, "w", encoding="utf-8").write(html)
print("escrito:", OUT, round(os.path.getsize(OUT) / 1048576, 2), "MB")
