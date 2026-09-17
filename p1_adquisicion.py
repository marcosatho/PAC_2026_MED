"""Funciones incluidas íntegramente en el primer cuaderno Colab de C1/P1."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import math
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt
from rasterio.plot import show

SERVICE = 'https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Limite_Politico_Admtivo/MapServer'
COLLECTION = 'UCSB-CHC/CHIRPS/V3/PENTAD'
CRS = 'EPSG:9377'
NODATA = -9999.0
SESSION = requests.Session()
SESSION.mount('https://', HTTPAdapter(max_retries=Retry(total=4, backoff_factor=1, status_forcelist=[429,500,502,503,504])))

def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def api(url, **params):
    response = SESSION.get(url, params={'f':'json', **params}, timeout=(20,180))
    response.raise_for_status()
    result = response.json()
    if 'error' in result:
        raise RuntimeError(f"Servicio oficial: {result['error']}")
    return result

def paths(root):
    result = {name:Path(root)/name for name in ['01_CUADERNOS','02_DATOS_ORIGINALES','03_DATOS_PREPARADOS','04_PREVISUALIZACIONES','05_METADATOS']}
    for p in result.values():
        p.mkdir(parents=True, exist_ok=True)
    return result

def boundaries(root, snapshot):
    """Descarga por OBJECTID para evitar truncamiento silencioso del servicio."""
    p = paths(root)
    raw = p['02_DATOS_ORIGINALES']/'limites_medellin'/snapshot
    prepared = p['03_DATOS_PREPARADOS']/snapshot
    prepared.mkdir(parents=True, exist_ok=True)
    gpkg = prepared/'limites_medellin_9377.gpkg'
    report_path = p['05_METADATOS']/f'limites_{snapshot}.json'
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding='utf-8'))
        for file, expected in report['sha256'].items():
            if sha(Path(root)/file.replace('\\','/')) != expected:
                raise RuntimeError(f'Cambio o descarga incompleta: {file}. Utilice otra fecha de captura.')
        return gpkg, report
    if gpkg.exists():
        raise RuntimeError('Captura parcial: elija un nuevo SNAPSHOT para no sobrescribir datos.')
    frames, report = {}, {'service':SERVICE, 'download_utc':datetime.now(timezone.utc).isoformat(), 'layers':{}, 'sha256':{}}
    for layer, name in [(0,'barrios_veredas'),(1,'comunas_corregimientos'),(2,'limite_medellin')]:
        url = f'{SERVICE}/{layer}'
        meta = api(url)
        save_json(raw/f'{name}_metadatos.json',meta)
        count = api(url+'/query',where='1=1',returnCountOnly='true')['count']
        ids = api(url+'/query',where='1=1',returnIdsOnly='true')['objectIds']
        if not ids or len(set(ids)) != count:
            raise RuntimeError(f'Conteo inconsistente: {name}')
        ids = sorted(ids)
        features, envelope = [], None
        for start in range(0,len(ids),100):
            chunk = api(url+'/query',objectIds=','.join(map(str,ids[start:start+100])),outFields='*',returnGeometry='true',outSR='9377')
            if chunk.get('exceededTransferLimit'):
                raise RuntimeError('El servidor truncó una página.')
            if envelope is None:
                envelope = {k:v for k,v in chunk.items() if k!='features'}
            features.extend(chunk['features'])
        oid = next(f['name'] for f in meta['fields'] if f['type']=='esriFieldTypeOID')
        if set(f['attributes'][oid] for f in features) != set(ids):
            raise RuntimeError('Faltan entidades o existen duplicados en la descarga.')
        rawfile = raw/f'{name}_original_9377.esrijson'
        save_json(rawfile,{**envelope,'features':features})
        frame = gpd.read_file(rawfile)
        if frame.crs is None or frame.crs.to_epsg()!=9377:
            raise RuntimeError(f'CRS inesperado en {name}: {frame.crs}')
        if frame.geometry.is_empty.any() or frame.geometry.isna().any():
            raise RuntimeError(f'Geometrías vacías: {name}')
        invalid = int((~frame.is_valid).sum())
        if invalid:
            raise RuntimeError(f'{name}: {invalid} geometrías inválidas; originales guardados, reparar explícitamente antes de continuar.')
        frames[name] = frame
        frame.to_file(gpkg,layer=name,driver='GPKG')
        # Copia de intercambio para EE; la referencia de trabajo sigue siendo 9377.
        frame.to_crs(4326).to_file(prepared/f'{name}_4326.geojson',driver='GeoJSON')
        report['layers'][name] = {'count':count,'crs':str(frame.crs),'invalid':invalid,'bounds':frame.total_bounds.tolist(),'description':meta.get('description'),'types':meta.get('types'), 'actualizaciones':frame['fecha_actualizacion'].astype(str).value_counts().to_dict() if 'fecha_actualizacion' in frame else {}}
        print(name, count, 'entidades; EPSG:9377')
    for source, field, cats in [('barrios_veredas','subtipo_barriovereda',{1:'barrios',2:'veredas'}),('comunas_corregimientos','subtipo_comunacorregimiento',{1:'comunas',2:'corregimientos'})]:
        frame=frames[source]
        if not set(frame[field].dropna().unique()).issubset(cats):
            raise RuntimeError(f'Subtipos desconocidos: {source}')
        for value,name in cats.items():
            part=frame[frame[field]==value].copy()
            if part.empty:
                raise RuntimeError(f'Sin entidades: {name}')
            part.to_file(gpkg,layer=name,driver='GPKG')
            report['layers'][name]={'count':len(part),'derived_from':source,'filter':f'{field}={value}'}
    outline=frames['limite_medellin'].geometry.union_all()
    report['area_municipal_km2']=outline.area/1e6
    report['coverage_check_km2']={name:frame.geometry.union_all().symmetric_difference(outline).area/1e6 for name,frame in frames.items() if name!='limite_medellin'}
    report['caveat']='La descripción del límite menciona 2014. Descarga actual del servicio no equivale a certificación de vigencia jurídica 2026.'
    fig,ax=plt.subplots(figsize=(9,9))
    frames['barrios_veredas'].boundary.plot(ax=ax,color='#a4afb5',linewidth=.35)
    frames['comunas_corregimientos'].boundary.plot(ax=ax,color='#287481',linewidth=.9)
    frames['limite_medellin'].boundary.plot(ax=ax,color='#a32b38',linewidth=1.8)
    ax.set(title='Control de descarga: límites oficiales de Medellín',xlabel='Este (m) — MAGNA-SIRGAS / Origen Nacional',ylabel='Norte (m) — EPSG:9377')
    ax.ticklabel_format(style='plain',useOffset=False);fig.tight_layout()
    fig.savefig(p['04_PREVISUALIZACIONES']/f'limites_{snapshot}.png',dpi=150);plt.close(fig)
    for f in list(raw.glob('*'))+list(prepared.glob('*')):
        report['sha256'][f.relative_to(root).as_posix()]=sha(f)
    save_json(report_path,report)
    return gpkg,report

def audit_boundaries(root,snapshot,gpkg):
    """Distingue registros del servicio y unidades identificadas por nombre."""
    result={}
    for name in ['barrios_veredas','comunas_corregimientos']:
        f=gpd.read_file(gpkg,layer=name)
        missing=f['nombre'].isna() | f['nombre'].fillna('').str.strip().eq('')
        result[name]={'records':len(f),'unnamed':f.loc[missing,['codigo','nombre']].fillna('').to_dict('records'),'duplicate_codes':f.loc[f['codigo'].duplicated(keep=False),'codigo'].tolist()}
    save_json(Path(root)/'05_METADATOS'/f'limites_revision_atributos_{snapshot}.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

def chirps(root,snapshot,gpkg,start_year=1981,end_year=2025,buffer_m=50000):
    """Requiere ee.Initialize. Descarga pentadas completas por año y región."""
    import ee
    if end_year<start_year or not 0<=buffer_m<=100000:
        raise ValueError('Periodo o buffer no permitido para esta descarga regional.')
    p=paths(root)
    raw=p['02_DATOS_ORIGINALES']/'CHIRPS_V3_PENTAD'/f'{start_year}_{end_year}_{snapshot}'
    raw.mkdir(parents=True,exist_ok=True)
    local=gpd.read_file(gpkg,layer='limite_medellin').to_crs(9377)
    aoi=gpd.GeoSeries([local.geometry.union_all().buffer(buffer_m).envelope],crs=9377).to_crs(4326)
    bbox=aoi.total_bounds.tolist()
    collection=ee.ImageCollection(COLLECTION).select('precipitation')
    proj=collection.first().projection().getInfo()
    affine=Affine(*proj['transform'])
    if affine.b or affine.d or affine.a<=0 or affine.e>=0:
        raise RuntimeError('Grilla no compatible con este recorte.')
    left,bottom,right,top=bbox
    col0=math.floor((left-affine.c)/affine.a);col1=math.ceil((right-affine.c)/affine.a)
    row0=math.floor((top-affine.f)/affine.e);row1=math.ceil((bottom-affine.f)/affine.e)
    subset=affine*Affine.translation(col0,row0)
    width,height=col1-col0,row1-row0
    if width*height*72*4>28*1024**2 or max(width,height)>10000:
        raise RuntimeError('Solicitud demasiado grande: dividir dominio antes de descargar.')
    files=[]
    for year in range(start_year,end_year+1):
        part=collection.filterDate(f'{year}-01-01',f'{year+1}-01-01').sort('system:time_start')
        stamps=part.aggregate_array('system:time_start').getInfo()
        dates=[datetime.fromtimestamp(t/1000,timezone.utc).strftime('%Y%m%d') for t in stamps]
        expected=[f'{year}{m:02d}{d:02d}' for m in range(1,13) for d in [1,6,11,16,21,26]]
        if dates!=expected:
            raise RuntimeError(f'{year}: fechas faltantes, repetidas o inesperadas; no se descargará como año completo.')
        file=raw/f'CHIRPS_V3_pentadas_{year}_nativo.tif'
        meta=file.with_suffix('.json')
        if file.exists() and meta.exists():
            old=json.loads(meta.read_text(encoding='utf-8'))
            if old['sha256']!=sha(file) or old['transform']!=list(subset)[:6] or old['dates']!=dates:
                raise RuntimeError('Archivo previo incompatible; cambiar SNAPSHOT.')
        else:
            image=part.toBands().rename(['P_'+d for d in dates]).toFloat().unmask(NODATA)
            url=image.getDownloadURL({'crs':proj['crs'],'crs_transform':list(subset)[:6],'dimensions':[width,height],'format':'GEO_TIFF','filePerBand':False})
            temp=file.with_suffix('.part')
            with SESSION.get(url,stream=True,timeout=(20,180)) as response:
                response.raise_for_status()
                with temp.open('wb') as stream:
                    for chunk in response.iter_content(1024*1024):stream.write(chunk)
            with rasterio.open(temp) as src:
                if src.count!=72 or src.width!=width or src.height!=height or src.crs.to_string()!=proj['crs'] or not src.transform.almost_equals(subset):
                    raise RuntimeError('Grilla o bandas inesperadas en GeoTIFF.')
                a=src.read()
                if not np.isfinite(a).all() or not (a!=NODATA).any() or ((a<0)&(a!=NODATA)).any():
                    raise RuntimeError('Precipitación inválida o región sin datos.')
            temp.replace(file)
            save_json(meta,{'collection':COLLECTION,'dates':dates,'units':'mm/pentad','crs':proj['crs'],'transform':list(subset)[:6],'sha256':sha(file),'download_utc':datetime.now(timezone.utc).isoformat(),'buffer_m':buffer_m})
        files.append(file);print(year,'72 pentadas guardadas')
    return files

def prepare_and_preview(root,snapshot,gpkg,files):
    """Copias reproyectadas y control básico; no realiza análisis de tendencias."""
    p=paths(root)
    out=p['03_DATOS_PREPARADOS']/snapshot/'CHIRPS_9377';out.mkdir(parents=True,exist_ok=True)
    with rasterio.open(files[0]) as first:
        target,nx,ny=calculate_default_transform(first.crs,CRS,first.width,first.height,*first.bounds)
        original_profile=first.profile.copy()
    all_years=[]
    for file in files:
        with rasterio.open(file) as src:
            data=src.read();missing=(data==NODATA)|~np.isfinite(data)
            annual=np.where(missing.any(axis=0),np.nan,np.where(missing,0,data).sum(axis=0,dtype='float64'))
            all_years.append(annual)
            profile=src.profile.copy();profile.update(crs=CRS,transform=target,width=nx,height=ny,nodata=NODATA,compress='deflate')
            with rasterio.open(out/file.name.replace('_nativo','_9377'),'w',**profile) as dst:
                for i in range(1,src.count+1):
                    reproject(source=data[i-1],destination=rasterio.band(dst,i),src_transform=src.transform,src_crs=src.crs,src_nodata=NODATA,dst_transform=target,dst_crs=CRS,dst_nodata=NODATA,resampling=Resampling.nearest)
                    dst.set_band_description(i,src.descriptions[i-1] or f'pentada_{i:02d}')
    mean=np.mean(np.stack(all_years),axis=0).astype('float32')
    valid=np.isfinite(mean)
    if not valid.any():raise RuntimeError('No hay climatología con cobertura completa.')
    original_profile.update(count=1,dtype='float32',nodata=NODATA,compress='deflate')
    mean_native=out/'P_media_anual_previsualizacion_nativa.tif'
    with rasterio.open(mean_native,'w',**original_profile) as dst:dst.write(np.where(valid,mean,NODATA),1)
    projected=np.full((ny,nx),NODATA,dtype='float32')
    reproject(np.where(valid,mean,NODATA),projected,src_transform=original_profile['transform'],src_crs=original_profile['crs'],src_nodata=NODATA,dst_transform=target,dst_crs=CRS,dst_nodata=NODATA,resampling=Resampling.nearest)
    profile=original_profile.copy();profile.update(crs=CRS,transform=target,width=nx,height=ny)
    result=out/'P_media_anual_previsualizacion_9377.tif'
    with rasterio.open(result,'w',**profile) as dst:dst.write(projected,1)
    boundary=gpd.read_file(gpkg,layer='limite_medellin')
    fig,ax=plt.subplots(figsize=(10,9))
    with rasterio.open(result) as src:show(src.read(1,masked=True),transform=src.transform,ax=ax,cmap='YlGnBu',interpolation='nearest')
    boundary.boundary.plot(ax=ax,color='#c32332',linewidth=1.7)
    gpd.read_file(gpkg,layer='comunas_corregimientos').boundary.plot(ax=ax,color='#303030',linewidth=.45)
    fig.colorbar(ax.images[0],ax=ax,label='Precipitación media anual (mm/año)')
    ax.set(title=f'Control CHIRPS v3: media anual de {len(files)} años completos',xlabel='Este (m) — MAGNA-SIRGAS / Origen Nacional',ylabel='Norte (m) — EPSG:9377')
    ax.ticklabel_format(style='plain',useOffset=False)
    fig.text(.1,.02,'Límite oficial superpuesto. Píxel original 0,05°. Reproyección por vecino más próximo; sin suavizado.',fontsize=9)
    fig.savefig(p['04_PREVISUALIZACIONES']/f'CHIRPS_{snapshot}.png',dpi=150,bbox_inches='tight');plt.show()
    save_json(p['05_METADATOS']/f'CHIRPS_preparacion_{snapshot}.json',{'crs':CRS,'resampling':'nearest','native_resolution_degrees':.05,'years':len(files),'inputs':[str(f.relative_to(root)) for f in files],'output':str(result.relative_to(root)),'purpose':'Previsualización básica; análisis final pendiente.'})
    return result
