from pathlib import Path

import geopandas as gpd
import numpy as np
from osgeo import gdal
from shapely import contains_xy

from recortar_pomca_medellin import GPKG, LAYERS, OUTPUT, classify_pixels, legend_entries


def main():
    legends = legend_entries()
    zones = gpd.read_file(GPKG, layer="comunas_corregimientos").to_crs(9377)

    for layer_id, meta in LAYERS.items():
        path = OUTPUT / f"{layer_id}_{meta['slug']}_medellin_render.tif"
        dataset = gdal.Open(str(path))
        rgba = np.moveaxis(dataset.ReadAsArray(), 0, -1).astype(np.uint8)
        classes, valid = classify_pixels(rgba, layer_id, legends)
        gt = dataset.GetGeoTransform()
        xs = gt[0] + (np.arange(dataset.RasterXSize) + 0.5) * gt[1]
        ys = gt[3] + (np.arange(dataset.RasterYSize) + 0.5) * gt[5]
        xx, yy = np.meshgrid(xs, ys)

        present, counts = np.unique(classes[valid], return_counts=True)
        print(f"\n{meta['title']}")
        print("Clases municipales:", [(legends[layer_id][i][0], int(n)) for i, n in zip(present, counts)])

        highest = int(present.max())
        print("Clase máxima presente:", legends[layer_id][highest][0])
        rows = []
        for _, zone in zones.iterrows():
            if not zone["nombre"]:
                continue
            inside = contains_xy(zone.geometry, xx, yy) & valid
            n_high = int(np.count_nonzero(inside & (classes == highest)))
            if n_high:
                rows.append((zone["nombre"], n_high, int(np.count_nonzero(inside))))
        for name, n_high, total in sorted(rows, key=lambda item: item[1], reverse=True):
            print(f"  {name}: {n_high} píxeles de clase máxima; {100*n_high/total:.1f}% de sus píxeles")


if __name__ == "__main__":
    main()
