# Producto 9 (Gobierno de datos climáticos y dashboard MERL) · Geovisor, mapa del territorio: métodos, cálculos y referencias

**Versión 2 · cortes de datos del 8 y 9 de octubre de 2026 · documento de trabajo para validación del equipo experto**

Este documento explica de dónde sale cada número de la herramienta (`01_HERRAMIENTA/Producto9_mapa_territorio_PAC_v2.html`): las cifras de las tarjetas de resumen, las tablas, los mapas por barrio y las marcas de «dónde falta». También reúne las referencias bibliográficas y las referencias de los datos. Los archivos de datos citados están en `02_DATOS/`.

Las capas marcadas con asterisco (*) son preliminares: las amenazas del POT 2026 se reconstruyeron de láminas en PDF y no son capas oficiales.

---

## 1. Dónde está cada cosa

| En la página | Se explica en | Archivo de datos |
|---|---|---|
| Tarjetas de resumen (9 cifras) | sección 6 | `A_tablas/P9_barrios_veredas_indicadores_v2.csv`, `A_tablas/P9_comunas_corregimientos_indicadores_v2.csv` |
| Capas de amenaza (deslizamientos, inundación, avenidas torrenciales) | 3.1 | `C_entradas_del_proyecto/POT2026_amenaza_*` |
| Multiamenaza (índice 1 a 27) | 3.2 | `B_capas_SIG/P9_capas_derivadas_9377.gpkg`, capa `multiamenaza_piezas` |
| Incendios forestales | 3.3 | `B_capas_SIG/P9_capas_servidor_alcaldia_2026-10-08_9377.gpkg`, capa `amenaza_incendios_forestales` |
| Temperatura de la superficie | 3.4 | `C_entradas_del_proyecto/LST_*` |
| Arbolado y verde urbano | 4.1 | `P9_arboles_medellin_*.gpkg`, `P9_espacios_verdes_urbanos_2019_9377.gpkg` |
| Obras de ladera y quebrada | 4.2 | `P9_capas_servidor_alcaldia_*.gpkg` |
| Alerta temprana y evacuación | 4.3 | `P9_capas_servidor_alcaldia_*.gpkg` |
| Marcas «dónde falta» | 5 | `A_tablas/P9_brechas_barrios_marcados_v2.csv` |
| Tabla por comuna y corregimiento | 7 | `A_tablas/P9_comunas_corregimientos_indicadores_v2.csv` |
| Nota de impacto de las medidas | 8 | catálogo integrado de medidas (hoja «Enfriamiento ADA-06») |

---

## 2. Convenciones generales

- **Sistema de coordenadas.** Todas las capas y los cálculos están en EPSG:9377 (MAGNA-SIRGAS, Origen Nacional). Las áreas se calculan en ese sistema. Para dibujar en la página se pasan a WGS84 y se simplifican solo para la pantalla; los cálculos nunca usan la versión simplificada.
- **Límites.** Comunas y corregimientos (23 polígonos: 16 comunas, 5 corregimientos y dos polígonos sin nombre, `SN01` y `SN02`) y barrios y veredas (332 polígonos), ambos de la capa oficial de límites político-administrativos (fecha de actualización de la capa: 17 de diciembre de 2014). El Distrito es la unión de los polígonos de comunas y corregimientos: 376,4 km² (37.640 ha).
- **Barrio «urbano».** Barrio cuyo código de comuna va de 01 a 16 (269 de los 332; incluye áreas institucionales dentro de comunas). Los otros 63 son veredas, barrios de corregimientos y áreas especiales; el inventario de árboles y el de espacios verdes son urbanos, y por eso esos 63 aparecen «sin evaluar» en los mapas de arbolado.
- **Tamaño mínimo.** Las marcas de «dónde falta» solo evalúan barrios de 5 ha o más (331 de 332; 268 urbanos). Los menores se descartan porque el borde de la capa pesa más que el contenido.
- **Cómo se agrega.** Nunca se remuestrea ni se interpola una capa. El único paso de agregación es de píxel o polígono al barrio o la comuna. Los puntos se asignan al barrio que los contiene (`within`); las líneas y los polígonos cuentan en cada barrio que tocan (`intersects`), salvo cuando se recorta el área (espacios verdes, amenazas e incendios), que se recortan de forma exacta a cada barrio.
- **Asterisco (*).** Capa preliminar. Se retira cuando el Distrito publique las capas oficiales del POT 2026.
- **Formato.** Cifras con coma decimal y punto de miles, como en la página.

---

## 3. Problemas: amenazas y calor

### 3.1 Amenazas del POT 2026* (deslizamientos, inundación, avenidas torrenciales)

**Fuente.** POT 2026, Cartografía 1, láminas 5 (movimientos en masa), 6 (inundación) y 7 (avenidas torrenciales), de la revisión de mediano plazo (agosto de 2026) (DAP, 2026b). Los criterios de cada clase vienen del estudio básico de amenaza (EBA) de la Universidad EAFIT, Anexo 16 (DAP, 2026a).

**Preparación (cálculo propio, ya hecho en el Producto 1).**
- Inundación y avenidas torrenciales: las manchas se vectorizaron de las láminas en PDF. Archivos: `POT2026_amenaza_inundacion_9377.gpkg` y `POT2026_amenaza_avenidas_torrenciales_9377.gpkg`, con tres clases (alta, media, baja).
- Movimientos en masa: la clase de cada celda se reconstruyó de la imagen de la lámina y quedó en un ráster de 972 × 762 celdas (unos 32 m por lado). Archivo: `POT2026_amenaza_movimientos_masa_clase_9377.tif` (1 = alta, 2 = media, 3 = baja, 0 = fuera). Para medir áreas, cada celda se vectoriza tal cual (conectividad de 4 vecinos), sin remuestrear.
- Las áreas de estas capas coinciden con las del EBA con diferencias menores de 0,3 % en inundación y avenidas torrenciales, y de hasta 1,1 puntos en movimientos en masa (verificación del Producto 1). En inundación, el estudio base conserva en algunas quebradas la zonificación del POT 2014; por eso las quebradas canalizadas o embovedadas entran como amenaza alta.

**Criterio de cada clase** (según el estudio base): inundación, crecida con período de retorno de 10 años (alta), 100 años (media) y 500 años (baja); avenidas torrenciales, por el índice de intensidad del flujo (alta cerca de 50 m³/s², media entre 1 y 50, baja menor a 1); deslizamientos, por la pendiente y la proporción de deslizamientos registrados (alta: pendiente mediana cercana a 30° y alrededor del 57 % de los deslizamientos registrados).

**Cálculo.**
- Porcentaje de un territorio en una clase = área de la clase dentro del territorio ÷ área del territorio × 100. La intersección es vectorial y exacta.
- Una limitación de cobertura: los deslizamientos cubren todo el Distrito (alta 37,8 %, media 15,3 %, baja 46,8 %; suman 99,9 % por huecos de la reconstrucción), mientras que la inundación y las avenidas torrenciales solo cubren sus manchas.

**Cifras que salen de aquí** (Distrito): deslizamientos alta 14.214 ha (37,8 %); inundación alta 573 ha (1,5 %), media 195 ha, baja 364 ha; avenidas torrenciales alta 586 ha (1,6 %), media 207 ha, baja 170 ha.

### 3.2 Multiamenaza (índice de 1 a 27)

**Qué es.** Criterio del equipo, no normativo. En cada amenaza, baja = 1, media = 2 y alta = 3. El índice es el producto de las tres: deslizamientos × inundación × avenidas torrenciales. Fuera de la mancha de inundación o de avenidas torrenciales, el factor vale 1, igual que «baja».

**Por qué un criterio propio.** No se encontró un indicador nacional de multiamenaza. Las guías nacionales tratan cada amenaza por separado: movimientos en masa (SGC, 2017), avenidas torrenciales (Ramos Cañón et al., 2021, publicación del SGC) e inundación (IDEAM, 2017). Las orientaciones del Ministerio de Vivienda y el SGC para incorporar la gestión del riesgo en el ordenamiento (MVCT y SGC, 2022) no definen un índice que las combine, y el índice municipal de riesgo del DNP mide riesgo, con población y capacidades, no amenaza. Las herramientas internacionales que combinan amenazas toman el valor máximo (ThinkHazard!), un promedio geométrico (INFORM) o suman niveles codificados; no se encontró ninguna que multiplique clases 1, 2 y 3.

**Procedimiento exacto** (`exporta_multiamenaza.py`, capa `multiamenaza_piezas`).
1. Se parte el Distrito en tres clases de deslizamientos (baja, media, alta) con la capa vectorizada.
2. Para inundación y para avenidas torrenciales se definen tres clases: alta = mancha alta; media = mancha media sin la alta; baja o ausente = el resto del Distrito.
3. Se intersectan las 27 combinaciones posibles. Cada pieza guarda sus tres clases, su índice y su área. Se descartan piezas de menos de 1 m².
4. Resultado: 27 piezas que cubren el 99,88 % del Distrito (el resto son huecos de la reconstrucción de las capas).

**Valores posibles.** Solo diez: 1, 2, 3, 4, 6, 8, 9, 12, 18 y 27. El índice es ordinal: 27 no es «27 veces» peor que 1. El producto hace que dos amenazas medias (2 × 2 = 4) pesen más que una alta sola (3).

**Áreas por valor del índice (Distrito).** 1: 16.753 ha · 2: 5.968 · 3: 14.341 · 4: 26 · 6: 98 · 8: menos de 1 · 9: 261 · 12: 2 · 18: 46 · 27: 101.

**Índice de 4 o más.** Un factor solo llega a 3 como máximo; por eso un índice de 4 o más solo puede salir de dos o más amenazas por encima de baja. Se usa para marcar superposición: **534 ha (1,4 % del Distrito)**.

**Valores por territorio.** En la tabla por comuna y corregimiento, «mediana» es el valor del índice en el que se acumula el 50 % del área del territorio (ordenados de menor a mayor), y «% con índice ≥ 4» es la suma de las áreas de las piezas con índice de 4 o más sobre el área cubierta del territorio.

**Límites.** «Baja» y «fuera de la mancha» valen igual (1). Los deslizamientos cubren todo el Distrito, así que el índice sigue casi siempre a los deslizamientos y se separa de ellos en el valle y las quebradas. No pondera consecuencias (personas, viviendas) ni encadenamientos entre amenazas.

### 3.3 Amenaza por incendios forestales

**Fuente.** Capa «Amenaza de incendios forestales» del plan municipal de gestión del riesgo (servidor de mapas de la Alcaldía, `ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer/8`). 409 polígonos con magnitud baja (381), alta (21) y media (7), uso actual y cobertura homogénea (377 de los 409 son «pastos enmalezados»). La capa no trae fecha de corte.

**Cálculo.** Área de cada magnitud recortada a los barrios (dentro del Distrito): alta 296 ha, media 95 ha, baja 2.895 ha. Son zonas susceptibles de cobertura vegetal, no todo el Distrito. No entra en el índice de multiamenaza.

**Límite.** Son escenarios de amenaza, no eventos con coordenadas. El ráster de susceptibilidad a incendios del convenio DAGRD–SIATA no se usa: tiene 38 valores distintos, cubre el 85 % del Distrito y no coincide con los incendios observados.

### 3.4 Calor: temperatura de la superficie

**Fuente.** Paquete de datos «Islas de calor» del Plan de Acción para el Cambio y la Variabilidad Climática del Valle de Aburrá (imágenes Landsat de la mañana, 30 m, mediana de 2013 a 2016), procesado a partir de Guzmán Echavarría (2018). La autoría formal del paquete está por confirmar.

**Cálculo (hecho en el Producto 1, `8.1_datos_LST_*`).** Mediana de los píxeles de 30 m de cada territorio. Hay dos versiones: la mediana directa («mediana») y la que descuenta el efecto de la pendiente y la orientación de las laderas («sin pendiente»). 271 de los 332 barrios tienen valor.

**Cifra de la tarjeta.** Diferencia entre comunas y corregimientos = promedio de las medianas de los territorios, ponderado por el número de píxeles de cada territorio. Resultado: comunas 33,0 °C y corregimientos 24,7 °C (diferencia de 8,3 °C); sin el efecto de la pendiente, 30,1 y 26,7 °C (diferencia de 3,4 °C).

**Límite.** Es temperatura de la superficie vista por satélite, no la temperatura del aire a 2 m. La temperatura del aire medida es un vacío (la red de estaciones del SIATA se pide por solicitud formal).

---

## 4. Soluciones: medidas que hoy están registradas

«Medida existente» significa lo que hoy aparece en el servidor de mapas de la Alcaldía (consulta del 8 de octubre de 2026). No es lo previsto ni lo planeado.

### 4.1 Arbolado y verde urbano

Hay tres lecturas del arbolado por barrio. No forman un índice compuesto: cada una responde una pregunta distinta.

1. **Árboles por hectárea (inventario).** Fuente: Sistema de Árbol Urbano, capa «Arbol Urbano» (`VC_Gestion_Ambiental/MapServer/0`), con 238.023 árboles de Medellín descargados; 237.384 caen dentro de los polígonos de barrios (los otros 639 quedan en el borde o fuera). Árboles por hectárea = número de árboles del inventario dentro del barrio ÷ área del barrio en ha. No cuenta bosques ni parques sin inventariar, ni arbolado privado.
   - Estado de los árboles dentro de barrios: 202.527 sanos (85,3 %), 6.718 muertos, 4.180 enfermos; el resto, sin estado conocido.
   - En los 269 barrios urbanos: 199.217 árboles en 10.056 ha = 19,8 árboles por hectárea (cifra de la tarjeta).
2. **% de cobertura arbórea (espacios verdes urbanos, 2019).** Fuente: inventario de espacios verdes urbanos del Área Metropolitana y la Universidad Nacional (2019; contrato 1344 de 2018), `VA_SistemaArbolUrbano_Base/MapServer/5`. Son polígonos dibujados sobre fotografías aéreas con una cobertura dominante (árboles, grama o pasto, arbustos, jardín, tierra…); en Medellín se delimitaron desde 4 m². Cada polígono se recorta al límite de cada barrio (intersección exacta). Cobertura arbórea % = área de los polígonos con cobertura «Árboles» dentro del barrio ÷ área del barrio × 100 (tope 100). Dentro de los barrios hay 3.756 ha de espacios verdes, de las cuales 1.361 ha son «Árboles», 2.179 ha pasto, 85 ha arbustos y 39 ha jardín.
3. **% de espacios verdes.** Igual que la anterior, sumando todos los polígonos verdes (árboles, pasto, arbustos, jardín y otros).

**Mapas por barrio.** Cinco clases con la misma cantidad de barrios cada una (quintiles de los 268 barrios urbanos de 5 ha o más). Cortes: árboles por hectárea 7,5 · 12,1 · 17,5 · 24,4; cobertura arbórea 1,9 · 4,7 · 8,7 · 16,7 %; espacios verdes 11,1 · 19,0 · 29,7 · 42,4 %. Veredas y barrios rurales aparecen sin evaluar.

**Por qué la marca de calor usa la cobertura arbórea.** Se compararon las tres lecturas con la temperatura de superficie sin pendiente de los 268 barrios urbanos (correlación de Pearson): árboles por hectárea −0,19; cobertura arbórea −0,54; espacios verdes en total −0,77. Cuanto más negativa, más se asocia el verde con menos calor. El inventario cuenta árboles en espacio público; la cobertura arbórea mide qué parte del barrio está bajo árboles.

**Otras capas de verde.**
- Zonas verdes con potencial verde: 1.098 polígonos (22 ha), del inventario de zonas verdes (`VC_Rec_Natural_Renovable/MapServer/4`, campo `potencial_verde` = «Si»). Son sobre todo franjas de amoblamiento (577), antejardines (257) y separadores (81).
- Techos verdes: polígonos de los espacios verdes urbanos con `cubierta_verde` = «Si» (363 que tocan barrios; 2,1 ha). Es una marca del inventario de 2019, no un inventario de techos.
- Ecoparques: 81 polígonos (`VC_Gestion_Ambiental/MapServer/2`); 71 de quebrada y otros cuerpos de agua, 6 de cerro, 3 de borde.
- Corredores verdes del POT 2014: 83 tramos (`vivienda_ciudad_terri/VC_Dllo_Territorial_Planificado/MapServer/3`); actuación: generación 49, mantenimiento 17, recuperación 17. Son trazados «posibles» del POT 2014, no los corredores construidos ni las cifras oficiales de la Secretaría de Medio Ambiente.

**Límites.** Las fuentes son de fechas distintas (temperatura 2013–2016, espacios verdes 2019, inventario de árboles de octubre de 2026). El área del barrio incluye calles y edificios. No mide altura, edad ni sombra real de la copa. Al corregir geometrías inválidas, 9 de los 189.014 polígonos de espacios verdes quedan sin área y no entran al cálculo.

### 4.2 Obras de ladera y quebrada

- **Obras de mitigación** (`VM_DAGRD/MapServer/3`): 131 registros, todos «terminada», de 2016 a 2022 (55 en 2016, 11 en 2017, 24 en 2018, 17 en 2020, 17 en 2021, 7 en 2022); una no tiene ubicación, así que el mapa muestra 130. En la descripción aparecen taludes (49), senderos (44), cunetas (43), muros (20), escalas (17), gaviones (6), filtros (5) y canales (4). Se concentran en Popular (47) y Villa Hermosa (40) por presupuesto participativo. **El valor de la obra se repite por contrato: no se puede sumar.**
- **Monitoreo geotécnico** (`VM_DAGRD/MapServer/8`): 68 instrumentos, 53 activos, 14 fallados y 1 no encontrado, con fecha de la última lectura.
- **Estudios y diseños** (`VM_DAGRD/MapServer/2`): 237 polígonos (geotécnicos, hidrológicos e hidráulicos y diseños de obra). Muestran dónde hay estudio, no obra.

**Conteos por barrio.** Obras y monitoreo: puntos dentro del barrio. Estudios: polígonos que tocan el barrio. 42 barrios tienen alguna obra y 22 algún instrumento.

**Límite.** El registro cubre solo el programa 2016–2022. No incluye obras de otras entidades ni la canalización de quebradas. El inventario de tramos de quebrada (`VA_Interv_Rec_Hidrico/MapServer/0`, 10.312 tramos) trae tipo de tramo y material de lecho en códigos sin diccionario; no se usa hasta tenerlo.

### 4.3 Alerta temprana y evacuación

`VC_Gestion_Riesgo/MapServer/` capas 6 (alarmas, 11), 12 (sensores de nivel, 13), 10 (puntos de encuentro, 39) y 11 (rutas de evacuación, 101). Están en seis quebradas de respuesta rápida: Doña María, La Picacha, La Iguaná, Malpaso, Potreritos y Santa Elena. Conteo por barrio: puntos dentro del barrio; rutas que lo tocan. 21 barrios tienen algún elemento.

**Límite.** Es ubicación de elementos; falta el tiempo de aviso, el alcance de la alarma y la cobertura real.

---

## 5. Dónde falta (marcas por barrio)

Una marca cruza un problema alto con una solución que el registro no muestra. **No dice que allí falte una obra; dice que el registro no la muestra.** Los umbrales son criterio del equipo y se calculan con los cuartiles de los barrios evaluados.

| Marca | Regla | Umbrales | Barrios |
|---|---|---|---|
| Calor alto y poco arbolado | barrio urbano de 5 ha o más con temperatura de superficie sin pendiente en el cuartil superior **y** cobertura arbórea en el cuartil inferior | ≥ 31,6 °C y ≤ 2,3 % | 34 de 268 |
| Deslizamiento alto sin obra ni monitoreo | barrio o vereda de 5 ha o más con deslizamiento alto en el cuartil superior **y** sin obras ni instrumentos | ≥ 31 % del área; obras = 0 y monitoreo = 0 | 51 de 331 |
| Avenida torrencial alta sin alerta temprana | barrio o vereda de 5 ha o más con amenaza torrencial alta en el cuartil superior de los que tienen alguna **y** sin ningún elemento de alerta | ≥ 2,7 ha; alarmas + sensores + puntos de encuentro + rutas = 0 | 50 de 331 |

**Cómo se llega a cada número.**
- Calor: 67 barrios cumplen el umbral de temperatura y 67 el de cobertura arbórea; 34 cumplen ambos. Las marcas están en las comunas 10 (8 barrios), 06 (5), 11 (5), 15 (5), 12 (3), 05 (2), 09 (2), 16 (2), 13 (1) y 14 (1).
- Ladera: 83 barrios tienen deslizamiento alto en el cuartil superior; 32 de ellos tienen alguna obra o instrumento; quedan 51.
- Alerta: 58 barrios tienen 2,7 ha o más de amenaza torrencial alta; 8 de ellos tienen elementos de alerta; quedan 50. Se usa el área absoluta y no el porcentaje, porque el riesgo depende de cuánta quebrada hay y no de qué tan grande es el barrio. No se considera el alcance de una alarma: un barrio vecino a otro con alarma aparece marcado.

**Qué falta decidir con el equipo** (también en la página, recuadro «Comentario para el equipo»):
- El criterio de calor es relativo (el cuarto más caliente de los barrios urbanos de toda la ciudad): siempre marca barrios y deja por fuera barrios calientes que no llegan al cuartil. Hay comunas calientes en conjunto, y ahí un umbral relativo no dice qué tan peligrosa es la temperatura.
- Alternativa: definir el calor con un umbral de riesgo, es decir, la temperatura desde la cual el cuerpo o el contacto con una superficie corren peligro (por ejemplo, el asfalto al mediodía). Para el cuerpo suele usarse la temperatura fisiológica equivalente; «biotemperatura», en sentido estricto, es otro concepto (promedio de temperaturas entre 0 y 30 °C, usado en zonas de vida). Valores locales ya recopilados: en la Unidad Deportiva Atanasio Girardot el asfalto tuvo una mediana de 37,5 °C y la grama sintética llegó a 60–70 °C al mediodía (vuelos con dron; Guzmán Echavarría, 2018).
- Por tiempo, la definición se afina con los datos ya recopilados; no se piden datos nuevos hasta decidirla.

---

## 6. Cifras de las tarjetas de resumen

| Cifra | Valor | Cómo se calcula | Sección |
|---|---|---|---|
| Deslizamientos, amenaza alta | 37,8 % del Distrito (14.214 ha) | área de la clase alta ÷ área del Distrito | 3.1 |
| Inundación, amenaza alta | 573 ha (1,5 %) | área de la mancha alta dentro del Distrito | 3.1 |
| Avenidas torrenciales, amenaza alta | 586 ha (1,6 %) | ídem | 3.1 |
| Dos o más amenazas superpuestas | 534 ha (1,4 %) | suma de las piezas con multiamenaza ≥ 4 | 3.2 |
| Diferencia de temperatura de superficie | 8,3 °C entre comunas y corregimientos (3,4 °C sin pendiente) | promedio de medianas por territorio, ponderado por píxeles | 3.4 |
| Árboles inventariados | 237.384; 19,8 por hectárea en barrios urbanos | árboles dentro de barrios; árboles de los 269 barrios urbanos ÷ su área | 4.1 |
| Calor alto y poco arbolado | 34 barrios de 268 urbanos | regla de la sección 5 | 5 |
| Deslizamiento alto sin obra ni monitoreo | 51 barrios de 331 | ídem | 5 |
| Torrencial alta sin alerta temprana | 50 barrios de 331 | ídem | 5 |

---

## 7. Tablas y fichas de la página

- **Tabla por comuna y corregimiento.** Una fila por territorio (23). Porcentajes de amenaza = área de la clase ÷ área del territorio. Temperatura = mediana de los píxeles de 30 m del territorio. «Árboles por ha» = árboles dentro de los barrios de la comuna ÷ área de esos barrios (solo comunas; en corregimientos el inventario es urbano). «Barrios con brecha» = número de barrios del territorio con cada marca (calor · ladera · alerta).
- **Ficha del barrio** (al hacer clic en el mapa): temperatura, amenaza alta de deslizamientos y de avenidas torrenciales, árboles y cobertura arbórea, obras, monitoreo, alerta temprana y las marcas del barrio. Si la capa de multiamenaza está activa, agrega el valor del índice en el punto: dentro de una mancha de inundación o torrencial lo da la pieza que contiene el punto; fuera, la clase de deslizamientos.
- **PARTE 5 (foto de la base de variables).** Conteos tomados de la base v1 del tablero (`Producto9_tablero_base_variables_PAC_v1.html`): por cada bloque (inundaciones, movimientos en masa, avenidas torrenciales, isla de calor) cuántas variables están asignadas y a qué escala se miden (comuna, estación, municipio o ciudad), y cuántas nombran el fenómeno en el nombre de la variable (búsqueda de texto). Es un conteo propio sobre la base del tablero, no una medición.
- **Descargas.** La página trae dos CSV: por comuna y corregimiento y por barrio y vereda (los mismos de `A_tablas`, con los nombres de columna de la página).

---

## 8. Nota de impacto de las medidas

La tabla de la PARTE 4 ordena las medidas por la evidencia local disponible, no por un cálculo de impacto. «Confianza» dice qué tan bien respalda esa evidencia el efecto esperado en Medellín. Las cifras vienen del catálogo integrado de medidas de adaptación (hoja «Enfriamiento ADA-06») y de sus fuentes; **son comparaciones entre lugares o temperaturas de superficie, no el efecto de plantar un árbol donde no lo hay.**

| Medida | Evidencia usada | Fuente |
|---|---|---|
| Arbolado | Barrios del valle con arbolado quedan unos 2 °C más frescos que barrios comparables sin él: compacto de baja altura 33,0 → 31,0 °C; abierto de mediana altura 30,5 → 28,5 °C. Sobre superficies duras, la copa baja la temperatura de contacto 8,5 °C frente al concreto y 11 °C frente al asfalto | Guzmán Echavarría (2018), figuras 3-7 y 3-15 (valores leídos de gráficos, ±0,5 °C) |
| Contraste del centro | Con cielo despejado, el Centro es 6 °C más caliente que el barrio arbolado Tricentenario (2 °C en días nublados) | Martínez Osorio (2017), conclusiones |
| Parques y zonas verdes pequeñas | 1 a 3 °C en parques de 0,5 a 2 ha; hasta 350 a 400 m de alcance en parques grandes. Literatura de otros climas | Damarla y Chattopadhyay (2025), citando otros estudios |
| Piso de prudencia | Sitio vegetado unos 0,5 °C más fresco en aire a 2 m, sin diferencia significativa | Bini et al. (2026) |
| Corredores verdes | «Hasta 2 °C» (Secretaría de Medio Ambiente, sin metodología publicada); la prensa reporta 3,5 a 5 °C en puntos con sombra | catálogo integrado de medidas |
| Techos | En la campaña local no se midió ningún techo verde; el techo de PVC blanco no resultó más fresco que el gris | Guzmán Echavarría (2018) |
| Obras de ladera | Línea base de 14 % de obras de mitigación y protección ejecutadas, meta de 22 % en 2023 | Plan de Acción Climática 2020, Tabla 1, vía PASCCM Tomo III |
| Alerta temprana | Línea base de 24 heridos por desastres naturales, meta de 18 en 2023 (año de la línea base sin confirmar) | ídem |
| Drenaje urbano sostenible | Sin inventario local; obras anunciadas o en construcción (Parque Primavera Norte, cancha de Villa Niza, Gran Parque Medellín) | Alcaldía de Medellín, sala de prensa |

Sobre la intuición de que el arbolado es la medida de mayor impacto: se sostiene para el calor, con evidencia local. Para inundación, deslizamientos e incendios, el efecto depende de la especie, la ubicación y el suelo, y no hay cifras locales. Un bosque nativo húmedo arde menos que un pastizal seco, y una plantación de pino arde más: es una hipótesis por documentar, no una cifra.

---

## 9. Advertencias y límites conocidos

1. Las amenazas del POT 2026 son preliminares (láminas en PDF); se reemplazan cuando haya capas oficiales.
2. Las marcas de «dónde falta» dependen de umbrales por cuartil y de registros parciales. No son un diagnóstico de necesidad.
3. Los registros de obras cubren solo el programa 2016–2022; el valor de las obras se repite por contrato.
4. El inventario de árboles no es un censo: cuenta individuos en espacio público.
5. Las fuentes tienen fechas distintas (2013–2016, 2019, 2026). Los cruces entre ellas son indicativos.
6. El servidor de mapas de la Alcaldía cambia en vivo: un conteo repetido otro día puede diferir en unidades (el de árboles pasó de 238.022 a 238.024 durante la descarga). Las cifras de este documento son las del corte indicado.
7. El servidor dio errores 503 al descargar los árboles con muchas peticiones en paralelo; la descarga se completó con menos hilos y reintentos.
8. No hay capa ni inventario de sistemas urbanos de drenaje sostenible, de techos verdes ni de jardines de lluvia.
9. El mapa base es de Esri y OpenStreetMap; antes de publicar fuera del equipo hay que revisar sus términos de uso.
10. **Falta anclar la información a la normatividad nacional e internacional** en la que se sustenta la plataforma (por ejemplo, la Ley 1523 de 2012, el Decreto 1077 de 2015 y el Marco de Sendai, que ya aparecen en el catálogo integrado de medidas). Esa conexión, capa por capa y cifra por cifra, todavía no está hecha; la hoja «Cobertura documental» del catálogo es el punto de partida.

---

## 10. Cómo se reproduce (código en `04_CODIGO/`)

Orden de ejecución (Python con geopandas, rasterio, shapely, pandas, numpy y openpyxl; en este trabajo se usó `uv`):

1. `inventario_capas.py`: lista las 2.608 capas del servidor de mapas (consulta del 8 de octubre de 2026) para buscar datos de medidas.
2. `descarga_medidas.py`: descarga las capas elegidas en EPSG:9377 con paginación y reintentos.
3. `datos_mapa.py` (con `parche_datos_v3.py`): amenazas, temperatura y multiamenaza por comuna y corregimiento; produce `mapa_datos.json`.
4. `medidas_calculo.py`: estadísticas por barrio (amenazas, incendios, árboles, espacios verdes, obras, monitoreo, alerta temprana).
5. `medidas_json.py`: umbrales, marcas, resumen por comuna, geometrías para la página y la base en Excel.
6. `exporta_multiamenaza.py` y `exporta_paquete_p9.py`: capas SIG y tablas de `02_DATOS/`.
7. `fusiona.py` y `armar_html_v2.py` (con `plantilla.html` y Leaflet 1.9.4): arman la página.

Las rutas de los scripts son las del equipo del autor (Drive del proyecto); hay que ajustarlas si se ejecutan en otro computador.

---

## 11. Datos: fuentes y fechas

| Dato | Proveedor | Dónde | Consulta | Vigencia |
|---|---|---|---|---|
| Amenaza por inundación, avenidas torrenciales y movimientos en masa (POT 2026) | DAP, revisión de mediano plazo del POT | Cartografía 1, láminas 6, 7 y 5; Anexo 16 (EBA) | agosto de 2026 | 2026, preliminar |
| Límites de comunas, corregimientos, barrios y veredas | Alcaldía de Medellín (GeoMedellín) | `mapas_nacionales/VC_Limite_Politico_Admtivo/MapServer` | septiembre de 2026 | 17-dic-2014 |
| Temperatura de la superficie | Plan de Acción para el Cambio y la Variabilidad Climática del Valle de Aburrá (paquete «Islas de calor») | carpeta compartida `Doc_Cambio climático MED`, archivo `31. Islas de calor AMVA.zip` | septiembre de 2026 | 2013–2016 |
| Árbol urbano | Sistema de Árbol Urbano, Alcaldía de Medellín | `ambiente_dllo_sost/VC_Gestion_Ambiental/MapServer/0` | 8–9 oct 2026 | vigente |
| Espacios verdes urbanos | Área Metropolitana del Valle de Aburrá y Universidad Nacional, Sede Medellín | `ambiente_dllo_sost/VA_SistemaArbolUrbano_Base/MapServer/5` | 8–9 oct 2026 | 2019 |
| Zonas verdes con potencial verde | Alcaldía de Medellín (ambiente y desarrollo sostenible) | `ambiente_dllo_sost/VC_Rec_Natural_Renovable/MapServer/4` | 8–9 oct 2026 | sin fecha |
| Ecoparques | Secretaría de Medio Ambiente | `ambiente_dllo_sost/VC_Gestion_Ambiental/MapServer/2` | 8–9 oct 2026 | sin fecha |
| Corredores verdes (trazados) | DAP, POT 2014 (Acuerdo 48 de 2014) | `vivienda_ciudad_terri/VC_Dllo_Territorial_Planificado/MapServer/3` | 8–9 oct 2026 | 17-dic-2014 |
| Obras de mitigación, monitoreo geotécnico, estudios | DAGRD | `ambiente_dllo_sost/VM_DAGRD/MapServer/` capas 3, 8 y 2 | 8–9 oct 2026 | 2016–2022; monitoreo con fecha de lectura |
| Alarmas, sensores de nivel, puntos de encuentro, rutas de evacuación | DAGRD | `ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer/` capas 6, 12, 10 y 11 | 8–9 oct 2026 | vigente |
| Amenaza por incendios forestales | DAGRD, plan municipal de gestión del riesgo | `ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer/8` | 8–9 oct 2026 | sin fecha de corte |

Servidor de mapas: `https://www.medellin.gov.co/servidormapas/rest/services/` (lectura pública). Catálogo geográfico con los metadatos de cada capa: `https://www.medellin.gov.co/giscatalogacion`. El inventario de todas las capas evaluadas, con lo que falta, está en `02_DATOS/Inventario_mapas_medidas_Distrito_v1.xlsx`.

---

## 12. Referencias

Los PDF de las fuentes del Producto 1 están en la carpeta compartida `01_Fuentes_y_bibliografia` (y en el respaldo `00_RESPALDO_PAC_2026_Referencias_7.1_8.1_8.5_8.6` del Drive del Producto 1). El nombre del archivo, cuando existe, va después de la flecha.

### Amenazas, ordenamiento y gestión del riesgo

- Departamento Administrativo de Planeación [DAP]. (2026a). *Anexo 16. Elaboración de estudios básicos de amenaza por movimientos en masa, inundación y avenidas torrenciales, para la inclusión de la gestión del riesgo en la revisión del POT Distrital de Medellín, Antioquia* [Informe técnico elaborado por la Universidad EAFIT, revisión de mediano plazo del POT]. Alcaldía de Medellín. (El portal lo rotula «Anexo 15»; la carátula dice «Anexo 16».) → `DAP_2026a_Anexo16_Informe_EBA.pdf`
- Departamento Administrativo de Planeación [DAP]. (2026b). *Cartografía 1* [Láminas 1 a 10 de 37, revisión de mediano plazo del POT, agosto de 2026]. Alcaldía de Medellín. https://www.medellin.gov.co/es/transparencia/plan-de-ordenamiento-territorial-de-medellin/que-es-pot/ → `DAP_2026b_Cartografia_1_POT2026.pdf`
- Concejo de Medellín. (2014). *Acuerdo 48 de 2014 (Plan de Ordenamiento Territorial de Medellín)*. Capas protocolizadas en el servidor de mapas de la Alcaldía.
- Servicio Geológico Colombiano [SGC]. (2017). *Guía metodológica para la zonificación de amenaza por movimientos en masa, escala 1:25.000* [Colección Guías y Manuales]. https://www2.sgc.gov.co/Archivos/GM(2017).pdf
- Ramos Cañón, A., et al. (2021). *Guía metodológica para zonificación de amenaza por avenidas torrenciales* [Libros del Servicio Geológico Colombiano; elaborada con la Pontificia Universidad Javeriana]. https://doi.org/10.32685/9789585313156 (texto: https://libros.sgc.gov.co/index.php/editorial/catalog/download/75/68/540?inline=1)
- Instituto de Hidrología, Meteorología y Estudios Ambientales [IDEAM]. (2017). *Guía metodológica para la elaboración de mapas de inundación* (110 pp.). Bogotá: IDEAM. https://ideam.gov.co/file-download/download/public/2879
- Ministerio de Vivienda, Ciudad y Territorio [MVCT] y Servicio Geológico Colombiano [SGC]. (2022). *Orientaciones técnicas para la incorporación de la gestión de riesgo de desastres en la planificación del ordenamiento territorial* (70 pp.; Convenio MVCT 719 de 2020 / SGC 010 de 2020). https://minvivienda.gov.co/sites/default/files/documentos/orientaciones-tecnica-pra-incorporacion-de-la-gestion-de-riesgo-de-desatres-en-la-planificacion-del-ordenamiento-territorial_mvct_2022.pdf
- Departamento Nacional de Planeación [DNP]. (2022). *Índice municipal de riesgo de desastres ajustado por capacidades* [Presentación, diciembre de 2022; publicación original, 2018]. https://www.dnp.gov.co/LaEntidad_/subdireccion-general-prospectiva-desarrollo-nacional/direccion-ambiente-desarrollo-sostenible/Paginas/indice-municipal-de-gestion-de-riesgo-ajustado-por-capacidades.aspx
- Banco Mundial y Global Facility for Disaster Reduction and Recovery [GFDRR]. (s. f.). *ThinkHazard!* https://thinkhazard.org (consultado en la revisión de octubre de 2026; no se leyó la metodología en detalle).
- Joint Research Centre de la Comisión Europea. (s. f.). *INFORM Risk Index*. https://drmkc.jrc.ec.europa.eu/inform-index (ídem).
- Área Metropolitana del Valle de Aburrá y Universidad Nacional de Colombia, Sede Medellín. (2019). *Análisis de la conectividad ecológica funcional y estructural en el Área Metropolitana del Valle de Aburrá* [Contrato 1344 de 2018]. Fuente del inventario de espacios verdes urbanos, según los metadatos de la capa.

### Calor, arbolado y medidas

- Guzmán Echavarría, G. (2018). *Análisis de la influencia del diseño urbano en la meteorología del Valle de Aburrá* [Tesis de maestría, Universidad Nacional de Colombia, sede Medellín]. https://redcol.minciencias.gov.co/Record/UNACIONAL2_f43ac94cc837366e182f7cef31609571 → `2018_UHI_Guzman_tesis_maestria.pdf`
- Martínez Osorio, A. (2017). *Islas de calor en el área urbana del Valle de Aburrá* [Tesis de maestría en Ingeniería, Recursos Hidráulicos, Universidad Nacional de Colombia, Sede Medellín]. → `2017_UHI_UNAL_MSC.pdf` (solo se leyeron las conclusiones)
- Damarla, S. P. y Chattopadhyay, S. (2025). Green infrastructure as a nature-based solution for urban heat island mitigation in Vijayawada: a multitemporal analysis using remote sensing and GIS (2013–2023). *IOP Conference Series: Earth and Environmental Science, 1579*, 012012. https://doi.org/10.1088/1755-1315/1579/1/012012 (los valores de enfriamiento que reporta son citas de otros estudios: Li et al., 2024; Anderson y Gough, 2022; Kim et al., 2023; Javaid et al., 2025; Agathangelidis et al., 2025)
- Bini, M. E., Balzan, M. V. y Bonoli, A. (2026). Nature-based solutions for urban heat island effect mitigation: the case study of Isla, Malta. *Environments, 13*(5), 276. https://doi.org/10.3390/environments13050276
- Paquete de datos «Isla de calor» (temperatura de superficie Landsat, 30 m) del Plan de Acción para el Cambio y la Variabilidad Climática del Valle de Aburrá, obtenido de la carpeta compartida `Doc_Cambio climático MED` de la Alcaldía (archivo `31. Islas de calor AMVA.zip`); su producto se cita a través de Guzmán Echavarría (2018). Falta confirmar la autoría formal del paquete.
- Secretaría de Salud de Medellín. (2021). *Plan de adaptación en salud al cambio y variabilidad climática, Medellín 2020-2050: Tomo I. Análisis de contexto, de salud y variables climáticas*. Alcaldía de Medellín. → `SecSalud_2021_PASCCM_Tomo_I.pdf`
- Secretaría de Salud de Medellín. (s. f.). *Plan de adaptación en salud al cambio y variabilidad climática, Medellín 2020-2050: Tomo II. Análisis de vulnerabilidad poblacional en salud al cambio y variabilidad climática*. Alcaldía de Medellín. → `SecSalud_sf_PASCCM_Tomo_II.pdf`
- Secretaría de Salud de Medellín. (s. f.). *Plan de adaptación en salud al cambio y variabilidad climática, Medellín 2020-2050: Tomo III*. Alcaldía de Medellín. Fuente de las metas del Plan de Acción Climática 2020 (Tablas 1 y 2). El PDF completo no está en la carpeta de fuentes del Producto 1; los valores se tomaron del catálogo integrado de medidas.
- Alcaldía de Medellín. (2020). *Plan de Acción Climática de Medellín 2020–2050*. Metas leídas a través del Tomo III del PASCCM; el documento original no se releyó.
- Equipo del proyecto. (2026). *Catálogo integrado de medidas de adaptación* (versión 3, 5 de octubre de 2026) [Libro de Excel]. Hojas «Enfriamiento ADA-06», «Línea base y metas» y «Cobertura documental».

### Metodología de seguimiento, evaluación y reporte

- C40 Cities Climate Leadership Group. (s. f.). *C40 City Monitoring, Evaluation and Reporting Guidance: Guidance for climate action planning teams* (38 pp.; documento de 2020–2021). Base del capítulo «Comentarios» de la página (leída completa; las definiciones y las preguntas están parafraseadas). Copia consultada: https://www.cakex.org/sites/default/files/documents/C40%20Cities%20(2020)%20CAP%20Monitoring,%20Evaluation%20and%20Reporting%20(MER)%20Guidance.pdf

### Datos y programas

- Alcaldía de Medellín. (s. f.-a). *Servidor de mapas (ArcGIS REST Services)* [Conjuntos de datos geográficos]. https://www.medellin.gov.co/servidormapas/rest/services/ (consultado el 8 y 9 de octubre de 2026).
- Alcaldía de Medellín. (s. f.-b). *Catálogo geográfico de la Alcaldía de Medellín* [Metadatos]. https://www.medellin.gov.co/giscatalogacion
- Alcaldía de Medellín. (s. f.-c). *VC_Limite_Politico_Admtivo* [Conjunto de datos]. https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Limite_Politico_Admtivo/MapServer
- Agafonkin, V. (2023). *Leaflet 1.9.4* [Programa, licencia BSD-2]. https://leafletjs.com
- Esri. (s. f.). *Mapas base «Light Gray Canvas», «Dark Gray Canvas» y «World Imagery»* [Teselas de mapa].
- Colaboradores de OpenStreetMap. (s. f.). *OpenStreetMap* [Teselas de mapa]. https://www.openstreetmap.org/copyright

---

## Anexo A. Columnas de las tablas

**`P9_barrios_veredas_indicadores_v2.csv`** (y capa `barrios_veredas_indicadores` del GeoPackage). Una fila por barrio o vereda (332).

| Columna | Qué es |
|---|---|
| `bid` | identificador del polígono en la capa oficial de barrios (`objectid`) |
| `codigo`, `nombre` | código y nombre del barrio o vereda |
| `comuna`, `comuna_nombre` | código y nombre de la comuna o corregimiento |
| `ha` | área del polígono (ha), en EPSG:9377 |
| `urbano` | verdadero si el código de comuna va de 01 a 16 |
| `mm_alta_ha`, `mm_media_ha`, `mm_baja_ha` | área en cada clase de deslizamientos* (ha) |
| `inu_*_ha`, `tor_*_ha` | ídem, inundación* y avenidas torrenciales* |
| `inc_alta_ha`, `inc_media_ha`, `inc_baja_ha` | área en cada magnitud de la amenaza por incendios forestales (ha) |
| `mm_alta`, `mm_media`, `mm_baja`, `inu_*`, `tor_*` | los mismos, en % del área del barrio |
| `lst_n` | temperatura de superficie, mediana del barrio sin efecto de la pendiente (°C, 2013–2016) |
| `arboles`, `arb_sanos`, `arb_muertos`, `arb_enfermos` | árboles del inventario dentro del barrio, por estado |
| `arb_ha` | árboles por hectárea = `arboles` ÷ `ha` |
| `sanos_pct` | % de árboles sanos |
| `evu_ha` | área de espacios verdes urbanos dentro del barrio (ha, 2019) |
| `evu_arboles_ha`, `evu_arbustos_ha`, `evu_pasto_ha`, `evu_jardin_ha` | por cobertura dominante (ha) |
| `evu_publico_ha` | espacios verdes de propiedad pública (ha) |
| `copa_pct` | cobertura arbórea (%) = `evu_arboles_ha` ÷ `ha` × 100, con tope de 100 |
| `verde_pct` | espacios verdes (%) = `evu_ha` ÷ `ha` × 100, con tope de 100 |
| `techos_n`, `techos_ha` | polígonos con cubierta verde marcada y su área |
| `pot_n`, `pot_ha` | zonas verdes con potencial verde (cuenta por centroide) y su área |
| `obras`, `monit`, `monit_activos`, `estudios` | obras de mitigación, instrumentos de monitoreo (y activos) y estudios |
| `alarmas`, `sensores`, `encuentro`, `rutas`, `sat_total` | elementos de alerta temprana y su suma |
| `f_calor`, `f_ladera`, `f_alerta` | marcas de «dónde falta» (verdadero o falso) |

**`P9_comunas_corregimientos_indicadores_v2.csv`.** Una fila por territorio (23).

| Columna | Qué es |
|---|---|
| `codigo`, `nombre`, `tipo`, `km2` | identificación y área |
| `mm_*`, `inu_*`, `tor_*` | % del territorio en cada clase de amenaza* |
| `lst`, `lst_n`, `cells` | temperatura de superficie (mediana y sin pendiente, °C) y número de píxeles de 30 m |
| `arboles`, `arb_ha` | árboles del inventario y árboles por ha (solo comunas) |
| `obras`, `monit`, `sat` | obras, instrumentos de monitoreo y elementos de alerta temprana |
| `br_calor`, `br_ladera`, `br_alerta`, `br_tot` | barrios del territorio con cada marca y total |
| `multiamenaza_mediana`, `multiamenaza_ge4_pct`, `multiamenaza_N_pct` | mediana del índice, % con índice ≥ 4 y % por cada valor (1, 2, 3, 4, 6, 8, 9, 12, 18, 27) |

**`P9_brechas_barrios_marcados_v2.csv`.** Una fila por barrio marcado y tipo de marca, con las variables que explican la marca.
