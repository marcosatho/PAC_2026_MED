import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
import {addContext} from './context-sheets.mjs';
const out='outputs/01a06cd6-b42f-7601-aa38-ef9732b841bf';
await fs.mkdir(out,{recursive:true});
const source=JSON.parse(await fs.readFile('source-data.json','utf8'));
const rows=[...source['Bibliografía 8.1'].slice(1),...JSON.parse(await fs.readFile('data.json','utf8'))].sort((a,b)=>a[0].localeCompare(b[0]));
const expected=[...Array.from({length:42},(_,i)=>`F${String(i+1).padStart(2,'0')}`),...Array.from({length:11},(_,i)=>`H${String(i+1).padStart(2,'0')}`)];
if(rows.length!==53||new Set(rows.map(r=>r[0])).size!==53||expected.some(id=>!rows.some(r=>r[0]===id)))throw new Error('Identificadores incompletos o duplicados');
for(const r of rows){r[11]=r[0]==='F17'?'Pendiente: sin fecha; vigencia declarada en conversación':r[0]==='F40'?'Incluida parcialmente: utilizar datos 2015–2026':'Incluida: 2015–2026';if(/^\d{4}$/.test(r[1]))r[1]=Number(r[1]);else if(/^\d{2}\/\d{2}\/\d{4}$/.test(r[1])){const [d,m,y]=r[1].split('/');r[1]=new Date(`${y}-${m}-${d}T00:00:00Z`);}}
rows.push(...JSON.parse(await fs.readFile('additions.json','utf8')));
const get=id=>rows.find(r=>r[0]===id);
get('F21')[1]=new Date('2024-02-28T00:00:00Z');get('F21')[2]='Noticia institucional';
get('F21')[4]='Dagrd entrega recomendaciones por aumento de temperatura y de incendios forestales';
get('F21')[8]='Reporta 186 incendios atendidos y 146 hectáreas afectadas en los dos primeros meses de 2024. Misma fuente que H13; no contar dos documentos independientes.';
get('F25')[1]=new Date('2023-08-28T00:00:00Z');get('F25')[2]='Noticia institucional';get('F25')[4]='Conozca qué se hace en Medellín para prevenir el dengue';
get('F25')[8]='Describe vigilancia y prevención de vectores en Medellín. La página citada es una noticia de 2023, no una serie 2023–2026. Misma fuente que H14. No documenta por sí sola un brote o una emergencia.';
get('F18')[8]+=' Portal operativo verificado: interrupciones desde el 31/08/2026. Misma fuente que H12.';
for(const [h,f] of [['H12','F18'],['H13','F21'],['H14','F25']]){const r=[...get(f)];r[0]=h;r[2]=f==='F18'?'Registro institucional / aviso operativo':'Noticia institucional';if(f==='F18'){r[1]=new Date('2026-08-31T00:00:00Z');r[11]='Incluida: 2015–2026; fecha de inicio del evento, no de publicación';}r[8]=`Misma fuente que ${f}. `+r[8];rows.push(r);}
rows.sort((a,b)=>a[0].localeCompare(b[0]));
if(rows.length!==70||new Set(rows.map(r=>r[0])).size!==70)throw new Error('Conteos o identificadores incorrectos');
const extension=JSON.parse(await fs.readFile('hemeroteca-extension.json','utf8'));
for(const r of extension){r[1]=new Date(`${r[1]}T00:00:00Z`);if(r.length!==12||r[1]<new Date('2015-01-01')||r[1]>new Date('2026-09-04'))throw Error('Fecha o columnas inválidas');}
rows.push(...extension);rows.sort((a,b)=>a[0].localeCompare(b[0]));
if(rows.length!==90||new Set(rows.map(r=>r[0])).size!==90)throw Error('Conteo de ampliación incorrecto');
if(new Set(rows.filter(r=>r[0][0]==='H').map(r=>r[10])).size!==34)throw Error('URL repetida en hemeroteca');
const wb=Workbook.create();
const headers=['ID','Año / fecha','Tipo de fuente','Autores / institución o medio','Título','Factor climático','Factores secundarios','Ámbito territorial','Aporte para numeral 8.1','DOI','URL','Criterio temporal'];
const acad=rows.filter(r=>r[0][0]==='F');const news=rows.filter(r=>r[0][0]==='H');
const exceptional=[['EX01',2014,'Artículo científico','Muñoz et al.','Quantification of the effect of precipitation as a triggering factor for landslides on the surroundings of Medellín – Colombia','Deslizamientos','Precipitación; taludes intervenidos','Medellín y alrededores','Relaciona precipitación y movimientos en masa. Antecedente histórico identificado en la conversación.','10.15446/dyna.v81n187.40640','https://doi.org/10.15446/dyna.v81n187.40640','Fuera de criterio: 2014. Conservada como antecedente excepcional.']];
exceptional[0][3]=source['Fuera de criterio'][1][1];exceptional[0][10]=source['Fuera de criterio'][1][5];
const sheets=[['Bibliografía',acad],['Hemeroteca',news],['Fuera de criterio',exceptional]];
for(const [name,data] of sheets){const sh=wb.worksheets.add(name);sh.showGridLines=false;sh.getRange(`A1:L${data.length+1}`).values=[headers,...data];sh.tables.add(`A1:L${data.length+1}`,true,name==='Bibliografía'?'Bibliografia':name==='Hemeroteca'?'Hemeroteca':'Excepciones');sh.getRange(`A1:L${data.length+1}`).format.font={name:'Arial',size:11};sh.getRange(`A1:L${data.length+1}`).format.wrapText=true;sh.getRange(`A1:L${data.length+1}`).format.verticalAlignment='top';const widths=[9,19,30,44,66,30,42,28,80,38, seventy(),48];function seventy(){return 70;}
widths.forEach((w,j)=>sh.getRangeByIndexes(0,j,data.length+1,1).format.columnWidth=w);sh.getRange('A1:L1').format={fill:'#243E54',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:44};sh.getRange(`A2:L${data.length+1}`).format.rowHeight=125;sh.freezePanes.freezeRows(1);sh.freezePanes.freezeColumns(1);data.forEach((r,i)=>{if(r[1] instanceof Date)sh.getCell(i+1,1).setNumberFormat('dd/mm/yyyy');});sh.getRange(`K2:K${data.length+1}`).format.font.color='#245A81';}
const s=wb.worksheets.add('Resumen');s.showGridLines=false;s.getRange('A1').values=[['PAC 2026 · Hemeroteca ampliada']];s.getRange('A1').format.font={name:'Arial',size:16,bold:true};
const notes=[['56 referencias académicas/técnicas y 34 registros de hemeroteca, incluidos 3 cruces entre repositorios.'],['87 fuentes distintas en las hojas principales; 88 incluyendo la excepción de 2014.'],['Criterio 2015–2026. Consulta de ampliación: 04/09/2026. F17 y F46 pendientes de validación temporal.'],['H15–H34: 20 fuentes nuevas sobre emergencias, episodios y gestión. La cobertura no es exhaustiva.'],['Conteos por factor principal, incluidos cruces y pendientes. Una fuente no equivale a un evento.'],['Ver Recuperación y Criterios y método: balances parciales, solapamientos, alcance territorial y vacíos.']];
notes.forEach((r,i)=>{s.getRange(`A${i+3}:D${i+3}`).merge();s.getCell(i+2,0).values=[r];});
s.getRange('A10:D10').values=[['Tipo de repositorio','Registros','Cruces repetidos','Fuentes distintas']];s.getRange('A11:A14').values=[['Bibliografía académica/técnica'],['Hemeroteca'],['Total principal'],['Excepciones históricas']];
await addContext(wb,rows);
s.getRange('B11:D14').formulas=[[`=COUNTA('Bibliografía'!A2:A${acad.length+1})`,'=0','=B11-C11'],[`=COUNTA('Hemeroteca'!A2:A${news.length+1})`,"=COUNTA('Recuperación'!A2:A4)",'=B12-C12'],['=SUM(B11:B12)','=SUM(C11:C12)','=SUM(D11:D12)'],["=COUNTA('Fuera de criterio'!A2:A2)",'=0','=B14-C14']];
s.getRange('A16:D16').values=[['Factor climático','Bibliografía','Hemeroteca','Total recuperado']];
const factors=[...new Set(rows.map(r=>r[5]))].sort();factors.forEach((f,i)=>{const n=17+i;s.getCell(n-1,0).values=[[f]];s.getRange(`B${n}:D${n}`).formulas=[[`=COUNTIF('Bibliografía'!$F$2:$F$${acad.length+1},A${n})`,`=COUNTIF('Hemeroteca'!$F$2:$F$${news.length+1},A${n})`,`=SUM(B${n}:C${n})`]];});
const n=17+factors.length;s.getCell(n-1,0).values=[['Total']];s.getRange(`B${n}:D${n}`).formulas=[[`=SUM(B17:B${n-1})`,`=SUM(C17:C${n-1})`,`=SUM(D17:D${n-1})`]];
s.getRange(`A1:D${n}`).format.font.name='Arial';s.getRange(`A2:D${n}`).format.font.size=11;s.getRange(`A1:D${n}`).format.wrapText=true;s.getRange('A:A').format.columnWidth=48;s.getRange('B:D').format.columnWidth=21;s.getRange('A3:D8').format.rowHeight=34;s.getRange('A3:D4').format.fill='#FFF1CC';
for(const r of [10,16])s.getRange(`A${r}:D${r}`).format={fill:'#243E54',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:34,wrapText:true};s.getRange(`A17:D${n}`).format.rowHeight=34;
console.log((await wb.inspect({kind:'table',range:`Resumen!A10:D${n}`,include:'values,formulas',tableMaxRows:20,tableMaxCols:4,maxChars:5000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30}})).ndjson);
if(s.getRange('D13').values[0][0]!==87||s.getRange(`C${n}`).values[0][0]!==34)throw new Error('Conteo incorrecto');
for(const [name,range] of [['Hemeroteca','A16:F19'],['Hemeroteca','G30:L35'],['Resumen',`A1:D${n}`],['Recuperación','A21:C25'],['Criterios y método','A21:C25']]){const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(`${out}/${name}-${range.replace(':','-')}.png`,new Uint8Array(await blob.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(wb)).save(`${out}/PAC_2026_hemeroteca_extendida.xlsx`);
console.log(JSON.stringify({academica:acad.length,hemeroteca:news.length,nuevas:extension.length,fuentesDistintas:s.getRange('D13').values[0][0]}));
