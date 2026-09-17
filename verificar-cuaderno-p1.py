"""Verificación local: sintaxis y transformación con una entrada sintética conocida."""
import ast
from pathlib import Path
import tempfile
import nbformat
import numpy as np
import rasterio
from rasterio.transform import from_origin
import matplotlib
matplotlib.use('Agg')
from p1_adquisicion import prepare_and_preview

n=nbformat.read('P1_07_1_CLIMA_RELIEVE/01_CUADERNOS/01_Obtencion_datos_CHIRPS_limites.ipynb',as_version=4)
nbformat.validate(n)
for c in n.cells:
    if c.cell_type=='code' and not c.source.startswith('%'):
        ast.parse(c.source)
gpkg=Path('P1_07_1_CLIMA_RELIEVE/03_DATOS_PREPARADOS/20260910/limites_medellin_9377.gpkg').resolve()
with tempfile.TemporaryDirectory(prefix='qa_p1_') as temp:
    root=Path(temp);files=[]
    for year,value in [(1991,1),(1992,3)]:
        f=root/f'prueba_{year}_nativo.tif'
        array=np.full((72,40,40),value,dtype='float32');array[:,0,0]=-9999
        with rasterio.open(f,'w',driver='GTiff',height=40,width=40,count=72,dtype='float32',crs='EPSG:4326',transform=from_origin(-76.5,7,.05,.05),nodata=-9999) as dst:
            dst.write(array)
        files.append(f)
    result=prepare_and_preview(root,'prueba',gpkg,files)
    with rasterio.open(result) as src:
        assert src.crs.to_epsg()==9377
        a=src.read(1,masked=True)
        assert a.count()>0 and np.allclose(a.compressed(),144), 'Se esperaba media anual (72+216)/2=144'
    native=result.parent/'P_media_anual_previsualizacion_nativa.tif'
    with rasterio.open(native) as src:
        assert src.read(1,masked=True).mask[0,0]
print('OK: cuaderno válido, celdas compilables, reproyección EPSG:9377, media anual y NoData comprobados con datos sintéticos temporales.')
