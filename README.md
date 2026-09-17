# PAC Medellin 2026

Repositorio de trazabilidad tecnica del proyecto **PAC Medellin 2026**. Contiene
codigo, cuadernos, documentacion metodologica, bitacora, metadatos y algunas
previsualizaciones necesarias para reconstruir los analisis.

## Alcance

El repositorio no funciona como almacen principal de datos. Los archivos
originales y los productos geoespaciales pesados se conservan en Google Drive o
se descargan nuevamente desde sus fuentes oficiales. GitHub conserva la logica
de adquisicion, procesamiento, analisis y visualizacion.

## Contenido principal

- `BITACORA.md`: registro acumulado de decisiones y avances.
- `ESTADO_PROYECTO.md`: estado operativo y tareas pendientes.
- `P1_07_1_CLIMA_RELIEVE/`: desarrollo del numeral 7.1, incluyendo CHIRPS,
  POMCA, Koppen-Geiger, CHELSA y clasificacion de fases del ENOS.
- `01_C1_Evidencia_Diagnostico_Prospectiva/`: borradores conceptuales del
  componente 1.
- Scripts y cuadernos ubicados en la raiz: versiones de trabajo que documentan
  la evolucion de los procedimientos.

## Datos no versionados

Entre las fuentes utilizadas se encuentran:

- CHIRPS para precipitacion.
- CHELSA v2.1 para precipitacion y temperatura.
- Indice ONI de NOAA/CPC para clasificar las fases del ENOS.
- Capas climaticas del POMCA del rio Aburra.
- Limites politico-administrativos oficiales de Medellin.
- Clasificacion climatica Koppen-Geiger.

Los inventarios, enlaces, fechas de consulta y procedimientos de descarga se
documentan en los archivos Markdown y en los metadatos del proyecto. Las rutas
locales no deben codificarse de manera permanente en los scripts.

## Recuperacion del proyecto

1. Clonar este repositorio.
2. Crear el entorno de Python requerido.
3. Recuperar los datos desde Google Drive o ejecutar los scripts de descarga.
4. Configurar las rutas locales sin registrar credenciales en Git.
5. Ejecutar los cuadernos en el orden indicado en cada subcarpeta.

## Seguridad

No deben incorporarse contrasenas, tokens, cuentas de servicio, credenciales de
Google Earth Engine ni documentos con informacion reservada. El repositorio debe
mantenerse privado mientras se desarrolla la consultoria.

