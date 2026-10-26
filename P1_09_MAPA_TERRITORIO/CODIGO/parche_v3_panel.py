# -*- coding: utf-8 -*-
"""Reordena el panel de capas: 1 problemas (amenazas y calor) -> 2 soluciones -> 3 dónde falta -> referencias; agrega «Quitar todas las capas»."""
import os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, "plantilla.html")
s = open(p, encoding="utf-8").read()
a = s.index('      <h3>Amenaza (POT) <span class="yr">(2026)</span> <span class="m6-star">*</span></h3>')
b = s.index('      <h3>Leyenda</h3>')
nuevo = '''      <div class="m6-topbar"><button class="btn" id="m6-clear" title="Quita del mapa todas las capas, incluidos los límites; el mapa base queda">Quitar todas las capas</button><span class="st">Primero los problemas, luego las soluciones</span></div>
      <h3>1 · Problemas <span class="yr">(amenazas y calor)</span></h3>
      <div class="m6-sub">Amenazas del POT 2026 <span class="yr">(2026)</span> <span class="m6-star">*</span></div>
      <div class="m6-hz"><label class="r"><input type="checkbox" data-h="mm" checked> Deslizamientos</label><input type="range" class="m6-hop" data-h="mm" min="10" max="100" value="65" aria-label="Opacidad de deslizamientos"></div>
      <div class="m6-hz"><label class="r"><input type="checkbox" data-h="inu"> Inundación</label><input type="range" class="m6-hop" data-h="inu" min="10" max="100" value="75" aria-label="Opacidad de inundación"></div>
      <div class="m6-hz"><label class="r"><input type="checkbox" data-h="tor"> Avenidas torrenciales</label><input type="range" class="m6-hop" data-h="tor" min="10" max="100" value="75" aria-label="Opacidad de avenidas torrenciales"></div>
      <div class="note" style="margin:2px 0 0;font-size:11.5px">Puede marcar varias; con dos o más, cada amenaza usa su propio color (tonos oscuro, medio y claro para alta, media y baja).</div>
      <div class="m6-sub">Incendios forestales · plan municipal de gestión del riesgo <span class="yr">(sin fecha de corte)</span></div>
      <div class="m6-hz"><label class="r"><input type="checkbox" data-h="inc"> Amenaza por incendios forestales</label><input type="range" class="m6-hop" data-h="inc" min="10" max="100" value="80" aria-label="Opacidad de incendios forestales"></div>
      <div class="m6-sub">Multiamenaza <span class="yr">(2026)</span> <span class="m6-star">*</span></div>
      <div class="m6-hz"><label class="r"><input type="checkbox" data-h="multi"> Índice 1 a 27</label><input type="range" class="m6-hop" data-h="multi" min="10" max="100" value="80" aria-label="Opacidad de la multiamenaza"></div>
      <div class="note" style="margin:2px 0 0;font-size:11.5px">Criterio del equipo, no normativo: baja = 1, media = 2, alta = 3; el índice es el producto de las tres amenazas (deslizamientos × inundación × avenidas torrenciales). Fuera de la mancha de inundación o de avenidas torrenciales vale 1. Detalle y límites debajo del mapa.</div>
      <div class="m6-sub">Calor · temperatura de la superficie <span class="yr">(2013–2016)</span></div>
      <label class="r"><input type="radio" name="m6-lst" value="none" checked> Ninguna</label>
      <label class="r"><input type="radio" name="m6-lst" value="barrio"> Por barrio, sin efecto de la pendiente</label>
      <label class="r"><input type="radio" name="m6-lst" value="com"> Por comuna, mediana</label>
      <label class="r"><input type="radio" name="m6-lst" value="comn"> Por comuna, sin efecto de la pendiente</label>
      <div class="op">Opacidad <input type="range" min="10" max="100" value="70" id="m6-opl" aria-label="Opacidad de la temperatura"></div>
      <h3>2 · Soluciones <span class="yr">(medidas que hoy están registradas)</span></h3>
      <div class="m6-sub">Arbolado y verde urbano</div>
      <label class="r"><input type="radio" name="m6-arb" value="none" checked> Sin mapa por barrio</label>
      <label class="r"><input type="radio" name="m6-arb" value="arb"> Árboles por hectárea <span class="yr">(inventario de árboles)</span></label>
      <label class="r"><input type="radio" name="m6-arb" value="copa"> % del barrio con cobertura arbórea <span class="yr">(2019)</span></label>
      <label class="r"><input type="radio" name="m6-arb" value="verde"> % del barrio con espacios verdes <span class="yr">(2019)</span></label>
      <div class="note" style="margin:0 0 2px;font-size:11.5px"><a href="#m6-abdet" class="m6-link" data-open="m6-abdet">Cómo se construyó el índice de arbolado</a></div>
      <label class="r"><input type="checkbox" data-m="pot"> Zonas verdes con potencial verde</label>
      <label class="r"><input type="checkbox" data-m="techo"> Techos verdes (cubierta verde marcada) <span class="yr">(2019)</span></label>
      <label class="r"><input type="checkbox" data-m="eco"> Ecoparques</label>
      <label class="r"><input type="checkbox" data-m="cor"> Corredores verdes, trazados del POT 2014 <span class="yr">(2014)</span></label>
      <div class="m6-sub">Obras de ladera y quebrada</div>
      <label class="r"><input type="checkbox" data-m="obras"> Obras de mitigación <span class="yr">(2016–2022)</span></label>
      <label class="r"><input type="checkbox" data-m="monit"> Monitoreo geotécnico</label>
      <label class="r"><input type="checkbox" data-m="estu"> Estudios y diseños de gestión del riesgo</label>
      <div class="m6-sub">Alerta temprana y evacuación</div>
      <label class="r"><input type="checkbox" data-m="alarm"> Alarmas y sensores de nivel</label>
      <label class="r"><input type="checkbox" data-m="enc"> Puntos de encuentro y rutas de evacuación</label>
      <h3>3 · Dónde falta <span class="m6-star">*</span> <span class="yr">(problema alto y solución sin registro, por barrio)</span></h3>
      <label class="r"><input type="radio" name="m6-bre" value="none" checked> Sin marca</label>
      <label class="r"><input type="radio" name="m6-bre" value="calor"> Calor alto y poco arbolado</label>
      <label class="r"><input type="radio" name="m6-bre" value="ladera"> Deslizamiento alto sin obra ni monitoreo</label>
      <label class="r"><input type="radio" name="m6-bre" value="alerta"> Avenida torrencial alta sin alerta temprana</label>
      <div class="note" style="margin:2px 0 0;font-size:11.5px">Las marcas son un criterio del equipo, con umbrales por cuartil escritos en el recuadro «Cómo se marcan las brechas».</div>
      <h3>Referencias</h3>
      <label class="r"><input type="checkbox" id="m6-lim" checked> Comunas y corregimientos <span class="yr">(2014)</span></label>
      <div class="filters" style="margin:6px 0 0"><select id="m6-base" aria-label="Mapa base"><option value="claro">Mapa base gris claro</option><option value="oscuro">Mapa base gris oscuro</option><option value="calles">Calles (OpenStreetMap)</option><option value="sat">Imagen satelital</option></select></div>
'''
s = s[:a] + nuevo + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("panel reordenado")
