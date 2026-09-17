"""Composiciones CHELSA v2.1 por ONI. Ejecutar en Colab con Drive montado."""
from pathlib import Path
import io, re
from urllib.request import urlopen
import numpy as np
import pandas as pd
import rasterio
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LOCAL_ROOT = Path(__file__).resolve().parent / 'P1_07_1_CLIMA_RELIEVE' / '08_CHELSA'
DRIVE_ROOT = Path('/content/drive/MyDrive/2.Consultoria/01_PAC_MEDELLIN_2026/2.Ejecución/C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA/P1_Caracterizacion_Socioeconomica_Ambiental/02_DOCUMENTOS_EN_ELABORACION/07_1_CLIMA_RELIEVE/08_CHELSA')
ROOT = LOCAL_ROOT if LOCAL_ROOT.exists() else DRIVE_ROOT
DATA = ROOT / '02_DATOS'
OUT = ROOT / '04_PREVISUALIZACIONES'
OUT.mkdir(parents=True, exist_ok=True)

# ONI oficial CPC: estaciones móviles trimestrales.
oni_url = 'https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt'
oni_file = Path(__file__).resolve().parent / 'oni.ascii.txt'
if oni_file.exists():
    oni = pd.read_fwf(oni_file, skiprows=1, names=['season','year','total','oni'])
else:
    with urlopen(oni_url, timeout=30) as response:
        oni = pd.read_fwf(io.BytesIO(response.read()), skiprows=1, names=['season','year','total','oni'])
oni = oni[(oni.year >= 1981) & (oni.year <= 2021)].copy()
center_month = {'DJF':2,'JFM':3,'FMA':4,'MAM':5,'AMJ':6,'MJJ':7,'JJA':8,'JAS':9,'ASO':10,'SON':11,'OND':12,'NDJ':1}
oni['month'] = oni.season.map(center_month)
oni['date'] = pd.to_datetime(dict(year=oni.year, month=oni.month, day=15))
oni['raw_phase'] = np.select([oni.oni >= .5, oni.oni <= -.5], ['El Niño','La Niña'], default='Neutral')

# Confirmación operacional: conservar solo corridas de cinco o más estaciones móviles.
oni['run'] = (oni.raw_phase != oni.raw_phase.shift()).cumsum()
run_size = oni.groupby('run').size()
oni['phase'] = np.where(oni.run.map(run_size) >= 5, oni.raw_phase, 'Neutral')
phase_month = oni.set_index(oni.date.dt.to_period('M'))['phase']

def files(variable):
    rows=[]
    for f in sorted((DATA/variable).glob('*.tif')):
        m = re.search(r'_(\d{2})_(\d{4})_V', f.name)
        if m: rows.append((pd.Period(f'{m.group(2)}-{m.group(1)}', freq='M'), f))
    return dict(rows)

paths = {'pr': files('pr'), 'tas': files('tas')}
periods = sorted(set(paths['pr']) & set(paths['tas']) & set(phase_month.index))
phases = ['El Niño','Neutral','La Niña']
arrays = {v:{p:[] for p in phases} for v in ('pr','tas')}
profile = None
for period in periods:
    phase = phase_month.loc[period]
    for variable in ('pr','tas'):
        with rasterio.open(paths[variable][period]) as src:
            raw = src.read(1).astype('float32')
            if profile is None: profile = (src.transform, src.bounds)
        if variable == 'tas': raw = raw * 0.1 - 273.15
        arrays[variable][phase].append(raw)

means = {v:{p: np.nanmean(a, axis=0) for p,a in arrays[v].items()} for v in arrays}
municipality = gpd.read_file(ROOT.parent / '03_DATOS_PREPARADOS/20260910/limite_medellin_4326.geojson').to_crs(4326)
transform, bounds = profile
extent = [bounds.left,bounds.right,bounds.bottom,bounds.top]
fig, axes = plt.subplots(3,2, figsize=(13,16), constrained_layout=True)
cmaps = {'pr':'Blues','tas':'RdYlBu_r'}
labels = {'pr':'Precipitación mensual (mm/mes)','tas':'Temperatura media (°C)'}
units = {'pr':'mm/mes','tas':'°C'}
for i, phase in enumerate(phases):
    for j, variable in enumerate(('pr','tas')):
        ax=axes[i,j]; image=means[variable][phase]
        finite=image[np.isfinite(image)]; lo,hi=np.nanpercentile(finite,[2,98])
        im=ax.imshow(image, extent=extent, origin='upper', cmap=cmaps[variable], vmin=lo, vmax=hi)
        levels=np.linspace(lo,hi,7)
        ax.contour(image, levels=levels, extent=extent, colors='0.2', linewidths=.45, alpha=.7)
        municipality.boundary.plot(ax=ax, color='#b5122b', linewidth=1.5)
        ax.set_title(f'{phase} — {labels[variable]}\n{len(arrays[variable][phase])} meses')
        ax.set_xlabel('Este (°)'); ax.set_ylabel('Norte (°)')
        fig.colorbar(im, ax=ax, shrink=.78, label=units[variable])
fig.suptitle('CHELSA v2.1 — composiciones mensuales según fases del ONI\nMedellín, 1981–2021', fontsize=16)
fig.savefig(OUT/'CHELSA_ENSO_1981_2021_6panel.png', dpi=220, bbox_inches='tight')
print('Periodos comunes:', periods[0], periods[-1], 'n=', len(periods))
print('Meses por fase:', {p:len(arrays['pr'][p]) for p in phases})
print('Figura:', OUT/'CHELSA_ENSO_1981_2021_6panel.png')
