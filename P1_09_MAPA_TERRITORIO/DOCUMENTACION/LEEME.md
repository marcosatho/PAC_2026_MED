# GEOVISOR · Producto 9 (Gobierno de datos climáticos y dashboard MERL): Mapa del territorio, pestaña 6 de la base de variables del PAC

**Plan de Acción Climática (PAC) de Medellín 2026 · Producto 9, Componente 4 · versión 2 · octubre de 2026**
Documento de trabajo para validación del equipo experto. Autor: Marcos Arango.

---

## 1. Qué es

Una página interactiva, en un solo archivo HTML, que ubica en el territorio lo que hoy se sabe sobre los problemas climáticos de Medellín y sobre las medidas que ya están registradas. Sigue una lógica: **primero los problemas, luego las soluciones, y al final dónde faltan**.

1. **Problemas.** Amenazas del POT 2026* (deslizamientos, inundación, avenidas torrenciales), amenaza por incendios forestales, multiamenaza (índice de 1 a 27) y temperatura de la superficie.
2. **Soluciones.** Tres medidas que hoy se pueden ubicar, una de cada tipo de herramienta: arbolado y verde urbano (basada en la naturaleza), obras de ladera y quebrada (gris) y alerta temprana y evacuación (no estructural).
3. **Dónde falta.** Marcas por barrio donde el problema es alto y la medida no aparece en los registros: calor alto y poco arbolado, deslizamiento alto sin obra ni monitoreo, y avenida torrencial alta sin alerta temprana.

\* *Capas preliminares: las amenazas del POT 2026 se reconstruyeron de láminas en PDF; no son capas oficiales.*

## 2. Qué hay en esta carpeta

```
LEEME.txt / LEEME.md              esta guía
01_HERRAMIENTA/
    Producto9_mapa_territorio_PAC_v2.html     la página (un solo archivo, unos 8 MB)
02_DATOS/
    Inventario_mapas_medidas_Distrito_v1.xlsx inventario de datos geoespaciales del Distrito que se pueden «minar»
    LEEME_DATOS.txt                           qué es cada archivo de datos
    A_tablas/                                 tablas por barrio y vereda, por comuna y corregimiento, y marcas (CSV y Excel)
    B_capas_SIG/                              capas para QGIS o ArcGIS (GeoPackage, EPSG:9377)
    C_entradas_del_proyecto/                  copias de las entradas que ya estaban en el Drive del Producto 1
03_DOCUMENTACION/
    METODOS_Y_REFERENCIAS.md                  cómo se calculó cada valor, fuentes de datos y referencias bibliográficas
    CORREO_cuerpo_borrador.txt                borrador del cuerpo del correo para el equipo
04_CODIGO/                                    scripts para reproducir los cálculos (con su propia guía)
```

## 3. Cómo abrir y usar la página

1. Copie `Producto9_mapa_territorio_PAC_v2.html` a su computador y ábralo con Chrome o Edge (doble clic). Los datos van dentro del archivo; el **mapa base necesita internet**.
2. **Panel de capas** (a la derecha del mapa, debajo en pantallas angostas), en el mismo orden de la lógica: 1 Problemas → 2 Soluciones → 3 Dónde falta → Referencias.
3. **«Quitar todas las capas»** (arriba del panel) deja solo el mapa base. Los límites de comunas se vuelven a marcar en «Referencias».
4. **Haga clic en el mapa:** se abre la ficha del barrio o vereda (temperatura, amenaza, árboles, obras, alerta y marcas) y, si la capa de multiamenaza está activa, el valor del índice en ese punto. En el panel aparece la ficha de su comuna o corregimiento.
5. **PARTE 4 de la página:** tres tarjetas, una por medida, con el botón «Ver en el mapa» que deja el mapa listo; el recuadro «Cómo se construyó el índice de arbolado»; el recuadro «Cómo se marcan las brechas»; el recuadro «Comentario para el equipo» y la tabla de evidencia de cada medida.
6. **Capítulo «Comentarios»** (al final de la página, 12 de octubre de 2026): una mirada general a la estructura del proyecto a la luz de la guía de seguimiento, evaluación y reporte de C40, con lo que el geovisor aporta, lo que falta y las preguntas para el equipo.
7. **Descargas dentro de la página:** CSV por comuna y corregimiento (PARTE 3) y por barrio y vereda (PARTE 4).

## 4. Cómo leer las marcas «dónde falta»

Una marca **no dice que allí falte una obra; dice que el registro no la muestra.** Los umbrales son criterio del equipo (el cuarto superior o inferior de los barrios evaluados) y están escritos en la página y en `METODOS_Y_REFERENCIAS.md`. Está por decidir con el equipo cómo se define «arbolado bajo» y «calor alto» (ver el recuadro «Comentario para el equipo»).

## 5. Qué hay que tener presente

- Las capas con asterisco (*) son preliminares.
- La temperatura de superficie es la vista por satélite (2013–2016), no la temperatura del aire.
- Los registros de obras cubren solo el programa 2016–2022; el inventario de árboles no es un censo.
- No se encontró inventario de sistemas urbanos de drenaje sostenible, de techos verdes ni de jardines de lluvia.
- Las fuentes son de fechas distintas (2013–2016, 2019, 2026): los cruces entre ellas son indicativos.
- **Falta anclar la información a la normatividad nacional e internacional** en la que se sustenta la plataforma; esa conexión todavía no está hecha. El catálogo integrado de medidas trae una hoja de cobertura documental (nacional, internacional, regional y distrital) que sirve de punto de partida.
- El mapa base es de Esri y OpenStreetMap; antes de publicar fuera del equipo hay que revisar sus términos de uso.

## 6. Cómo compartirla con el equipo

1. Esta carpeta (`GEOVISOR`) está en el Drive del autor y también en el OneDrive del proyecto: `P9_Gobierno_de_datos_climaticos_y_dashboard_MERL / 02_Documentos_en_elaboracion / GEOVISOR`. En el Drive, compartirla con el equipo con permiso de **lector** (el equipo no necesita editar; los comentarios van por correo o en el documento de seguimiento).
2. Enviar el correo con el enlace a la carpeta; el borrador del cuerpo está en `03_DOCUMENTACION/CORREO_cuerpo_borrador.txt`. El HTML pesa unos 8 MB: cabe como adjunto, pero conviene mandarlo como enlace para que todos usen la misma versión.
3. Pedir al equipo que empiece por este archivo y por la PARTE 4 de la página, y que envíe sus observaciones sobre los puntos «por decidir».
4. Las versiones nuevas se guardan con un número de versión en el nombre (`..._v3.html`) y las anteriores se conservan en una subcarpeta `ARCHIVO/`.

## 7. Datos y referencias

- **Fuentes y fechas de cada dato, métodos de cálculo, cifras de las tarjetas y referencias bibliográficas:** `03_DOCUMENTACION/METODOS_Y_REFERENCIAS.md` (secciones 11 y 12).
- **Inventario de todos los datos geoespaciales evaluados** (2.608 capas del servidor de mapas de la Alcaldía; las 23 que sirven para medidas; lo que no existe): `02_DATOS/Inventario_mapas_medidas_Distrito_v1.xlsx`.
- **Servidor de mapas de la Alcaldía** (lectura pública): https://www.medellin.gov.co/servidormapas/rest/services/ · **Catálogo geográfico:** https://www.medellin.gov.co/giscatalogacion
