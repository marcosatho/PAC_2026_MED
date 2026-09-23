# Índice — todo lo usado/citado en 7.1 y 8.1 (PAC 2026)

Generado el 2026-09-22. Carpeta plana (sin subcarpetas), 41 archivos. Prefijo `7.1_` u `8.1_` indica a qué numeral pertenece cada archivo.

## Bibliografía en formato APA

### Con PDF fuente en esta carpeta

1. Sistema de Alerta Temprana de Medellín y el Valle de Aburrá [SIATA]. (2019). *Convenio interadministrativo para aunar esfuerzos para el monitoreo y modelación de variables hidrometeorológicas, geotécnicas y sísmicas, y el desarrollo de un sistema de información para el DAGRD: Componente 1, Monitoreo, modelación y comunicación* [Informe técnico, Convenio N.º 4600082037 de 2019]. Área Metropolitana del Valle de Aburrá; Departamento Administrativo de Gestión del Riesgo de Desastres de Medellín.
   → `DAGRED_SIATA_Escenarios_Clima.pdf` (PDF original) y `8.1_texto_extraido_SIATA2019.txt` (texto extraído)

2. Universidad de Antioquia. (2026a). *Actualización de la evaluación de riesgos climáticos e implementación de acciones para la gestión de emisiones y el ruido en Medellín: Escenarios de cambio climático* [Informe técnico, Contrato interadministrativo N.º 4600105139 de 2025]. Alcaldía de Medellín.
   → `UDEA_Escenarios cambio climático_CCMED.pdf` y `8.1_texto_extraido_UdeA2026a.txt`

3. Universidad de Antioquia. (2026b). *Actualización de la evaluación de riesgos climáticos e implementación de acciones para la gestión de emisiones y el ruido en Medellín: Resultados del documento técnico de revisión y actualización de metodología* [Informe técnico, Contrato interadministrativo N.º 4600105139 de 2025]. Alcaldía de Medellín.
   → `UDEA_Resultados metodologia_CCMED.pdf` y `8.1_texto_extraido_UdeA2026b.txt`

### Solo enlace (sin archivo descargable)

4. El Espectador. (2026, 21 de septiembre). *Regresa el racionamiento de agua en Medellín: conozca cómo funcionará*. https://www.elespectador.com/colombia/regresa-el-racionamiento-de-agua-en-medellin-conozca-como-funcionara/

5. Alcaldía de Medellín. (s. f.). *VC_Limite_Politico_Admtivo* [Conjunto de datos]. https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Limite_Politico_Admtivo/MapServer

6. UCSB Climate Hazards Center. (s. f.). *CHIRPS v3 Pentad* [Conjunto de datos]. Google Earth Engine. https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_PENTAD

7. Karger, D. N., Brun, P., y Zilker, F. (2025). *CHELSA-monthly climate data at high resolution* [Conjunto de datos]. EnviDat. https://doi.org/10.16904/envidat.686

8. Beck, H. E., McVicar, T. R., Vergopolan, N., Berg, A., Lutsko, N. J., Dufour, A., Zeng, Z., Jiang, X., van Dijk, A. I. J. M., y Miralles, D. G. (2023). High-resolution (1 km) Köppen-Geiger maps for 1901–2099 based on constrained CMIP6 projections. *Scientific Data, 10*, Artículo 724. https://doi.org/10.1038/s41597-023-02549-6

9. Área Metropolitana del Valle de Aburrá. (s. f.). *POMCA río Aburrá* [Servicio de mapas]. https://sim.metropol.gov.co/arcgis/rest/services/POMCA/POMCA/MapServer

10. Instituto Geográfico Agustín Codazzi [IGAC]. (s. f.). *Origen Nacional*. https://origen.igac.gov.co/herramientas.html

### Cita secundaria (sin documento original en nuestro poder)

11. Corantioquia y UNAL. (2017), como se citó en SIATA (2019).

12. Plan de Gestión Integral de la Biodiversidad y los Servicios Ecosistémicos [PGIBSE]. (2013), como se citó en SIATA (2019).

### Incompletas / pendientes

13. IDEAM y EPM — series climatológicas de estaciones, sin identificar la serie/estación específica.

14. Alcaldía de Medellín / AeroEstudios. (2021). *DTM-LiDAR de Medellín, 1 m* — dato oficial, licencia semilibre, sin URL pública.

---

## Contenido de la carpeta (41 archivos)

**8.1 — Amenazas climáticas**
- 3 PDF fuente completos + 3 `.txt` con el texto extraído para citar
- `8_1_6_final.md` — único texto redactado que se guardó como archivo (8.1.6, incluye el bloque de déficit alimentario; 8.1.2 nunca se guardó, solo quedó en el chat; 8.1.10 ya no existe como numeral aparte)
- `8.1_taxonomia_clasificacion_amenazas.xlsx`
- 8 scripts Python (`8.1_script_*.py`) que generaron las figuras
- 11 figuras PNG (`8.1_figura_*.png`): precipitación extrema (diferencia 2040-2030, réplica 1990/2030/2040, cambios proyectados), riesgo por escasez hídrica y por precipitación extrema por comuna, aridez en Antioquia y en corregimientos rurales de Medellín, extractos de SIATA (Fig. 4.10 acueducto, Fig. 4.11 hidroeléctricas), y el chequeo de susceptibilidad a incendios

**7.1 — Clima y relieve**
- 4 notebooks (`7.1_nb_*.ipynb`): CHIRPS/límites, análisis de precipitación, clasificación Köppen, descarga CHELSA
- `7.1_README.md`, `7.1_POMCA_INVENTARIO_DATOS.md`, `7.1_POMCA_CAPAS_CLIMATICAS_DESCARGADAS.md`, `7.1_CHELSA_DESCARGA_ESTADO.md`
- 6 scripts Python (`7.1_script_*.py`): Köppen, relieve DTM-LiDAR (layout y base), POMCA, descarga CHELSA

## Excluido intencionalmente (por tamaño, no por relevancia)

- Los 146 archivos ráster del convenio DAGRD-SIATA (116 MB) — quedan en Drive, `08_1_AMENAZAS/01_DATOS_ORIGINALES`.
- El geodatabase de riesgo de la UdeA `C4600105139_2025_CCMED.gdb.zip` (158 MB) — queda en `C:\Users\marco\Downloads` (ya estaba ahí antes de esta carpeta).
- El DTM-LiDAR original de Medellín (paquete pesado, licencia restringida) — queda en Drive.
- Avísame si de todos modos quieres que copie alguno de estos aquí.
