import fs from 'node:fs/promises';
export async function addContext(w,rows){
const get=id=>rows.find(r=>r[0]===id);
function sheet(name,heads,data,widths,tableName){const s=w.worksheets.add(name);s.showGridLines=false;const end=String.fromCharCode(64+heads.length),n=data.length+1;s.getRange(`A1:${end}${n}`).values=[heads,...data];s.tables.add(`A1:${end}${n}`,true,tableName);s.getRange(`A1:${end}${n}`).format={font:{name:'Arial',size:11},wrapText:true,verticalAlignment:'top'};widths.forEach((v,j)=>s.getRangeByIndexes(0,j,n,1).format.columnWidth=v);s.getRange(`A1:${end}1`).format={fill:'#243E54',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:44};s.getRange(`A2:${end}${n}`).format.rowHeight=95;s.freezePanes.freezeRows(1);return s;}
const universe=JSON.parse(await fs.readFile('universe.json','utf8'));
sheet('Universo',['Amenaza / proceso','Familia','Temporalidad preliminar','Interacciones'],universe,[55,35,43,108],'Universo');
const origin='https://chatgpt.com/c/6a9a8bcc-a7ec-83e9-babe-bfff25a3720c';
const audit=[
['H12','Cruce con F18','Mismo portal EPM. La fecha 31/08/2026 corresponde al inicio de las interrupciones. No duplicar la fuente en conteos de documentos.',get('F18')[10]],
['H13','Cruce con F21','Misma noticia DAGRD, publicada el 28/02/2024. Se incorporó a hemeroteca por su información de incendios atendidos.',get('F21')[10]],
['H14','Cruce con F25','Misma noticia del 28/08/2023. Se corrigió el rango 2023–2026 de la tabla anterior. Es prevención y vigilancia, no un reporte de emergencia.',get('F25')[10]],
['F01–F13','Recuperación del archivo original','Se incorporaron las 13 filas del archivo original conservando ID, título, autores, DOI y URL. No se verificaron nuevamente todas las publicaciones.','Archivo proporcionado: PAC_2026_Bibliografia_Amenazas_8_1.xlsx'],
['F14–F42; H01–H11','Recuperación de tablas','Filas recuperadas de la conversación. F18, F21 y F25 se contrastaron en esta revisión. Las demás conservan los metadatos previos sin auditoría bibliográfica integral.',origin],
['F43–F49','Fuentes omitidas recuperadas','Siete fuentes citadas antes de las tablas numeradas: dos tesis, presentación AGU, preprint, artículo de adaptación, DTS de vulnerabilidad y escenarios IDEAM.',origin],
['F50–F56','Marcos metodológicos identificados','Se localizaron documentos específicos de IPCC, UNDRR–ISC y OMS para respaldar las menciones conceptuales. La versión exacta originalmente consultada no es trazable en todos los casos.',origin],
['F46','Versión y año pendientes','La conversación aporta el DOI .1 sin año. Un manuscrito con igual título y autores lleva fecha 21/11/2022. No se confirmó que sea la misma versión; no asignar ese año al DOI sin verificar.','https://d197for5662m48.cloudfront.net/documents/publicationstatus/97463/preprint_pdf/945a8dd99d7fc2fee7f0cf4aa6aa0c19.pdf'],
['F48','DTS recuperado por referencia oficial','El PAC cita C40–Alcaldía (2020a), Estudio de Vulnerabilidad. Se conserva el enlace al catálogo oficial. El PDF individual del DTS no pudo abrirse.','https://www.medellin.gov.co/es/wp-content/uploads/2021/09/PAC-MED_20210223.pdf'],
['F49','Fecha de actualización verificada','IDEAM anunció los nuevos escenarios el 12/12/2024. El horizonte futuro 2021–2100 no es una fecha de publicación fuera del criterio.','https://ideam.gov.co/sites/default/files/prensa/boletines/2024-12-12/130_ce_el_ideam_presenta_nuevas_proyecciones_climaticas_para_colombia_12_12_2024.pdf'],
['F17','Fecha pendiente','La vigencia declarada no acredita el año de publicación. Se conserva sin inventar una fecha.',get('F17')[10]],
['F29','Autores pendientes','La tabla original dice Varios autores. Se conserva ese dato y requiere completar la autoría desde la publicación.',get('F29')[10]],
['H08','Fecha incompleta','La conversación aporta solo 2026. No se inventó día ni mes.',get('H08')[10]],
['EX01','Excepción conservada','Fuente de 2014 recuperada del Excel original y de la conversación. Se cuenta aparte del periodo principal.','https://revistas.unal.edu.co/index.php/dyna/article/view/40640'],
['Sin ID bibliográfico','Antecedentes de dengue 2012–2013','La conversación los menciona sin autores ni títulos. No se pueden construir referencias verificables ni contarlos como documentos identificados.',origin],
['Hemeroteca general','Alcance de la recuperación y ampliación','La recuperación dejó 14 registros. H15–H34 añaden 20 fuentes localizadas mediante búsqueda posterior, con noticias de inundaciones, avenidas torrenciales, deslizamientos, aire, calor, incendios, agua y dengue. No se atribuyen a la conversación original ni constituyen cobertura exhaustiva.',origin],
['Universo','Clasificación preliminar','Se conservan 23 procesos de la tabla general y 3 del complemento alimentario. No equivale a demostrar ocurrencia ni tendencia local. Temporalidades y familias son una propuesta operativa.',origin],
['F09; F45; F46','Productos relacionados','Tesis, presentación y preprint pertenecen a una misma línea de investigación. No tratarlos automáticamente como tres evidencias independientes.',origin],
['F27; F44','Productos relacionados','Artículo y tesis sobre capa límite. Revisar solapamientos antes de sintetizar resultados o cuantificar evidencia.',origin],
['Fechas de documentos','Publicación frente a carga del archivo','Las fechas conservadas de las tablas previas no fueron auditadas en su totalidad. Un año en la ruta de descarga no prueba el año de publicación.',origin],
['H15–H34','Ampliación del 04/09/2026','20 fuentes adicionales: fechas, títulos, territorios y contenido pertinente contrastados en las páginas citadas. Se conservaron las 12 columnas y los 14 registros anteriores. La bibliografía F01–F56 no se volvió a auditar en esta ampliación.','URL individual en Hemeroteca, columna K'],
['H23; H24','Mismo episodio en dos municipios','Ambas noticias se refieren al 24/06/2025 en Granizal–Cañada Negra–Santo Domingo. Son dos documentos distintos, con territorios y momentos de balance diferentes. No sumarlos como dos emergencias independientes.','H23; H24'],
['H13; H30; H31','Balances de incendios solapados','H31 registra una fecha de enero de 2024, H13 los primeros meses y H30 un total de 2024 más un parcial de 2025. No sumar acumulados ni comparar periodos de distinta duración como una tendencia.','H13/F21; H30; H31'],
['H19; H29','Discrepancias de fecha visibles','H19: entradilla dice septiembre, mientras publicación y cuerpo remiten a octubre de 2024; se conserva la discrepancia. H29: fecha de autoría 16/07/2026, con marca adicional del 17/07. Se usa fecha de autoría.','H19; H29'],
['Cobertura pendiente','Hemeroteca abierta','La búsqueda es temática y selectiva. Falta un barrido sistemático por año, municipio y amenaza, especialmente años iniciales, granizo y efectos sobre ecosistemas y calidad del agua. Las noticias no permiten estimar frecuencias completas ni atribución climática.','Corte de búsqueda: 04/09/2026']
];sheet('Recuperación',['Referencia','Situación','Detalle','Fuente / procedencia'],audit,[23,42,115,90],'Recuperacion');
const criteria=[
['Ventana temporal','2015–2026 inclusive para publicaciones y noticias. Fuentes anteriores solo como excepciones identificadas.','Acuerdo de la conversación'],
['Publicación y periodo analizado','Una publicación reciente puede estudiar datos anteriores a 2015. No se excluye por el periodo observado. Los escenarios futuros pueden extenderse más allá de 2026.','Criterio de catalogación'],
['Fecha en hemeroteca','Usar publicación cuando se conoce. Si se usa la fecha del evento, declararlo. H12 usa inicio de interrupciones; H08 solo tiene año.','Criterio de catalogación'],
['Alcance del riesgo','Incluir amenazas súbitas y presiones lentas, crónicas y acumulativas. No limitar el análisis a desastres o emergencias declaradas.','Conversación; F50–F54'],
['Nivel conceptual','Distinguir condicionantes climáticos, amenazas derivadas y efectos climáticamente sensibles.','Conversación; F50–F52'],
['Dimensiones simultáneas','Clasificar por familia temática, temporalidad (súbita, lenta o mixta) e interacción (individual, compuesta o en cascada).','Conversación; F50–F53'],
['Origen territorial','Local: origen e impacto municipal. Regional: origen metropolitano o antioqueño. Extraterritorial: origen externo con efectos urbanos.','Conversación'],
['Cadena alimentaria','Evento climático → territorio productor → producción/transporte → abastecimiento → precio mayorista → IPC → acceso económico.','Conversación; F31–F42'],
['Indicadores alimentarios','Abastecimiento físico y procedencia: SIPSA-A. Precios mayoristas: SIPSA-P. Precios al consumidor: IPC. Sistema regional: FAO/RUAF.','F31–F42'],
['Cruce territorial propuesto','Producto, municipio y departamento de origen, cantidad, mercado destino y mes/año. Contrastar concentración de proveedores con exposición climática de sus territorios.','Conversación; F39'],
['Agua','Distinguir sequía de intermitencia del servicio. Analizar disponibilidad, almacenamiento, distribución y capacidad de hogares para afrontar interrupciones.','Conversación; F14–F18'],
['Calor','Distinguir incremento de temperatura, isla de calor, calor extremo y estrés térmico. Considerar humedad, radiación, ventilación, vivienda y población.','Conversación; F07–F09; F43–F46'],
['Salud y vectores','No asumir automáticamente más cambio climático = más dengue. Incorporar clima, saneamiento, agua almacenada, movilidad, densidad y control vectorial.','Conversación; F23–F26; F54–F56'],
['Calidad del aire','Meteorología, topografía y emisiones condicionan dispersión, acumulación, remoción y transporte. Diferenciar episodios agudos y exposición crónica.','Conversación; F22; F27–F30; F44'],
['Proceso del 8.1','Definir universo; clasificar conceptos y temporalidad; verificar existencia; caracterizar frecuencia, magnitud, duración, estacionalidad y tendencia; territorializar; identificar interacciones.','Conversación'],
['Preguntas de caracterización','¿Cambian magnitud, frecuencia/duración, distribución espacial, estacionalidad y ocurrencia conjunta de factores?','Conversación'],
['Preguntas territoriales','¿Qué servicios dependen del clima? ¿Qué condiciones amplifican impactos? ¿Qué efectos cotidianos preceden emergencias? ¿Qué grupos, ecosistemas y sectores soportan más efectos?','Conversación'],
['Candidatos por validar','Vientos fuertes, rayos, granizo, estrés ecosistémico y calidad/temperatura del agua necesitan evidencia local para definir su inclusión y tratamiento.','Conversación'],
['Enlace con otros numerales','8.1 amenazas; 8.2 exposición y sensibilidad; 8.3 capacidad adaptativa; 8.4 grupos y territorios prioritarios; 8.5 tendencias y pérdidas. Verificar la referencia preliminar a comunas 1, 3 y 8.','Solicitud inicial de la conversación'],
['Ampliación de hemeroteca','Búsqueda de noticias periodísticas y publicaciones institucionales 2015–2026, con corte al 04/09/2026. Prioridad a vacíos temáticos y evidencia territorial. Incluye eventos, balances y avisos de gestión.','H15–H34'],
['Unidad de conteo','Una fila cuenta un documento o registro. Varias noticias pueden describir un mismo evento. Los tres cruces H12–H14 se descuentan solo en el total de fuentes distintas entre repositorios.','Resumen; Recuperación'],
['Balances de afectación','Registrar periodo y fecha del balance. Evitar sumar acumulados parciales con anuales, balances de distinta fecha o víctimas compartidas entre municipios.','H15–H16; H23–H24; H13–H30–H31'],
['Alcance territorial de noticias','Medellín es el ámbito principal. Otros municipios del Valle de Aburrá aportan contexto metropolitano; San Luis documenta conectividad externa. No trasladar sus pérdidas al municipio de Medellín.','H21–H24; H33–H34'],
['Atribución y tendencias','Ocurrencia de una emergencia no demuestra causalidad del cambio climático. Contrastar meteorología, exposición y condicionantes con series oficiales y estudios. Calor observado no equivale automáticamente a isla de calor.','H15–H34']
];sheet('Criterios y método',['Tema','Contenido recuperado','Referencia'],criteria,[34,132,50],'Criterios');
console.log(JSON.stringify({universo:universe.length,recuperacion:audit.length,criterios:criteria.length}));
}
