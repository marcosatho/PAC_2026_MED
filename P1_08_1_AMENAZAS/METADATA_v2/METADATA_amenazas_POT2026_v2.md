# Metadata — mapas de amenaza POT 2026, versión 2 (capas oficiales)

Fecha: 2026-10-18. Responsable de la preparación: Marcos Arango Tamayo (ITM), con apoyo de Claude.
La versión 1 (zonas vectorizadas de las láminas PDF y raster de movimientos en masa de ~32 m) **no se modificó ni se borró**: sigue en `01_DAGRD_SIATA_ESCENARIOS/02_DATOS_PREPARADOS/` y en `P1_08_1_AMENAZAS/FIGURAS/` del repositorio. La v2 vive en carpetas y archivos con sufijo `_v2`.

## 1. Fuente de la v2

| Dato | Valor |
|---|---|
| Archivo recibido | `YDRAY-GDB_Form_DiccTopolog.zip` (245 MB; fechas internas 2026-03-03 a 2026-10-15). Guardado sin modificar en `../01_DATOS_ORIGINALES/` (junto con `co255_2025_ebamedellin_AmeazasJulio26.gdb.rar`, el EBA de julio, 209 MB). |
| SHA-256 del zip | `a5a80c402fb76313fb1c4d1d4ce11a573671b9e1962e8a578d4d95f1da2e0de2` (RAR del EBA: `5222305573552daa4d8a1c321600e57752ae1f6548317b8d5cce6828506d0e76`; copia reparada del EBA en `../02_DATOS_PREPARADOS/EBA_amenazas_julio2026_reparada_9377.gpkg`, `51de173a3f5b5f6e…`) |
| Estado de la información (correo del DAP) | **No protocolizada**: sigue en revisión, análisis y validación del Concejo Distrital y es susceptible de cambios hasta su aprobación oficial. No todas las capas integran la revisión de mediano plazo: algunas traen ajustes parciales (inventarios, intervenciones ejecutadas) y otras se mantienen como en el Acuerdo 48 de 2014. Las tres figuras v2 lo declaran en una línea superior y en el pie. Trazabilidad capa por capa: `Trazabilidad_capas_POT2026_vs_2014_v2.xlsx` (esta carpeta). |
| Geodatabase | `mj_rev_pot_2025_med.gdb` (417 tablas; sistema MAGNA-SIRGAS 2018 / Origen-Nacional, EPSG:9377) |
| Diccionario de datos | `FO_GINF041_DiccDatosGeo_mj_rev_pot_2026.xlsx` (formato FO-GINF-041 del Departamento Administrativo de Planeación, DAP) |
| Resumen de topología | `Topologia.xlsx` (excepciones topológicas por capa; responsable: Luz Andrea Monsalve) |
| Procedencia | **Por confirmar**: quién la envió y si hay autorización de uso en el PAC (el P1 §4.5 dice que el uso formal de la información técnica del POT está sin resolver). Se asume, por instrucción de Marcos, que son los datos propios del POT 2026. |

Capas usadas (feature dataset `c_AmenazayRiesgo`):

| Capa en la gdb | Capa en la v2 | Polígonos | Elaboración (diccionario) |
|---|---|---|---|
| `gur_ar_amenaza_inundaciones` | `amenaza_inundacion` | 1.852 | 2026-05-17 |
| `gur_ar_amenaza_avtorrenciales` | `amenaza_avenidas_torrenciales` | 1.332 | 2026-05-17 |
| `gur_ar_amenaza_mov_masa` | `amenaza_movimientos_masa` | 13.805 | 2026-05-17 |

Campos conservados: `categoria` (Alta/Media/Baja), `fenomeno`, `descripcion`, `categoria_proteccion`, `subcategoria_proteccion`, `estudio`, `fuente`; añadidos `objectid_orig`, `area_ha` y `reparada`. Según el diccionario, el campo `estudio` está clasificado como **dato privado** (no publicable como dato abierto); el resto es dato público.

## 2. Qué dice el diccionario (resumen)

- Las tres capas se describen como la zonificación de amenaza alta/media/baja por cada fenómeno; el diccionario no nombra al estudio básico de amenaza, pero el campo `fuente` lo hace (ver abajo). La capa `gur_ar_condicion_amenaza` sí dice que se construyó sobre el estudio básico de amenaza (EBA) tras depuración espacial (excluye espacio público existente y la subcategoría de protección y conservación ambiental, y en suelo rural se cruza con las áreas de actividad). **No se usó** para estos mapas.
- Reglas topológicas declaradas: sin superposición y sin huecos; excepción: el perímetro del Distrito.
- Valores del campo `fuente`: «Estudio básico de amenazas - 2025» (inundación 1.744; torrenciales 1.210; movimientos en masa 13.507), «Estudio de detalle» (72; 122; 298) y, solo en inundación, «POT acuerdo 48 de 2014» (36 polígonos, 4,95 ha = 0,4 % del área de inundación).

## 3. Cotejo con la geodatabase del EBA de julio 2026 (`co255_2025_ebamedellin_AmeazasJulio26.gdb.rar`)

| Capa | EBA (julio) | POT (esta v2) | Diferencia |
|---|---|---|---|
| Movimientos en masa | 13.805 polígonos; 14.025,68 / 5.567,33 / 18.046,65 ha (alta/media/baja) | igual | ninguna (mismos conteos y áreas) |
| Avenidas torrenciales | 1.332; 586,72 / 207,00 / 169,42 ha | igual | ninguna |
| Inundación | 1.848; 575,13 / 194,59 / 363,61 ha | 1.852; 575,13 / 194,59 / 363,68 ha | +4 polígonos (4 astillas de «Estudio La Palma», < 10 m² cada una) y ajustes de borde en unos 11 polígonos (el mayor: +0,07 ha en un polígono de amenaza baja). Diferencia total: 0,07 ha |

Conclusión: la gdb del POT contiene la misma zonificación del EBA de julio con campos estandarizados (`fuente`, `estudio`) y es la versión con diccionario y topología documentados; por eso se usó como base de la v2. Las cifras citadas en el P1 (8.1.3 a 8.1.5) no cambian.

## 4. Tratamiento aplicado

1. Lectura directa del zip (`/vsizip/`), sin extraer; EPSG:9377 verificado capa por capa.
2. Geometrías no válidas (autointersección de anillos): 2 en inundación, 1 en torrenciales y 44 en movimientos en masa (las mismas 47 del EBA). Se corrigieron con `shapely.make_valid` y quedan marcadas con `reparada = 1`. Las áreas totales por categoría coinciden con las de la gdb original a dos decimales.
3. Sin remuestreo, simplificación ni cambio de escala: geometría original. Los polígonos de las tres capas están contenidos en el límite municipal (0,000 ha fuera) y los de movimientos en masa cubren el 100 % del Distrito (37.639,66 ha).
4. Mapas con el mismo diseño de la v1 (hoja tipo POMCA, escala de tres colores baja → media → alta, límites de comunas y corregimientos de 2014) para que reemplacen a los de la v1.

## 5. Resultados

| Fenómeno | Alta | Media | Baja | Total |
|---|---|---|---|---|
| Inundación (ha) | 575,13 | 194,59 | 363,68 | 1.133,40 |
| Avenidas torrenciales (ha) | 586,72 | 207,00 | 169,42 | 963,14 |
| Movimientos en masa (ha) | 14.025,68 | 5.567,33 | 18.046,65 | 37.639,66 |
| Movimientos en masa (% del Distrito) | 37,26 | 14,79 | 47,95 | 100 |

Cambios frente a la v1: inundación y avenidas torrenciales sin diferencias de fondo (±0,01 %); **movimientos en masa** pasa de un mosaico de celdas de ~32 m reconstruido de una lámina a polígonos oficiales (porcentajes 37,25 / 14,80 / 47,95 en la v1 frente a 37,26 / 14,79 / 47,95 en la v2).

## 6. Defectos de metadata encontrados en el diccionario

- `gur_ar_riesgo_inundaciones`: la descripción es copia de la de avenidas torrenciales («zonas de amenaza alta por avenida torrencial…»).
- Hay un campo `fuente` sin clasificación de publicación en `gur_ar_riesgo_mov_masa`.
- El nombre de la gdb dice 2025 y el diccionario 2026; las capas de amenaza se elaboraron el 2026-05-17 y las de riesgo el 2026-02-25.
- El campo `estudio` no es publicable: si las figuras o tablas llegan a citarlo, hay que revisar con el DAP.

## 7. Pendientes

- Confirmar procedencia y autorización de uso de la gdb (ver §1).
- Definir la referencia final de la capa en el documento (la v2 cita «DAP, 2026» y el EBA «Universidad EAFIT, en DAP, 2026»; en la v1 eran DAP 2026a y 2026b).
- Rehacer con los polígonos oficiales lo que dependa de las capas de la v1: figura 8.1.5.2 (movimientos en masa por territorio), el geovisor del P9 (capas «POT 2026*») y la librería de datos.

## 8. Reproducir

Scripts en el repositorio `PAC_2026_MED/P1_08_1_AMENAZAS/CODIGO/`: `prepare_pot2026_hazard_layers_v2.py` (lee el zip y escribe `pot2026_amenazas_oficial_v2_9377.gpkg` y su resumen JSON) y `mapas_amenaza_pot2026_v2.py` (genera las tres figuras). Se ejecutan con el Python de QGIS 3.44 (`python-qgis-ltr.bat`); las rutas con espacios o tildes se pasan por las variables de entorno `V2_ZIP`, `V2_OUT`, `V2_PREP` y `V2_FIGS`.
