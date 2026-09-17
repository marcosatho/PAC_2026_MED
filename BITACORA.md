# Bitácora de acompañamiento PAC 2026

## 2026-09-10 — Corrección del plan de ataque

- Se revisó el alcance con el usuario: la primera hoja contiene observaciones someras de textos; las otras dos desarrollan productos visuales y contenido de 7.1 y 8.5.
- Error reconocido: la entrega anterior añadió una matriz de 17 frentes y porcentajes inferidos, dejando las tablas originales sin corregir. No utilizar esos porcentajes como avance verificado.
- Se preparó Plan_de_ataque_corregido.xlsx con las tres hojas originales reorganizadas: 4 textos, 6 productos para 7.1 y 7 temas para 8.5. Se aclararon redacción, campos, vacíos y tareas. No se verificaron externamente los textos ni la disponibilidad de datos.
- La versión ajustada anterior queda como antecedente, sustituida por la corregida para este trabajo.
- Ubicación acordada: G:/Mi unidad/2.Consultoria/01_PAC_MEDELLIN_2026/2.Ejecución/C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA/PAC_2026_MED_ACOMP_IA.
- Limitaciones: la tarea aún tiene su espacio de trabajo local; scripts anteriores contienen rutas locales. El borrador temático Markdown requiere revisión frente al alcance aclarado.
- Próximo paso: revisión del usuario sobre las tres tablas; después, lectura y comprobación de las fuentes seleccionadas.

## Regla de actualización

Al cerrar cada sesión, añadir fecha, trabajo realizado, decisiones, entregables vigentes, errores, limitaciones y próximos pasos. Actualizar ESTADO_PROYECTO.md cuando cambie el estado. Nunca registrar como comprobada una fuente que solo se ha propuesto.

## 2026-09-10 — Inicio de adquisición de datos C1/P1/7.1

- Se inspeccionó la estructura desde 2.Consultoria/01_PAC_MEDELLIN_2026 hasta C1/P1. Se identificó FIGURAS_BASE.ipynb en 02_DOCUMENTOS_EN_ELABORACION; se conserva intacto.
- Se preparó el proceso en P1/02_DOCUMENTOS_EN_ELABORACION/07_1_CLIMA_RELIEVE, con cuadernos, datos originales, preparados, previsualizaciones y metadatos.
- El usuario proporcionó el identificador Earth Engine thinkingcabezon. No se recibieron ni almacenaron contraseñas. La autorización se realiza en Colab.
- Se descargaron capas públicas oficiales del servicio VC_Limite_Politico_Admtivo de Medellín: 332 registros barrios/veredas, 23 comunas/corregimientos y 1 límite municipal. Se conservan originales Esri JSON EPSG:9377, metadatos, GeoPackage de siete capas y copias GeoJSON de intercambio.
- Se comprobaron conteos completos por identificadores, geometrías válidas, códigos sin duplicados y cobertura. Las subdivisiones difieren del límite en aproximadamente 2,5 m².
- Hallazgo: SN01 y SN02 no tienen nombre. El servicio contiene 16 comunas y 5 corregimientos con nombre más esos dos registros. Se conservaron y se registró la salvedad. La descripción del límite menciona 2014; no se certifica vigencia normativa 2026.
- Primer cuaderno autocontenido creado: 01_Obtencion_datos_CHIRPS_limites.ipynb. CHIRPS v3 Pentad, 1991–2020 inicial, contexto regional de 50 km, descarga anual de 72 bandas, cuadrícula original y copias EPSG:9377 por vecino más próximo. Previsualización con límite superpuesto, sin suavizado. El segundo cuaderno de análisis queda pendiente por indicación del usuario.
- Verificación: estructura y sintaxis del notebook; descarga real de límites; reproyección, promedio anual y tratamiento NoData probados con entrada sintética temporal. No se descargó CHIRPS ni se validó el acceso Earth Engine: falta ejecutar OAuth en Colab.
- Incidencias técnicas resueltas: faltaban librerías geoespaciales y el acceso de red local necesitó permiso. Se usó un entorno aislado local que no se traslada a Drive.
- Siguiente paso: abrir el notebook en Colab, autorizar Drive/Earth Engine con acceso a thinkingcabezon y ejecutar la descarga CHIRPS. Revisar códigos sin nombre antes de análisis territorial.

## 2026-09-10 — Segundo cuaderno de precipitación

- Se creó `02_Analisis_precipitacion_pixeles_gaussiano.ipynb` en `P1/02_DOCUMENTOS_EN_ELABORACION/07_1_CLIMA_RELIEVE/01_CUADERNOS`.
- El análisis lee las descargas anuales, comprueba huellas y 72 pentadas, identifica todos los píxeles que intersectan Medellín, calcula área y fracción dentro del municipio y clasifica completos/parciales/solo contacto.
- La comprobación con los datos reales produjo 5 píxeles completos, 19 parciales y 0 solo contacto; cobertura geométrica completa del municipio.
- Se generan dos figuras: píxeles originales con clasificación y comparación de valores originales frente a superficie gaussiana. También GeoPackage, CSV, GeoTIFF y metodología con parámetros.
- Filtro inicial: sigma 6 km, soporte de 12 km por eje, dominio regional antes del recorte, soporte NoData normalizado. La malla de representación es 1 km; no cambia la resolución efectiva CHIRPS (~5,6 km).
- Limitación: la prueba fue local usando los datos de Drive. El notebook debe ejecutarse en Colab para confirmar autorización, lectura de Drive y exportación final. La cifra de píxeles es verificable, no una conclusión climática.

## 2026-09-10 — Próxima fase: ENSO, series y promedio areal

- Se definió verificar primero la periodicidad real de las descargas CHIRPS. Para clasificar Niño, Niña y neutral mediante ONI y confirmación por periodo móvil se requiere conservar datos mensuales o agregar explícitamente las pentadas a meses; no basta el promedio anual ya resumido.
- Próximos productos: mapas de precipitación por fase Niño/Niña/neutral hasta 2025; serie temporal anual separada por fase; precipitación municipal ponderada por área con `P = sum(Pi * Ai) / sum(Ai)` usando `exact_extract`; y ficha de minería del paper de E. Aristizábal.
- Se reconoce una confusión de visualización: la figura válida usa la superficie gaussiana regional (`smooth`/`P_gaussiana_regional_9377.tif`) con el límite municipal superpuesto. El ráster municipal enmascarado puede mostrar bordes escalonados de `NoData`; no usarlo para diagnosticar cobertura del dato.
- Próxima tarea inmediata: auditar bandas, fechas, unidades y periodicidad de los archivos CHIRPS antes de implementar la clasificación ONI.
# Sesión 2026-09-13 — CHELSA

Se inició la descarga directa en Drive de 984 recortes mensuales CHELSA v2.1 (`pr`, `tas`) para 1981–2021. Objetivo solicitado: 1981–2025. El inventario público confirma 96 meses-variable sin publicar en 2022–2025. Auditoría diaria: `pr` ausente en esos cuatro años; `prec` y `tas` solo tienen 270 días de 2025. No mezclar `prec` sin corrección con `pr`. Scripts, notebook y detalle en `CHELSA_DESCARGA_ESTADO.md`; destino Drive: `07_1_CLIMA_RELIEVE/08_CHELSA`. Revisar `resumen.json` para el estado final de descarga.

## 2026-09-15 — Inventario del repositorio institucional de cambio climático

- Se revisó, con acceso autenticado de solo lectura, la carpeta de SharePoint/OneDrive `Doc_Cambio climático MED` de la Alcaldía de Medellín.
- La raíz contiene 33 elementos: 10 carpetas temáticas, 21 PDF, 1 DOCX y 1 ZIP.
- Se inventariaron las ramas de hojas de ruta; reportes CDP–ICLEI 2020–2024; planes de acción; aportes al Plan de Desarrollo; seguimiento y evaluación del PAC; inventarios INGEI 2015–2023; proyectos UCAP CAI-Pv y ZUAP; y documentos generales sobre PAC, vulnerabilidad, riesgos, cobeneficios y escenarios climáticos.
- Hallazgo principal para el componente climático: `25. Convenio Dagrd-SIATA Escenarios/Archivos_Soporte` contiene 12 grupos de información geoespacial y 146 elementos. Incluye precipitación y temperatura media mensual para 1990, 2030 y 2040; precipitación extrema; días sobre umbrales de temperatura máxima; susceptibilidad a incendios; probabilidad de precipitación mayor a 75 mm; índices de riesgo; T2, ETP, ETR y capas vectoriales de Medellín y Antioquia.
- Se creó `DICCIONARIO_DATOS_SHAREPOINT_CAMBIO_CLIMATICO_MED.md`, con inventario jerárquico, clasificación funcional, usos potenciales para el PAC 2026, alertas y campos recomendados para un catálogo formal.
- Limitaciones: el inventario se basa en nombres y metadatos visibles. No se inspeccionó todavía el contenido de `Directorio de documentos.docx`, `Estructura_Información.pdf`, `Diccionario Anexos.xlsx` ni del archivo `31. Islas de calor AMVA.zip` de 228 MB. Tampoco se confirmaron unidades, CRS, resolución, métodos o escenarios de los GeoTIFF.
- Control de calidad pendiente: comprobar si `18. Reporte INGEI 2021_Vfinal.pdf` y `22. Reporte 2021_INGEI_Vfinal.pdf` son duplicados reales mediante hash o comparación interna.
- Próximo paso recomendado: abrir primero los tres documentos de control y después auditar técnicamente las capas DAGRD–SIATA antes de incorporarlas a los análisis del numeral 7.1.

## 2026-09-15 — Corrección de composiciones CHELSA–ONI

- Se corrigió la interpretación temporal: el ONI clasifica meses, no años calendario. Se descartó como producto válido la versión intermedia que asignaba una sola fase a cada año.
- La versión vigente clasifica 492 meses de 1981–2021: 126 meses El Niño, 249 neutrales y 117 La Niña, después de exigir cinco temporadas móviles consecutivas para confirmar Niño o Niña.
- Para controlar la estacionalidad, primero se promedia por mes calendario dentro de cada fase. La precipitación anual equivalente es la suma de los doce campos mensuales condicionados; la temperatura media anual equivalente es su promedio.
- Se corrigió el desfase en la asignación de las temporadas móviles: DJF corresponde a enero, JFM a febrero y así sucesivamente hasta NDJ en diciembre.
- Se generó `CHELSA_ENSO_MESES_ANUALIZADO_1981_2021_MAGNA_SIRGAS_layout_v4.png`, con una barra de color por variable, fases en el margen izquierdo e isolíneas recortadas a Medellín.
- También se generó una versión nueva del mapa POMCA de temperatura con la paleta `RdYlBu_r` de CHELSA, sin sobrescribir el original: `23_temperatura_medellin_carta_paleta_CHELSA.png` y PDF.
