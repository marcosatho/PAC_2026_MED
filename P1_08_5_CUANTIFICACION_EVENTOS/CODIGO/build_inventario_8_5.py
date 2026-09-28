# -*- coding: utf-8 -*-
"""Build the unified event inventory workbook for numeral 8.5 (quantification of events) from the prepared sources.

Sheets: Léeme, Fuentes, Series_anuales, Conciliacion, Eventos_Geohazards, Eventos_UNGRD, DAGRD_2005_2018, Hemeroteca_8_5, Pendientes.

usage: build_inventario_8_5.py <ev85_dir> <oni.csv> <hemeroteca.xlsm> <out.xlsx>"""
from osgeo import gdal  # noqa: F401
import json
import sys
import numpy as np
import pandas as pd
import openpyxl
from enso_episodes import load_oni, classify
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")
EV, ONI, HEM, OUT = sys.argv[1:5]

# ---------------------------------------------------------------------------------------------------- sources
geo = pd.read_csv(f"{EV}/geohazards_medellin_limpio.csv", dtype={"cod": str})
geo["date"] = pd.to_datetime(geo["date"])
geo_u = geo[~geo["dup_same_day_110m"]].copy()
geo_u["fatalities"] = geo_u["fatalities_verified"]

ung = pd.DataFrame(json.load(open(f"{EV}/ungrd_medellin_raw.json", encoding="utf-8")))
for c in ["fallecidos", "heridos", "desaparecidos", "personas", "familias", "viviendas_destruidas", "viviendas_averiadas", "hectareas"]:
    ung[c] = pd.to_numeric(ung[c], errors="coerce")
ung["fecha"] = pd.to_datetime(ung["fecha"])
ung["duplicado"] = ung.duplicated(keep="first")
FAMILY = {"MOVIMIENTO EN MASA": "movimiento en masa", "INUNDACION": "inundación", "CRECIENTE SUBITA": "creciente súbita",
          "AVENIDA TORRENCIAL": "avenida torrencial", "INCENDIO DE COBERTURA VEGETAL": "incendio de cobertura vegetal",
          "VENDAVAL": "vendaval", "AMENAZAS CONCATENADAS O COMPLEJAS": "amenazas concatenadas"}
ung["climatico"] = ung["evento"].isin(FAMILY)
ung_u = ung[~ung["duplicado"]]

dag = pd.read_csv(f"{EV}/dagrd_eventos_por_territorio_2005_2018.csv", dtype={"cod": str})
dag_tot = dag[dag["territorio_raw"].str.startswith("Total")].pivot_table(index="anio", columns="amenaza", values="eventos", aggfunc="sum")

sir = pd.read_csv(f"{EV}/sirmed_emergencias_2004_2026.csv", low_memory=False)
sir["fecha"] = pd.to_datetime(sir["fecha_registro"])
sir["year"] = sir["fecha"].dt.year
_xy = sir["coordenadas"].astype(str).str.split(",", n=1, expand=True)
sir["latitud"] = pd.to_numeric(_xy[0], errors="coerce")
sir["longitud"] = pd.to_numeric(_xy[1], errors="coerce")

dsi = pd.read_pickle(f"{EV}/desinventar/desinventar_medellin.pkl")

o = pd.read_csv(ONI, header=0, names=["date", "oni"], parse_dates=["date"])
o = o[o["oni"] > -99]
o["year"] = o["date"].dt.year
oni_mean = o.groupby("year")["oni"].mean().round(2)
_cl = classify(load_oni(ONI), pd.period_range("1990-01", "2026-07", freq="M"))
_nn = _cl[_cl["fase"] == "La Niña"].groupby(_cl[_cl["fase"] == "La Niña"].index.year).size()
nina = {int(y): bool(_nn.get(y, 0) >= 6) for y in oni_mean.index}

UDEA_FIRES = {2018: 134, 2019: 364, 2020: 296, 2021: 133, 2022: 70, 2023: 177, 2024: 165, 2025: 18}   # Universidad de Antioquia (2026b)
DAGRD_FIRES = {2016: 536, 2017: 214, 2018: 226, 2024: 422}   # Tabla 15 (2016-2018); press release DAGRD 2025-07-24 (2024)

# ---------------------------------------------------------------------------------------------------- annual series
rows = []
for y in range(1990, 2027):
    g = geo_u[geo_u["year"] == y]
    u = ung_u[(ung_u["fecha"].dt.year == y) & ung_u["climatico"]]
    um = ung_u[(ung_u["fecha"].dt.year == y) & (ung_u["evento"] == "MOVIMIENTO EN MASA")]
    rows.append({
        "Año": y,
        "ONI medio (NOAA)": oni_mean.get(y, np.nan),
        "Año con La Niña (≥6 meses dentro de un episodio de La Niña)": ("sí" if nina.get(y) else "no") if y in nina else "",
        "Geohazards: registros (sin duplicados probables)": len(g),
        "Geohazards: personas fallecidas": int(g["fatalities"].sum()),
        "DAGRD: movimientos en masa (Tabla 13)": dag_tot["movimiento en masa"].get(y, np.nan),
        "DAGRD: inundaciones y avenidas torrenciales (Tabla 14)": dag_tot["inundación y avenida torrencial"].get(y, np.nan),
        "DAGRD: incendios de cobertura vegetal": DAGRD_FIRES.get(y, np.nan),
        "UdeA: incendios validados en coberturas vegetales": UDEA_FIRES.get(y, np.nan),
        "SIRMED: movimientos en masa": int(((sir["year"] == y) & (sir["tipo_incidente"] == "Movimiento en masa")).sum()) if y >= 2021 else np.nan,
        "SIRMED: inundaciones": int(((sir["year"] == y) & (sir["tipo_incidente"] == "Inundaciones")).sum()) if y >= 2021 else np.nan,
        "SIRMED: incendios forestales": int(((sir["year"] == y) & (sir["tipo_incidente"] == "Incendio forestal")).sum()) if y >= 2021 else np.nan,
        "SIRMED: todas las emergencias": int((sir["year"] == y).sum()) if y >= 2021 else np.nan,
        "UNGRD: eventos climáticos (sin duplicados)": len(u) if 2019 <= y <= 2022 else np.nan,
        "UNGRD: movimientos en masa": len(um) if 2019 <= y <= 2022 else np.nan,
        "UNGRD: personas fallecidas (eventos climáticos)": int(u["fallecidos"].sum()) if 2019 <= y <= 2022 else np.nan,
    })
series = pd.DataFrame(rows)
series["Notas"] = ""
series.loc[series["Año"] == 2018, "Notas"] = "UdeA: desde el 23 de enero. DAGRD (Tabla 15): 226 con todos los incendios atendidos."
series.loc[series["Año"] == 2024, "Notas"] = "DAGRD: 422 incendios forestales según comunicado de julio de 2025 (H30); UdeA: 165 validados en coberturas vegetales."
series.loc[series["Año"] == 2025, "Notas"] = "UdeA: solo enero a abril. Geohazards: registros parciales."
series.loc[series["Año"] == 2026, "Notas"] = "Año en curso: registros parciales. SIRMED hasta el 25 de septiembre."
series.loc[series["Año"] == 2021, "Notas"] = "SIRMED: primer año con registro completo (antes de 2021 hay 472 registros sueltos)."
series.loc[series["Año"].between(2019, 2022), "Notas"] += " UNGRD: conjunto 'Emergencias UNGRD' (2019-2022), 36 filas repetidas eliminadas."
print(series.to_string())

# ---------------------------------------------------------------------------------------------------- reconciliation
rec = []


def add(comp, a_name, a_val, b_name, b_val, lectura):
    ratio = (b_val / a_val) if (isinstance(a_val, (int, float)) and isinstance(b_val, (int, float)) and a_val) else np.nan
    rec.append({"Comparación": comp, "Fuente A": a_name, "Valor A": a_val, "Fuente B": b_name, "Valor B": b_val,
                "B / A": round(ratio, 2) if pd.notna(ratio) else "", "Lectura": lectura})


for y in range(2019, 2023):
    g = int(((geo_u["year"] == y)).sum())
    um = int(((ung_u["fecha"].dt.year == y) & (ung_u["evento"] == "MOVIMIENTO EN MASA")).sum())
    add(f"Movimientos en masa {y}", "Geohazards (deslizamientos y flujos)", g, "UNGRD (movimientos en masa)", um,
        "Geohazards recoge más registros que los reportados a la UNGRD; no se suman.")
g1922 = int(geo_u["year"].between(2019, 2022).sum()); u1922 = int(((ung_u["evento"] == "MOVIMIENTO EN MASA")).sum())
add("Movimientos en masa 2019-2022", "Geohazards", g1922, "UNGRD", u1922, "Cobertura de la UNGRD: solo lo reportado al nivel nacional.")
add("Fallecidos por movimientos en masa 2019-2022", "Geohazards", int(geo_u.loc[geo_u["year"].between(2019, 2022), "fatalities"].sum()),
    "UNGRD", int(ung_u.loc[ung_u["evento"] == "MOVIMIENTO EN MASA", "fallecidos"].sum()), "Comparar con la lista de eventos con fallecidos.")
add("Incendios 2018", "UdeA (validados en coberturas vegetales, desde 23 ene)", 134, "DAGRD Tabla 15 (todos los atendidos)", 226,
    "Criterios de conteo distintos: el DAGRD cuenta reportes atendidos; la UdeA, incendios validados en coberturas vegetales.")
add("Incendios 2024", "UdeA (validados en coberturas vegetales)", 165, "DAGRD comunicado 24/07/2025 (H30)", 422,
    "Igual que 2018: no sumar ni comparar como tendencia; se presenta como rango según el criterio.")
add("Tabla 15 DAGRD: total impreso frente a suma de filas, 2016", "Suma de filas por comuna", 518, "Total general impreso", 536, "Diferencia de 18 eventos sin fila asignada en la fuente.")
add("Tabla 15 DAGRD: total impreso frente a suma de filas, 2017", "Suma de filas por comuna", 200, "Total general impreso", 214, "Diferencia de 14 eventos.")
add("Tabla 15 DAGRD: total impreso frente a suma de filas, 2018", "Suma de filas por comuna", 217, "Total general impreso", 226, "Diferencia de 9 eventos.")
add("Tablas 13 y 14 DAGRD: suma de filas frente al total impreso", "Suma de filas", "coincide en las 14 anualidades", "Total general impreso", "coincide", "Verificado sin diferencias.")
add("UNGRD: filas repetidas", "Filas del conjunto para Medellín", int(len(ung)), "Filas únicas", int(len(ung_u)), "El bloque de 2022 está cargado tres veces; se eliminaron 36 filas idénticas.")
add("Geohazards: ubicación por defecto", "Registros de Medellín", int(len(geo)), "Con la coordenada del centroide municipal", int(geo["default_location"].sum()),
    "No sirven para análisis por comuna; se usan solo en series por año y década.")
add("Geohazards: duplicados probables", "Registros de Medellín", int(len(geo)), "Mismo día y a menos de ~110 m", int(geo["dup_same_day_110m"].sum()),
    "Se excluyen de las series (se conservan marcados).")
add("SIRMED: API frente a descarga manual (27 nov 2024 - 25 sep 2026)", "Descarga manual del portal", 13933, "Servicio capas/range (layer=emergencias)", 13933,
    "Mismas filas y mismos identificadores: la consulta por año reproduce la descarga del portal.")
add("SIRMED: cobertura histórica", "Registros antes de 2021", int((sir["year"] < 2021).sum()), "Registros de 2021 a 2026", int((sir["year"] >= 2021).sum()),
    "El registro completo empieza en 2021; los 44.317 del histórico son casi todos de 2021 en adelante.")
add("Incendios forestales 2024", "SIRMED (tipo 'Incendio forestal')", int(((sir["year"] == 2024) & (sir["tipo_incidente"] == "Incendio forestal")).sum()),
    "DAGRD comunicado 24/07/2025 (H30)", 422, "Los dos conteos del DAGRD son cercanos; la Universidad de Antioquia (165) valida solo coberturas vegetales.")
add("Movimientos en masa por comuna: orden SIRMED 2021-2025 frente a DAGRD 2005-2018", "Correlación de rangos, 16 comunas", 0.99, "", "",
    "El orden de las comunas es casi idéntico en las dos series aunque los niveles difieran (400-600 al año frente a 830-4.780).")
add("Movimientos en masa: peso de los corregimientos", "DAGRD 2005-2018 (Tabla 13)", "13 %", "SIRMED 2021-2025", "34 %", "San Antonio de Prado (246) supera hoy a cualquier comuna; verificar si es cambio real o de cobertura.")
add("Inundaciones por territorio: SIRMED 2021-2025 frente a DAGRD 2005-2018", "Correlación de rangos, 20 territorios", 0.26, "", "",
    "Cambia el reparto: laderas en 2005-2018 (la tabla incluye avenidas torrenciales), valle desde 2021.")
add("Incendios por territorio: SIRMED 2021-2025 frente a DAGRD Tabla 15 2016-2018", "Correlación de rangos, 21 territorios", 0.14, "", "",
    "La Tabla 15 tiene San Cristóbal casi vacío (14 en tres años) y Guayabal en primer lugar: no coincide con SIRMED ni con la Universidad de Antioquia; no se usa.")
add("Incendios: San Cristóbal", "UdeA 2018-2025", "42 %", "SIRMED 2021-2025", "19 %", "Mismo primer lugar; SIRMED reparte más hacia laderas urbanas (Robledo, Villa Hermosa, San Javier: 28 % frente a 10 %).")
add("Villatina, 27 sep 1987: fallecidos", "Geohazards", 500, "DesInventar", 500, "Coinciden (también las fuentes de prensa: cerca de 500).")
add("Media Luna, jul 1954: fallecidos", "Geohazards (sin corregir)", 100, "DesInventar", 70, "DesInventar y la prensa (más de 70) contradicen el 100 de Geohazards; se usa 'más de 70'.")
add("El Socorro, 31 may 2008: fallecidos", "Geohazards", 28, "DesInventar", 27, "DesInventar y la revista EIA dan 27; se usa 27.")
ls_ = dsi[dsi["evento"].isin(["LANDSLIDE", "SPATE"])]
for dec in (1980, 1990, 2000, 2010):
    add(f"Fallecidos por deslizamientos y avenidas, década de {dec}", "Geohazards (verificado)", int(geo_u.loc[(geo_u["year"] // 10) * 10 == dec, "fatalities"].sum()),
        "DesInventar (deslizamientos y avenidas torrenciales)", int(ls_.loc[(ls_["anio"] // 10) * 10 == dec, "muertos"].sum()),
        "Dos inventarios independientes dan totales muy parecidos por década.")
add("DesInventar: eventos de Medellín con valor de pérdidas en dinero", "Eventos 1921-2017", int(len(dsi)), "Con pérdidas en pesos o dólares", int(((dsi["perdidas_cop"] > 0) | (dsi["perdidas_usd"] > 0)).sum()),
    "Todos anteriores a 1997 y en pesos de cada época; de 1997 a 2017 (304 eventos) ninguno trae valor. No permite una serie.")
recdf = pd.DataFrame(rec)

# ---------------------------------------------------------------------------------------------------- hemeroteca anchors
wb_h = openpyxl.load_workbook(HEM, data_only=True)
hh = {r[0]: r for r in wb_h["Hemeroteca"].iter_rows(min_row=2, values_only=True) if r[0]}
FIG = {   # figures read from the hemeroteca notes (columns 'Aporte'); not to be added across items
    "H13": ("incendios de cobertura vegetal", "Medellín", "186 incendios atendidos y 146 ha afectadas en enero-febrero de 2024", "Solape con H30 y H31: no sumar."),
    "H30": ("incendios de cobertura vegetal", "Medellín", "422 incendios forestales en 2024; 33 en lo corrido de 2025 (a julio)", "Año completo frente a fracción del siguiente: no inferir tendencia."),
    "H15": ("lluvias (temporada)", "Medellín", "198 emergencias por lluvias al inicio de la temporada 2023: 134 caídas de árboles, 28 inundaciones, 36 movimientos en masa", "Acumulado parcial; puede incluir H16."),
    "H16": ("inundaciones y viento", "Conquistadores, Parques del Río, Campo Valdés", "14/01/2023: 2 personas fallecidas y 23 lesionadas", "Balance preliminar; posiblemente incluido en H15."),
    "H17": ("deslizamiento y creciente", "Altavista, El Manzanillo, Belén, Guayabal", "29/04/2025: 1 fallecida, 1 desaparecida, 2 viviendas colapsadas, cerca de 40 afectadas", "Cifras provisionales."),
    "H18": ("inundación (lluvia intensa)", "El Poblado, Monterrey, Las Vegas", "28/01/2026: unos 87 mm en 44 minutos (SIATA, según la nota); desbordamiento de La Presidenta", "Dato localizado; contrastar con la estación."),
    "H19": ("lluvias (día)", "El Poblado, Popular, Manrique", "37 emergencias en un día: 17 caídas de árboles, 14 inundaciones, 6 deslizamientos", "Fecha con inconsistencia editorial (septiembre u octubre de 2024)."),
    "H20": ("movimiento en masa", "San Antonio de Prado, La Verde", "13/07/2022: movimiento en masa hacia la quebrada Doña María; monitoreo con sensores", "Sin cifras de afectación."),
    "H23": ("avenida torrencial", "Santo Domingo (límite con Bello)", "24/06/2025: 23 familias, 80 personas y 6 viviendas en evacuación temporal", "Mismo episodio de Granizal (Bello, 27 muertos, H24): no sumar víctimas entre municipios."),
    "H31": ("sequía / El Niño", "Valle de Aburrá", "29/01/2024: plantas que abastecen al menos al 90 % de la ciudad en niveles adecuados", "Contexto; solapa con H13 y H30."),
    "H12": ("sequía / El Niño", "Medellín", "Interrupciones programadas de acueducto desde el 31/08/2026 (EPM)", "Ver también El Espectador 21/09/2026 en 8.1.6."),
    "H32": ("dengue", "Medellín", "Más de 1.000 casos a mediados de mayo de 2024; situación de epidemia", "Acumulado parcial de casos notificados."),
    "H28": ("calor", "Valle de Aburrá", "Mayo de 2023: temperaturas cercanas a 31 °C y noches cálidas", "Episodio, no tendencia."),
    "H29": ("calor", "Valle de Aburrá", "Primera quincena de julio de 2026: máximas de hasta 32 °C, 2 a 3 °C sobre el promedio histórico", "Episodio, no tendencia."),
}
hem_rows = []
for hid, (hz, terr, cifras, nota) in FIG.items():
    r = hh[hid]
    hem_rows.append({"ID": hid, "Fecha": str(r[1])[:10], "Medio o institución": r[3], "Título": r[4], "Amenaza": hz, "Territorio": terr,
                     "Cifras reportadas": cifras, "Precaución": nota, "URL": r[10]})
hemdf = pd.DataFrame(hem_rows)

# ---------------------------------------------------------------------------------------------------- catalogue of sources
n_geo_valid = len(geo_u)
src = pd.DataFrame([
    ["S1", "Inventario de movimientos en masa Geohazards (Antioquia)", "Geohazards", "1871-2026", "Municipio, sitio, coordenada",
     "Fecha, tipo (deslizamiento / flujo de detritos), detonante, fallecidos, pérdidas (unidades sin documentar), fuente, incertidumbre",
     f"1.099 (1.082 sin duplicados probables; 267 con ubicación por defecto)", "Cargada", "Descarga del visor; archivo JSON en Descargas. Fuentes principales: prensa (El Colombiano), Ingeominas, tesis UNAL."],
    ["S2", "Emergencias UNGRD (datos.gov.co, wwkg-r6te)", "UNGRD", "2019-2022", "Municipio (divipola 5001)",
     "Evento, fecha, fallecidos, heridos, personas, familias, viviendas, hectáreas, recursos ejecutados",
     f"132 filas (96 únicas)", "Cargada", "El bloque de 2022 está repetido tres veces. Recursos ejecutados = 0 para Medellín. Sin ubicación intramunicipal."],
    ["S3", "Eventos reportados al DAGRD por comuna (PASCCM Tomo I, Tablas 13-15)", "Secretaría de Salud de Medellín (2021), con registros del DAGRD",
     "2005-2018 (movimientos en masa e inundaciones); 2016-2018 (incendios)", "Comuna y corregimiento", "Conteo anual de eventos reportados",
     "Movimientos en masa 29.077; inundaciones y avenidas 1.912; incendios 976", "Cargada y validada (sumas = totales en Tablas 13 y 14)",
     "Tabla 15: filas suman 518, 200 y 217 frente a totales 536, 214 y 226."],
    ["S4", "Incendios de cobertura vegetal (Universidad de Antioquia, 2026b)", "Universidad de Antioquia - SIATA", "2018-2025 (abril)", "Comuna y corregimiento",
     "Incendios validados en coberturas vegetales", "1.357", "Cargada (series por año y territorio)", "Ver 8.1.8."],
    ["S5", "Hemeroteca ampliada PAC 2026", "Equipo PAC", "2015-2026", "Variable", "Balances institucionales y notas de prensa",
     "14 registros útiles para 8.5", "Cargada (hoja Hemeroteca_8_5)", "Cada cifra es un balance parcial: no sumar."],
    ["S6", "SIRMED - histórico de emergencias", "Alcaldía de Medellín (DAGRD)", "2004-hoy", "Barrio, dirección, coordenadas",
     "Fecha, tipo de incidente, fallecidos, lesionados, clasificación ICAD", "44.317 registros (472 antes de 2021; 7.100 a 8.200 al año desde 2021)",
     "Cargada (consulta por año al servicio del portal)", "44.317 eventos únicos; registro completo desde 2021. No se encadena con la serie del DAGRD de 2005-2018 (sin años en común)."],
    ["S7", "SIRMED - capa de eventos históricos", "Alcaldía de Medellín", "1880-2025", "Comuna, barrio, coordenadas", "Fecha, título, descripción, fallecidos, lesionados",
     "50", "PENDIENTE: descarga", "Sirve para contrastar los eventos mayores con Geohazards."],
    ["S8", "Atlas de Riesgo de Colombia (UNGRD e INGENIAR)", "UNGRD", "Modelado", "Departamento y municipio", "Valor expuesto (millones de pesos)", "-",
     "PENDIENTE: revisar visor", "Da exposición económica, no pérdidas ocurridas."],
    ["S9", "MEData - personas en riesgo o emergencia atendidas", "Alcaldía de Medellín", "2023", "Distrito", "Personas beneficiadas con acompañamiento social",
     "-", "PENDIENTE", "Indicador de atención, no de pérdidas."],
    ["S11", "Índice oceánico de El Niño (ONI), mensual", "NOAA (PSL y CPC)", "1950-julio 2026", "Global", "Índice por trimestre asignado al mes central", "-", "Cargada",
     "Hasta dic. 2024 del archivo PSL (22 may 2026); de 2025 a jul. 2026 de la tabla oficial del CPC (oni.ascii.txt, 27 sep 2026). Coinciden en la fase de todos los meses en que se solapan."],
    ["S10", "DesInventar Sendai: base de Colombia", "UNDRR / UNGRD / OSSO", "1921-2017 (Medellín)", "Municipio", "Muertos, heridos, viviendas, afectados, pérdidas en dinero", "737 (78 con pesos, 1 con dólares)",
     "Cargada (consulta por municipio al servidor DesInventar)", "Sin valores de pérdidas desde 1997. Sirve para contrastar fallecidos (coincide con Geohazards por década)."],
], columns=["ID", "Fuente", "Institución", "Cobertura temporal", "Cobertura territorial", "Variables útiles", "Registros para Medellín", "Estado", "Observaciones"])

pend = pd.DataFrame([
    ["1", "Empalme entre la serie del DAGRD 2005-2018 y SIRMED 2021-2026", "No comparten años y los niveles difieren. Preguntar al DAGRD qué cambió (sistema de registro, criterios) y si existen datos de 2019-2020.", "Marcos / Juliana", "Alta"],
    ["2", "Serie de pérdidas económicas", "DesInventar solo trae dinero hasta 1996; UNGRD registra cero recursos para Medellín en 2019-2022. Preguntar al DAGRD y a Hacienda por el gasto anual en atención de emergencias; explorar el Fondo de Adaptación y aseguradoras.", "Marcos / Juliana", "Alta"],
    ["3", "Capa de eventos históricos de SIRMED (50 registros)", "Contraste de eventos mayores con Geohazards.", "Marcos", "Media"],
    ["4", "Tomo III del plan de salud (plan estratégico de acción)", "Contiene metas y líneas de base de eventos; no leído.", "Marcos", "Media"],
    ["5", "Ubicación de los 267 registros de Geohazards con coordenada por defecto", "Recuperar barrio o sector desde los campos 'site' y 'county' si el texto lo permite.", "Marcos", "Media"],
    ["6", "Series de eventos de sequía y calor", "El plan de ataque (E06) pide episodios térmicos: definir variable y umbral con series del SIATA.", "Marcos / Juliana", "Media"],
    ["7", "Calidad del aire (E07)", "Definir si se cubre en 8.5 o solo en 7.4.", "Juliana", "Baja"],
], columns=["#", "Pendiente", "Detalle", "Responsable propuesto", "Prioridad"])

readme = pd.DataFrame({"Inventario de eventos climáticos y de desastre para el numeral 8.5 (v1)": [
    "Proyecto: Actualización del PAC de Medellín 2026 - Entregable P1, numeral 8.5 'Cuantificación de los eventos'.",
    "Elaborado el 26 de septiembre de 2026 a partir de las fuentes de la hoja Fuentes. Datos preparados por código (carpeta 03_CODIGO).",
    "Hojas: Fuentes (qué hay y en qué estado) · Series_anuales (una fila por año, una columna por fuente) · Series_mensuales_SIRMED (por mes, con la fase de El Niño-La Niña) · Conciliacion (comparaciones y controles de calidad) · "
    "Eventos_SIRMED, Eventos_Geohazards, Eventos_DesInventar y Eventos_UNGRD (registros preparados) · DAGRD_2005_2018 (eventos por comuna y año) · Hemeroteca_8_5 (balances puntuales) · Pendientes.",
    "Regla de uso: las fuentes miden cosas distintas (reportes atendidos, eventos validados, registros históricos). Las columnas de una misma amenaza no se suman entre fuentes.",
    "Las celdas vacías de una serie significan 'sin dato en esa fuente', no cero. En las tablas del DAGRD una celda en blanco se leyó como cero eventos.",
]})

# ---------------------------------------------------------------------------------------------------- write workbook
geo_out = geo.rename(columns={"date": "Fecha", "year": "Año", "type_es": "Tipo", "trigger_es": "Detonante", "fatalities": "Fallecidos (inventario)", "fatalities_verified": "Fallecidos (verificado)", "verificacion": "Verificación",
                              "losses_raw": "Pérdidas (unidades sin documentar)", "uncertainty": "Incertidumbre", "source": "Fuente original",
                              "site": "Sitio", "county": "Localidad", "default_location": "Ubicación por defecto",
                              "dup_same_day_110m": "Duplicado probable", "territorio": "Comuna o corregimiento", "cod": "Código"})
geo_out["Fecha"] = geo_out["Fecha"].dt.strftime("%Y-%m-%d")
geo_out = geo_out[["id", "Fecha", "Año", "Tipo", "Detonante", "Fallecidos (inventario)", "Fallecidos (verificado)", "Verificación", "Pérdidas (unidades sin documentar)", "Incertidumbre", "Fuente original",
                   "Sitio", "Localidad", "Código", "Comuna o corregimiento", "lon", "lat", "Ubicación por defecto", "Duplicado probable"]]
ung_out = ung.copy()
ung_out["fecha"] = ung_out["fecha"].dt.strftime("%Y-%m-%d")
ung_out = ung_out[["fecha", "evento", "climatico", "duplicado", "fallecidos", "heridos", "desaparecidos", "personas", "familias", "viviendas_destruidas",
                   "viviendas_averiadas", "hectareas", "recursos_ejecutados", "valor_total_apoyo_del_fngrd"]]
ung_out.columns = ["Fecha", "Evento", "Evento climático", "Fila repetida", "Fallecidos", "Heridos", "Desaparecidos", "Personas", "Familias",
                   "Viviendas destruidas", "Viviendas averiadas", "Hectáreas", "Recursos ejecutados", "Apoyo FNGRD"]
sir_out = sir[["Evento_id", "fecha_registro", "year", "tipo_incidente", "comuna", "barrio", "latitud", "longitud", "numero_fallecidos", "numero_lesionados", "fenomeno_amenazante", "Estado"]].copy()
sir_out.columns = ["Evento_id", "Fecha", "Año", "Tipo de incidente", "Comuna o corregimiento", "Barrio", "Latitud", "Longitud", "Fallecidos", "Lesionados", "Fenómeno amenazante", "Estado del caso"]
dsi_out = dsi[["serial", "evento", "fecha", "lugar", "muertos", "heridos", "desaparecidos", "viv_destruidas", "viv_averiadas", "afectados_directos", "afectados_indirectos",
               "reubicados", "evacuados", "perdidas_usd", "perdidas_cop", "comentarios"]].copy()
dsi_out["fecha"] = dsi_out["fecha"].dt.strftime("%Y-%m-%d")
dsi_out.columns = ["Serial", "Evento", "Fecha", "Lugar", "Fallecidos", "Heridos", "Desaparecidos", "Viviendas destruidas", "Viviendas averiadas", "Afectados directos",
                   "Afectados indirectos", "Reubicados", "Evacuados", "Pérdidas USD", "Pérdidas pesos (de cada época)", "Comentarios (extracto)"]
mon = pd.read_csv(f"{EV}/sirmed_series_mensuales_2021_2026.csv")
mon.columns = ["Mes", "SIRMED: movimientos en masa", "SIRMED: inundaciones", "SIRMED: incendios forestales", "Índice oceánico de El Niño (NOAA)",
               "Fase del mes (regla de la NOAA: cinco meses seguidos; El Niño* = en formación, supuesto)"]
mon["Notas"] = ""
mon.loc[mon["Mes"] == "2026-09", "Notas"] = "Septiembre de 2026: eventos hasta el 25."
mon.loc[mon["Mes"] == "2026-04", "Notas"] = "Abril de 2026: índice +0,46, justo bajo el umbral de El Niño (+0,5). Mayo a julio: +0,95, +1,39 y +1,80; solo tres meses seguidos, el episodio aún no está completo (El Niño*)."
mon.loc[mon["Mes"] == "2026-08", "Notas"] = "Agosto y septiembre de 2026: sin índice publicado; se clasifican como El Niño* bajo el supuesto de que el episodio se complete según la definición de la NOAA (cinco meses seguidos con el índice en +0,5 o más: mayo a septiembre)."
mon.loc[mon["Mes"] == "2025-10", "Notas"] = "Octubre a diciembre de 2025: índice en −0,5 o menos solo tres meses seguidos; no es episodio de La Niña según la NOAA (fase neutra)."
dag_w = dag.pivot_table(index=["amenaza", "territorio_raw"], columns="anio", values="eventos", aggfunc="sum").reset_index()
dag_w.columns = [str(c) for c in dag_w.columns]
dag_w = dag_w.rename(columns={"amenaza": "Amenaza", "territorio_raw": "Comuna o corregimiento"})

sheets = [("Léeme", readme), ("Fuentes", src), ("Series_anuales", series), ("Conciliacion", recdf), ("Series_mensuales_SIRMED", mon), ("Eventos_SIRMED", sir_out), ("Eventos_Geohazards", geo_out), ("Eventos_DesInventar", dsi_out),
          ("Eventos_UNGRD", ung_out), ("DAGRD_2005_2018", dag_w), ("Hemeroteca_8_5", hemdf), ("Pendientes", pend)]
with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    for name, df in sheets:
        df.to_excel(xw, sheet_name=name, index=False)
wb = openpyxl.load_workbook(OUT)
head_fill = PatternFill("solid", fgColor="D9E1F2")
for ws in wb.worksheets:
    ws.freeze_panes = "A2"
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = head_fill
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, col in enumerate(ws.columns, 1):
        width = max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:200])
        ws.column_dimensions[get_column_letter(i)].width = min(max(10, width + 2), 60)
    if ws.title in ("Léeme", "Fuentes", "Conciliacion", "Hemeroteca_8_5", "Pendientes"):
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
wb["Léeme"].column_dimensions["A"].width = 140
wb.save(OUT)
print("saved", OUT)
