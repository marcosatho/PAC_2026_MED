# -*- coding: utf-8 -*-
"""Parse the DesInventar (Colombia database, Medellín 05001) 'View data' HTML into a table and summarize losses.

usage: desinventar_parse.py <results.html> <out_csv>"""
from osgeo import gdal  # noqa: F401
import html
import re
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40); pd.set_option("display.max_colwidth", 40)
src, out = sys.argv[1:3]
t = open(src, encoding="utf-8", errors="replace").read()
i = t.index('class="IE_Table_borders')
tbl = t[i:]
rows = re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, flags=re.S | re.I)
print("rows found:", len(rows))


def cells(r):
    cs = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, flags=re.S | re.I)
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", c))).strip() for c in cs]


for k in range(3):
    print(k, cells(rows[k]))
data = [cells(r) for r in rows[2:] if len(cells(r)) >= 10]
print("data rows:", len(data), "| widths:", pd.Series([len(x) for x in data]).value_counts().to_dict())
print(data[0]); print(data[1])

cols = ["serial", "evento", "departamento", "municipio", "_x", "fecha", "lugar", "muertos", "heridos", "desaparecidos", "viv_destruidas", "viv_averiadas",
        "afectados_directos", "afectados_indirectos", "reubicados", "evacuados", "perdidas_usd", "perdidas_cop", "centros_educativos", "hospitales",
        "cultivos_ha", "ganado_perdido", "vias_m", "glide", "comentarios"]
df = pd.DataFrame(data, columns=cols).drop(columns="_x")
NUM = ["muertos", "heridos", "desaparecidos", "viv_destruidas", "viv_averiadas", "afectados_directos", "afectados_indirectos", "reubicados", "evacuados",
       "perdidas_usd", "perdidas_cop", "centros_educativos", "hospitales", "cultivos_ha", "ganado_perdido", "vias_m"]
for c in NUM:
    df[c] = pd.to_numeric(df[c].str.replace(",", "", regex=False), errors="coerce")
df["fecha"] = pd.to_datetime(df["fecha"], format="%Y/%m/%d", errors="coerce")
df["anio"] = df["fecha"].dt.year
df["fuente_serial"] = df["serial"].str.extract(r"^([A-Za-z]+)")[0]
print("\nrecords:", len(df), "| dates:", df["fecha"].min(), "->", df["fecha"].max(), "| bad dates:", int(df["fecha"].isna().sum()))
print("serial prefixes:", df["fuente_serial"].value_counts().to_dict())
print("events:", df["evento"].value_counts().to_dict())
print("\nrecords per decade:", df.groupby((df["anio"] // 10) * 10).size().to_dict())
print("\nby year (all events):")
g = df.groupby("anio").agg(n=("serial", "size"), muertos=("muertos", "sum"), viv_destr=("viv_destruidas", "sum"), viv_aver=("viv_averiadas", "sum"),
                            usd=("perdidas_usd", "sum"), cop=("perdidas_cop", "sum"), n_usd=("perdidas_usd", lambda s: int((s > 0).sum())), n_cop=("perdidas_cop", lambda s: int((s > 0).sum())))
print(g.to_string())
print("\nnon-zero loss records: USD", int((df["perdidas_usd"] > 0).sum()), "| COP", int((df["perdidas_cop"] > 0).sum()), "| total USD %.0f | total COP %.0f" % (df["perdidas_usd"].sum(), df["perdidas_cop"].sum()))
print("\ntop 15 by USD losses:")
print(df.sort_values("perdidas_usd", ascending=False).head(15)[["serial", "evento", "fecha", "lugar", "muertos", "viv_destruidas", "perdidas_usd", "perdidas_cop"]].to_string())
df.drop(columns=["comentarios"]).to_csv(out, index=False, encoding="utf-8-sig")
df.to_pickle(out.replace(".csv", ".pkl"))
print("saved", out)
