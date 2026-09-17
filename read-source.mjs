import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('C:/Users/marco/Downloads/PAC_2026_Bibliografia_Amenazas_8_1.xlsx'));
console.log((await w.inspect({kind:'workbook,sheet,table',maxChars:5000,tableMaxRows:2,tableMaxCols:12})).ndjson);
const data={};for(const s of w.worksheets.items){data[s.name]=s.getUsedRange().values;}
await fs.writeFile('source-data.json',JSON.stringify(data,null,2));
console.log(JSON.stringify(data));
