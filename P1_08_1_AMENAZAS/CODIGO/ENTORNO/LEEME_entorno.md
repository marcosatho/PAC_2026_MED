# Entorno de Python de los mapas y figuras del P1 (7.1 y 8.1)

Fecha: 2026-10-18. Sistema: Windows 11. Python 3.12.14 en los dos entornos.

## Qué librerías y qué versiones

| Librería | Para qué se usa | Entorno A: Codex + `.mapdeps` | Entorno B: QGIS 3.44.14 |
|---|---|---|---|
| geopandas | leer y cruzar capas vectoriales | 1.1.4 | 1.1.4 |
| shapely | geometrías (`make_valid`) | 2.1.2 | 2.1.2 |
| pyogrio | leer GeoPackage y geodatabase | 0.13.0 | 0.13.0 |
| pyproj | proyecciones (EPSG:9377) | 3.8.0 | 3.7.2 |
| rasterio | leer ráster (DTM, temperatura, días calurosos) | 1.5.1 | 1.5.1 (instalado en el usuario, ver abajo) |
| affine | transformaciones de ráster | 3.0.1 | 3.0.1 |
| GDAL/OGR (`osgeo`) | zip y RAR de gdb, metadata, `gdal.Warp` | no incluido | 3.13.3 |
| matplotlib | mapas y gráficos | 3.11.2 | 3.11.1 |
| numpy / pandas | cálculos | 2.5.3 / 3.0.5 | 2.4.6 / 3.0.5 |
| pillow | tamaños de imagen, vistas previas | 12.3.0 | 12.3.0 |
| openpyxl / lxml / pypdf | Excel, Word por XML, PDF | 3.1.5 / 6.1.1 / 6.10.0 | 3.1.5 / 6.1.1 / 6.15.0 |

Archivos con la lista completa y exacta de paquetes de cada entorno:
- `requirements_mapas.txt`: lo mínimo para instalar con pip (versiones del entorno A).
- `freeze_python_codex_mapdeps.txt` (93 paquetes) y `freeze_python_qgis_3.44.txt` (117 paquetes).

## Dónde están los entornos en este equipo

- **A. Python de Codex + `.mapdeps`:** `C:\Users\marco\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` con la variable `PYTHONPATH=C:\Users\marco\.codex\.chatgpt-projects\g-p-6a9707bd4d7881918247b690a771ddbd\.mapdeps` (y `MPLCONFIGDIR` en `.mpl-p1` de la misma carpeta). Aquí se corrieron los scripts que usan rasterio: relieve, Köppen, días calurosos, temperatura de la superficie, diferencia 2040–2030, riesgo.
- **B. Python de QGIS 3.44.14:** `C:\Program Files\QGIS 3.44.14\bin\python-qgis-ltr.bat`. Aquí se corrieron los de GDAL (`osgeo`): mapas del POMCA, mapas de amenaza v2 (capa oficial del DAP), lectura de las geodatabases, inventario de metadata.

## Cosas que conviene saber para replicar

1. rasterio y `osgeo` no conviven en el entorno A; en el B, rasterio sale del usuario (`C:\Users\marco\AppData\Roaming\Python\Python312\site-packages`) y no se probó mezclarlo con `osgeo` en un mismo script.
2. El lanzador `python-qgis-ltr.bat` falla con argumentos que tengan espacios o tildes; por eso varias rutas se pasan por variables de entorno (`V2_ZIP`, `V2_OUT`, `V2_PREP`, `V2_FIGS`).
3. Con `python -I` (modo aislado) Python ignora los paquetes del usuario: rasterio parece «no instalado» aunque lo esté.
4. Los scripts de figuras en km se corren con `figuras_km/corre_en_km.py` (cambia ejes y regla al guardar) usando `corre_todo.sh` (entorno A) y `corre_qgis.sh` (entorno B).
5. Las rutas de los datos apuntan a Drive (`G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\…`); en otro equipo hay que ajustarlas.
