import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / '.mapdeps'))
import rasterio
folder = Path(sys.argv[1])
for variable in ('pr','tas'):
    files = sorted((folder/variable).glob('*.tif'))
    if not files:
        continue
    with rasterio.open(files[0]) as src:
        data=src.read(1, masked=True)
        print(json.dumps(dict(variable=variable, archivo=files[0].name, shape=src.shape, crs=str(src.crs), bounds=list(src.bounds), resolucion=src.res, scales=src.scales, offsets=src.offsets, validos=int(data.count()), min=float(data.min()), max=float(data.max()), tags=src.tags(), banda_tags=src.tags(1)), ensure_ascii=False))
