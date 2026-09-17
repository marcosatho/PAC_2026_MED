import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
import { levels, families, processes } from './classification-data.mjs';

const outputDir = 'outputs/01a06cd6-b42f-7601-aa38-ef9732b841bf';
const outputPath = `${outputDir}/PAC_2026_clasificacion_amenazas.xlsx`;
await fs.mkdir(outputDir, { recursive: true });

const wb = Workbook.create();
const navy = '#243E54', blue = '#3E647A', pale = '#EAF2F6', gold = '#F4C95D';

function setFont(range, size=11, bold=false, color='#17252E') {
  range.format.font = { name:'Arial', size, bold, color };
}

function dataSheet(name, title, subtitle, headers, data, widths, tableName) {
  const sh = wb.worksheets.add(name);
  sh.showGridLines = false;
  const end = String.fromCharCode(64 + headers.length);
  const tableStart = 4, tableEnd = tableStart + data.length;
  sh.getRange(`A1:${end}1`).merge();
  sh.getRange('A1').values = [[title]];
  sh.getRange(`A2:${end}2`).merge();
  sh.getRange('A2').values = [[subtitle]];
  sh.getRange(`A${tableStart}:${end}${tableEnd}`).values = [headers, ...data];
  sh.tables.add(`A${tableStart}:${end}${tableEnd}`, true, tableName);
  sh.getRange(`A1:${end}${tableEnd}`).format.wrapText = true;
  sh.getRange(`A1:${end}${tableEnd}`).format.verticalAlignment = 'top';
  setFont(sh.getRange(`A1:${end}${tableEnd}`));
  sh.getRange(`A1:${end}1`).format = { fill:navy, font:{name:'Arial',size:16,bold:true,color:'#FFFFFF'}, rowHeight:34 };
  sh.getRange(`A2:${end}2`).format = { fill:pale, font:{name:'Arial',size:10,color:blue}, rowHeight:36, wrapText:true };
  sh.getRange(`A${tableStart}:${end}${tableStart}`).format = { fill:blue, font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'}, rowHeight:38, wrapText:true };
  sh.getRange(`A${tableStart+1}:${end}${tableEnd}`).format.rowHeight = name==='Matriz operativa' ? 62 : 82;
  widths.forEach((w,i)=>sh.getRangeByIndexes(0,i,tableEnd,1).format.columnWidth=w);
  sh.freezePanes.freezeRows(tableStart);
  sh.freezePanes.freezeColumns(1);
  return sh;
}

const guide = wb.worksheets.add('Guía');
guide.showGridLines = false;
guide.getRange('A1:D1').merge();
guide.getRange('A1').values = [['PAC 2026 · Guía de clasificación de amenazas y riesgos climáticos']];
guide.getRange('A3:D3').values = [['Componente','Función','Contenido','Registros']];
guide.getRange('A4:D7').values = [
  ['Niveles conceptuales','Ordenan la cadena causal','Desde condicionantes climáticos hasta impactos territoriales y consecuencias en cascada',levels.length],
  ['Familias de riesgo','Organizan la investigación','Agrupan temas, subgrupos y elementos que deben buscarse en fuentes e indicadores',families.length],
  ['Matriz operativa','Define las unidades de análisis','Asigna familia principal, temporalidad e interacciones a cada amenaza, proceso o efecto',processes.length],
  ['Carpeta de destino indicada','Referencia para copiar el archivo en Google Drive','/content/drive/MyDrive/2.Consultoria/01_PAC_MEDELLIN_2026/2.Ejecución/C1/P1','—']
];
guide.getRange('A9:D9').values = [['Clasificación','Definición','Uso en el análisis','Ejemplo']];
guide.getRange('A10:D14').values = [
  ['Súbita o aguda','Se manifiesta en minutos, horas o días.','Registrar fecha, duración, magnitud, localización y afectaciones.','Inundación o vendaval'],
  ['Lenta o crónica','Se acumula o evoluciona durante meses o años.','Analizar tendencias, persistencia, estacionalidad y extensión territorial.','Sequía o aumento de temperatura'],
  ['Mixta','Combina preparación progresiva con manifestación aguda.','Examinar condiciones antecedentes y el desencadenante inmediato.','Deslizamiento por saturación'],
  ['Evento compuesto','Dos o más amenazas coinciden o se suceden.','Evitar analizar cada amenaza como si actuara aisladamente.','Lluvia, viento y deslizamientos'],
  ['Impacto en cascada','La afectación inicial se transmite a otros sistemas.','Seguir la secuencia entre servicios, movilidad, economía, alimentos y población.','Deslizamiento → cierre vial → desabastecimiento']
];
guide.getRange('A16:D16').merge();
guide.getRange('A16').values = [['Nota de uso']];
guide.getRange('A17:D18').merge();
guide.getRange('A17').values = [['Las familias no son excluyentes. Cada proceso se ubica en una familia principal para ordenar el análisis, pero puede relacionarse con otras mediante la columna Interacciones principales. La ocurrencia de un evento no demuestra por sí sola atribución al cambio climático; la clasificación debe contrastarse con evidencia local, series oficiales y estudios técnicos.']];
guide.getRange('A1:D18').format.wrapText = true;
guide.getRange('A1:D18').format.verticalAlignment = 'top';
setFont(guide.getRange('A1:D18'));
guide.getRange('A1:D1').format = { fill:navy, font:{name:'Arial',size:16,bold:true,color:'#FFFFFF'}, rowHeight:38 };
for (const r of [3,9,16]) guide.getRange(`A${r}:D${r}`).format = { fill:blue, font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'}, rowHeight:34, wrapText:true };
guide.getRange('A4:D7').format.rowHeight = 65;
guide.getRange('A10:D14').format.rowHeight = 65;
guide.getRange('A17:D18').format = { fill:'#FFF4D6', font:{name:'Arial',size:11,color:'#17252E'}, rowHeight:54, wrapText:true };
[30,48,82,18].forEach((w,i)=>guide.getRangeByIndexes(0,i,18,1).format.columnWidth=w);
guide.freezePanes.freezeRows(3);

dataSheet('Niveles conceptuales','Niveles conceptuales','Cadena analítica desde las condiciones físicas del clima hasta los impactos urbanos y sistémicos.',['Nivel','Definición','Aplicación para Medellín'],levels,[48,72,92],'Niveles');
dataSheet('Familias de riesgo','Familias de riesgo','Agrupación temática para orientar la búsqueda de evidencia, indicadores, eventos y fuentes.',['Familia de riesgo','Subgrupo','Elementos para investigar'],families,[51,43,105],'Familias');
dataSheet('Matriz operativa','Matriz operativa de amenazas y procesos','Clasificación principal, temporalidad e interacciones. Una misma fila puede conectarse con varias familias.',['Amenaza o proceso','Familia principal','Temporalidad','Interacciones principales'],processes,[53,38,40,93],'Matriz');

const guideCheck = await wb.inspect({kind:'table',range:'Guía!A1:D18',include:'values,formulas',tableMaxRows:20,tableMaxCols:4,maxChars:7000});
console.log(guideCheck.ndjson);
const matrixCheck = await wb.inspect({kind:'table',range:'Matriz operativa!A4:D48',include:'values,formulas',tableMaxRows:8,tableMaxCols:4,maxChars:4000});
console.log(matrixCheck.ndjson);
const errors = await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'final formula error scan'});
console.log(errors.ndjson);

for (const [sheetName,range,fileName] of [
  ['Guía','A1:D18','classification-guide.png'],
  ['Niveles conceptuales','A1:C8','classification-levels.png'],
  ['Familias de riesgo','A1:C22','classification-families.png'],
  ['Matriz operativa','A1:D48','classification-matrix.png']
]) {
  const blob = await wb.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(`${outputDir}/${fileName}`,new Uint8Array(await blob.arrayBuffer()));
}

await (await SpreadsheetFile.exportXlsx(wb)).save(outputPath);
console.log(JSON.stringify({outputPath,levels:levels.length,families:families.length,processes:processes.length}));
