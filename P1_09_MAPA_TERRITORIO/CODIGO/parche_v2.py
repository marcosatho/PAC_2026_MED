# -*- coding: utf-8 -*-
"""Parche v2 de la plantilla: selección múltiple de amenazas, leyenda ampliada con criterios del POT, años entre paréntesis."""
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plantilla.html")
s = open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert s.count(old) >= 1, "no encontrado: " + old[:80]
    s = s.replace(old, new, 1)


# ---------- CSS ----------
rep("#t6 .m6-panel{border:1px solid var(--line);border-radius:10px;padding:14px;background:var(--surface);font-size:13px}",
    "#t6 .m6-panel{border:1px solid var(--line);border-radius:10px;padding:14px;background:var(--surface);font-size:13px;max-height:640px;overflow-y:auto}\n"
    "@media (max-width:1000px){#t6 .m6-panel{max-height:none}}\n"
    "#t6 .yr{color:var(--muted);font-weight:400;font-size:.82em;white-space:nowrap}\n"
    "#t6 .m6-hz{display:grid;grid-template-columns:minmax(0,1fr) 76px;gap:8px;align-items:center}\n"
    "#t6 .m6-hz input[type=range]{width:100%}\n"
    "#t6 .lg{display:grid;grid-template-columns:18px minmax(0,1fr);gap:8px;margin:6px 0;align-items:start;color:var(--ink2);font-size:12.5px}\n"
    "#t6 .lg i{width:16px;height:12px;border-radius:2px;display:inline-block;border:1px solid rgba(0,0,0,.18);margin-top:3px}\n"
    "#t6 .lg small{display:block;color:var(--muted);font-size:11.5px;line-height:1.35}\n"
    "#t6 .lg-t{font-weight:600;margin:10px 0 2px;color:var(--ink)}\n"
    "#t6 .lg-t:first-child{margin-top:0}")

# ---------- HTML del panel ----------
a = s.index('      <h3>Amenaza (POT 2026) <span class="m6-star">*</span></h3>')
b = s.index('      <h3>Temperatura de la superficie</h3>')
s = s[:a] + '''      <h3>Amenaza (POT) <span class="yr">(2026)</span> <span class="m6-star">*</span></h3>
      <div class="m6-hz"><label class="r"><input type="checkbox" data-h="mm" checked> Deslizamientos</label><input type="range" class="m6-hop" data-h="mm" min="10" max="100" value="65" aria-label="Opacidad de deslizamientos"></div>
      <div class="m6-hz"><label class="r"><input type="checkbox" data-h="inu"> Inundación</label><input type="range" class="m6-hop" data-h="inu" min="10" max="100" value="75" aria-label="Opacidad de inundación"></div>
      <div class="m6-hz"><label class="r"><input type="checkbox" data-h="tor"> Avenidas torrenciales</label><input type="range" class="m6-hop" data-h="tor" min="10" max="100" value="75" aria-label="Opacidad de avenidas torrenciales"></div>
      <div class="note" style="margin:2px 0 0;font-size:11.5px">Puede marcar varias; con dos o más, cada amenaza usa su propio color (tonos oscuro, medio y claro para alta, media y baja).</div>
''' + s[b:]
rep('<h3>Temperatura de la superficie</h3>', '<h3>Temperatura de la superficie <span class="yr">(2013–2016)</span></h3>')
rep('<label class="r"><input type="checkbox" id="m6-lim" checked> Comunas y corregimientos</label>',
    '<label class="r"><input type="checkbox" id="m6-lim" checked> Comunas y corregimientos <span class="yr">(2014)</span></label>')
rep('<h2>Mapa interactivo: amenazas del POT 2026* y temperatura de la superficie</h2>',
    '<h2>Mapa interactivo: amenazas del POT 2026* y temperatura de la superficie <span class="yr">(2013–2016)</span></h2>')

# ---------- JS: estado y capas ----------
rep("hazLayers={},lstLayers={},base={},baseCur=null,hazCur='mm',lstCur='none'",
    "hazLayers={},lstLayers={},base={},baseCur=null,on={mm:true,inu:false,tor:false},lstCur='none'")
rep("    map.createPane('haz');map.getPane('haz').style.zIndex=410;\n",
    "    ['mm','inu','tor'].forEach((h,i)=>{map.createPane('haz_'+h);map.getPane('haz_'+h).style.zIndex=410+i*2;});\n")
rep("hazLayers[h]=L.geoJSON(D.haz_geo[h],{pane:'haz',interactive:false,renderer:L.canvas({pane:'haz'}),",
    "hazLayers[h]=L.geoJSON(D.haz_geo[h],{pane:'haz_'+h,interactive:false,renderer:L.canvas({pane:'haz_'+h}),")

a = s.index("  function apply(){")
b = s.index("  function legendInit(){")
nuevo = '''  const HUE={mm:{alta:'#b3271b',media:'#ec835a',baja:'#f7cbb5'},inu:{alta:'#0b4f9c',media:'#4f8fd6',baja:'#b8d3f0'},tor:{alta:'#5b2a86',media:'#9b6bc2',baja:'#d9c3ea'}};
  const nOn=()=>Object.values(on).filter(Boolean).length;
  const hazColor=(h,c)=>nOn()>=2?HUE[h][c]:COL[c];
  const opH=h=>document.querySelector('.m6-hop[data-h='+h+']').value/100, opL=()=>document.getElementById('m6-opl').value/100;
  function apply(){
    Object.values(hazLayers).forEach(l=>map.removeLayer(l));
    Object.values(lstLayers).forEach(l=>map.removeLayer(l));
    ['mm','inu','tor'].forEach(h=>{if(on[h]){hazLayers[h].addTo(map);hazLayers[h].setStyle(f=>({stroke:false,fillColor:hazColor(h,f.properties.clase),fillOpacity:opH(h)}));}});
    if(lstCur!=='none'){lstLayers[lstCur].addTo(map);lstLayers[lstCur].setStyle({fillOpacity:opL()});}
    if(document.getElementById('m6-lim').checked)limLayer.addTo(map);else map.removeLayer(limLayer);
    legend();
  }
  /* criterios de cada clase según el estudio de amenaza del POT 2026 (EBA, Universidad EAFIT; DAP, 2026a) */
  const CRIT={
    mm:{alta:'Laderas fuertes a muy fuertes (pendiente mediana ≈ 30°). Reúne ~57 % de los deslizamientos registrados.',media:'Relieves moderados a fuertes (≈ 26°). ~25 % de los deslizamientos registrados.',baja:'Relieves suaves a moderados (≈ 14°): planicies aluviales y laderas bajas. ~19 % de los registrados.'},
    inu:{alta:'Crecida con período de retorno de 10 años (10 % de probabilidad al año). Las quebradas canalizadas o embovedadas entran como alta por defecto.',media:'Crecida de 100 años (1 % al año).',baja:'Crecida de 500 años (0,2 % al año).'},
    tor:{alta:'Mayor intensidad del flujo: índice de intensidad ≈ 50 m³/s² (evento de 25 años).',media:'Índice de intensidad de flujo entre 1 y 50 m³/s².',baja:'Recurrencia de 500 años; índice de intensidad menor a 1 m³/s².'}
  };
  const HZY={mm:'Deslizamientos',inu:'Inundación',tor:'Avenidas torrenciales'};
  function legend(){
    let h='';
    ['mm','inu','tor'].forEach(k=>{if(!on[k])return;
      h+='<div class="lg-t">'+HZY[k]+' <span class="yr">(2026)</span> <span class="m6-star">*</span></div>'+
        ['alta','media','baja'].map(c=>'<div class="lg"><i style="background:'+hazColor(k,c)+'"></i><div><b>Amenaza '+c+'</b> · '+fmt(TOT[k+'_'+c])+' % del Distrito ('+fmt(TOT[k+'_'+c+'_ha'],0)+' ha)<small>'+CRIT[k][c]+'</small></div></div>').join('');
    });
    if(lstCur!=='none'){
      const lab=['< 26','26–28','28–30','30–32','32–34','≥ 34'];
      h+='<div class="lg-t">Temperatura de la superficie, °C <span class="yr">(2013–2016)</span></div>'+
        RAMP.map((c,i)=>'<div class="lg" style="margin:2px 0"><i style="background:'+c+'"></i><div>'+lab[i]+'</div></div>').join('')+'<div class="lg" style="margin:2px 0"><i style="background:#cfcfcf"></i><div>Sin dato</div></div><small style="color:var(--muted);font-size:11.5px">Mediana de imágenes Landsat de la mañana (30 m). '+(lstCur==='com'?'Valor crudo.':'Sin el efecto de la pendiente y la orientación de las laderas.')+'</small>';
    }
    if(document.getElementById('m6-lim').checked)h+='<div class="lg-t">Límites <span class="yr">(2014)</span></div><div class="lg"><i style="background:transparent;border:2px solid #1E463D"></i><div>Comunas y corregimientos</div></div>';
    if(!h)h='<span class="st" style="color:var(--muted)">Active una capa.</span>';
    document.getElementById('m6-leg').innerHTML=h;
  }

'''
s = s[:a] + nuevo + s[b:]

# handlers
rep("    document.querySelectorAll('input[name=m6-haz]').forEach(i=>i.addEventListener('change',()=>{if(i.checked){hazCur=i.value;if(map)apply();else legend();}}));",
    "    document.querySelectorAll('input[data-h]').forEach(i=>i.addEventListener('change',()=>{on[i.dataset.h]=i.checked;if(map)apply();else legend();}));\n"
    "    document.querySelectorAll('.m6-hop').forEach(i=>i.addEventListener('input',()=>{if(map)apply();}));")
rep("    ['m6-oph','m6-opl'].forEach(id=>document.getElementById(id).addEventListener('input',()=>{if(map)apply();}));",
    "    document.getElementById('m6-opl').addEventListener('input',()=>{if(map)apply();});")
rep("_state:()=>({hazCur,lstCur,sel})", "_state:()=>({on,lstCur,sel})")
rep("document.getElementById('m6-lim').addEventListener('change',()=>{if(map)apply();});",
    "document.getElementById('m6-lim').addEventListener('change',()=>{if(map)apply();else legend();});")

# ---------- años en tabla y KPI ----------
rep("[['nombre','Territorio',0],['km2','km²',1],['mm_alta','Deslizamientos alta (%)*',1],['inu_alta','Inundación alta (%)*',1],['tor_alta','Torrenciales alta (%)*',1],['lst','Temp. superficie (°C)',1],['lst_n','Temp. sin pendiente (°C)',1]]",
    "[['nombre','Territorio <span class=\"yr\">(2014)</span>',0],['km2','km²',1],['mm_alta','Deslizamientos alta (%)* <span class=\"yr\">(2026)</span>',1],['inu_alta','Inundación alta (%)* <span class=\"yr\">(2026)</span>',1],['tor_alta','Torrenciales alta (%)* <span class=\"yr\">(2026)</span>',1],['lst','Temp. superficie (°C) <span class=\"yr\">(2013–2016)</span>',1],['lst_n','Temp. sin pendiente (°C) <span class=\"yr\">(2013–2016)</span>',1]]")
rep("'del Distrito en amenaza alta por deslizamientos* ('+fmt(TOT.mm_alta_ha,0)+' ha)'", "'del Distrito en amenaza alta por deslizamientos* (2026; '+fmt(TOT.mm_alta_ha,0)+' ha)'")
rep("'en amenaza alta por inundación* ('+fmt(TOT.inu_alta)+' % del Distrito)'", "'en amenaza alta por inundación* (2026; '+fmt(TOT.inu_alta)+' % del Distrito)'")
rep("'en amenaza alta por avenidas torrenciales* ('+fmt(TOT.tor_alta)+' % del Distrito)'", "'en amenaza alta por avenidas torrenciales* (2026; '+fmt(TOT.tor_alta)+' % del Distrito)'")
rep("'más caliente la superficie en comunas ('+fmt(TOT.lst_com)+' °C) que en corregimientos ('+fmt(TOT.lst_cor)+' °C); '",
    "'más caliente la superficie en comunas ('+fmt(TOT.lst_com)+' °C) que en corregimientos ('+fmt(TOT.lst_cor)+' °C) (2013–2016); '")
rep("<h2>Lo que la base de variables tiene hoy en estos cuatro bloques</h2>",
    "<h2>Lo que la base de variables tiene hoy en estos cuatro bloques <span class=\"yr\">(v1, octubre de 2026)</span></h2>")

open(p, "w", encoding="utf-8").write(s)
print("ok | hazCur restantes:", s.count("hazCur"), "| m6-oph:", s.count("m6-oph"), "| name=m6-haz:", s.count("m6-haz"))
