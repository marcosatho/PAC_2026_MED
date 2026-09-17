# Capas climáticas del POMCA río Aburrá

Se descargaron las capas 22 (evapotranspiración), 23 (temperatura) y 24 (precipitación) desde el servicio ArcGIS REST del Área Metropolitana del Valle de Aburrá.

Cada capa se entrega como:

- imagen PNG renderizada por el servidor;
- archivo mundial PGW para su ubicación espacial;
- archivo PRJ con EPSG:21897;
- metadatos JSON de la capa.

## Advertencia de uso

El servicio es un `MapServer` y publica estas tres fuentes como `Raster Layer`. No tiene habilitado WCS y, al solicitar TIFF, devuelve de todas formas una imagen PNG. Por ello, los archivos descargados son cartografía georreferenciada para consulta visual, no rásteres numéricos originales. No deben emplearse para calcular promedios de precipitación, temperatura o evapotranspiración.

Para obtener los valores numéricos originales se requiere la geodatabase o el anexo climático citado por el POMCA: `Anexos_Diagnostico/Anexo8_Caract_FisicoBiotica/1Clima`.

## Servicio

`https://sim.metropol.gov.co/arcgis/rest/services/POMCA/POMCA/MapServer`
