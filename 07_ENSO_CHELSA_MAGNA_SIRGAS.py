from pathlib import Path
import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch
from scipy.ndimage import zoom, distance_transform_edt
from rasterio.transform import from_bounds
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.transform import array_bounds
from rasterio.features import geometry_mask

BASE=Path(__file__).resolve().parent
ROOT=BASE/'P1_07_1_CLIMA_RELIEVE'/'08_CHELSA'
DATA=ROOT/'02_DATOS'; OUT=ROOT/'04_PREVISUALIZACIONES'; OUT.mkdir(parents=True,exist_ok=True)
boundary=gpd.read_file(ROOT.parent/'03_DATOS_PREPARADOS'/'20260910'/'limite_medellin_4326.geojson').to_crs(9377)
divisions=gpd.read_file(ROOT.parent/'03_DATOS_PREPARADOS'/'20260910'/'comunas_corregimientos_4326.geojson').to_crs(9377)
divisions = gpd.clip(divisions, boundary)
exec(open(BASE/'05_ENSO_CHELSA_plot.py',encoding='utf-8').read().split("fig, axes = plt.subplots")[0])

with rasterio.open(paths['pr'][periods[0]]) as src:
    transform,width,height=calculate_default_transform(src.crs,'EPSG:9377',src.width,src.height,*src.bounds,resolution=1000)
    src_transform=src.transform
def warp(a):
    # CHELSA usa 65535 como nodata. Se convierte antes de reproyectar para
    # evitar huecos internos en las composiciones ENSO.
    a=np.where(a>=65000, np.nan, a).astype('float32')
    out=np.full((height,width),np.nan,dtype='float32')
    reproject(a,out,src_transform=src_transform,src_crs='EPSG:4326',dst_transform=transform,dst_crs='EPSG:9377',resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan)
    return out
means={v:{p:[] for p in phases} for v in ('pr','tas')}
for period in periods:
    p=phase_month.loc[period]
    for v in ('pr','tas'):
        with rasterio.open(paths[v][period]) as src: a=src.read(1).astype('float32'); a[a>=65000]=np.nan
        if v=='tas': a=a*.1-273.15
        means[v][p].append(a)
means={v:{p:warp(np.nanmean(np.stack(a),axis=0)) for p,a in means[v].items()} for v in means}

def fill_nearest(a):
    """Completa nodata internos con el valor válido espacialmente más cercano."""
    good=np.isfinite(a)
    if good.all(): return a
    _, idx=distance_transform_edt(~good, return_indices=True)
    out=a.copy()
    out[~good]=a[tuple(idx[:,~good])]
    return out

# El cálculo se hace sobre el dominio regional completo. Después se aplica
# el límite municipal solo como recorte cartográfico.
means={v:{p:fill_nearest(a) for p,a in means[v].items()} for v in means}
mask=geometry_mask(boundary.geometry,transform=transform,out_shape=(height,width),invert=True)
for v in means:
    # Conservamos el raster completo para que el suavizado y las isolíneas
    # tengan vecinos fuera del límite; la máscara se aplica solo al dibujar.
    pass

def interpolate_grid(a, factor=5):
    """Interpola la retícula original; no altera los valores climáticos."""
    valid=np.isfinite(a).astype(float)
    vals=np.nan_to_num(a, nan=0.0)
    num=zoom(vals, factor, order=3)
    den=zoom(valid, factor, order=3)
    return np.divide(num, den, out=np.full_like(num, np.nan), where=den>0.05)

def municipality_clip_path(gdf):
    paths=[]
    for geom in gdf.geometry:
        polys=list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
        for poly in polys:
            for ring in [poly.exterior, *poly.interiors]:
                xy=np.asarray(ring.coords)
                paths.append(MplPath(xy, [MplPath.MOVETO]+[MplPath.LINETO]*(len(xy)-2)+[MplPath.CLOSEPOLY]))
    return MplPath.make_compound_path(*paths)
clip_path = municipality_clip_path(boundary)
# Usamos el rango completo dentro del municipio: así ningún valor queda
# fuera de la escala y se evitan zonas visualmente vacías.
limits={v:(np.nanmin(np.concatenate([a[mask] for a in means[v].values()])),
           np.nanmax(np.concatenate([a[mask] for a in means[v].values()]))) for v in means}
# La extensión de imshow debe corresponder al raster reproyectado, no al
# rectángulo del municipio. Luego el municipio se usa exclusivamente como
# máscara; de lo contrario la imagen se estira y queda concentrada en el
# centro del límite municipal.
rbounds = array_bounds(height, width, transform)
rleft, rbottom, rright, rtop = rbounds
extent=[rleft, rright, rbottom, rtop]
left, bottom, right, top = boundary.total_bounds
fig,axes=plt.subplots(3,2,figsize=(13,16),constrained_layout=True)
for i,p in enumerate(phases):
    for j,v in enumerate(('pr','tas')):
        ax=axes[i,j]; cmap='Blues' if v=='pr' else 'RdYlBu_r'; unit='mm/mes' if v=='pr' else '°C'; lo,hi=limits[v]; a=means[v][p]
        interp=interpolate_grid(a)
        # Garantía final de cobertura: si quedara algún hueco numérico tras
        # la reproyección/interpolación, se rellena con el promedio regional
        # de la composición; no se dejan celdas blancas dentro del municipio.
        interp=np.where(np.isfinite(interp), interp, np.nanmean(a))
        h,w=interp.shape
        hi_transform=from_bounds(rleft,rbottom,rright,rtop,w,h)
        hi_mask=geometry_mask(boundary.geometry,transform=hi_transform,out_shape=(h,w),invert=True)
        display=np.where(hi_mask,interp,np.nan)
        levels=np.linspace(lo,hi,8)
        im=ax.contourf(interp,levels=levels,extent=extent,cmap=cmap,extend='both')
        im.set_clip_path(clip_path, transform=ax.transData)
        cs=ax.contour(interp,levels=levels,extent=extent,colors='0.12',linewidths=.75)
        cs.set_clip_path(clip_path, transform=ax.transData)
        divisions.boundary.plot(ax=ax,color='0.15',linewidth=.35); boundary.boundary.plot(ax=ax,color='#b5122b',linewidth=1.7); ax.set_xlim(left-1000,right+1000); ax.set_ylim(bottom-1000,top+1000); ax.set_title(f'{p} — {"Precipitación mensual" if v=="pr" else "Temperatura media"}\n1981–2021'); ax.set_xlabel('Este (m) — MAGNA-SIRGAS / Origen Nacional'); ax.set_ylabel('Norte (m) — MAGNA-SIRGAS / Origen Nacional'); ax.set_aspect('equal'); fig.colorbar(im,ax=ax,shrink=.72,label=unit,ticks=levels)
fig.suptitle('CHELSA v2.1 — composiciones ENSO recortadas a Medellín',fontsize=16)
out=OUT/'CHELSA_ENSO_1981_2021_MAGNA_SIRGAS_Medellin.png'; fig.savefig(out,dpi=220,bbox_inches='tight'); print(out)
