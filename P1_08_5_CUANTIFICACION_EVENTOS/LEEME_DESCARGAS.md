# Cómo se obtuvieron los datos de SIRMED, DesInventar e IDEAM (27-28 de septiembre de 2026)

## SIRMED, histórico de emergencias (44.317 eventos)
El portal web guarda los datos en un servicio propio. Consulta por año (una llamada por año, de 2004 a 2026):

    curl "https://www.medellin.gov.co/sirmed-api/api/v1/capas/range?layer=emergencias&from=AAAA-01-01&to=AAAA-12-31"

Resultado: el registro completo empieza en 2021 (7.100 a 8.200 eventos al año); antes de 2021 hay 472 registros sueltos.
Los archivos por año están en 01_DATOS_ORIGINALES/SIRMED_capas_range_por_anio. Se comprobó contra la descarga manual del portal
(13.933 filas del 27/11/2024 al 25/09/2026): mismas filas y mismos identificadores.

## DesInventar Sendai, base de Colombia, municipio de Medellín (737 eventos, 1921-2017)
Se abre una sesión (cookie) en la página de consulta y se pide la vista de datos con el filtro geográfico (Antioquia = 05, Medellín = 05001):

    curl -c cj.txt "https://www.desinventar.net/DesInventar/main.jsp?countrycode=col&lang=EN"
    curl -b cj.txt "https://www.desinventar.net/DesInventar/results.jsp?bookmark=1&countrycode=col&maxhits=1000&lang=EN&logic=AND&sortby=0&frompage=/main.jsp&level0=05&level1=05001"

El HTML resultante se convierte en tabla con desinventar_parse.py.

## IDEAM, estación Aeropuerto Olaya Herrera (código 27015330), dato horario 2014-2026
Portal de datos abiertos (Socrata), tres conjuntos por separado (temperatura media, máxima y mínima), filtrando por estación.
Paginado por año porque una sola consulta ordenada por fecha se cae por tiempo de espera:

    curl -G "https://www.datos.gov.co/resource/sbwg-7ju4.json" --data-urlencode "$select=fechaobservacion,valorobservado,codigosensor,descripcionsensor,nombreestacion" --data-urlencode "$where=codigoestacion='0027015330' AND codigosensor='0068'" --data-urlencode "$limit=50000"
    curl -G "https://www.datos.gov.co/resource/ccvq-rp9s.json" --data-urlencode "$where=codigoestacion='0027015330' AND fechaobservacion between 'AAAA-01-01T00:00:00' and 'AAAA-12-31T23:59:59'"
    curl -G "https://www.datos.gov.co/resource/afdg-3zpb.json" --data-urlencode "$where=codigoestacion='0027015330' AND fechaobservacion between 'AAAA-01-01T00:00:00' and 'AAAA-12-31T23:59:59'"

Los conjuntos de máxima y mínima traen, desde 2024, picos imposibles (hasta 45 °C) y mínimas falsas cercanas a 0 °C que pasaron el control de calidad que dice aplicar el IDEAM; se filtraron comparando cada lectura contra la temperatura horaria del primer conjunto (script `olaya_analysis.py`).

Las normales climatológicas (1971-2000, 1981-2010, 1991-2020) salen de un cuarto conjunto, filtrado por el mismo código de estación:

    curl -G "https://www.datos.gov.co/resource/nsz2-kzcq.json" --data-urlencode "$where=upper(estaci_n) like '%OLAYA%' OR c_digo='27015330'"

Scripts: `olaya_fetch.py` y `olaya_fetch2.py` (descarga), `olaya_analysis.py` (control de calidad y series diaria/mensual), `olaya_decadas.py` (tabla de periodos).
