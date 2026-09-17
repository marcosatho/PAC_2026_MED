# CHELSA — descarga para Medellín

Fecha de revisión: 2026-09-13. Periodo solicitado: enero de 1981 a diciembre de 2025.

Se consultó el inventario real del servidor público, no solamente las fechas del catálogo. Para `pr` y `tas`, los archivos mensuales v2.1 terminan en diciembre de 2021. Las carpetas de 2022 existen pero no contienen los GeoTIFF mensuales solicitados. Hay 492 meses disponibles por variable en 1981–2021 y 48 meses ausentes por variable en 2022–2025.

La extensión diaria tampoco permite una serie homogénea hasta diciembre de 2025: `pr` tiene cero archivos en 2022–2025; `prec` y `tas` tienen 365, 365, 366 y 270 archivos respectivamente por año. `prec` es precipitación sin corrección de sesgo; la documentación oficial indica que no debe mezclarse con `pr`. No se sustituye una por otra ni se rellenan meses ausentes.

Los recortes conservan la cuadrícula geográfica nativa, valores originales, escala, offset y etiquetas del archivo fuente. Ventana EPSG:4326: oeste -75.95, sur 5.85, este -75.20, norte 6.60. Incluye Medellín y un margen regional para evitar pérdidas de cobertura en los bordes durante futuros análisis. No es aún un recorte estricto municipal, un mapa suavizado ni una conversión a grados Celsius. Verificar las unidades y el factor de escala del producto antes del análisis.

Notebook: `04_Descarga_CHELSA_1981_2025.ipynb`. Ejecuta `descargar_chelsa_mensual.py`, que consulta el inventario, lee ventanas remotas y permite reanudar la descarga. Los archivos globales completos no se descargan.

Salidas: `02_DATOS/pr`, `02_DATOS/tas`, `02_DATOS/inventario_1981_2025.csv`, `02_DATOS/auditoria_diaria_2022_2025.csv` y `02_DATOS/resumen.json`.

Próximo paso: verificar escalas/unidades y elaborar composiciones mensuales ENOS con fase Neutral al centro, controlando la estacionalidad. El periodo disponible conjunto comprobado es 1981–2021. Completar hasta 2025 requiere una fuente adicional o esperar nuevas publicaciones; no se ha autorizado una sustitución automática.

Fuentes: https://www.chelsa-climate.org/datasets/chelsa_monthly y https://www.chelsa-climate.org/datasets/chelsa_daily. Inventario: https://os.unil.cloud.switch.ch/chelsa02/?prefix=chelsa/global/monthly/

Datos mensuales: Karger, D. N., Brun, P., y Zilker, F. (2025). CHELSA-monthly climate data at high resolution. EnviDat. https://doi.org/10.16904/envidat.686. Licencia CC0.

Control de muestra enero de 1981: ambos recortes tienen 91 × 91 píxeles, todos válidos, resolución 0.0083333333 grados y CRS EPSG:4326. En `pr` la escala es 1, unidad kg/m²/mes; valores regionales 7–95 mm/mes. En `tas` la escala es 0.1, unidad K: convertir los valores crudos con `T_C = raw * 0.1 - 273.15`; rango regional de la muestra 10.75–27.65 °C. Estos rangos incluyen el buffer y no son estadísticas municipales. Ambos archivos identifican ERA5 como forzante y model-output como tipo de producto.
