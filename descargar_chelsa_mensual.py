"""Descarga reanudable de ventanas CHELSA; inventario real 1981-2025."""
import os, sys, json, csv, re, argparse
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

LOCAL = Path(__file__).resolve().parent
if (LOCAL / '.mapdeps').exists():
    sys.path.insert(0, str(LOCAL / '.mapdeps'))
import rasterio
from rasterio.windows import from_bounds, Window

BASE = 'https://os.unil.cloud.switch.ch/chelsa02/'
NS = {'s': 'http://s3.amazonaws.com/doc/2006-03-01/'}

def inventory(variable):
    result = {}
    marker = ''
    while True:
        query = {'prefix': f'chelsa/global/monthly/{variable}/', 'max-keys': 1000}
        if marker:
            query['marker'] = marker
        with urlopen(BASE + '?' + urlencode(query), timeout=90) as response:
            root = ET.fromstring(response.read())
        keys = [x.text for x in root.findall('s:Contents/s:Key', NS)]
        for key in keys:
            match = re.search(r'CHELSA_' + variable + r'_(\d{2})_(\d{4})_V\.2\.1\.tif$', key)
            if match:
                month, year = map(int, match.groups())
                result[(year, month)] = BASE + key
        if root.findtext('s:IsTruncated', namespaces=NS) != 'true':
            return result
        marker = root.findtext('s:NextMarker', namespaces=NS) or keys[-1]

def download(row, destination, bounds):
    if not row['url']:
        return row
    target = destination / row['variable'] / (row['url'].split('/')[-1].replace('.tif', '_Medellin_buffer.tif'))
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        if target.exists():
            with rasterio.open(target) as src:
                src.read(1)
            row.update(status='descargado', archivo=str(target))
            return row
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif', GDAL_HTTP_TIMEOUT='90', GDAL_HTTP_MAX_RETRY='3'):
            with rasterio.open('/vsicurl/' + row['url']) as src:
                if src.crs.to_epsg() != 4326:
                    raise ValueError('CRS inesperado: ' + str(src.crs))
                import math
                w = from_bounds(*bounds, transform=src.transform)
                window = Window(math.floor(w.col_off), math.floor(w.row_off), math.ceil(w.col_off+w.width)-math.floor(w.col_off), math.ceil(w.row_off+w.height)-math.floor(w.row_off))
                data = src.read(window=window)
                profile = src.profile.copy()
                profile.update(width=data.shape[2], height=data.shape[1], transform=src.window_transform(window), compress='deflate')
                temp = target.with_suffix('.partial.tif')
                with rasterio.open(temp, 'w', **profile) as dst:
                    dst.write(data)
                    dst.scales = src.scales
                    dst.offsets = src.offsets
                    dst.update_tags(**src.tags(), source_url=row['url'])
                    for band in range(1, src.count+1):
                        dst.update_tags(band, **src.tags(band))
                os.replace(temp, target)
        row.update(status='descargado', archivo=str(target))
    except Exception as exc:
        row.update(status='error', detalle=str(exc))
    return row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    destination = Path(args.out)
    destination.mkdir(parents=True, exist_ok=True)
    # Ventana regional que cubre Medellín y margen exterior; se conserva cuadrícula nativa.
    bounds = [-75.95, 5.85, -75.20, 6.60]
    rows = []
    for variable in ('pr', 'tas'):
        available = inventory(variable)
        print(variable, 'archivos publicados', len(available), 'ultimo', max(available), flush=True)
        for year in range(1981, 2026):
            for month in range(1, 13):
                url = available.get((year, month), '')
                rows.append(dict(variable=variable, year=year, month=month, url=url, status='pendiente' if url else 'no_publicado', archivo='', detalle=''))
    def save():
        with (destination/'inventario_1981_2025.csv').open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    save()
    selected = [r for r in rows if r['url']]
    if args.limit:
        selected = selected[:args.limit]
    with ThreadPoolExecutor(max_workers=4) as executor:
        jobs = [executor.submit(download, r, destination, bounds) for r in selected]
        for n, job in enumerate(as_completed(jobs), 1):
            job.result()
            if n % 20 == 0 or n == len(jobs):
                save()
                print('procesados', n, '/', len(jobs), flush=True)
    save()
    summary = {s: sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}
    (destination/'resumen.json').write_text(json.dumps(dict(periodo_solicitado='1981-2025', bounds_4326=bounds, estados=summary, nota='Valores originales sin conversion. Verificar escalas y unidades antes del analisis. No se rellenan meses ausentes.'), indent=2), encoding='utf-8')
    print(summary, flush=True)

if __name__ == '__main__':
    main()
