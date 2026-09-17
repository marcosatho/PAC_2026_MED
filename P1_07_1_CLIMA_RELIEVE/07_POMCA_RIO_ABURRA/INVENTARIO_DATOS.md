# Inventario preliminar de datos - POMCA río Aburrá

## Fuente revisada

- Actualización del POMCA del río Aburrá, fase de diagnóstico, tomo I de caracterización básica y del medio físico-biótico (documento de 2018 con resultados técnicos preparados en 2016).
- Copia oficial localizada en el portal de Cornare.

## Régimen de lluvias

El numeral 2.3.1.8.1 describe un régimen de precipitación bimodal. El primer periodo lluvioso se extiende aproximadamente desde comienzos de marzo hasta finales de junio y el segundo desde mediados de septiembre hasta finales de noviembre. Los máximos señalados se presentan en abril-mayo y septiembre-noviembre, con el mayor valor mensual generalmente en octubre. Los mínimos se presentan en enero y julio.

El documento emplea tres estaciones como referencias de las partes alta, media y baja de la cuenca:

- La Salada (2701526): 2.546,1 mm/año.
- Aeropuerto Olaya Herrera (2701507): 1.734,6 mm/año.
- Hacienda El Progreso (2701515): 1.952,6 mm/año.

La Tabla 13 inventaría 82 estaciones. Para la distribución espacial se usaron 81 estaciones pluviométricas y climatológicas, después de excluir la estación Meseta San Pedro (2701080) por un cambio abrupto en la curva de dobles masas. Se generaron isoyetas anuales y mensuales mediante kriging y un ráster de 200 x 200 m. El promedio estimado para toda la cuenca fue 2.148,8 mm/año.

## ENSO

El POMCA analizó la precipitación mensual frente a ONI, SOI y MEI. Reclasificó los registros mensuales por fases El Niño, La Niña y neutral, y produjo promedios mensuales multianuales por estación. Esta metodología es directamente comparable con la tarea prevista para CHIRPS, aunque el periodo del POMCA llega aproximadamente hasta 2015.

## Bases y anexos mencionados

El informe declara la existencia de:

- Series climatológicas originales suministradas por IDEAM y EPM.
- Series ajustadas después de controles de consistencia y homogeneidad.
- Resultados de dobles masas, diagramas de caja, pruebas Pettitt y Mann-Kendall.
- Histogramas mensuales multianuales por estación.
- Carpeta `Anexos_Diagnostico/Anexo8_Caract_FisicoBiotica/1Clima`.
- Geodatabase de cartografía básica y salidas cartográficas temáticas.

## Disponibilidad pública comprobada

- El portal principal de Cornare publica los tomos del POMCA en PDF.
- La página de información cartográfica publica para el río Aburrá un archivo RAR de zonificación. Al inspeccionarlo se encontraron únicamente un KML (`doc.kml`) y un archivo de estilo XSL; no contiene la geodatabase climática.
- No se encontró en las páginas públicas revisadas un enlace directo al `Anexo8_Caract_FisicoBiotica/1Clima`, a las series mensuales originales o a los rásteres de precipitación de 200 m.

## Datos recuperables del PDF

La Tabla 13 se extrajo a `tabla_13_inventario_estaciones_precipitacion.csv`; contiene código, nombre, tipo, periodo disponible, cantidad de datos mensuales y faltantes para 82 estaciones. La Tabla 19 contiene precipitación media multianual para 68 subcuencas del POMCA, con doce valores mensuales y el total anual; se extrajo a `tabla_19_precipitacion_mensual_subcuencas.csv` para control y comparación.

## Limitaciones

- Los valores del informe son históricos y no llegan a 2025.
- La tabla por subcuencas es un producto interpolado, no la serie temporal mensual original de cada estación.
- Antes de reutilizar las capas deben verificarse sistema de coordenadas, metadatos, periodo de referencia y método de interpolación.
- Para obtener los anexos originales probablemente será necesario solicitarlos a AMVA, Corantioquia, Cornare o al contratista del POMCA.
