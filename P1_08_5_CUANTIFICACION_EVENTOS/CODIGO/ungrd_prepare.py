# -*- coding: utf-8 -*-
"""Tidy the UNGRD 'Emergencias UNGRD' (datos.gov.co wwkg-r6te) records for Medellín, 2019-2022.

usage: ungrd_prepare.py <raw.json> <out_dir>"""
import json, sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40); pd.set_option("display.max_colwidth", 50)
RAW, OUT = sys.argv[1:3]
d = pd.DataFrame(json.load(open(RAW, encoding="utf-8")))

NUM = ["fallecidos", "heridos", "desaparecidos", "personas", "familias", "viviendas_destruidas", "viviendas_averiadas",
       "vias_averiadas", "hectareas", "recursos_ejecutados", "valor_total_apoyo_del_fngrd", "acueducto", "alcantarillado",
       "centros_educativos", "centros_de_salud"]
for c in NUM:
    d[c] = pd.to_numeric(d[c], errors="coerce")
d["fecha"] = pd.to_datetime(d["fecha"], errors="coerce")
n_raw = len(d)
d = d.drop_duplicates(subset=["fecha", "evento", "fallecidos", "heridos", "personas", "familias", "viviendas_destruidas", "viviendas_averiadas", "hectareas"]).copy()
print("exact duplicate rows removed:", n_raw - len(d))
d["year"] = d["fecha"].dt.year
d["month"] = d["fecha"].dt.month

FAMILY = {"MOVIMIENTO EN MASA": "movimiento en masa", "INUNDACION": "inundación", "CRECIENTE SUBITA": "creciente súbita",
          "AVENIDA TORRENCIAL": "avenida torrencial", "INCENDIO DE COBERTURA VEGETAL": "incendio de cobertura vegetal",
          "VENDAVAL": "vendaval", "AMENAZAS CONCATENADAS O COMPLEJAS": "amenazas concatenadas"}
d["familia_es"] = d["evento"].map(FAMILY).fillna("otros eventos (no climáticos)")
d["climatico"] = d["evento"].isin(FAMILY)
keep = ["fecha", "year", "month", "evento", "familia_es", "climatico", "fallecidos", "heridos", "desaparecidos", "personas", "familias",
        "viviendas_destruidas", "viviendas_averiadas", "vias_averiadas", "acueducto", "alcantarillado", "centros_educativos",
        "centros_de_salud", "hectareas", "recursos_ejecutados", "valor_total_apoyo_del_fngrd", "otros_afectacion"]
t = d[keep].sort_values("fecha")
t["fecha"] = t["fecha"].dt.strftime("%Y-%m-%d")
t.to_csv(f"{OUT}/ungrd_medellin_2019_2022.csv", index=False, encoding="utf-8-sig")

c = d[d["climatico"]]
print("all records:", len(d), "| climate-related:", len(c))
print("\nby family (climate):")
print(c.groupby("familia_es").agg(eventos=("evento", "size"), fallecidos=("fallecidos", "sum"), heridos=("heridos", "sum"),
                                   personas=("personas", "sum"), viv_destruidas=("viviendas_destruidas", "sum"),
                                   viv_averiadas=("viviendas_averiadas", "sum"), hectareas=("hectareas", "sum")).to_string())
print("\nby year (climate):")
print(c.groupby("year").agg(eventos=("evento", "size"), fallecidos=("fallecidos", "sum"), personas=("personas", "sum"),
                            viv_destruidas=("viviendas_destruidas", "sum"), viv_averiadas=("viviendas_averiadas", "sum")).to_string())
print("\nclimate events with deaths or many homes/ha:")
print(c[(c["fallecidos"] > 0) | (c["viviendas_destruidas"] > 5) | (c["hectareas"] > 100)][
    ["fecha", "evento", "fallecidos", "heridos", "personas", "viviendas_destruidas", "viviendas_averiadas", "hectareas"]].to_string())
print("\nresources fields (sum, all rows):", d[["recursos_ejecutados", "valor_total_apoyo_del_fngrd"]].sum().to_dict())
print("non-climate deaths:", int(d.loc[~d["climatico"], "fallecidos"].sum()), "of total", int(d["fallecidos"].sum()))
