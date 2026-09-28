# -*- coding: utf-8 -*-
"""Extract the DAGRD event tables (Tabla 13 landslides 2005-2018, Tabla 14 floods and torrential floods 2005-2018,
Tabla 15 vegetation fires 2016-2018) from PASCCM Tomo I (Secretaría de Salud de Medellín, 2021, pp. 204-206).

The PDF tables have no ruling lines, so cells are rebuilt from word coordinates: each number is assigned to the
year column whose x-centre is closest; blank cells stay empty (no events reported). Column totals are validated
against the printed 'Total general' row.

usage: dagrd_tables_extract.py <out_dir>"""
import re
import sys
import fitz
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40)
OUT = sys.argv[1]
PDF = "C:/Users/marco/Downloads/PAC_2026_Referencias_7.1_8.1/SecSalud_2021_PASCCM_Tomo_I.pdf"
doc = fitz.open(PDF)


def lines_of(page):
    """Words grouped in text lines: list of (y, [(x0, x1, text)...]) sorted top to bottom."""
    words = page.get_text("words")
    rows = []
    for x0, y0, x1, y1, w, *_ in sorted(words, key=lambda t: (round((t[1] + t[3]) / 2), t[0])):
        yc = (y0 + y1) / 2
        for r in rows:
            if abs(r[0] - yc) < 2.5:
                r[1].append((x0, x1, w)); break
        else:
            rows.append([yc, [(x0, x1, w)]])
    return sorted(rows, key=lambda r: r[0])


def is_num(s):
    return re.fullmatch(r"\d{1,5}", s) is not None


def parse(page_no, start, table_id, label_x_max, col_centers=None):
    """Return {label: {year: value}} for the block of rows on a page that belongs to `table_id`."""
    page = doc[page_no - 1]
    rows = lines_of(page)
    res, cur, pending_label = {}, start, None
    centers = col_centers
    for y, ws in rows:
        text = " ".join(w for _, _, w in ws)
        m = re.match(r"Tabla (\d+)\.", text)
        if m:
            cur = int(m.group(1)); pending_label = None; continue
        if cur != table_id:
            continue
        yrs = [(x0 + x1) / 2 for x0, x1, w in ws if re.fullmatch(r"20\d\d", w)]
        if len(yrs) >= 3:
            centers = {int(w): (x0 + x1) / 2 for x0, x1, w in ws if re.fullmatch(r"20\d\d", w)}
            continue
        label_ws = [w for x0, x1, w in ws if x0 < label_x_max]
        num_ws = [((x0 + x1) / 2, w) for x0, x1, w in ws if x0 >= label_x_max and is_num(w)]
        label = " ".join(label_ws).strip()
        if not num_ws:
            if re.match(r"(\d\d\.|Total)", label):
                pending_label = label
            continue
        if not re.match(r"(\d\d\.|Total)", label):
            label = (pending_label + " " + label).strip() if pending_label else label
        pending_label = None
        if centers is None:
            continue
        cells = {}
        for xc, w in num_ws:
            yr = min(centers, key=lambda k: abs(centers[k] - xc))
            cells[yr] = int(w)
        if re.match(r"(\d\d\.|Total)", label):
            res[label] = cells
    return res, centers


def to_df(res, years):
    df = pd.DataFrame(res).T.reindex(columns=years)
    return df


# ---- Table 13 (page 204) ------------------------------------------------------------------------------------
YRS = list(range(2005, 2019))
t13, c13 = parse(204, None, 13, 148)
df13 = to_df(t13, YRS)
# ---- Table 14: rows 01-02 on page 204 (own header), rows 03-90 + total on page 205 (columns from the total row) ----
t14a, c14a = parse(204, None, 14, 148)
# page 205 has no year header for Table 14: reuse the x-centres of the printed 'Total general' row (14 values)
p205 = lines_of(doc[204])
tot_line = [ws for y, ws in p205 if any(w == "Total" for _, _, w in ws)][0]
tot_nums = [((x0 + x1) / 2) for x0, x1, w in tot_line if is_num(w)]
assert len(tot_nums) == 14, len(tot_nums)
c14b = {yr: xc for yr, xc in zip(YRS, tot_nums)}
t14b, _ = parse(205, 14, 14, 148, col_centers=c14b)
df14 = to_df({**t14a, **t14b}, YRS)
# ---- Table 15: rows 01-04 on page 205, rest on page 206 (three columns 2016-2018) ------------------------------
YRS15 = [2016, 2017, 2018]
t15a, _ = parse(205, 14, 15, 280)
p206 = lines_of(doc[205])
tot206 = [ws for y, ws in p206 if any(w == "Total" for _, _, w in ws)][0]
n206 = [((x0 + x1) / 2) for x0, x1, w in tot206 if is_num(w)]
c15b = {yr: xc for yr, xc in zip(YRS15, n206)}
t15b, _ = parse(206, 15, 15, 280, col_centers=c15b)
df15 = to_df({**t15a, **t15b}, YRS15)


def report(name, df, years):
    body = df[~df.index.str.startswith("Total")]
    tot = df[df.index.str.startswith("Total")].iloc[0]
    s = body.sum()
    print(f"\n=== {name}: {len(body)} territories | printed total vs sum of rows")
    print(pd.DataFrame({"total_impreso": tot, "suma_filas": s, "diferencia": tot - s}).T.to_string())


for name, df, yrs in (("Tabla 13 movimientos en masa", df13, YRS), ("Tabla 14 inundaciones y avenidas torrenciales", df14, YRS),
                      ("Tabla 15 incendios de cobertura vegetal", df15, YRS15)):
    print("\n", name); print(df.to_string())
    report(name, df, yrs)


def tidy(df, hazard):
    d = df.copy()
    d.index.name = "territorio_raw"
    d = d.reset_index().melt(id_vars="territorio_raw", var_name="anio", value_name="eventos")
    d["amenaza"] = hazard
    d["eventos"] = d["eventos"].fillna(0).astype(int)   # blank cell = no events reported
    d["cod"] = d["territorio_raw"].str.extract(r"^(\d\d)\.")[0]
    d["territorio"] = d["territorio_raw"].str.replace(r"^\d\d\.\s*", "", regex=True).str.replace("12 de Octubre", "Doce de Octubre") \
        .str.replace("Laureles Estadio", "Laureles-Estadio").str.replace("Palmitas", "San Sebastián de Palmitas")
    return d


long = pd.concat([tidy(df13, "movimiento en masa"), tidy(df14, "inundación y avenida torrencial"), tidy(df15, "incendio de cobertura vegetal")])
long.to_csv(f"{OUT}/dagrd_eventos_por_territorio_2005_2018.csv", index=False, encoding="utf-8-sig")
print("\nsaved", len(long), "rows")
