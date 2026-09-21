# -*- coding: utf-8 -*-
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np

SRC_DIR = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\08_1_AMENAZAS\01_DAGRD_SIATA_ESCENARIOS\01_DATOS_ORIGINALES\Archivos_Soporte\3_Precip_extrema"
OUT_DIR = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\08_1_AMENAZAS\01_DAGRD_SIATA_ESCENARIOS\02_DATOS_PREPARADOS"
DST_CRS = "EPSG:9377"

files = [
    "PPT_1990_Percentil_90.tif", "PPT_2030_Percentil_90.tif", "PPT_2040_Percentil_90.tif",
    "PPT_1990_Percentil_95.tif", "PPT_2030_Percentil_95.tif", "PPT_2040_Percentil_95.tif",
]

import os
os.makedirs(OUT_DIR, exist_ok=True)

for fname in files:
    src_path = f"{SRC_DIR}/{fname}"
    dst_path = f"{OUT_DIR}/{fname.replace('.tif', '_9377.tif')}"
    with rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, DST_CRS, src.width, src.height, *src.bounds, resolution=200
        )
        kwargs = src.meta.copy()
        kwargs.update({"crs": DST_CRS, "transform": transform, "width": width, "height": height})
        with rasterio.open(dst_path, "w", **kwargs) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=DST_CRS,
                resampling=Resampling.bilinear,
            )
    print("reprojected", fname, "->", dst_path)
