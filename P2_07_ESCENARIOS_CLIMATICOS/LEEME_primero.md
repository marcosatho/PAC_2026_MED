# P2 · Prospectiva climática — qué se hizo y qué sigue (26 de octubre de 2026)

**Documento:** `P2_Prospectiva_climatica_borrador_v0.1.docx` (capítulo 7, borrador estructural; 20 figuras, 10 tablas, formato del P1).
**Carpetas:** `figuras/` (PNG), `codigo/` (programas), `datos_derivados/` (cifras calculadas).

## Hallazgos que conviene leer primero

1. **El texto previo del equipo no se sostiene en dos puntos** (tabla 7.7 del documento).
   - «Aumento de precipitación de 10–20 % para el AMVA en 2021–2040»: el mapa del Ideam da **0–10 %** sobre Medellín; 10–20 % es la clase del centro de la región Andina en general. La temperatura (1–1,5 °C) sí coincide.
   - «Proyección sustancialmente más alta que la del PAC vigente»: para temperatura, **no** (SIATA +1,04 °C hacia 2030–2040; Ideam 1–1,5 °C hacia 2021–2040). Las diferencias reales son el escenario (RCP 4,5 frente a cuatro SSP), el número de modelos (1 frente a 19 o 25) y 2050 en adelante.
   - Las cifras 0,86 °C y 4,7 % de Antioquia no están en la ficha de 2015 (da 0,8 °C y 4,88 %); el Anexo 14 las atribuye a la NDC 2020, no a la Tercera Comunicación. **Por verificar.**
   - Errata en el Anexo 14 (p. 21): dice «década 1940–1950»; es 2040–2050.
2. **La lluvia mensual de los ráster del SIATA no sirve para cifras**: cada década es un solo año simulado (junio pasa de 105 a 19 mm; septiembre, de 180 a 410 mm). Se usó solo el cambio de temperatura, de lluvia extrema, de días calurosos y de índices de amenaza. El informe lo advierte (pp. 22-23, 31, 48).
3. **Los ráster de temperatura del SIATA están en kelvin** (282–300), aunque su documento de estructura dice °C. Al convertir, el cambio coincide con lo que dice el informe (+1,05 y +1,2 °C): la conversión es correcta.
4. **Los ráster del SIATA ya estaban en el Drive del P1** (`08_1_AMENAZAS/01_DAGRD_SIATA_ESCENARIOS/01_DATOS_ORIGINALES/Archivos_Soporte`); por eso hay mapas propios de 2030 y 2040 (el P1 solo mapeó la referencia 1990–2000 de los días calurosos).
5. **La geodatabase de la UdeA** (zip en Descargas) trae 75 ráster; los climáticos son solo **SSP3-7.0, 2021–2050, cuatro modelos**. Entre modelos, la lluvia de los días muy lluviosos va de −9 a +151 mm al año en las celdas de Medellín.

## Decisiones que tomé sin consultarte
- Capítulo titulado «7. Escenarios climáticos que sustentan las trayectorias» (el título de tu texto), con numeración propia de figuras y tablas (7.n).
- Usé el borrador del P1 (`PAC_P1_BORRADOR_RT (2).docx`) como **plantilla de estilos**; no lo modifiqué. Todo se guardó en Descargas, nada dentro de las carpetas del PAC.
- Para los mapas instalé en una carpeta temporal las librerías de gráficos (matplotlib, shapely, pyproj, pyshp). No son datos.
- Extraje la geodatabase de la UdeA del zip a una carpeta temporal solo para leerla.
- Del OneDrive de la Alcaldía solo listé las carpetas (lectura, sin descargas). El correo «Informes UdeA» lo leí solo en su primer mensaje.
- Los mapas del Ideam (2024) son **lecturas de clases de color** de sus figuras publicadas (Anexo A del documento): sirven como orden de magnitud, no como dato.
- La valoración de confianza de la tabla 7.6 es mía (acuerdo entre estudios y entre modelos).

## Lo que no hice
- No leí completos: el Anexo 1 de Meteorología de la UdeA (2026d), las secciones de 2026b, 2026c y 2026g fuera de las páginas citadas, ni la nota técnica IDEAM-2023-001 (solo su resumen: es una metodología alternativa con temperatura media y 33 modelos).
- No descargué nada. Los datos del Ideam (visor), la Tercera Comunicación y NEX-GDDP-CMIP6 están en la tabla 7.8 con enlace.
- No pude abrir el Word en una aplicación que pagine (no hay Word ni LibreOffice accesibles sin pedir permisos); la estructura se verificó por código. **Conviene abrirlo y revisar saltos de página y tamaño de figuras.**

## Pendientes para la mañana (tabla 7.9)
1. Descargar las capas de Antioquia del visor del Ideam y reemplazar la lectura de mapas.
2. Pedir a la UdeA los ráster de los demás SSP y de 2071–2100.
3. Verificar 0,86 °C y 4,7 % en la Tercera Comunicación (2017) y la NDC (2020).
4. Decidir el escenario central del PAC (SSP2-4.5 o SSP3-7.0).
5. Dar letra a la geodatabase de la UdeA en la lista de referencias del P1 (la «h» ya está tomada).
