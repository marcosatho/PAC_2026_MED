# Contexto y respaldos del proyecto PAC 2026 (Medellín)

Este documento existe para una sola cosa: si se pierde este computador, decir exactamente qué se recupera, de dónde, y qué falta. Léelo de arriba hacia abajo si estás reconstruyendo el proyecto desde cero.

Actualizado: 2026-09-28.

## Qué es este proyecto

Acompañamiento del Producto 1 (P1, Caracterización socioeconómica y ambiental) del Plan de Acción Climática (PAC) de Medellín 2026, contrato C1. El trabajo hecho hasta ahora cubre los numerales 7.1 (clima y relieve), 8.1 (amenazas climáticas), 8.5 (cuantificación de eventos) y 8.6 (síntesis de El Niño/La Niña), más los Anexos A y B del documento maestro.

## Dónde está todo, y qué tan seguro está

| Ubicación | Qué contiene | ¿Sobrevive a perder este PC? |
|---|---|---|
| **GitHub** — [github.com/marcosatho/PAC_2026_MED](https://github.com/marcosatho/PAC_2026_MED) | Código (scripts .py, notebooks), los `.md` de seguimiento, textos fuente (`.md`) de cada numeral, figuras, datos preparados **pequeños**, `Anexo_A_B_PAC_2026.xlsx` | **Sí.** Es GitHub; basta con `git clone` desde cualquier equipo con la cuenta correcta. |
| **Google Drive** — `G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\...` | El documento maestro, los PDF fuente, los Word "listos para pegar" de cada numeral, los datos crudos grandes, los ráster del convenio DAGRD-SIATA, el DTM-LiDAR | **Sí, confirmado técnicamente el 2026-09-28**: `G:` es Google Drive File Stream (proceso `GoogleDriveFS.exe`, volumen "marcosatho@gmail.com - Google..."), no un disco local. Todo lo que está bajo `G:\Mi unidad\` vive en la nube de esa cuenta de Google. |
| **Descargas** — `C:\Users\marco\Downloads\...` | Copias de trabajo del documento maestro, la carpeta plana de referencias, dos paquetes grandes (islas de calor, geodatabase UdeA) | **No.** Es disco local de este PC, sin sincronización. Todo lo que solo esté aquí se pierde si se pierde el PC. |
| `PAC_2026_MED_ACOMP_IA` (dentro de Drive) | Espejo local de un proyecto de ChatGPT (bibliografía parcial de 8.1) | Sí sobrevive (está bajo `G:\`), pero es un espejo externo: solo se actualiza corriendo ese proyecto en ChatGPT, no desde aquí. |

**Antes de hoy, el documento maestro, los PDF fuente y la carpeta de referencias completa existían solo en Descargas — sin respaldo real.** El 2026-09-28 se copiaron a Drive (ver más abajo) precisamente para cerrar ese riesgo.

## Copias de seguridad hechas el 2026-09-28

Las cuatro se completaron y se verificaron por tamaño exacto contra el original en Descargas (mismo número de bytes en los tres archivos sueltos; mismo conteo de 158 archivos en la carpeta):

- `Entregable_P1_v1_equipo_coordinacion_RESPALDO_2026-09-28.docx` → `P1_Caracterizacion_Socioeconomica_Ambiental\` (raíz), copia de la versión más reciente del documento maestro que estaba en Descargas (versión "(2)", 26 de septiembre).
- Carpeta completa `PAC_2026_Referencias_7.1_8.1` (158 archivos, ~344 MB: PDF fuente, textos extraídos, datos preparados y originales, figuras, Word de cada numeral, `Anexo_A_B_PAC_2026.xlsx`) → `P1_Caracterizacion_Socioeconomica_Ambiental\00_RESPALDO_PAC_2026_Referencias_7.1_8.1_8.5_8.6\`.
- `31. Islas de calor AMVA.zip` (239 MB) → `P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\08_1_AMENAZAS\02_ISLAS_DE_CALOR_AMVA\01_DATOS_ORIGINALES\`.
- `C4600105139_2025_CCMED.gdb.zip` (geodatabase de riesgo de la UdeA, 158 MB) → `P1_Caracterizacion_Socioeconomica_Ambiental\02_DOCUMENTOS_EN_ELABORACION\08_1_AMENAZAS\04_UDEA_GEODATABASE_RIESGO\01_DATOS_ORIGINALES\`.

Estas copias son adicionales: los originales siguen en Descargas, no se movieron ni se borró nada.

## Principio de recuperación: si algo no quedó copiado, se vuelve a correr

No todo se respaldó copiando el archivo pesado — para los datos que salen de una API o un portal público, respaldar es más simple: guardar la receta exacta de cómo pedirlos de nuevo. Eso ya existe para las fuentes de 8.5:

- `P1_08_5_CUANTIFICACION_EVENTOS/LEEME_DESCARGAS.md` (en este repositorio): las consultas exactas para volver a bajar SIRMED, DesInventar y las cuatro series del IDEAM (Aeropuerto Olaya Herrera).
- Los scripts que procesan esas descargas ya están en `P1_08_5_CUANTIFICACION_EVENTOS/CODIGO/`, `P1_08_1_AMENAZAS/CODIGO/` y `P1_ANEXOS/`.

Si algún dato crudo grande se perdiera sin haber sido copiado (por ejemplo, si en el futuro se agrega una fuente nueva y no da tiempo de respaldarla), el camino no es entrar en pánico: es volver a correr la receta documentada. Por eso este documento prioriza que las recetas y los scripts estén en GitHub, no solo los datos ya bajados.

**Advertencia técnica:** Google Drive File Stream sube los archivos a la nube en segundo plano después de copiarlos al disco virtual `G:\`. Que un archivo aparezca en `G:\` no garantiza que ya terminó de subirse — si vas a confiar en este respaldo de inmediato (por ejemplo, para apagar el PC), confirma en la aplicación de Google Drive que la sincronización está al día (ícono de la nube, sin flechas de carga pendientes).

## Qué falta por respaldar (a la fecha de este documento)

- Los `.docx` de Word "listos para pegar" de cada numeral (8.1, 8.5, 8.6, Anexos) existen en Descargas y también en las subcarpetas correspondientes de `02_DOCUMENTOS_EN_ELABORACION` dentro de Drive — ya respaldados por partida doble, sin acción pendiente.
- Las versiones anteriores del documento maestro (`(1).docx`, la versión sin sufijo) no se copiaron, solo la más reciente. Si se necesitan las versiones intermedias, están en Descargas.
- La carpeta `PAC_2026_MED_ACOMP_IA` es un espejo de un proyecto de ChatGPT: si se pierde el acceso a ese proyecto de ChatGPT, no hay forma de regenerarlo desde aquí; solo queda la foto que ya está guardada en Drive.

## Cómo reconstruir el proyecto desde cero (si se pierde este PC)

1. Instalar Google Drive para escritorio e iniciar sesión con `marcosatho@gmail.com`. Con eso vuelve todo lo de la tabla de arriba marcado "Sí" bajo Drive, incluido el respaldo del 2026-09-28.
2. `git clone https://github.com/marcosatho/PAC_2026_MED.git`. Con eso vuelve el código, los `.md` de seguimiento y los textos fuente de cada numeral.
3. Leer `ESTADO_PROYECTO.md` y las últimas entradas de `BITACORA.md` (ambos en el repositorio) para saber en qué quedó cada numeral.
4. Para retomar un numeral: el texto fuente está en `P1_0X_.../TEXTOS/*.md` (repositorio) y su Word "listo para pegar" en la carpeta correspondiente de Drive (`02_DOCUMENTOS_EN_ELABORACION/`) o en el respaldo `00_RESPALDO_PAC_2026_Referencias_7.1_8.1_8.5_8.6/`.

## Mantenimiento de este documento

Actualizar cuando cambie de forma relevante dónde vive algo, o cuando se agregue una fuente de datos nueva que no quede claramente en Drive o en GitHub. No hace falta actualizarlo por cada commit — para eso está `BITACORA.md`.
