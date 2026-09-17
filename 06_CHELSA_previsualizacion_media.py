from pathlib import Path
import numpy as np
import rasterio
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent / 'P1_07_1_CLIMA_RELIEVE' / '08_CHELSA'
DATA = ROOT / '02_DATOS'; OUT = ROOT / '04_PREVISUALIZACIONES'; OUT.mkdir(parents=True, exist_ok=True)
LIMIT = ROOT.parent / '03_DATOS_PREPARADOS' / '20260910' / 'limite_medellin_4326.geojson'

def mean_raster(variable):
    files = sorted((DATA / variable).glob('*.tif'))
    if len(files) != 492: raise RuntimeError(f'{variable}: hay {len(files)} archivos; se esperaban 492')
    with rasterio.open(files[0]) as src:
        extent=[src.bounds.left,src.bounds.right,src.bounds.bottom,src.bounds.top]
    stack=[]
    for f in files:
        with rasterio.open(f) as src:
            arr=src.read(1).astype('float32')
            if variable == 'tas': arr=arr*0.1-273.15
            stack.append(arr)
    return np.nanmean(np.stack(stack), axis=0), extent

pr, extent = mean_raster('pr')
tas, _ = mean_raster('tas')
municipality = gpd.read_file(LIMIT).to_crs(4326)
fig, axes = plt.subplots(1, 2, figsize=(15, 7), constrained_layout=True)
for ax, image, title, cmap, unit in [(axes[0],pr,'Precipitación media mensual\nCHELSA v2.1 · 1981–2021','Blues','mm/mes'), (axes[1],tas,'Temperatura media mensual\nCHELSA v2.1 · 1981–2021','RdYlBu_r','°C')]:
    lo, hi = np.nanpercentile(image, [2,98]); im=ax.imshow(image, extent=extent, origin='upper', cmap=cmap, vmin=lo, vmax=hi)
    ax.contour(image, levels=np.linspace(lo,hi,8), extent=extent, colors='0.25', linewidths=.45, alpha=.7)
    municipality.boundary.plot(ax=ax, color='#b5122b', linewidth=1.7)
    ax.set_title(title); ax.set_xlabel('Longitud (°)'); ax.set_ylabel('Latitud (°)'); fig.colorbar(im, ax=ax, shrink=.82, label=unit)
fig.suptitle('Medellín — previsualización CHELSA v2.1', fontsize=16)
target=OUT/'CHELSA_media_1981_2021_P_T.png'; fig.savefig(target, dpi=220, bbox_inches='tight'); print(target)
