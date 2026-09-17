import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const sourcePath = 'C:/Users/marco/AppData/Local/Temp/codex-file-preview-ML0Zfe/Plan de ataque.xlsx';
const outputDir = 'outputs/01a089a5-63bb-7163-bf32-9b8c2e1100a4';
await fs.mkdir(outputDir, { recursive: true });

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const summary = await workbook.inspect({
  kind: 'workbook,sheet,table',
  include: 'id,name,values,formulas',
  tableMaxRows: 50,
  tableMaxCols: 30,
  maxChars: 30000,
});
console.log(summary.ndjson);

for (const sheet of workbook.worksheets.items) {
  const preview = await workbook.render({
    sheetName: sheet.name,
    autoCrop: 'all',
    scale: 1.5,
    format: 'png',
  });
  const safeName = sheet.name.replace(/[\\/:*?"<>|]/g, '_');
  await fs.writeFile(`${outputDir}/source-${safeName}.png`, new Uint8Array(await preview.arrayBuffer()));
}
