# Estado del acompañamiento PAC 2026

Actualizado: 2026-09-21.

## Relieve: DTM LiDAR oficial localizado

Se descargó el DTM-LiDAR oficial de Medellín de 2021, resolución de 1 m y escala 1:1.000, desde el Banco de Imágenes de GeoMedellín. El original está en `C:/Users/marco/Downloads/imagen960_DTM_2021_11_07.zip` y no se versiona en GitHub. El ráster usa `MAGNA_Medellín_Antioquia_2010` (EPSG:6257 / WKID 102768); los derivados deberán reproyectarse a EPSG:9377.

La licencia es Semilibre. El archivo original no se puede redistribuir ni comercializar y debe permanecer en el almacenamiento restringido del proyecto. Los productos derivados requieren citación del titular y el metadato solicita contacto previo. Antes de publicar mapas se debe verificar que el uso se encuentre cubierto por el contrato o convenio vigente con el Distrito.

Pendiente inmediato: almacenar el ZIP en Drive, extraerlo, verificar el GeoTIFF, recortarlo al límite municipal y producir elevación, pendiente, relieve sombreado, curvas de nivel, perfiles y estadísticas territoriales.

Actualización: el ZIP fue respaldado y verificado por SHA-256, el DTM fue extraído y se generó el derivado municipal `DTM_Medellin_2021_10m_EPSG9377.tif` (EPSG:9377, 10 m). Están disponibles dos previsualizaciones: relieve hipsométrico con curvas cada 100 m y pendiente clasificada. Pendientes: estadísticas por comuna/corregimiento, perfiles topográficos y definición editorial de las figuras finales.

## Repositorio institucional de cambio climático inventariado

Se revisó la carpeta compartida de SharePoint `Doc_Cambio climático MED` de la Alcaldía de Medellín. La raíz contiene 33 elementos: 10 carpetas, 21 PDF, 1 DOCX y 1 ZIP. El inventario jerárquico y la clasificación funcional están en [DICCIONARIO_DATOS_SHAREPOINT_CAMBIO_CLIMATICO_MED.md](DICCIONARIO_DATOS_SHAREPOINT_CAMBIO_CLIMATICO_MED.md).

La colección de mayor interés inmediato para 7.1 es `25. Convenio Dagrd-SIATA Escenarios/Archivos_Soporte`: contiene 12 grupos y 146 elementos geoespaciales asociados con precipitación, temperatura, extremos, incendios, índices de riesgo, evapotranspiración y escenarios 1990/2030/2040. Estos insumos están inventariados, pero todavía no validados técnicamente.

Pendientes de revisión interna: `Directorio de documentos.docx`, `Estructura_Información.pdf`, `Diccionario Anexos.xlsx` y `31. Islas de calor AMVA.zip`. Antes de utilizar las capas se deben confirmar unidades, CRS, resolución, NoData, cobertura, escenarios, metodología y licencia o restricciones de uso.

## Descarga CHELSA activa

Fuente seleccionada para P y T: CHELSA v2.1 mensual. Destino en Drive: `07_1_CLIMA_RELIEVE/08_CHELSA`. Periodo solicitado 1981–2025; inventario real disponible 1981–2021 (492 meses por variable). No hay `pr` corregida diaria en 2022–2025; `prec` sin corrección no se debe mezclar con `pr`. En 2025 `tas` y `prec` tienen 270 días publicados. Se preparó notebook reanudable y se inició descarga de 984 recortes. Ver `CHELSA_DESCARGA_ESTADO.md` y resumen de descarga en Drive. Temperatura cruda requiere escala 0.1 y conversión de K a °C, comprobado en muestra de enero de 1981.

## Alcance acordado

Acompañamiento del proyecto completo, comenzando por clima y desastres. El plan de ataque conserva tres funciones: observación preliminar de textos; desarrollo visual y de contenido de 7.1; desarrollo visual y de contenido de 8.5.

## Entrega vigente

[Plan de ataque corregido](outputs/01a089a5-63bb-7163-bf32-9b8c2e1100a4/Plan_de_ataque_corregido.xlsx).

La versión Plan_de_ataque_ajustado.xlsx con la matriz adicional de 17 frentes queda sustituida. Sus avances fueron inferidos y no representan progreso verificado.

## Pendientes

- Revisión del usuario de las tablas corregidas.
- Verificación de referencias, repositorios, versiones, cobertura y datos.
- Revisar el borrador temático 01_C1_Evidencia_Diagnostico_Prospectiva/_BORRADOR_SIN_NOMBRE.md; todavía no es una estructura aprobada ni tiene nombre definitivo.
- Adaptar rutas de los scripts antes de utilizarlos desde G:.

## Proceso activo C1 / P1 / 7.1

Ubicación: `../P1_Caracterizacion_Socioeconomica_Ambiental/02_DOCUMENTOS_EN_ELABORACION/07_1_CLIMA_RELIEVE`.

Primer cuaderno: [Obtención de datos y previsualización](../P1_Caracterizacion_Socioeconomica_Ambiental/02_DOCUMENTOS_EN_ELABORACION/07_1_CLIMA_RELIEVE/01_CUADERNOS/01_Obtencion_datos_CHIRPS_limites.ipynb). Proyecto Earth Engine: thinkingcabezon.

Límites oficiales descargados y comprobados en EPSG:9377. Hay 332 registros de barrios/veredas y 23 de comunas/corregimientos, incluidos SN01 y SN02 sin nombre. Se conserva el límite municipal y los metadatos originales. Consultar README del proceso antes de interpretar conteos administrativos.

CHIRPS v3 Pentad: descarga implementada para 1981–2025, pendiente de confirmar su ejecución final en Colab. El producto conserva 72 pentadas por año; antes del análisis ENSO debe verificarse si existen descargas mensuales o si las pentadas deben agregarse a meses. Buffer regional de 50 km; cuadrícula nativa y copias MAGNA-SIRGAS / Origen Nacional.

FIGURAS_BASE.ipynb existente permanece intacto. El segundo cuaderno de análisis existe y contiene las funciones de píxeles, promedio anual y superficie gaussiana. Los scripts antiguos aún dependen de rutas locales; el notebook usa la ruta de Drive en Colab.

Segundo cuaderno creado: `02_Analisis_precipitacion_pixeles_gaussiano.ipynb`. En la prueba local encontró 5 píxeles completos, 19 parciales y 0 de solo contacto. Genera la comparación de píxeles originales y superficie gaussiana, con σ=6 km y soporte de 12 km por eje. La ejecución en Colab sigue pendiente.

## Próxima fase: ENSO, series temporales y promedio areal

Antes de producir resultados condicionados por ENSO se debe auditar la estructura temporal de CHIRPS. La clasificación Niño/Niña/neutral mediante ONI y confirmación por periodo móvil requiere datos mensuales, o una agregación explícita de las pentadas a meses, hasta 2025.

Productos acordados:

1. Mapas comparables de precipitación para fases Niño, Niña y neutral.
2. Serie temporal anual de precipitación separada por fase ENSO.
3. Precipitación media municipal con `exact_extract` y ponderación por área: `P = sum(Pi * Ai) / sum(Ai)`.
4. Ficha de minería del paper de E. Aristizábal, con datos, método, resultados, escala y limitaciones.

Controles: no usar un promedio anual que haya perdido la información mensual para clasificar ENSO; conservar ONI, ventana móvil, meses incluidos, píxeles, áreas de intersección y fuentes. El mapa gaussiano de referencia debe usar el ráster regional completo y superponer el límite municipal.

## Seguimiento

Actualizar BITACORA.md en cada sesión y este documento cuando haya cambios. Comunicar errores y limitaciones de manera explícita. La carpeta acordada de acompañamiento es PAC_2026_MED_ACOMP_IA dentro de C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA.

## Relieve — estado vigente

El DTM LiDAR oficial de Medellín 2021 ya fue recortado al municipio, reproyectado a EPSG:9377 y preparado a 10 m para los productos derivados. Las figuras de publicación vigentes son las versiones `carta_v3` de elevación y pendiente, compuestas con el mismo esquema visual de los mapas POMCA (leyenda al norte, escala centrada, norte, límites políticos y fuente) y con un margen exterior de 750 m para evitar el recorte del límite municipal. El código reproducible es `12_RELIEVE_LAYOUT_POMCA.py`; los datos originales y derivados pesados permanecen fuera de GitHub por tamaño y restricciones de licencia.

## Amenazas — numeral 8.1, estado vigente

Se retomó el numeral 8.1 (Amenazas climáticas relevantes), hasta ahora un esqueleto en `Entregable_P1_v1_equipo_coordinacion.docx`: tabla introductoria con 8 familias de amenaza, subsecciones 8.1.2–8.1.10 vacías, y una taxonomía sin validar por el equipo (niveles causales + familias de riesgo, ya construida en `PAC_2026_clasificacion_amenazas.xlsx`). Dos preguntas quedan pendientes de Juliana/Marcos antes de redactar contenido que dependa de ellas: fuente oficial de zonificación de amenaza (Evaluación 2020 C40/Alcaldía vs. POT 2026) y adopción de esa taxonomía.

Subsección 8.1.2 (precipitación extrema y cambios proyectados) tiene un primer borrador de 500 palabras, lenguaje semitécnico con citas APA, basado en SIATA (2019, Convenio 4600082037) y Universidad de Antioquia (2026a/2026b, Contrato 4600105139 de 2025).

Los 146 archivos geoespaciales del Convenio DAGRD-SIATA (`Archivos_Soporte`) se descargaron completos desde SharePoint y quedaron en Drive, `P1_.../08_1_AMENAZAS/01_DAGRD_SIATA_ESCENARIOS/01_DATOS_ORIGINALES` (fuera de GitHub por tamaño, 116 MB). Los 6 ráster de `3_Precip_extrema` (P90/P95, 1990/2030/2040) ya están reproyectados de la proyección nativa del convenio (WRF, "PCS MAG Ant Medellín") a EPSG:9377.

Hallazgo metodológico relevante sobre el geodatabase de riesgo de la UdeA (`C4600105139_2025_CCMED.gdb.zip`): la amenaza climática (`H_precip`) es constante (valor máximo, 5 de 5) en las 24 comunas/corregimientos para precipitación extrema, porque Medellín queda cubierto por apenas ~4 píxeles del modelo climático. El "riesgo" que muestran esos mapas refleja casi exclusivamente exposición y vulnerabilidad, no variación real de la amenaza dentro de la ciudad — hay que tenerlo presente antes de citar esas categorías como si describieran diferencias de amenaza intraurbana.

Dos figuras nuevas, en el estilo cartográfico del proyecto y recortadas al polígono exacto del límite municipal (`all_touched=True`, sin huecos internos junto al borde): diferencia de precipitación extrema horaria 2040 vs. 2030 (P90/P95), y réplica de la comparación 1990/2030/2040 del informe DAGRD-SIATA para Medellín. Código en `P1_08_1_AMENAZAS/DAGRD_SIATA_ESCENARIOS/` de este repositorio.

Pendiente: subsecciones 8.1.3 en adelante con el mismo formato; resolver con el equipo las dos preguntas abiertas; revisar `Directorio de documentos.docx`, `Diccionario Anexos.xlsx` y `31. Islas de calor AMVA.zip` (todavía sin abrir, ver diccionario de datos de SharePoint).
