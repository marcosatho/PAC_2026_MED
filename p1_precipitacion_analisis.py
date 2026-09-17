from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.features import geometry_mask
from shapely.geometry import Polygon, mapping
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, ListedColormap, BoundaryNorm, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Patch

CRS='EPSG:9377'
NOTE=('CHIRPS combina estimaciones satelitales y estaciones. Aceptación exploratoria por concordancia de orden de magnitud '
      'reportada por el usuario; fuentes externas todavía sin incorporar. No constituye validación cuantitativa local. '
      'Posibles sesgos espaciales y temporales, especialmente en terreno montañoso. El suavizado no mejora la resolución efectiva de 0,05°.')

# Paletas separadas: discreta para los píxeles nativos y continua para el campo gaussiano.
PALETA_DISCRETA = ListedColormap(['#ffffcc','#d9f0a3','#addd8e','#78c679','#41ab5d','#238443','#005a32'], name='precipitacion_discreta')
PALETA_GAUSSIANA = LinearSegmentedColormap.from_list('precipitacion_gaussiana', ['#fff7bc','#d9f0a3','#addd8e','#78c679','#41ab5d','#238443','#005a32'], N=256)

def read_mean(root,snapshot,years):
    directory=Path(root)/'02_DATOS_ORIGINALES'/'CHIRPS_V3_PENTAD'/f'{years[0]}_{years[-1]}_{snapshot}'
    arrays=[];files=[];ref=None
    for year in years:
        f=directory/f'CHIRPS_V3_pentadas_{year}_nativo.tif'
        meta=json.loads(f.with_suffix('.json').read_text(encoding='utf-8'))
        expected=[f'{year}{m:02d}{d:02d}' for m in range(1,13) for d in [1,6,11,16,21,26]]
        if meta['dates']!=expected or meta['collection']!='UCSB-CHC/CHIRPS/V3/PENTAD':
            raise ValueError(f'Fechas o colección inesperadas: {f.name}')
        if hashlib.sha256(f.read_bytes()).hexdigest()!=meta['sha256']:
            raise ValueError(f'Huella SHA256 distinta: {f.name}')
        with rasterio.open(f) as src:
            if src.count!=72 or src.crs.to_epsg()!=4326:
                raise ValueError('Se requieren 72 pentadas y cuadrícula nativa EPSG:4326.')
            if ref is None:ref=src.profile.copy()
            if src.transform!=ref['transform'] or src.width!=ref['width'] or src.height!=ref['height']:
                raise ValueError('Los años no comparten cuadrícula.')
            a=src.read().astype('float64')
            invalid=~np.isfinite(a)|(a==-9999)
            if src.nodata is not None:invalid|=(a==src.nodata)
            if ((a<0)&~invalid).any():raise ValueError('Precipitación negativa inesperada.')
            a[invalid]=np.nan
            arrays.append(np.sum(a,axis=0))
        files.extend([f,f.with_suffix('.json')])
    mean=np.mean(np.stack(arrays),axis=0)
    return mean,ref,files

def native_cells(mean,profile,municipality):
    records=[];shapes=[]
    tf=profile['transform']
    for r in range(mean.shape[0]):
        for c in range(mean.shape[1]):
            shape=Polygon([tf*(c,r),tf*(c+1,r),tf*(c+1,r+1),tf*(c,r+1)])
            shapes.append(shape.segmentize(.0025))
            records.append({'pixel_id':f'r{r:03d}_c{c:03d}','fila':r,'columna':c,'P_mm_anio':float(mean[r,c])})
    grid=gpd.GeoDataFrame(records,geometry=shapes,crs=4326).to_crs(CRS)
    grid=grid[grid.intersects(municipality)].copy()
    grid['area_pixel_m2']=grid.area
    intersections=grid.geometry.intersection(municipality)
    grid['area_en_medellin_m2']=intersections.area
    grid['fraccion_en_medellin']=grid.area_en_medellin_m2/grid.area_pixel_m2
    # Tolerancia exclusivamente numérica, expresada en m²; no se excluyen intersecciones pequeñas.
    grid['clase']=np.where(grid.area_en_medellin_m2<=1e-6,'Solo contacto',np.where(grid.area_pixel_m2-grid.area_en_medellin_m2<=1e-6,'Completo','Parcial'))
    coverage=intersections.area.sum()/municipality.area
    if abs(coverage-1)>1e-6:raise ValueError(f'Cuadrícula incompleta: cobertura {coverage}')
    if grid.loc[grid.area_en_medellin_m2>1e-6,'P_mm_anio'].isna().any():raise ValueError('Hay píxeles municipales sin datos completos.')
    return grid

def filtered_surface(mean,profile,municipality,resolution=1000,sigma_m=6000,radius_m=12000):
    if resolution<=0 or sigma_m<=0 or radius_m<=0 or radius_m/resolution>100:
        raise ValueError('Parámetros gaussianos no válidos.')
    h,w=mean.shape
    bounds=rasterio.transform.array_bounds(h,w,profile['transform'])
    tf,nx,ny=calculate_default_transform(profile['crs'],CRS,w,h,*bounds,resolution=resolution)
    regional=np.full((ny,nx),np.nan)
    reproject(mean,regional,src_transform=profile['transform'],src_crs=profile['crs'],src_nodata=np.nan,dst_transform=tf,dst_crs=CRS,dst_nodata=np.nan,resampling=Resampling.nearest)
    valid=np.isfinite(regional)
    radius=int(math.ceil(radius_m/resolution))
    kwargs={'sigma':sigma_m/resolution,'radius':radius,'mode':'constant','cval':0.0}
    weights=gaussian_filter(valid.astype('float64'),**kwargs)
    values=gaussian_filter(np.where(valid,regional,0),**kwargs)
    smooth=np.divide(values,weights,out=np.full_like(values,np.nan),where=weights>1e-12)
    inside=geometry_mask([mapping(municipality)],out_shape=regional.shape,transform=tf,invert=True)
    # El filtro opera antes del recorte, con todo el contexto. Se exige soporte completo dentro de Medellín.
    if (weights[inside]<.999999).any():raise ValueError('Contexto o datos insuficientes para el filtro; ampliar dominio o revisar NoData.')
    if not inside.any():raise ValueError('Máscara municipal vacía.')
    return regional,smooth,inside,tf

def map_axes(ax,municipality,title,pad=3500):
    x0,y0,x1,y1=municipality.bounds
    ax.set_xlim(x0-pad,x1+pad);ax.set_ylim(y0-pad,y1+pad)
    ax.set_aspect('equal');ax.set_title(title,fontsize=12,pad=12)
    ax.set_xlabel('Este (m)');ax.set_ylabel('Norte (m)')
    ax.ticklabel_format(style='plain',useOffset=False)
    ax.tick_params(axis='x',rotation=25,labelsize=9);ax.tick_params(axis='y',labelsize=9)
    ax.annotate('N',xy=(.95,.96),xytext=(.95,.85),xycoords='axes fraction',ha='center',arrowprops={'arrowstyle':'->','color':'#27333b'})
    sx=x0;sy=y0-pad*.65
    ax.plot([sx,sx+5000],[sy,sy],color='#27333b',linewidth=2)
    ax.text(sx+2500,sy+300,'5 km',ha='center',fontsize=9)

def run_analysis(root,snapshot='20260910',start_year=1981,end_year=2025,sigma_m=6000,radius_m=12000,resolution=1000,output=None):
    root=Path(root)
    years=list(range(start_year,end_year+1))
    if not years:raise ValueError('Periodo vacío.')
    runid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out=Path(output) if output else root/'06_ANALISIS_PRECIPITACION'/runid
    out.mkdir(parents=True,exist_ok=False)
    gpkg=root/'03_DATOS_PREPARADOS'/snapshot/'limites_medellin_9377.gpkg'
    limits=gpd.read_file(gpkg,layer='limite_medellin').to_crs(CRS)
    municipality=limits.geometry.union_all()
    if not municipality.is_valid:raise ValueError('Límite municipal inválido.')
    mean,profile,files=read_mean(root,snapshot,years)
    grid=native_cells(mean,profile,municipality)
    grid.to_file(out/'pixeles_CHIRPS_medellin.gpkg',layer='pixeles_completos',driver='GPKG')
    positive=grid[grid.area_en_medellin_m2>1e-6].copy()
    clipped=positive.copy();clipped.geometry=clipped.geometry.intersection(municipality)
    clipped.to_file(out/'pixeles_CHIRPS_medellin.gpkg',layer='porciones_en_medellin',driver='GPKG')
    grid.drop(columns='geometry').to_csv(out/'pixeles_interseccion.csv',index=False,encoding='utf-8-sig')
    regional,smooth,inside,tf=filtered_surface(mean,profile,municipality,resolution,sigma_m,radius_m)
    for name,data in [('P_regional_sin_suavizar_9377',regional),('P_gaussiana_regional_9377',smooth),('P_gaussiana_Medellin_9377',np.where(inside,smooth,np.nan))]:
        with rasterio.open(out/(name+'.tif'),'w',driver='GTiff',height=data.shape[0],width=data.shape[1],count=1,dtype='float32',crs=CRS,transform=tf,nodata=-9999,compress='deflate') as dst:
            dst.write(np.where(np.isfinite(data),data,-9999).astype('float32'),1)
            dst.update_tags(units='mm/year',period=f'{start_year}-{end_year}',native_resolution='0.05 degrees',purpose='exploratory cartographic representation')
    counts={name:int((grid.clase==name).sum()) for name in ['Completo','Parcial','Solo contacto']}
    color_range=np.r_[positive.P_mm_anio.to_numpy(),smooth[inside]]
    vmin=math.floor(np.nanmin(color_range)/100)*100
    vmax=math.ceil(np.nanmax(color_range)/100)*100
    norm_gauss=Normalize(vmin=vmin,vmax=vmax)
    niveles_discretos=np.linspace(vmin,vmax,PALETA_DISCRETA.N+1)
    norm_discreto=BoundaryNorm(niveles_discretos,PALETA_DISCRETA.N,clip=True)
    colors={'Completo':'#299d8f','Parcial':'#f2b24b','Solo contacto':'#ae4c82'}
    fig,axs=plt.subplots(1,2,figsize=(14,8))
    grid.plot(column='P_mm_anio',ax=axs[0],cmap=PALETA_DISCRETA,norm=norm_discreto,edgecolor='#52616b',linewidth=.6)
    grid.plot(ax=axs[1],color=grid.clase.map(colors),edgecolor='#52616b',linewidth=.6)
    for ax in axs:
        limits.boundary.plot(ax=ax,color='#a82236',linewidth=1.8)
        for _,record in grid.iterrows():
            p=record.geometry.representative_point();ax.text(p.x,p.y,record.pixel_id.replace('r','').replace('_c','/'),ha='center',va='center',fontsize=6,color='#253340')
    map_axes(axs[0],municipality,'Píxeles originales que intersectan Medellín',pad=8000)
    map_axes(axs[1],municipality,'Relación de cada píxel con el límite',pad=8000)
    axs[1].legend(handles=[Patch(facecolor=colors[k],label=f'{k}: {counts[k]}') for k in colors],loc='lower right',fontsize=9)
    fig.colorbar(ScalarMappable(norm=norm_discreto,cmap=PALETA_DISCRETA),ax=axs[0],shrink=.65,label='Precipitación media anual (mm/año)')
    fig.suptitle(f'CHIRPS v3 · Precipitación {start_year}–{end_year}',fontsize=16)
    fig.text(.08,.045,'MAGNA-SIRGAS / Origen Nacional (EPSG:9377). Bordes de la cuadrícula nativa de 0,05°. IDs: fila/columna.',fontsize=10)
    fig.text(.08,.02,'Aceptación exploratoria; validación cuantitativa local pendiente. Fuente: CHIRPS v3 y Alcaldía de Medellín.',fontsize=9)
    fig.subplots_adjust(bottom=.17,top=.88,wspace=.32)
    fig.savefig(out/'01_pixeles_originales_y_cobertura.png',dpi=180);plt.show();plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(13,8))
    clipped.plot(column='P_mm_anio',ax=axs[0],cmap=PALETA_DISCRETA,norm=norm_discreto,edgecolor='#64727d',linewidth=.5)
    extent=rasterio.transform.array_bounds(*smooth.shape,tf)
    left,bottom,right,top=extent
    # La visualización suavizada conserva el contexto exterior; el límite se dibuja encima.
    axs[1].imshow(np.ma.masked_invalid(smooth),extent=[left,right,bottom,top],origin='upper',cmap=PALETA_GAUSSIANA,norm=norm_gauss,interpolation='nearest')
    for ax in axs:limits.boundary.plot(ax=ax,color='#a82236',linewidth=1.5)
    map_axes(axs[0],municipality,'Valores originales recortados por el límite')
    map_axes(axs[1],municipality,f'Filtro gaussiano: σ = {sigma_m/1000:g} km')
    fig.suptitle(f'Precipitación media anual · Medellín · {start_year}–{end_year}',fontsize=15)
    fig.subplots_adjust(bottom=.2,top=.87,wspace=.3,right=.88)
    fig.colorbar(ScalarMappable(norm=norm_discreto,cmap=PALETA_DISCRETA),ax=axs[0],shrink=.65,label='mm/año — píxeles discretos')
    fig.colorbar(ScalarMappable(norm=norm_gauss,cmap=PALETA_GAUSSIANA),ax=axs[1],shrink=.65,label='mm/año — superficie gaussiana')
    fig.text(.08,.075,f'EPSG:9377. Filtro sobre dominio regional antes del recorte; la figura conserva el excedente exterior. Semiancho de soporte {radius_m/1000:g} km por eje.',fontsize=9)
    fig.text(.08,.05,f'Malla de representación: {resolution:g} m. Resolución efectiva del dato original: 0,05° (~5,6 km).',fontsize=9)
    fig.text(.08,.025,'El suavizado modifica valores y gradientes; no añade información observada. Validación local pendiente.',fontsize=9)
    fig.savefig(out/'02_precipitacion_original_vs_gaussiana.png',dpi=180);plt.show();plt.close(fig)
    record={'run_utc':runid,'period':[start_year,end_year],'snapshot':snapshot,'crs':CRS,'sigma_m':sigma_m,'radius_per_axis_m':radius_m,'support_shape':'square; separable Gaussian','display_grid_m':resolution,'counts':counts,'coverage_fraction':float(positive.area_en_medellin_m2.sum()/municipality.area),'note':NOTE,'definitions':{'Completo':'Área del píxel fuera de Medellín <= 1e-6 m²','Parcial':'Intersección de área positiva y área exterior > 1e-6 m²','Solo contacto':'Intersección topológica con área <= 1e-6 m²'},'inputs_sha256':{f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files+[gpkg]}}
    (out/'metodologia_y_control.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'APUNTES.md').write_text('# Precipitación: alcance y reservas\n\n'+NOTE+'\n\nSe requiere incorporar la referencia externa consultada por el usuario y contrastar con estaciones para validar cuantitativamente.\n\nEl filtro gaussiano usa el entorno regional antes del recorte; maneja NoData mediante pesos normalizados y exige soporte completo en Medellín. Los píxeles se identifican en la cuadrícula geográfica original y se proyectan a EPSG:9377 para intersección y área. La máscara del ráster suavizado usa el centro de cada celda de representación.\n',encoding='utf-8')
    print('Píxeles:',counts,'\nResultados:',out)
    return out,grid,record
