# Guía de redacción PAC 2026

Criterios acordados con Marcos Arango durante la redacción del numeral 8.1 (amenazas climáticas relevantes). Aplican a todo el Entregable P1 y a los que siguen. Cuando algo de aquí choque con una petición nueva, gana la petición nueva y se actualiza esta guía.

## 1. Principio: describir la ciudad, no los estudios

El documento es en el fondo una revisión bibliográfica, pero el lector no necesita saber quién estudió qué: necesita saber qué le pasa a Medellín, dónde y a quién. Los estudios son la evidencia y aparecen como cita al final de la frase.

| Evitar (narra los estudios) | Preferir (narra la ciudad) |
|---|---|
| "SIATA (2019) proyecta un aumento de las lluvias… La Universidad de Antioquia (2026b) lo cuantificó… En cambio, el estudio básico del POT 2026 no describe escenarios…" | "El siguiente mapa muestra cómo responderían las laderas de Medellín ante una lluvia muy fuerte de un solo día. Una gran parte de la ciudad está en amenaza y coincide con las laderas de fuerte pendiente; entre la amenaza media y la alta se cubre más de la mitad del Distrito (52 %)." |
| "Los dos estudios no son directamente comparables…" | Solo se contrasta si hay discrepancia real que cambie una decisión: "Los resultados no apuntan necesariamente a lo mismo. Las proyecciones de 2019 mostraban un empeoramiento marcado en Riogrande; las de 2026 no lo confirman." |

## 2. Reglas de redacción

1. **Sujeto de la frase:** la ciudad y su gente (qué pasa, dónde, a quién afecta, cuánto). Las fuentes van entre paréntesis, al final.
2. **Contrastes entre estudios:** solo cuando uno dice más y otro menos y eso importa para decidir. Se dice de frente ("no apuntan necesariamente a lo mismo").
3. **Sin limitaciones ni metodología en los párrafos descriptivos.** Lo que un modelo no incluye (sismos, estudios de detalle, resolución, periodo) va en una nota de limitaciones aparte. Tampoco se escribe "el estudio aclara que…" ni "ningún estudio cuantifica…" dentro de la descripción.
4. **Una idea por frase, máximo tres frases por párrafo.** Sin párrafos de "En síntesis" que repitan lo dicho: una síntesis solo se justifica si aporta algo nuevo.
5. **Sin traslape entre el párrafo previo y el posterior a una figura:** antes del mapa solo se presenta qué muestra; el hallazgo se dice una sola vez, después.
6. **Orden dentro de cada numeral:** qué pasa → dónde → a quién afecta → cómo cambia.
7. **Lenguaje semitécnico para tomadores de decisión.** Sin siglas ni jerga sin explicar (SPI, P95, TRIGRS, SSP5-8.5…). Los nombres de instituciones (SIATA, EPM, POT, DAGRD) sí van.
8. **Cifras humanas:** una sola comparación cotidiana por cifra y el dato exacto entre paréntesis. Ejemplos usados: 1.000 m³/s = una piscina olímpica cada 2,5 s; 1.133 ha ≈ 1.600 canchas de fútbol; 1.357 incendios en 7,3 años = uno cada dos días; "entre 1,4 y 3 veces el pico actual"; 18.003 casos de dengue en 2016 = casi 50 por día.
9. **Estructura de cada amenaza:** X.1 "Caracterización de …: situación actual o histórica" y X.2 "Cambios proyectados en …". Unas 500 palabras por numeral (X.1 + X.2).
10. **Las figuras de proyecciones van en el producto P2.** En 8.1 las figuras describen la situación actual o histórica; los textos de "Cambios proyectados" pueden ir sin figura.
11. **Aire y superficie en calor urbano:** presentar la temperatura del aire y la de la superficie (satélite) por separado y decir cuál es cuál.
12. **Citas APA con lista de referencias.** Si el cálculo es propio sobre datos ajenos, se dice: "(Guzmán Echavarría, 2018; cálculo propio)". Cita secundaria: "como se citó en".

## 3. Figuras

- **Estilo carta (POMCA):** 7,2 × 6,6 in para un mapa; límite municipal en `#bd1f36` (1,8 pt), comunas y corregimientos en `#252525` (0,42 pt), escala de 5 km, flecha norte, ejes MAGNA-SIRGAS / Origen Nacional (EPSG:9377), leyenda en el espacio libre sin tapar datos, dpi 300, fuente al pie. Escala baja–media–alta en `YlOrRd` para amenazas.
- **Pie de figura corto:** "Figura X. Descripción. Fuente: elaboración propia a partir de Autor (año)." La numeración se reinicia en cada numeral.
- **Precisión declarada en una frase** cuando la capa no es oficial: "zonas vectorizadas de la lámina en PDF, por lo que su precisión es limitada".
- **Se construyen a partir de datos, no de capturas** de figuras ajenas. Los datos crudos de un informe se transcriben, se cruzan con el texto y se grafican.
- **No se grafica lo dudoso:** si una fuente es internamente inconsistente (tasas de dengue de 2008–2009 frente a sus casos), se grafica solo lo consistente. Si una capa no tiene calidad para el mensaje (ráster de susceptibilidad a incendios de SIATA: 38 valores distintos, cobertura del 85 % y sin correspondencia con los incendios observados), no se publica.
- **No dar más resolución de la que hay:** celdas de 1 km se muestran como celdas, sin interpolar.
- Ninguna leyenda ni pie explica limitaciones largas; eso va en la nota de limitaciones.

## 4. Verificación

- Verificar cada cifra contra la fuente primaria y, si hay dos, contra ambas. Registrar discrepancias (por ejemplo, el EBA del POT 2026 se rotula "Anexo 15" en el portal y "Anexo 16" en su carátula).
- Comprobar que las áreas o totales de una capa derivada reproducen las de la fuente (los mapas de amenaza del POT 2026 coinciden con el EBA: menos de 0,3 % en inundación y avenidas torrenciales, hasta 1,1 puntos en movimientos en masa).
- No registrar como comprobada una fuente que solo se propuso.

## 5. Convenciones de trabajo

- Los cuadernos, el código y sus comentarios van en inglés; los textos del entregable y las figuras, en español.
- Comunicación directa: hechos y correcciones, sin frases de relleno.
- Los Word se arman sobre el documento maestro (`build_docx_8_1.py`, estilos Heading 3 y 4 y Normal) para que el pegado no cambie el formato; sin control de cambios.
- Cada entrega guarda texto, figuras, scripts y datos preparados en la carpeta del numeral, y se actualiza `INDICE_REFERENCIAS_7.1_8.1.md`.

## 6. Lista de chequeo antes de entregar un numeral

- [ ] ¿Cada párrafo habla de la ciudad y no de "el estudio X"?
- [ ] ¿Sin limitaciones, metodología ni salvedades dentro de la descripción?
- [ ] ¿Cada cifra técnica tiene su comparación cotidiana y su dato exacto?
- [ ] ¿Sin siglas crudas ni jerga sin explicar?
- [ ] ¿Sin traslape entre el párrafo previo y el posterior a cada figura?
- [ ] ¿Pies de figura en la forma "Figura X. …. Fuente: …" y numeración reiniciada?
- [ ] ¿Cifras verificadas con la fuente y cálculos propios declarados?
- [ ] ¿Referencias APA completas y el índice de la carpeta actualizado?
