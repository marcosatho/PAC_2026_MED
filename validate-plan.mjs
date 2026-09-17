import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const originalPath = 'C:/Users/marco/AppData/Local/Temp/codex-file-preview-ML0Zfe/Plan de ataque.xlsx';
const outputPath = 'outputs/01a089a5-63bb-7163-bf32-9b8c2e1100a4/Plan_de_ataque_ajustado.xlsx';
const original = await SpreadsheetFile.importXlsx(await FileBlob.load(originalPath));
const output = await SpreadsheetFile.importXlsx(await FileBlob.load(outputPath));

for (const sourceSheet of original.worksheets.items) {
  const outputSheet = output.worksheets.getItem(sourceSheet.name);
  const before = JSON.stringify(sourceSheet.getUsedRange().values);
  const after = JSON.stringify(outputSheet.getUsedRange().values);
  if (before !== after) throw new Error(`Unexpected value change in ${sourceSheet.name}`);
}

const plan = await output.inspect({
  kind: 'table',
  range: 'Plan bibliográfico!A2:R24',
  include: 'values,formulas',
  tableMaxRows: 30,
  tableMaxCols: 18,
  maxChars: 30000,
});
console.log(plan.ndjson);

const errors = await output.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: { useRegex: true, maxResults: 300 },
  summary: 'saved workbook formula error scan',
});
console.log(errors.ndjson);
console.log('Original sheet values preserved. Saved workbook validation passed.');
