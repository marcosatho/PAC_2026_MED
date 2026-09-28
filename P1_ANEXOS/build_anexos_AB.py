# -*- coding: utf-8 -*-
"""Build Anexo A (Matriz de fuentes y trazabilidad) and Anexo B (Matriz de variables e indicadores) of the
master P1 document, sections 15.A and 15.B, which existed only as empty placeholders. Source: this project's
own INDICE_REFERENCIAS.md (38 APA entries + 3 secondary-citation + 3 incomplete/pending + 2 unread), and the
variables actually built and used across numerals 7.1, 8.1, 8.5 and 8.6 this session.

usage: build_anexos_AB.py <out.xlsx>"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = sys.argv[1]
P1 = "Producto 1 (C1 — Evidencia diagnóstico y prospectiva)"

# ---------------------------------------------------------------------------------------------------------------
# Anexo A: ID, Numeral(es), Año, Tipo, Autores/Institución, Título, Ámbito territorial, Aporte, Veredicto de
# relevancia, Estado de uso, Producto del contrato, DOI/URL
A_HEAD = ["ID", "Numeral(es)", "Año", "Tipo de fuente", "Autores / institución", "Título", "Ámbito territorial",
          "Aporte", "Veredicto de relevancia", "Estado de uso", "Producto del contrato", "DOI / URL"]
A = [
["F01", "8.1.2", 2019, "Informe técnico", "SIATA / AMVA / DAGRD",
 "Convenio interadministrativo 4600082037: monitoreo y modelación hidrometeorológica, geotécnica y sísmica",
 "Valle de Aburrá", "Escenarios de precipitación y temperatura 1990/2030/2040; días de calor sobre umbral; capas de riesgo",
 "Alta: fuente primaria del convenio DAGRD-SIATA, usada en varios numerales", "Incluida", P1, "PDF en carpeta de referencias"],
["F02", "8.1.2, 8.1.5", 2026, "Informe técnico", "Universidad de Antioquia",
 "Escenarios de cambio climático (Contrato 4600105139 de 2025)", "Medellín",
 "Proyecciones climáticas y geodatabase de riesgo (H×E×V) por comuna/corregimiento",
 "Alta: única fuente de proyección climática municipal", "Incluida", P1, "PDF en carpeta de referencias"],
["F03", "8.1.2, 8.1.5, 8.1.7", 2026, "Informe técnico", "Universidad de Antioquia",
 "Resultados del documento técnico de revisión y actualización de metodología (Contrato 4600105139 de 2025)", "Medellín",
 "Metodología del geodatabase de riesgo; explica por qué la amenaza climática es constante intramunicipal",
 "Alta: aclara una limitación metodológica citada en el texto", "Incluida", P1, "PDF en carpeta de referencias"],
["F04", "8.1.3, 8.1.4, 8.1.5", 2026, "Informe técnico", "Departamento Administrativo de Planeación [DAP] / Universidad EAFIT",
 "Anexo 16. Estudios básicos de amenaza por movimientos en masa, inundación y avenidas torrenciales (POT Distrital)", "Medellín",
 "Áreas oficiales de amenaza alta/media/baja por comuna y corregimiento, base de las Figuras 1 y 2 de 8.1.5",
 "Alta: fuente oficial de zonificación de amenaza del POT 2026", "Incluida", P1,
 "medellin.gov.co/.../Anexo-15_InformeEBA-1.pdf"],
["F05", "8.1.3, 8.1.4, 8.1.5", 2026, "Cartografía oficial", "Departamento Administrativo de Planeación [DAP]",
 "Cartografía 1 (láminas 1 a 10 de 37, revisión de mediano plazo del POT)", "Medellín",
 "Láminas de amenaza (inundación, avenida torrencial, movimientos en masa) vectorizadas para los mapas de 8.1",
 "Alta, con reserva: no son capas oficiales georreferenciadas, se leyeron de imágenes PDF (declarado en los pies de figura)",
 "Incluida", P1, "medellin.gov.co/.../que-es-pot/"],
["F06", "7.1.5, 8.1.5, 8.5.1, 8.6", 2026, "Artículo científico", "Aristizábal, E. V., Sanchez, O. I. y Korup, O.",
 "Landslide timing and rainfall regimes in a rapidly urbanizing tropical mountain valley in Colombia (Natural Hazards)",
 "Valle de Aburrá", "Relación lluvia-deslizamiento por fase ENSO 1950–2023; su Figura 3 se tradujo al español para 8.5.1",
 "Alta: única fuente con esa relación a escala del valle; acceso abierto CC BY 4.0", "Incluida", P1,
 "doi.org/10.1007/s11069-026-08028-6"],
["F07", "8.1.7", 2018, "Tesis de maestría", "Guzmán Echavarría, G.",
 "Análisis de la influencia del diseño urbano en la meteorología del Valle de Aburrá", "Valle de Aburrá",
 "Temperatura de superficie por comuna/corregimiento/barrio; base del paquete de islas de calor AMVA",
 "Alta: única fuente con temperatura de superficie a escala de barrio", "Incluida", P1,
 "redcol.minciencias.gov.co (UNACIONAL2_f43ac94cc837366e182f7cef31609571)"],
["F08", "8.1.9, 8.5", 2021, "Documento técnico", "Secretaría de Salud de Medellín",
 "Plan de adaptación en salud al cambio y variabilidad climática, Medellín 2020-2050: Tomo I", "Medellín",
 "Casos de dengue 2000–2018; Tablas 13–15 de eventos DAGRD por comuna 2005–2018, base de las Figuras 1 y 2 de 8.5.1",
 "Alta: única fuente con eventos DAGRD desagregados por comuna 2005–2018", "Incluida", P1,
 "medellin.gov.co/.../PASCCM-Tomo-I..."],
["F09", "8.1.9", "s. f.", "Documento técnico", "Secretaría de Salud de Medellín",
 "Plan de adaptación en salud al cambio y variabilidad climática, Medellín 2020-2050: Tomo II", "Medellín",
 "Tabla 9 de vulnerabilidad y riesgo en salud por comuna", "Alta", "Incluida", P1,
 "medellin.gov.co/.../PASCCM-Tomo-II..."],
["F10", "8.1.6", 2026, "Noticia institucional", "El Espectador",
 "Regresa el racionamiento de agua en Medellín: conozca cómo funcionará", "Medellín",
 "Evento reciente de racionamiento citado en 8.1.6 y 8.5.4", "Media: prensa, un solo evento puntual", "Solo enlace", P1,
 "elespectador.com/.../regresa-el-racionamiento..."],
["F11", "7.1, 8.1, 8.5", "s. f.", "Conjunto de datos oficial", "Alcaldía de Medellín",
 "VC_Limite_Politico_Admtivo (límites de comunas, corregimientos, barrios y veredas)", "Medellín",
 "Base geoespacial de todos los mapas por comuna/corregimiento del proyecto", "Alta: insumo geoespacial transversal",
 "Incluida", P1, "medellin.gov.co/servidormapas/.../VC_Limite_Politico_Admtivo"],
["F12", "7.1", "s. f.", "Conjunto de datos", "UCSB Climate Hazards Center",
 "CHIRPS v3 Pentad", "Global / Medellín", "Precipitación pentadal para el análisis ENSO de 7.1.5",
 "Alta", "Incluida", P1, "Google Earth Engine, UCSB-CHC_CHIRPS_V3_PENTAD"],
["F13", "7.1", 2025, "Conjunto de datos", "Karger, D. N., Brun, P. y Zilker, F.",
 "CHELSA — monthly climate data at high resolution", "Global / Medellín", "Precipitación y temperatura mensual para 7.1",
 "Alta", "Incluida", P1, "doi.org/10.16904/envidat.686"],
["F14", "7.1.3", 2023, "Artículo científico", "Beck, H. E. et al.",
 "High-resolution (1 km) Köppen-Geiger maps for 1901–2099 based on constrained CMIP6 projections",
 "Global / Medellín", "Clasificación climática de Köppen-Geiger de 7.1.3", "Alta", "Incluida", P1,
 "doi.org/10.1038/s41597-023-02549-6"],
["F15", "7.1", "s. f.", "Servicio de mapas", "Área Metropolitana del Valle de Aburrá",
 "POMCA río Aburrá", "Valle de Aburrá", "Caracterización de amenazas del POMCA usada en 7.1 y 8.1", "Alta",
 "Incluida", P1, "sim.metropol.gov.co/arcgis/.../POMCA/MapServer"],
["F16", "Todos", "s. f.", "Referencia técnica", "Instituto Geográfico Agustín Codazzi [IGAC]",
 "Origen Nacional (EPSG:9377)", "Colombia", "Sistema de referencia de todos los mapas del proyecto", "Alta: estándar cartográfico obligatorio",
 "Incluida", P1, "origen.igac.gov.co/herramientas.html"],
["F17", "8.1.9", 2017, "Cita secundaria", "Corantioquia y UNAL",
 "(citado en SIATA, 2019)", "Valle de Aburrá", "Citada dentro del convenio DAGRD-SIATA", "Media: sin documento original",
 "Cita secundaria", P1, "No aplica"],
["F18", "7.2", 2013, "Cita secundaria", "Plan de Gestión Integral de la Biodiversidad y los Servicios Ecosistémicos [PGIBSE]",
 "(citado en SIATA, 2019)", "Valle de Aburrá", "Citada dentro del convenio DAGRD-SIATA", "Media: sin documento original",
 "Cita secundaria", P1, "No aplica"],
["F19", "8.1.9", 2018, "Cita secundaria", "Área Metropolitana del Valle de Aburrá [AMVA]",
 "(citado en Secretaría de Salud de Medellín, 2021)", "Valle de Aburrá",
 "Proyecciones climáticas usadas en 8.1.9.2", "Media: sin documento original", "Cita secundaria", P1, "No aplica"],
["F20", "8.1.7", "s. f.", "Pendiente", "IDEAM y EPM",
 "Series climatológicas de estaciones (sin identificar estación)", "Medellín",
 "Pendiente original; resuelto parcialmente por F31–F34 (Olaya Herrera, en 8.5.4, no en 8.1.7)",
 "Baja hasta identificar la estación; ya resuelta para 8.5", "Pendiente", P1, "No aplica"],
["F21", "7.1", 2021, "Dato oficial", "Alcaldía de Medellín / AeroEstudios",
 "DTM-LiDAR de Medellín, 1 m", "Medellín", "Modelo digital del terreno para el relieve de 7.1.2",
 "Alta, licencia semilibre: requiere citación del titular y verificar cobertura contractual antes de publicar mapas",
 "Incluida (con restricción de licencia)", P1, "Sin URL pública; GeoMedellín"],
["F22", "8.1.7", "s. f.", "Pendiente de confirmar autoría", "Plan de Acción para el Cambio y la Variabilidad Climática del Valle de Aburrá",
 "Paquete \"Isla de calor\" (temperatura de superficie Landsat, 30 m)", "Valle de Aburrá",
 "Insumo raster de las Figuras 2 y 3 de 8.1.7, vía Guzmán Echavarría (2018)",
 "Alta, con reserva de autoría formal del paquete", "Incluida (autoría por confirmar)", P1,
 "Carpeta SharePoint Doc_Cambio climático MED"],
["F23", "8.5.1", "s. f.", "Base de datos", "Geohazards",
 "Inventario de movimientos en masa de Antioquia", "Antioquia / Medellín",
 "1.082 registros de Medellín con fecha, ubicación y fallecidos, 1871–2026; base de las Figuras 4 y 5 de 8.5.1",
 "Alta: única serie histórica de deslizamientos con fallecidos a este plazo", "Incluida", P1,
 "geohazards.com.co/#/geovisor/inventarios-geohazards"],
["F24", "8.5.1, 8.5.2, 8.5.3", 2026, "Base de datos oficial", "Alcaldía de Medellín",
 "Histórico de emergencias (capa «emergencias», SIRMED)", "Medellín",
 "44.317 eventos 2004–2026 (completo desde 2021); base de la Figura 3 y de los mapas de inundación de 8.5.2",
 "Alta: única serie de emergencias reciente y con volumen suficiente para mensualizar", "Incluida", P1,
 "medellin.gov.co/sirmed/historico-emergencias"],
["F25", "8.5.5", 2023, "Conjunto de datos oficial", "Unidad Nacional para la Gestión del Riesgo de Desastres [UNGRD]",
 "Emergencias UNGRD, 2019-2022", "Medellín", "Base de la Tabla 1 de 8.5.5 (fallecidos, heridos, viviendas)",
 "Alta: única fuente con pérdidas humanas y materiales estructurada por evento", "Incluida", P1,
 "datos.gov.co/d/wwkg-r6te"],
["F26", "8.5.1, 8.5.5", "s. f.", "Base de datos", "Oficina de las Naciones Unidas para la Reducción del Riesgo de Desastres [UNDRR]",
 "DesInventar Sendai: base de datos de Colombia", "Medellín",
 "737 eventos 1921–2017; única fuente con algún dato de pérdidas económicas (79 eventos, solo hasta 1996)",
 "Media-alta: el dato económico es incompleto y desactualizado, pero es la única fuente que existe", "Incluida", P1,
 "desinventar.net/DesInventar/main.jsp?countrycode=col"],
["F27", "8.5.1, 8.5.2", "s. f.", "Serie de referencia", "National Oceanic and Atmospheric Administration [NOAA]",
 "Oceanic Niño Index (ONI)", "Global", "Clasificación de El Niño y La Niña de todas las figuras por fase del proyecto",
 "Alta: estándar internacional para clasificar ENSO", "Incluida", P1, "psl.noaa.gov/data/timeseries/month/"],
["F28", "8.5.1", "2008, 2014, 2022, 2024", "Prensa / literatura técnica", "Ortiz Jiménez; Ospina Zapata; Aristizábal; Alcaldía de Medellín",
 "Notas de prensa e informes usados para verificar cifras de tragedias (Media Luna, Villatina, Alto Verde, El Socorro)",
 "Medellín", "Corrección de las cifras de fallecidos del inventario Geohazards", "Alta para el fin puntual de verificar cifras",
 "Incluida", P1, "Enlaces completos en 8.5_texto_8_5.md"],
["F29", "8.5.4", "s. f.", "Base de datos horaria", "Instituto de Hidrología, Meteorología y Estudios Ambientales [IDEAM]",
 "Temperatura ambiente del aire", "Medellín (Aeropuerto Olaya Herrera)",
 "Serie horaria 2014–2026 usada como referencia de control de calidad de las Figuras 9 y 10", "Alta", "Incluida", P1,
 "datos.gov.co/d/sbwg-7ju4"],
["F30", "8.5.4", "s. f.", "Base de datos horaria", "Instituto de Hidrología, Meteorología y Estudios Ambientales [IDEAM]",
 "Temperatura máxima del aire", "Medellín (Aeropuerto Olaya Herrera)",
 "Serie horaria de máxima diaria, filtrada; base de la Figura 9 y 10", "Alta, con control de calidad propio aplicado",
 "Incluida", P1, "datos.gov.co/d/ccvq-rp9s"],
["F31", "8.5.4", "s. f.", "Base de datos horaria", "Instituto de Hidrología, Meteorología y Estudios Ambientales [IDEAM]",
 "Temperatura mínima del aire", "Medellín (Aeropuerto Olaya Herrera)",
 "Serie horaria de mínima diaria, filtrada; base de la Figura 9 y 10", "Alta, con control de calidad propio aplicado",
 "Incluida", P1, "datos.gov.co/d/afdg-3zpb"],
["F32", "8.5.4", "s. f.", "Conjunto de datos oficial", "Instituto de Hidrología, Meteorología y Estudios Ambientales [IDEAM]",
 "Normales climatológicas de Colombia", "Medellín (Aeropuerto Olaya Herrera)",
 "Normales 1971–2000, 1981–2010, 1991–2020; línea base de la Figura 10 y de la tendencia por década",
 "Alta: única normal oficial de referencia de largo plazo", "Incluida", P1,
 "datos.gov.co/.../Normales-Climatológicas-de-Colombia/nsz2-kzcq"],
["F33", "8.6", 2019, "Artículo científico", "Bedoya-Soto, J. M., Aristizábal, E., Carmona, A. M. y Poveda, G.",
 "Seasonal shift of the diurnal cycle of rainfall over Medellín's valley, central Andes of Colombia (1998–2005)",
 "Valle de Aburrá", "Ciclo diurno de la lluvia (pico en la tarde oct.–abr., en la madrugada may.–sep.), citado en 8.6",
 "Alta: única fuente local sobre ciclo diurno de precipitación", "Incluida", P1, "doi.org/10.3389/feart.2019.00092"],
["F34", "8.6", 2026, "Noticia (estimación de tercero)", "Gaona, J. / Infobae",
 "El Niño amenaza con volver a encarecer los alimentos y el corrientazo en Colombia", "Colombia",
 "Estimación del equipo técnico del Banco de la República (1,5–3,26 p.p. de inflación) citada en 8.6",
 "Media: cifra de prensa, no informe primario del Banco de la República", "Incluida (con reserva declarada)", P1,
 "infobae.com/colombia/2026/09/07/..."],
["F35", "8.6", 2021, "Informe técnico internacional", "Panel Intergubernamental de Expertos sobre el Cambio Climático [IPCC]",
 "Climate Change 2021: The Physical Science Basis (Capítulo 4)", "Global",
 "ENSO como ciclo natural amplificado, no causado, por el cambio climático; base del segundo párrafo de 8.6",
 "Alta: fuente de referencia internacional del IPCC", "Incluida", P1, "ipcc.ch/report/ar6/wg1/"],
["F36", "8.6", 2015, "Marco internacional", "Oficina de las Naciones Unidas para la Reducción del Riesgo de Desastres [UNDRR]",
 "Marco de Sendai para la Reducción del Riesgo de Desastres 2015-2030", "Global",
 "Prioridad 1 (entender el riesgo), base del cierre de 8.6", "Alta: marco de referencia internacional adoptado por Colombia",
 "Incluida", P1, "undrr.org/publication/sendai-framework-disaster-risk-reduction-2015-2030"],
["F37", "8.1.9", 2012, "Artículo científico", "Revista Iatreia",
 "Dengue.pdf (artículo de 9 páginas)", "Medellín / Antioquia", "Posible complemento de 8.1.9, no usado",
 "Baja hasta lectura: no se ha evaluado su aporte", "Disponible, sin leer ni citar", P1,
 "Drive, carpeta 8.1"],
["F38", "8.1.7", "2017/2019", "Tesis y artículo", "Soto-Estrada (2019) y tesis UNAL",
 "2017_UHI_UNAL_MSC.pdf y 2019_UHI_UNAM.pdf", "Valle de Aburrá",
 "Posible serie Landsat 1986–2016 para la tendencia de calor urbano de 8.1.7, no usado",
 "Media hasta lectura: podría dar tendencia de largo plazo que hoy falta", "Disponible, sin leer ni citar", P1,
 "Drive, 1.Documentación\\Secundaria\\UHI"],
]

# ---------------------------------------------------------------------------------------------------------------
# Anexo B: variables e indicadores realmente construidos y usados
B_HEAD = ["Variable", "Numeral(es)", "Dimensión", "Definición", "Unidad", "Fuente", "Periodicidad",
          "Cobertura territorial y temporal"]
B = [
["Precipitación mensual/pentadal", "7.1", "Clima", "Lámina de agua acumulada por periodo", "mm", "CHIRPS v3 / CHELSA",
 "Pentadal (CHIRPS) / mensual (CHELSA)", "Medellín, 1981–2025"],
["Temperatura media/máxima/mínima (satelital, ráster)", "7.1", "Clima", "Temperatura del aire modelada por celda",
 "°C", "CHELSA", "Mensual", "Medellín, 1981–2025"],
["Clasificación climática de Köppen-Geiger", "7.1.3", "Clima", "Clase climática por celda según criterios de Köppen-Geiger",
 "Categórica", "Beck et al. (2023)", "Estática (proyección a 2099)", "Medellín, 1 km"],
["Índice Oceánico El Niño (ONI)", "7.1.5, 8.5, 8.6", "Clima (variabilidad interanual)",
 "Anomalía de temperatura superficial del mar en la región Niño 3.4, media móvil de 3 meses", "°C", "NOAA (PSL / CPC)",
 "Mensual", "Global, 1950–2026"],
["Fase El Niño / La Niña / Neutro (episodio)", "7.1.5, 8.5, 8.6", "Clima (variabilidad interanual, indicador propio)",
 "Episodio de ≥5 meses consecutivos con ONI ≥ +0,5 (El Niño) o ≤ −0,5 (La Niña); si no se cumple, «neutro»; episodio abierto al final de la serie se marca provisional",
 "Categórica", "Elaboración propia a partir de NOAA (regla de la OMM/NOAA)", "Mensual", "Global, aplicado a Medellín, 1950–2026"],
["Amenaza por movimientos en masa / inundación / avenida torrencial (POT 2026)", "8.1.3–8.1.5", "Amenaza",
 "Nivel de amenaza (alta/media/baja) por unidad de suelo, según el estudio básico de amenaza", "Categórica / % de área",
 "DAP (2026a, 2026b)", "Estática (POT 2026)", "Medellín, por comuna y corregimiento"],
["Riesgo climático (Amenaza × Exposición × Vulnerabilidad)", "8.1.2, 8.1.5, 8.1.7", "Riesgo",
 "Índice compuesto 1–5 por componente, clasificado por rupturas de Jenks", "Ordinal (1–5)", "Universidad de Antioquia (2026a, 2026b)",
 "Estática", "Medellín, por comuna y corregimiento"],
["Temperatura de superficie (LST)", "8.1.7", "Calor urbano", "Temperatura de la superficie terrestre estimada por satélite",
 "°C", "Landsat, vía Guzmán Echavarría (2018)", "Puntual (mediana 2013–2016)", "Medellín, 30 m, por barrio"],
["Días con temperatura máxima sobre 28/29/30 °C", "8.1.7, 8.5.4", "Calor urbano", "Conteo de días con Tx sobre un umbral",
 "Días/mes o días/año", "SIATA (referencia 1990–2000) / IDEAM (dato real, estación Olaya Herrera)", "Diaria, agregada a mensual/anual",
 "Medellín; SIATA 1990–2000, IDEAM 2014–2026"],
["Temperatura máxima y mínima diaria (estación)", "8.5.4", "Clima observado", "Extremos diarios de temperatura del aire",
 "°C", "IDEAM (estación Aeropuerto Olaya Herrera, código 27015330)", "Horaria, agregada a diaria/mensual", "Medellín, dic. 2014–sep. 2026"],
["Normal climatológica de temperatura", "8.5.4", "Clima, línea base", "Promedio de 30 años de un periodo fijo, según la Directriz 1203 de la OMM",
 "°C", "IDEAM", "Ventanas de 30 años, desplazadas cada 10", "Medellín (Olaya Herrera), 1971–2020"],
["Movimientos en masa atendidos", "8.1.5, 8.5.1", "Eventos", "Número de eventos de movimiento en masa atendidos por el DAGRD o registrados en SIRMED",
 "Eventos/año o /mes", "DAGRD (PASCCM Tomo I) / SIRMED (Alcaldía de Medellín)", "Diaria, agregada a mensual/anual",
 "Medellín, por comuna y corregimiento, 2005–2018 y 2021–2026"],
["Inundaciones y avenidas torrenciales atendidas", "8.1.3, 8.1.4, 8.5.2", "Eventos", "Número de eventos de inundación o avenida torrencial atendidos",
 "Eventos/año o /mes", "DAGRD (PASCCM Tomo I) / SIRMED", "Diaria, agregada a mensual/anual",
 "Medellín, por comuna y corregimiento, 2005–2018 y 2021–2026"],
["Incendios de cobertura vegetal", "8.1.8, 8.5.3", "Eventos", "Número de incendios de cobertura vegetal atendidos o validados",
 "Eventos/año o /mes", "DAGRD / SIRMED / Universidad de Antioquia (2026b)", "Diaria, agregada a mensual/anual",
 "Medellín, por comuna, 2016–2026"],
["Deslizamientos y flujos de detritos registrados, con fallecidos", "8.5.1", "Pérdidas humanas",
 "Registro histórico de eventos con fecha, ubicación y número de fallecidos", "Eventos y personas", "Geohazards",
 "Por evento, agregada a década", "Medellín, 1871–2026"],
["Eventos climáticos UNGRD y sus efectos", "8.5.5", "Pérdidas humanas y materiales",
 "Fallecidos, heridos, personas afectadas, viviendas destruidas y averiadas por evento", "Personas / viviendas",
 "UNGRD", "Por evento, agregada a año", "Medellín, 2019–2022"],
["Eventos DesInventar y pérdidas económicas", "8.5.1, 8.5.5", "Pérdidas económicas",
 "Registro histórico de eventos con valor económico de pérdidas cuando está disponible", "Eventos y pesos corrientes",
 "UNDRR (DesInventar Sendai)", "Por evento", "Medellín, 1921–2017 (valor económico solo hasta 1996)"],
["Casos de dengue", "8.1.9", "Salud sensible al clima", "Casos reportados por año", "Casos/año",
 "Secretaría de Salud de Medellín (PASCCM Tomo I)", "Anual", "Medellín, 2000–2018"],
["Relieve y pendiente", "7.1.2", "Relieve", "Elevación y pendiente del terreno", "m / grados",
 "DTM-LiDAR (Alcaldía de Medellín / AeroEstudios, 2021)", "Estática", "Medellín, 1 m (derivado a 10 m)"],
["Inflación asociada a El Niño", "8.6", "Economía", "Puntos porcentuales adicionales de inflación nacional estimados para un episodio de El Niño moderado a fuerte",
 "Puntos porcentuales", "Equipo técnico del Banco de la República, vía Infobae", "Por episodio ENSO, con rezago de 6–12 meses",
 "Colombia (nacional, no específico de Medellín)"],
["Ciclo diurno de la precipitación", "8.6", "Clima, alta frecuencia",
 "Hora del día de mayor precipitación media, por temporada del año", "Hora local (LST)",
 "Bedoya-Soto, Aristizábal, Carmona y Poveda (2019)", "Horaria, agregada por temporada", "Valle de Aburrá, 1998–2005"],
]

# ---------------------------------------------------------------------------------------------------------------
wb = Workbook()

HEADER_FILL = PatternFill("solid", fgColor="243E54")
HEADER_FONT = Font(name="Arial", size=10.5, bold=True, color="FFFFFF")
BODY_FONT = Font(name="Arial", size=10)
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def write_sheet(ws, head, rows, widths):
    ws.sheet_view.showGridLines = False
    for j, h in enumerate(head, start=1):
        c = ws.cell(1, j, h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[1].height = 34
    for i, row in enumerate(rows, start=2):
        for j, val in enumerate(row, start=1):
            c = ws.cell(i, j, val)
            c.font = BODY_FONT
            c.alignment = WRAP
            c.border = BORDER
        ws.row_dimensions[i].height = 60
    for j, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(head))}{len(rows) + 1}"


wsA = wb.active
wsA.title = "A. Fuentes y trazabilidad"
write_sheet(wsA, A_HEAD, A, [7, 14, 9, 16, 26, 42, 16, 42, 34, 18, 30, 30])

wsB = wb.create_sheet("B. Variables e indicadores")
write_sheet(wsB, B_HEAD, B, [34, 16, 20, 46, 14, 34, 20, 34])

wsN = wb.create_sheet("Notas")
wsN.sheet_view.showGridLines = False
notes = [
    ["Anexo A. Matriz de fuentes y trazabilidad"],
    ["Construida a partir de INDICE_REFERENCIAS.md (PAC_2026_Referencias_7.1_8.1, actualizado 2026-09-28) y del "
     "repositorio marcosatho/PAC_2026_MED. Cubre los numerales 7.1, 8.1, 8.5 y 8.6."],
    ["«Estado de uso» sigue las mismas categorías que ya usaba INDICE_REFERENCIAS.md: Incluida, Solo enlace, Cita "
     "secundaria, Pendiente y Disponible sin leer ni citar."],
    ["«Veredicto de relevancia» es una valoración nueva de esta matriz, no estaba en el índice original; se anotó "
     "para cada fuente al construir esta tabla."],
    [""],
    ["Anexo B. Matriz de variables e indicadores"],
    ["Reúne las variables efectivamente construidas o descargadas para 7.1, 8.1, 8.5 y 8.6 en este trabajo. No es "
     "un catálogo teórico: cada fila tiene una fuente y una cobertura verificadas."],
    [""],
    ["Ambos anexos quedan pendientes de revisión por el equipo de coordinación antes de incorporarse al cuerpo del documento maestro."],
]
bold_rows = {1, 6}  # the two "Anexo A. / Anexo B." headings
for i, r in enumerate(notes, start=1):
    wsN.cell(i, 1, r[0]).font = Font(name="Arial", size=10.5, bold=(i in bold_rows))
    wsN.cell(i, 1).alignment = Alignment(wrap_text=True, vertical="top")
wsN.column_dimensions["A"].width = 110

wb.save(OUT)
print("saved", OUT, "| Anexo A:", len(A), "filas | Anexo B:", len(B), "filas")
