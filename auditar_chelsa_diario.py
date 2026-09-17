"""Inventario de extensión diaria, sin descargar ni mezclar productos."""
import csv, calendar, sys
from pathlib import Path
from urllib.request import urlopen
import xml.etree.ElementTree as ET
root = Path(sys.argv[1]); root.mkdir(parents=True, exist_ok=True)
rows = []
for variable in ('pr', 'prec', 'tas'):
    for year in range(2022, 2026):
        url = f'https://os.unil.cloud.switch.ch/chelsa02/?prefix=chelsa/global/daily/{variable}/{year}/&max-keys=1000'
        with urlopen(url, timeout=90) as response:
            xml = ET.fromstring(response.read())
        keys = [x.text for x in xml.findall('{*}Contents/{*}Key') if x.text.endswith('.tif')]
        if xml.findtext('{*}IsTruncated') == 'true':
            raise RuntimeError('Listado truncado: revisar paginacion')
        for month in range(1, 13):
            count = sum(f'_{month:02d}_{year}_' in key for key in keys)
            rows.append(dict(variable=variable, year=year, month=month, dias_publicados=count, dias_esperados=calendar.monthrange(year,month)[1], consulta=url))
        print(variable, year, len(keys), flush=True)
with (root/'auditoria_diaria_2022_2025.csv').open('w', newline='', encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
