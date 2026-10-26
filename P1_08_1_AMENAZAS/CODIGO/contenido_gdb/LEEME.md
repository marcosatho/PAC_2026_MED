# Mapas y resumen del contenido de la geodatabase del POT 2026 (DAP)

Fecha: 2026-10-20. Prepara los 23 mapas 16:9, la lámina índice, el PDF y el Excel de resumen que acompañan el correo sobre el contenido de la geodatabase.

**Estado de la información:** propuesta de revisión del POT 2026, aún no protocolizada (correo del DAP). Todo mapa lleva esa nota.

## Orden de corrida

1. Descomprimir la carpeta `mj_rev_pot_2025_med.gdb` del zip `YDRAY-GDB_Form_DiccTopolog.zip` (Drive: `08_1_AMENAZAS\05_POT2026_AMENAZAS_OFICIAL_V2\01_DATOS_ORIGINALES`) en una carpeta `gdb\` junto a estos scripts. El zip no se modifica. Leer capas dentro del zip es unas diez veces más lento.
2. `cache_capas.py`: lee las 82 capas de datos y las guarda en `cache\*.pkl` (EPSG:9377, sin tocar la geometría). Escribe `resumen_campos.json`.
3. Copiar aquí `Trazabilidad_capas_POT2026_vs_2014_v2.xlsx` (carpeta `METADATA_v2`): de ahí salen el número de elementos y el «origen propuesto» de cada capa.
4. `mapas_contenido_gdb_pot2026.py`: dibuja las 23 láminas en `salida\`. Con `MAPAS_ONLY=01,05` rehace solo algunas. Tarda varios minutos por las capas pesadas (anillo de gas, 238.000 tramos); se pueden correr varios procesos en paralelo, cada uno con su lista en `MAPAS_ONLY`.
5. `arma_excel_indice_pdf.py`: arma `Contenido_geodatabase_POT2026_resumen.xlsx`, `00_indice_contenido_geodatabase.png` y `Mapas_contenido_geodatabase_POT2026.pdf`.
6. `dominios.py` (Python de QGIS, usa `osgeo`): vuelca los dominios de valores codificados de la geodatabase (por ejemplo, `tipo_sistema` 1 = metro, 2 = metrocable…). Ya se usaron para rotular el mapa de transporte.

## Entorno

Python 3.12 con geopandas, shapely, pyogrio, matplotlib, openpyxl y pillow (ver `..\ENTORNO\LEEME_entorno.md`; es el entorno A). Las rutas del límite municipal (`LIM`) y de las estadísticas de amenaza (`STATS`) apuntan a Drive y se cambian con las variables `MAPAS_LIM` y `MAPAS_STATS`.

## Decisiones de diseño

- Mismo estilo que los mapas del Producto 1: fondo gris claro, comunas y corregimientos, límite municipal en rojo, ejes en km con regla alineada con las marcas, nota de «no protocolizada» arriba. Formato 16:9 con un panel de texto (capas, número de elementos, origen propuesto y lo que se ve).
- Orden de las láminas: el de los grupos de la geodatabase (a. división administrativa, b. norma del suelo, c. amenaza y riesgo, d. sistemas generales, e. planificación complementaria, f. financiación).
- Líneas y puntos se recortan al Distrito solo para dibujar; los conteos del panel son los de la capa completa.
- El «origen propuesto» (2014, 2026, inventario…) es una inferencia nuestra, no una declaración del DAP; sale de la tabla de trazabilidad del 18-oct.
