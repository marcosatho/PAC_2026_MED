# C1 / P1 / 7.1 — Datos, mapas y gráficas

## Ubicación

`2.Consultoria/01_PAC_MEDELLIN_2026/2.Ejecución/C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA/P1_Caracterizacion_Socioeconomica_Ambiental/02_DOCUMENTOS_EN_ELABORACION/07_1_CLIMA_RELIEVE`

Esta ubicación se integra con las carpetas existentes de P1. El cuaderno previo `FIGURAS_BASE.ipynb` permanece intacto. El seguimiento general continúa en `PAC_2026_MED_ACOMP_IA`, al nivel de C1.

## Organización

- `01_CUADERNOS`: primer cuaderno autocontenido para Colab.
- `01_CUADERNOS`: cuaderno 01 para descarga y cuaderno 02 para análisis de precipitación.
- `02_DATOS_ORIGINALES`: capturas del servicio oficial y CHIRPS en cuadrícula nativa, organizados por fecha.
- `03_DATOS_PREPARADOS`: GeoPackage EPSG:9377, copias GeoJSON de intercambio EPSG:4326 y rásteres reproyectados.
- `04_PREVISUALIZACIONES`: controles básicos, no figuras definitivas.
- `05_METADATOS`: fuentes, conteos, fechas, configuración y huellas SHA256.

## Cómo ejecutar

Abrir `01_CUADERNOS/01_Obtencion_datos_CHIRPS_limites.ipynb` desde Drive con Google Colaboratory y ejecutar de arriba abajo. Autorizar Drive y Earth Engine mediante Google. Proyecto configurado: `thinkingcabezon`. No introducir contraseñas en el cuaderno ni en la conversación.

El cuaderno verifica las capas ya descargadas y descarga CHIRPS para 1981–2025. El producto es pentadal: 72 bandas por año. Antes del análisis ENSO se debe comprobar si existen archivos mensuales o si las pentadas se agregarán explícitamente a meses. El buffer regional inicial es 50 km. Los datos se guardan directamente en esta estructura del proyecto.

Después de ejecutar el cuaderno 01, abrir `01_CUADERNOS/02_Analisis_precipitacion_pixeles_gaussiano.ipynb`. Este segundo cuaderno reutiliza las descargas, clasifica los 5 píxeles completos y 19 parciales que intersectan Medellín en la comprobación actual, y genera la comparación original/suavizada. La cifra se recalcula cada vez que cambian el periodo o el límite.

## Referencia espacial

MAGNA-SIRGAS / Origen Nacional, EPSG:9377, para mapas y archivos preparados. Los originales CHIRPS conservan su cuadrícula geográfica de 0,05°. El cambio de proyección usa vecino más próximo, no implica una mejora de resolución. La previsualización superpone Medellín sobre la cuadrícula con contexto regional.

## Alcance y pendientes

El primer cuaderno descarga y realiza controles básicos. El segundo cuaderno realiza el análisis de píxeles, promedio anual y superficie gaussiana. La siguiente fase añadirá mapas y series temporales condicionados por ENSO y el promedio areal ponderado.

La descarga de CHIRPS y la autorización de `thinkingcabezon` deben ejecutarse en Colab. Tener el ID no equivale a disponer de acceso autenticado.

La capa oficial del límite tiene una descripción que menciona 2014; se conserva el texto del servicio y sus fechas. Se utiliza como geometría publicada por la Alcaldía, sin certificar una actualización normativa de 2026.

## Resultado de la primera descarga, 2026-09-10

Se descargaron 1 límite municipal, 332 registros de barrios/veredas y 23 de comunas/corregimientos. Las geometrías son válidas. La diferencia de cobertura de las dos subdivisiones respecto al límite es aproximadamente 2,5 m², calculada en EPSG:9377.

La capa de comunas/corregimientos contiene 16 comunas con nombre, 5 corregimientos con nombre y dos registros sin nombre: SN01 (subtipo comuna) y SN02 (subtipo corregimiento). Las capas separadas por subtipo conservan esos registros, de modo que contienen 17 y 6 entidades respectivamente. No interpretar esos conteos como número de unidades administrativas reconocidas. Revisar los registros sin nombre antes de hacer estadísticas territoriales.

Los 332 registros se distribuyen en 271 del subtipo barrio y 61 del subtipo vereda; son conteos del servicio descargado, no una certificación administrativa.

## Fuentes

- [Servicio oficial de Medellín](https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Limite_Politico_Admtivo/MapServer): capas 0, 1 y 2.
- [CHIRPS v3 Pentad](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_PENTAD): precipitación en mm/pentada; resolución 0,05°.
- [IGAC: Origen Nacional](https://origen.igac.gov.co/herramientas.html).

## Próxima tarea acordada

1. Auditar los archivos CHIRPS descargados: bandas, fechas, unidades y periodicidad real.
2. Preparar la tabla ONI con clasificación Niño, Niña y neutral, confirmada mediante periodo móvil y extendida hasta 2025.
3. Generar mapas comparables y la serie temporal anual por fase ENSO.
4. Calcular la precipitación municipal con `exact_extract`: `P = sum(Pi * Ai) / sum(Ai)`.
5. Crear una ficha de minería del paper de E. Aristizábal y verificar cualquier hallazgo antes de incorporarlo al texto.
