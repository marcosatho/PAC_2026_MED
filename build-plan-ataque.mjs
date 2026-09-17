import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const sourcePath = 'C:/Users/marco/AppData/Local/Temp/codex-file-preview-ML0Zfe/Plan de ataque.xlsx';
const outputDir = 'outputs/01a089a5-63bb-7163-bf32-9b8c2e1100a4';
const outputPath = `${outputDir}/Plan_de_ataque_ajustado.xlsx`;
await fs.mkdir(outputDir, { recursive: true });

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const sheet = workbook.worksheets.add('Plan bibliográfico');
sheet.showGridLines = false;
sheet.tabColor = '#1F4E78';

const headers = [
  'ID', 'Frente', 'Numeral PAC', 'Bloque / subtema', 'Pregunta guía',
  'Evidencia buscada', 'Fuentes prioritarias', 'Escala / cobertura', 'Periodo',
  'Criterio de calidad', 'Producto esperado', 'Prioridad', 'Estado', 'Avance',
  'Próximo paso', 'Ruta / DOI', 'Hallazgo / nota', 'Sección MD'
];

const rows = [
  ['C01','Clima','7.1','Contexto climático general','¿Cuáles son las condiciones climáticas de base de Medellín y del Valle de Aburrá?','Tipo de clima; precipitación; temperatura; humedad; radiación; viento','IDEAM; SIATA/AMVA; literatura hidroclimática reciente','Medellín + Valle de Aburrá','1991–2020 y actualización reciente','Fuente oficial o publicación arbitrada; método y periodo explícitos','Síntesis de línea base + tabla climática','Alta','Exploración inicial',0.2,'Extraer variables, periodos y cifras comparables de las fuentes núcleo','','Separar clima observado de escenarios futuros','6.1 Contexto climático'],
  ['C02','Clima','7.1','Variabilidad espacial','¿Cómo varía el clima entre fondo de valle, laderas, comunas y corregimientos?','Gradientes altitudinales; contraste urbano-rural; circulación valle-ladera','SIATA; Ramírez-Cardona y Jiménez; DEM POT/LiDAR','Valle–ladera–corregimientos','Últimos 5 años de literatura; series según fuente','Resolución compatible con la escala de interpretación','Mapa conceptual de gradientes + texto explicativo','Alta','Exploración inicial',0.2,'Definir unidades territoriales y variables comparables','','No tratar Medellín como una superficie climática homogénea','6.2 Variabilidad espacial'],
  ['C03','Clima','7.1','Precipitación media y estacional','¿Cuál es el patrón espacial y el régimen anual de precipitación?','Media anual; ciclo mensual; temporadas húmedas/secas; variabilidad interanual','CHIRPS v3; SIATA/IDEAM; Aristizábal et al.','Regional + validación local','1991–2020; actualización disponible','Satélite validado con estaciones; declarar resolución y sesgos','Mapa de precipitación + ciclo anual','Alta','En curso',0.4,'Comparar CHIRPS con estaciones y documentar límites de uso diario','','CHIRPS sirve para climatología regional, no para detalle barrial','6.3 Precipitación'],
  ['C04','Clima','7.1','Temperatura y exposición térmica','¿Qué patrones térmicos se observan y cómo se relacionan con el diseño urbano y la altitud?','Temperatura del aire; LST; máximos; gradiente altitudinal; UHI','SIATA; Landsat 8/9; estudio de diseño urbano y meteorología','Distrito; comuna/corregimiento cuando sea válido','2013–2025 para Landsat; series de estación disponibles','Distinguir LST de temperatura del aire; control de nubosidad','Mapa térmico + gráfico temporal','Alta','Exploración inicial',0.2,'Localizar datos y revisar método replicable del estudio urbano','','La nubosidad limita la representatividad de Landsat','6.4 Temperatura'],
  ['C05','Clima','7.1','Relieve como condicionante','¿Cómo condicionan el relieve y la orientación de laderas la lluvia, la temperatura y la circulación?','Elevación; pendiente; orientación; encajonamiento; divisorias','DEM POT 2026/LiDAR; Copernicus DEM; literatura de capa límite','Distrito + Valle de Aburrá','Estático; literatura reciente','Preferir DTM local; declarar limitaciones de DSM','Mapas de relieve y pendiente + mecanismo explicativo','Alta','Exploración inicial',0.2,'Confirmar acceso a DEM oficial y derivar productos básicos','','Copernicus es alternativa regional, no sustituto del detalle local','6.5 Relieve y clima'],
  ['C06','Clima','7.1','Clima–hidrología y cobertura','¿Cómo conectan precipitación, relieve, drenaje y cobertura con la respuesta hidrológica?','Drenaje; cuencas; escorrentía; cobertura vegetal; NDVI','POMCA; red hídrica oficial; Sentinel-2; MERIT Hydro como contexto','Cuenca–microcuenca–distrito','2017–2025 para coberturas','Red oficial para quebradas urbanas; composiciones multitemporales','Mapa integrado relieve–agua–cobertura','Media','Exploración inicial',0.2,'Inventariar cartografía local y definir jerarquía de fuentes','','MERIT Hydro es demasiado grueso para muchas quebradas urbanas','6.6 Relación clima–hidrología'],
  ['C07','Clima','7.1','Tendencias y escenarios','¿Qué cambios observados y proyectados son relevantes para el PAC 2026?','Tendencias de temperatura/precipitación; extremos; escenarios','IDEAM Cuarta Comunicación; series SIATA/IDEAM; estudios recientes','Medellín–Antioquia–Colombia según dato','Observado + horizontes futuros oficiales','No confundir variabilidad con tendencia; declarar escenario y horizonte','Tabla de cambios + implicaciones territoriales','Alta','Exploración inicial',0.2,'Extraer escenarios, horizontes y rangos con trazabilidad','','Mantener escenarios como contexto prospectivo, no como clima observado','6.7 Tendencias y escenarios'],
  ['D01','Desastres','8.1','Taxonomía y fuente oficial','¿Qué taxonomía y qué fuente territorial principal adoptará el diagnóstico?','Definiciones; cadena amenaza–exposición–vulnerabilidad–riesgo; zonificación','POT 2026; UNDRR/Sendai; AECOM/C40; fuentes distritales','Distrito','Vigente al PAC 2026','Autoridad institucional; consistencia conceptual y territorial','Nota metodológica + taxonomía validada','Alta','En curso',0.4,'Comparar categorías y justificar adopción de fuente base','','Hay desarrollo previo, falta validación y decisión de adopción','7.1 Marco de amenazas'],
  ['D02','Desastres','8.1 / 8.5','Movimientos en masa','¿Dónde y cuándo ocurren y qué relación tienen con lluvia, relieve y ENSO?','Inventario; fecha; localización; tipo; lluvia antecedente; daños','Geohazards; Aristizábal et al.; SIATA/IDEAM','Evento/punto + unidad político-administrativa','Serie histórica disponible','Inventario con método, cobertura y duplicados documentados','Mapa + línea temporal + ficha de relación climática','Alta','En curso',0.4,'Revisar repositorio del paper y diccionario de Geohazards','','Fuente directa prometedora; requiere revisión de datos y licencia','7.2 Movimientos en masa'],
  ['D03','Desastres','8.1 / 8.5','Precipitaciones extremas','¿Qué umbrales, máximos y patrones espacio-temporales caracterizan la lluvia extrema?','Máximos horarios/diarios; intensidad; duración; estaciones; radar','SIATA radar/estaciones; IDEAM; paper de lluvia extrema; satélite para contraste','Estación/radar + Valle de Aburrá','Últimos 10 años o serie disponible','Priorizar observación local; satélite no sustituye extremos diarios','Serie de extremos + mapa de eventos','Alta','Exploración inicial',0.2,'Localizar datos de radar/estaciones y definir métricas de extremo','','Validar máximos satelitales contra observación en tierra','7.3 Precipitación extrema'],
  ['D04','Desastres','8.1 / 8.5','Inundaciones','¿Qué eventos, zonas y factores recurrentes se identifican?','Fecha; lugar; profundidad/afectación; lluvia; drenaje; pérdidas','DAGRD; SIATA; bomberos; POT; hemeroteca como complemento','Evento + barrio/comuna/cuenca','Serie disponible; énfasis 2022–2026 en literatura','Fuente oficial primero; prensa solo para completar y triangular','Inventario + línea temporal + mapa','Alta','Por iniciar',0,'Solicitar/inventariar bases oficiales antes de ampliar hemeroteca','','Evitar que prensa sea la única fuente de ocurrencia','7.4 Inundaciones'],
  ['D05','Desastres','8.1 / 8.5','Avenidas torrenciales','¿Qué eventos están documentados y cómo se distinguen de inundaciones y movimientos en masa?','Fecha; cuenca; tipo de flujo; detonante; daños','DAGRD; POMCA; POT; Geohazards; literatura especializada','Evento + cuenca','Serie disponible','Definición explícita y clasificación consistente','Inventario depurado + mapa por cuenca','Media','Por iniciar',0,'Verificar cobertura de Geohazards y catálogos distritales','','Definir equivalencias antes de usar debris flow','7.5 Avenidas torrenciales'],
  ['D06','Desastres','8.1 / 8.5','Incendios de cobertura vegetal','¿Dónde, cuándo y bajo qué condiciones climáticas se concentran los incendios?','Fecha; área; cobertura; sequedad; temperatura; precipitación previa','Bomberos/DAGRD; IDEAM; MODIS/VIIRS como contraste','Evento + área quemada','Serie disponible','Separar detección satelital de reporte confirmado','Mapa + estacionalidad + ficha de condiciones','Media','Por iniciar',0,'Identificar base oficial y variables mínimas del inventario','','Frente sin desarrollo en la tabla original','7.6 Incendios'],
  ['D07','Desastres','8.1 / 8.5','Calor extremo','¿Qué episodios de calor y territorios de mayor exposición pueden documentarse?','Máximas; duración; anomalías; LST; población expuesta','SIATA/IDEAM; Landsat; salud pública si está disponible','Estación + comuna/corregimiento','Serie disponible; literatura 2022–2026','Umbral justificable; distinguir calor meteorológico de LST','Serie de episodios + mapa de exposición','Alta','Exploración inicial',0.2,'Definir umbral y revisar continuidad de series','','Conectar después con vulnerabilidad, sin duplicar el análisis social','7.7 Calor extremo'],
  ['D08','Desastres','7.4 / 8.5','Episodios de calidad del aire','¿Qué episodios críticos se relacionan con condiciones meteorológicas y territoriales?','PM2.5/PM10; estabilidad; viento; capa límite; alertas','SIATA/AMVA; informe anual de calidad del aire; estudio de capa límite','Estación + Valle de Aburrá','Serie disponible; foco reciente','Datos oficiales; método de agregación y umbral explícitos','Línea temporal + explicación meteorológica','Media','Exploración inicial',0.2,'Definir episodios, contaminantes y vínculo con meteorología','','No convertir 7.1 en análisis detallado de calidad del aire','7.8 Calidad del aire'],
  ['D09','Desastres','8.5','Cuantificación integrada de eventos','¿Cómo consolidar eventos, magnitud y pérdidas sin duplicados?','ID; fecha; tipo; coordenadas; fuente; magnitud; víctimas; pérdidas; confianza','DAGRD; SIATA; bomberos; salud; Geohazards; hemeroteca','Evento + unidad territorial','Serie histórica disponible','Proveniencia por registro; reglas de deduplicación; campos faltantes explícitos','Base maestra de eventos + diccionario de datos','Alta','Por iniciar',0,'Diseñar esquema mínimo y protocolo de deduplicación','','Es el principal vacío operativo identificado','7.9 Cuantificación de eventos'],
  ['X01','Transversal','7.1 / 8','Síntesis territorial','¿Qué hallazgos climáticos y de desastres deben alimentar riesgo, adaptación y priorización?','Hallazgos robustos; vacíos; escalas; implicaciones','Resultados de C01–C07 y D01–D09','Distrito + unidades pertinentes','PAC 2026','Cada afirmación debe remontar a evidencia y limitación','Matriz hallazgo–evidencia–implicación','Alta','Por iniciar',0,'Cerrar después de completar los bloques prioritarios','','Evitar adelantar conclusiones sin trazabilidad','8 Síntesis y brechas']
];

sheet.getRange('A2:R2').merge();
sheet.getRange('A2').values = [['Plan de exploración bibliográfica — Clima y desastres']];
sheet.getRange('A3:R3').merge();
sheet.getRange('A3').values = [['PAC 2026 | Matriz maestra para organizar búsquedas, evidencia, productos y redacción']];

sheet.getRange('A5').values = [['Registros']];
sheet.getRange('B5').formulas = [[`=COUNTA(A8:A${7 + rows.length})`]];
sheet.getRange('D5').values = [['Avance medio']];
sheet.getRange('E5').formulas = [[`=AVERAGE(N8:N${7 + rows.length})`]];
sheet.getRange('G5').values = [['Por iniciar']];
sheet.getRange('H5').formulas = [[`=COUNTIF(N8:N${7 + rows.length},0)`]];
sheet.getRange('J5').values = [['Con desarrollo']];
sheet.getRange('K5').formulas = [[`=COUNTIF(N8:N${7 + rows.length},0.4)`]];
sheet.getRange('M5').values = [['Escala de avance']];
sheet.getRange('N5:R5').merge();
sheet.getRange('N5').values = [['0% nulo | 20% incipiente | 40% desarrollo interesante']];

sheet.getRange('A7:R7').values = [headers];
sheet.getRange(`A8:R${7 + rows.length}`).values = rows;
const table = sheet.tables.add(`A7:R${7 + rows.length}`, true, 'PlanBibliografico');
table.style = 'TableStyleMedium2';
table.showBandedRows = true;
table.showFilterButton = true;

sheet.getRange(`L8:L${7 + rows.length}`).dataValidation = { rule: { type: 'list', values: ['Alta','Media','Baja'] } };
sheet.getRange(`M8:M${7 + rows.length}`).dataValidation = { rule: { type: 'list', values: ['Por iniciar','Exploración inicial','En curso','Síntesis lista','Cerrado'] } };
sheet.getRange(`N8:N${7 + rows.length}`).dataValidation = { rule: { type: 'list', values: [0,0.2,0.4] } };

sheet.getRange(`N8:N${7 + rows.length}`).conditionalFormats.add('cellIs', { operator: 'equal', formula: 0, format: { fill: '#FCE8E6', font: { color: '#B91C1C', bold: true } } });
sheet.getRange(`N8:N${7 + rows.length}`).conditionalFormats.add('cellIs', { operator: 'equal', formula: 0.2, format: { fill: '#FFF2CC', font: { color: '#8A5A00', bold: true } } });
sheet.getRange(`N8:N${7 + rows.length}`).conditionalFormats.add('cellIs', { operator: 'equal', formula: 0.4, format: { fill: '#E2F0D9', font: { color: '#2F641C', bold: true } } });

const all = sheet.getRange(`A2:R${7 + rows.length}`);
all.format.font = { name: 'Arial', size: 10, color: '#243447' };
all.format.verticalAlignment = 'center';
sheet.getRange('A2').format.font = { name: 'Arial', size: 16, bold: true, color: '#1F4E78' };
sheet.getRange('A3').format.font = { name: 'Arial', size: 10, italic: true, color: '#667085' };
sheet.getRange('A2:A3').format.rowHeight = 24;
sheet.getRange('A5:R5').format.fill = '#EAF0F6';
sheet.getRange('A5:R5').format.font = { name: 'Arial', size: 10, bold: true, color: '#1F4E78' };
sheet.getRange('B5').format.font = { name: 'Arial', size: 12, bold: true, color: '#111827' };
sheet.getRange('E5').format.font = { name: 'Arial', size: 12, bold: true, color: '#111827' };
sheet.getRange('H5').format.font = { name: 'Arial', size: 12, bold: true, color: '#111827' };
sheet.getRange('K5').format.font = { name: 'Arial', size: 12, bold: true, color: '#111827' };
sheet.getRange('E5').format.numberFormat = '0%';
sheet.getRange(`N8:N${7 + rows.length}`).format.numberFormat = '0%';
sheet.getRange(`A7:R${7 + rows.length}`).format.wrapText = true;
sheet.getRange('A7:R7').format.rowHeight = 36;
sheet.getRange(`A8:R${7 + rows.length}`).format.rowHeight = 76;
sheet.getRange(`A8:D${7 + rows.length}`).format.font = { name: 'Arial', size: 10, color: '#243447', bold: true };
sheet.getRange(`L8:N${7 + rows.length}`).format.horizontalAlignment = 'center';
sheet.getRange(`A7:R7`).format.horizontalAlignment = 'center';

const widths = [9,12,14,24,36,34,34,22,18,30,25,12,20,11,34,22,32,24];
for (let i = 0; i < widths.length; i++) sheet.getRangeByIndexes(0, i, 1, 1).format.columnWidth = widths[i];
sheet.freezePanes.freezeRows(7);
sheet.freezePanes.freezeColumns(4);

workbook.recalculate();

const preview = await workbook.render({
  sheetName: 'Plan bibliográfico',
  range: `A1:R${7 + rows.length}`,
  scale: 1.2,
  format: 'png',
});
await fs.writeFile(`${outputDir}/Plan_bibliografico.png`, new Uint8Array(await preview.arrayBuffer()));

const check = await workbook.inspect({
  kind: 'table',
  range: `Plan bibliográfico!A2:R${7 + rows.length}`,
  include: 'values,formulas',
  tableMaxRows: 30,
  tableMaxCols: 18,
  maxChars: 30000,
});
await fs.writeFile(`${outputDir}/Plan_de_ataque_ajustado.inspect.ndjson`, check.ndjson);

const errors = await workbook.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: { useRegex: true, maxResults: 300 },
  summary: 'final formula error scan',
});
console.log(errors.ndjson);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
