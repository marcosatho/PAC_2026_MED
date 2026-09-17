from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://sim.metropol.gov.co/arcgis/rest/services/POMCA/POMCA/MapServer"
BBOX = (818290.0, 1153058.1, 884560.0, 1219988.1)
WKID = 21897
WIDTH = 663
HEIGHT = 670

CRS_WKT = (
    'PROJCS["MAGNA-SIRGAS / Colombia Bogota zone",'
    'GEOGCS["MAGNA-SIRGAS",'
    'DATUM["Marco_Geocentrico_Nacional_de_Referencia",'
    'SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],'
    'AUTHORITY["EPSG","6686"]],'
    'PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],'
    'UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],'
    'AUTHORITY["EPSG","4686"]],'
    'PROJECTION["Transverse_Mercator"],'
    'PARAMETER["latitude_of_origin",4.59620041666667],'
    'PARAMETER["central_meridian",-74.0775079166667],'
    'PARAMETER["scale_factor",1],'
    'PARAMETER["false_easting",1000000],'
    'PARAMETER["false_northing",1000000],'
    'UNIT["metre",1,AUTHORITY["EPSG","9001"]],'
    'AXIS["Easting",EAST],AXIS["Northing",NORTH],'
    'AUTHORITY["EPSG","21897"]]'
)

LAYERS = {
    22: "evapotranspiracion",
    23: "temperatura",
    24: "precipitacion",
}


def read_url(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "PAC-Medellin-2026/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def write_world_file(path: Path) -> None:
    xmin, ymin, xmax, ymax = BBOX
    pixel_x = (xmax - xmin) / WIDTH
    pixel_y = (ymax - ymin) / HEIGHT
    center_x = xmin + pixel_x / 2
    center_y = ymax - pixel_y / 2

    path.write_text(
        "\n".join(
            [
                f"{pixel_x:.15f}",
                "0.0",
                "0.0",
                f"{-pixel_y:.15f}",
                f"{center_x:.15f}",
                f"{center_y:.15f}",
            ]
        )
        + "\n",
        encoding="ascii",
    )


def main(output_dir: str) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    service_metadata_url = f"{BASE}?f=pjson"
    legend_url = f"{BASE}/legend?f=pjson"

    (output / "metadatos_servicio.json").write_bytes(read_url(service_metadata_url))
    (output / "leyenda_servicio.json").write_bytes(read_url(legend_url))

    downloads = []

    for layer_id, slug in LAYERS.items():
        layer_metadata_url = f"{BASE}/{layer_id}?f=pjson"
        metadata_path = output / f"{layer_id}_{slug}_metadatos.json"
        metadata_path.write_bytes(read_url(layer_metadata_url))

        params = {
            "bbox": ",".join(str(value) for value in BBOX),
            "bboxSR": str(WKID),
            "imageSR": str(WKID),
            "size": f"{WIDTH},{HEIGHT}",
            "dpi": "96",
            "format": "png32",
            "transparent": "true",
            "layers": f"show:{layer_id}",
            "f": "image",
        }
        export_url = f"{BASE}/export?{urllib.parse.urlencode(params)}"
        image = read_url(export_url)

        if not image.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError(f"La capa {layer_id} no devolvio un PNG valido")

        png_path = output / f"{layer_id}_{slug}_pomca_render.png"
        png_path.write_bytes(image)
        write_world_file(png_path.with_suffix(".pgw"))
        png_path.with_suffix(".prj").write_text(CRS_WKT, encoding="utf-8")

        downloads.append(
            {
                "layer_id": layer_id,
                "name": slug,
                "source": layer_metadata_url,
                "export_url": export_url,
                "png": png_path.name,
                "world_file": png_path.with_suffix(".pgw").name,
                "crs_file": png_path.with_suffix(".prj").name,
            }
        )

    manifest = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_service": BASE,
        "bbox": BBOX,
        "crs": f"EPSG:{WKID}",
        "width": WIDTH,
        "height": HEIGHT,
        "approximately_m_per_pixel": {
            "x": (BBOX[2] - BBOX[0]) / WIDTH,
            "y": (BBOX[3] - BBOX[1]) / HEIGHT,
        },
        "data_status": "rendered_map_images_not_raw_numeric_rasters",
        "warning": (
            "El MapServer no expone WCS ni el archivo raster fuente. "
            "Estas imagenes conservan georreferenciacion, pero sus bandas "
            "contienen colores renderizados y no valores climaticos originales."
        ),
        "downloads": downloads,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python descargar_capas_climaticas_pomca.py CARPETA_SALIDA")
    main(sys.argv[1])
