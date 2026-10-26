# -*- coding: utf-8 -*-
"""Plan de ubicación de las figuras en los capítulos 7.1 y 8.1 del borrador RT (piloto local).

Cada entrada: dónde va (índice del elemento del cuerpo del RT después del cual se inserta), qué archivo, qué leyenda.
Las leyendas parten de las del P1 v2 (corregidas) y de los pies de las figuras v2 de amenaza; todas son propuesta."""
import os

DL = r"C:\Users\marco\Downloads"
R81 = os.path.join(DL, "PAC_2026_Referencias_7.1_8.1")
PROY = r"G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION"
REL = PROY + r"\07_1_CLIMA_RELIEVE"
AMZ = PROY + r"\08_1_AMENAZAS\05_POT2026_AMENAZAS_OFICIAL_V2\03_FIGURAS"
K71 = REL + r"\10_FIGURAS_EJES_KM"
K81 = PROY + r"\08_1_AMENAZAS\06_FIGURAS_EJES_KM"
ENSO_REPO = r"C:\Users\marco\Documents\GitHub\PAC_2026_MED\P1_07_1_CLIMA_RELIEVE\08_CHELSA\04_PREVISUALIZACIONES\CHELSA_ENSO_MESES_ANUALIZADO_1981_2021_MAGNA_SIRGAS_layout_v4.png"
MEDIA = r"C:\Users\marco\AppData\Local\Temp\claude\G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude\446a2666-30c7-4c61-98e1-c82458a0665f\scratchpad\inventario_figuras\media_P1v2"
FIG = lambda n: os.path.join(R81, n)


def buscar(nombre, raiz=REL):
    for d, _, fs in os.walk(raiz):
        if nombre in fs:
            return os.path.join(d, nombre)
    return ""


DEF_ALC = "Alcaldía de Medellín"
POMCA = ("Fuente: elaboración propia a partir de Corantioquia, AMVA y Cornare (2018) y de la información político-administrativa "
         "de la Alcaldía de Medellín. Los intervalos son clases de la cartografía publicada y no valores ráster continuos.")
AMZ_FUENTE = ("Fuente: elaboración propia a partir de la capa de amenaza de la propuesta de revisión del POT 2026 (Departamento Administrativo de "
              "Planeación [DAP], 2026; aún no protocolizada), construida con el estudio básico de amenaza (Universidad EAFIT, 2025) y estudios de detalle.")

# anchor = índice del elemento del RT después del cual se inserta; sec = encabezado de la subsección
P = [
    # ---------------- 7.1 Relieve y clima
    dict(k="elev", v2=1, anchor=557, sec="7.1 · Relieve, pendientes y cuencas", tipo="Mapa", src=os.path.join(K71, "elevacion_medellin_DTM_2021_carta_v3_km.png"),
         titulo="Distribución de la elevación del terreno en el Distrito de Medellín, en metros sobre el nivel del mar.",
         fuente="Fuente: elaboración propia a partir del modelo digital de terreno LiDAR de 2021 de la Alcaldía de Medellín.",
         leyenda="del P1 v2 (ajustada)", llamada="al final del párrafo 1: «(Figura 7.1)»",
         obs="La cita del DTM LiDAR 2021 no está en la lista de referencias del RT. Figura regenerada con ejes en km a partir del script 12_RELIEVE_LAYOUT_POMCA (versión v3)."),
    dict(k="pend", v2=2, anchor=558, sec="7.1 · Relieve, pendientes y cuencas", tipo="Mapa", src=os.path.join(K71, "pendiente_medellin_DTM_2021_carta_v3_km.png"),
         titulo="Distribución de las pendientes del terreno en el Distrito de Medellín, clasificadas en intervalos de grados.",
         fuente="Fuente: elaboración propia a partir del modelo digital de terreno LiDAR de 2021 de la Alcaldía de Medellín.",
         leyenda="del P1 v2 (ajustada)", llamada="el texto ya cita «(Figura 7.1)»: pasa a «(Figuras 7.2 y 7.3)»",
         obs="Va antes del gráfico de clases de pendiente que ya está en el RT (queda como 7.3)."),
    dict(k="koppen", v2=3, anchor=563, sec="7.1 · Climatología de base", tipo="Mapa", src=os.path.join(K71, "Koppen_Geiger_1991_2020_Medellin_carta_km.png"),
         titulo=("Clasificación climática de Köppen-Geiger para el Distrito de Medellín, periodo 1991–2020. El mapa presenta las clases Af (tropical lluvioso) "
                 "y Cfb (templado, sin estación seca y con verano templado), con una resolución espacial aproximada de 1 km, sobre el límite municipal y las "
                 "divisiones de comunas y corregimientos."),
         fuente=("Fuente: elaboración propia a partir de Beck et al. (2023) y de la información político-administrativa de la Alcaldía de Medellín. "
                 "La clasificación representa condiciones macroclimáticas y no incorpora las variaciones microclimáticas intraurbanas."),
         leyenda="del P1 v2 (ajustada)", llamada="al final del párrafo 1 de «Climatología de base»: «(Figura 7.4)»",
         obs="El P1 v2 decía que el mapa tiene las clases Af, Am y Cfb; el mapa muestra solo Af y Cfb. Beck et al. (2023) no está en las referencias del RT, y el texto del RT no menciona Köppen."),
    dict(k="prec", v2=4, anchor=564, sec="7.1 · Climatología de base", tipo="Mapa", src=os.path.join(K71, "24_precipitacion_medellin_carta_km.png"),
         titulo="Precipitación media anual en el Distrito de Medellín según el POMCA del río Aburrá, en milímetros por año.",
         fuente=POMCA, leyenda="del P1 v2 (ajustada; el P1 v2 citaba el POMCA como 2016 y el RT como 2018)",
         llamada="al final del párrafo 2: «(Figura 7.5)»", obs=""),
    dict(k="temp", v2=6, anchor=565, sec="7.1 · Climatología de base", tipo="Mapa", src=os.path.join(K71, "23_temperatura_medellin_carta_km.png"),
         titulo="Temperatura media anual en el Distrito de Medellín según el POMCA del río Aburrá, en grados Celsius.",
         fuente=POMCA, leyenda="nueva (el P1 v2 no tenía leyenda)", llamada="al final del párrafo 3: «(Figura 7.6)»",
         obs="En el P1 v2 esta imagen no tenía leyenda."),
    dict(k="et", v2=5, anchor=565, sec="7.1 · Climatología de base", tipo="Mapa", src=os.path.join(K71, "22_evapotranspiracion_medellin_carta_km.png"),
         titulo="Evapotranspiración real anual en el Distrito de Medellín según el POMCA del río Aburrá, en milímetros por año.",
         fuente=POMCA, leyenda="del P1 v2 (ajustada)", llamada="requiere un párrafo nuevo sobre evapotranspiración",
         obs="El texto de 7.1 del RT no habla de evapotranspiración. Decisión: agregar un párrafo (el P1 v2 lo tenía) o dejar la figura fuera."),
    dict(k="enso", v2=7, anchor=572, sec="7.1 · Variabilidad interanual", tipo="Mapa (panel)", src=ENSO_REPO,
         titulo=("Precipitación y temperatura medias anualizadas según la fase del ENOS (El Niño, neutral y La Niña) en el Distrito de Medellín, 1981–2021. "
                 "Las composiciones se elaboraron con datos mensuales de CHELSA v2.1 clasificados con el índice ONI; las isolíneas y los intervalos de color son "
                 "promedios de cada fase y no las condiciones de un mes o evento particular."),
         fuente="Fuente: elaboración propia con datos de CHELSA v2.1 y de NOAA/CPC.",
         leyenda="del P1 v2 (ajustada)", llamada="al final del párrafo de «Variabilidad interanual»: «(Figura 7.8)»",
         obs="El archivo fuente existe en el repositorio (CHELSA_ENSO_MESES_ANUALIZADO_…_layout_v4.png, idéntico a la imagen del P1 v2; ya viene con ejes en km). CHELSA y NOAA no están en las referencias del RT."),
    # ---------------- 8.1 Amenazas
    dict(k="riesgo_pe", v2=18, anchor=735, sec="8.1 · Lluvia intensa y lluvia antecedente", tipo="Mapa", src=os.path.join(K81, "riesgo_precipitacion_extrema_comunas_km.png"),
         titulo="Riesgo actual por precipitación extrema, por comuna y corregimiento.",
         fuente="Fuente: elaboración propia a partir de Universidad de Antioquia (2026a, 2026b).",
         leyenda="del P1 v2", llamada="al final del párrafo «Comportamiento observado»: «(Figura 8.1)»",
         obs="Es un mapa de riesgo (no de amenaza): se puede pasar a 8.4, donde está la Tabla 8.9 con la clase de riesgo de la ERC 2026."),
    dict(k="dif", v2=19, anchor=739, sec="8.1 · Lluvia intensa y lluvia antecedente", tipo="Mapa", src=os.path.join(K81, "diferencia_precipitacion_extrema_2040_2030_km.png"),
         titulo="Diferencia en la precipitación extrema horaria entre 2040 y 2030 en Medellín. Azul: aumento; rojo: disminución.",
         fuente="Fuente: elaboración propia a partir de SIATA (2019).", leyenda="del P1 v2", llamada="en «Cambios proyectados»: «(Figura 8.3)»", obs=""),
    dict(k="aum", v2=20, anchor=739, sec="8.1 · Lluvia intensa y lluvia antecedente", tipo="Gráfico", src=FIG("8.1_figura_cambios_proyectados_precipitacion_extrema.png"),
         titulo="Aumento proyectado de la precipitación extrema en Antioquia, corto y largo plazo, escenario SSP3-7.0.",
         fuente="Fuente: elaboración propia a partir de Universidad de Antioquia (2026a).", leyenda="del P1 v2", llamada="en «Cambios proyectados»: «(Figura 8.4)»",
         obs="Comparte tema con la Tabla 8.1 y la Figura 8.1 del RT; revisar que no repita información."),
    dict(k="mm", v2=23, anchor=743, sec="8.1 · Movimientos en masa", tipo="Mapa (v2 oficial)", src=os.path.join(AMZ, "Figura_8_1_5_1_amenaza_movimientos_en_masa_POT2026_v2.png"),
         titulo=("Amenaza por movimientos en masa en el Distrito de Medellín según la propuesta de revisión del POT 2026 (aún no protocolizada): "
                 "alta, 37,26 % del Distrito; media, 14,79 %; baja, 47,95 %."),
         fuente=AMZ_FUENTE, leyenda="nueva (versión v2 con la capa oficial)", llamada="en «Zonificación normativa»: «(Figura 8.5)»",
         obs="Reemplaza el mapa reconstruido de una lámina PDF. La referencia de la capa del DAP necesita su letra en la lista de referencias."),
    dict(k="mm_terr", v2=32, anchor=744, sec="8.1 · Movimientos en masa", tipo="Gráfico (pendiente)", src="",
         titulo="PENDIENTE: proporción del suelo en amenaza por movimientos en masa, por corregimiento y comuna.",
         fuente="Hay que rehacerla con los polígonos oficiales de la capa v2.", leyenda="por rehacer", llamada="", placeholder=True,
         obs="La versión del P1 v2 se hizo con el cotejo anterior; se rehace con la capa v2."),
    dict(k="inund", v2=21, anchor=747, sec="8.1 · Inundaciones", tipo="Mapa (v2 oficial)", src=os.path.join(AMZ, "Figura_8_1_3_1_amenaza_inundaciones_POT2026_v2.png"),
         titulo=("Amenaza por inundaciones en el Distrito de Medellín según la propuesta de revisión del POT 2026 (aún no protocolizada): "
                 "alta, 575 ha; media, 195 ha; baja, 364 ha."),
         fuente=AMZ_FUENTE, leyenda="nueva (versión v2 con la capa oficial)", llamada="en «Zonificación normativa»: «(Figura 8.6)»",
         obs="La zonificación equivale a la creciente de 100 años solo en las quebradas modeladas; en las demás se usaron otros métodos (anexo del EBA, 9.5)."),
    dict(k="torr", v2=22, anchor=752, sec="8.1 · Avenidas torrenciales", tipo="Mapa (v2 oficial)", src=os.path.join(AMZ, "Figura_8_1_4_1_amenaza_avenidas_torrenciales_POT2026_v2.png"),
         titulo=("Amenaza por avenidas torrenciales en el Distrito de Medellín según la propuesta de revisión del POT 2026 (aún no protocolizada): "
                 "alta, 587 ha; media, 207 ha; baja, 169 ha."),
         fuente=AMZ_FUENTE, leyenda="nueva (versión v2 con la capa oficial)", llamada="en «Zonificación normativa»: «(Figura 8.7)»", obs=""),
    dict(k="dias", v2=29, anchor=755, sec="8.1 · Calor extremo e isla de calor", tipo="Mapa", src=os.path.join(K81, "Figura_8_1_7_1_dias_calurosos_referencia_1990_2000_km.png"),
         titulo="Días al año con temperatura máxima superior a 28 °C y 29 °C en el Distrito de Medellín, clima de referencia 1990–2000.",
         fuente="Fuente: elaboración propia a partir de SIATA (2019).", leyenda="del P1 v2", llamada="en «Comportamiento observado»: «(Figura 8.8)»", obs=""),
    dict(k="lst", v2=30, anchor=756, sec="8.1 · Calor extremo e isla de calor", tipo="Mapa", src=os.path.join(K81, "Figura_8_1_7_2_temperatura_superficie_continua_km.png"),
         titulo="Temperatura de la superficie en el Distrito de Medellín, mediana de imágenes de satélite de la mañana, 2013–2016.",
         fuente="Fuente: elaboración propia a partir de Guzmán Echavarría (2018).", leyenda="del P1 v2", llamada="en «La isla de calor añade…»: «(Figura 8.9)»",
         obs="Guzmán Echavarría (2018) no está en las referencias del RT (el estudio del AMVA sí se menciona en el texto)."),
    dict(k="lst_b", v2=31, anchor=756, sec="8.1 · Calor extremo e isla de calor", tipo="Mapa", src=os.path.join(K81, "Figura_8_1_7_3_temperatura_superficie_por_barrio_km.png"),
         titulo="Temperatura promedio de la superficie por barrio, descontado el efecto de la pendiente.",
         fuente="Fuente: elaboración propia a partir de Guzmán Echavarría (2018).", leyenda="del P1 v2", llamada="en «La isla de calor añade…»: «(Figura 8.10)»", obs=""),
    dict(k="esc", v2=25, anchor=761, sec="8.1 · Sequía y escasez hídrica", tipo="Mapa", src=os.path.join(K81, "riesgo_escasez_hidrica_comunas_km.png"),
         titulo=("Riesgo actual por escasez hídrica, por comuna y corregimiento. El riesgo más alto se concentra en el norte y centro de la ciudad (Popular, "
                 "Santa Cruz, Manrique, Aranjuez, Doce de Octubre, Villa Hermosa); los corregimientos rurales no presentan amenaza según este indicador, "
                 "salvo la cabecera urbana de San Antonio de Prado."),
         fuente="Fuente: elaboración propia a partir de Universidad de Antioquia (2026a, 2026b).", leyenda="del P1 v2",
         llamada="en «Comportamiento observado»: «(Figura 8.11)»", obs="Mapa de riesgo: también puede ir en 8.4."),
    dict(k="def_acu", v2=26, anchor=762, sec="8.1 · Sequía y escasez hídrica", tipo="Mapa", src=FIG("8.1_figura_Figura_4_10_SIATA2019_acueducto.png"),
         titulo=("Cambio proyectado del déficit hídrico en las cuencas que alimentan los acueductos de Medellín, hacia mediados de siglo. En rojo, las cuencas "
                 "donde el déficit empeora más (Riogrande, al occidente); en azul, donde mejora (La Fe, al oriente)."),
         fuente="Fuente: SIATA (2019).", leyenda="del P1 v2", llamada="en «Cambios proyectados»: «(Figura 8.12)»", obs="Figura del estudio abierto del SIATA (2019): basta citar la fuente."),
    dict(k="def_hid", v2=27, anchor=762, sec="8.1 · Sequía y escasez hídrica", tipo="Mapa", src=FIG("8.1_figura_Figura_4_11_SIATA2019_hidroelectricas.png"),
         titulo=("Cambio proyectado del déficit hídrico en las cuencas que alimentan las centrales hidroeléctricas de EPM, hacia mediados de siglo. "
                 "Casi todas empeoran (rojo y naranja), salvo Guatapé, sin cambio."),
         fuente="Fuente: SIATA (2019).", leyenda="del P1 v2", llamada="en «Cambios proyectados»: «(Figura 8.13)»", obs="Figura del estudio abierto del SIATA (2019): basta citar la fuente."),
    dict(k="arid", v2=28, anchor=762, sec="8.1 · Sequía y escasez hídrica", tipo="Mapa", src=FIG("8.1_figura_Figura_4_13_SIATA2019_aridez_antioquia.png"),
         titulo=("Cambio porcentual proyectado en el índice de aridez hacia mediados de siglo, en las zonas agrícolas del departamento de Antioquia que abastecen "
                 "al Valle de Aburrá. El rojo indica mayor aumento de la sequedad del suelo; se concentra en el centro y el nororiente del departamento."),
         fuente="Fuente: SIATA (2019, figura 4.13).", leyenda="del P1 v2", llamada="en «Cambios proyectados»: «(Figura 8.14)»", obs="Figura del estudio abierto del SIATA (2019): basta citar la fuente."),
    dict(k="inc", v2=33, anchor=765, sec="8.1 · Incendios de cobertura vegetal", tipo="Gráfico", src=FIG("8.1_figura_Figura_8_1_8_1_incendios_por_anio_y_territorio.png"),
         titulo="Incendios de cobertura vegetal en Medellín, enero de 2018 a abril de 2025 (1.357 eventos), por año y por territorio.",
         fuente=("Fuente: elaboración propia a partir de Universidad de Antioquia (2026b), secciones V y VIII. Incendios validados en coberturas vegetales "
                 "(98 % registrados por el SIATA); 2025 incluye solo hasta el 30 de abril."),
         leyenda="nueva (el P1 v2 no tenía leyenda)", llamada="en «Comportamiento observado»: «(Figura 8.15)»", obs=""),
    dict(k="enso_ds", v2=24, anchor=768, sec="8.1 · El Niño-Oscilación del Sur como factor común", tipo="Gráfico", src=FIG("8.5_figura_Figura_8_5_6_precipitacion_deslizamientos_fase_ENSO_Aristizabal2026_es.png"),
         titulo=("Precipitación mensual (líneas discontinuas, eje izquierdo) y deslizamientos reportados (barras, eje derecho) en el Valle de Aburrá según la fase de "
                 "El Niño y La Niña, 1950–2023. Azul: La Niña; rojo: El Niño; gris: neutro. Los meses se clasifican con el índice oceánico de la NOAA "
                 "(La Niña: −0,5 o menos; El Niño: +0,5 o más; neutro: entre ambos)."),
         fuente="Fuente: adaptada de Aristizábal et al. (2026, figura 3), licencia CC BY 4.0; se tradujeron los rótulos al español.",
         leyenda="del P1 v2 (ajustada; en el P1 v2 estaba en movimientos en masa)", llamada="en el párrafo de ENSO: «(Figura 8.16)»",
         obs="Se movió de movimientos en masa a la sección ENSO, que es donde el RT habla de la lluvia y los deslizamientos por fase."),
    dict(k="dengue", v2=34, anchor=769, sec="8.1 · El Niño-Oscilación del Sur como factor común", tipo="Gráfico", src=FIG("8.1_figura_Figura_8_1_9_1_dengue_casos_por_anio.png"),
         titulo="Casos de dengue por año en Medellín, 2000–2018.",
         fuente="Fuente: elaboración propia a partir de Secretaría de Salud de Medellín (2021).", leyenda="del P1 v2", llamada="en el párrafo del dengue: «(Figura 8.17)»",
         obs="Secretaría de Salud de Medellín (2021) no está en las referencias del RT."),
    dict(k="salud", v2=35, anchor=770, sec="8.1 · Salud (sin subsección en el RT)", tipo="Gráfico y mapa (pendientes)", src="",
         titulo="PENDIENTE: riesgo de la población en salud por el clima (ranking y mapa por comuna y corregimiento).",
         fuente="El RT no tiene subsección de salud sensible al clima; habría que restaurarla (el P1 v2 la tenía como 8.1.9).", leyenda="sin ubicación en el RT",
         llamada="", placeholder=True, obs="Figuras 35 y 36 del P1 v2. Los archivos existen en 8.1_figura_Figura_8_1_9_2 y 8_1_9_3."),
]
for p in P:
    p.setdefault("placeholder", False)
