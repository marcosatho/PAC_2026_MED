# -*- coding: utf-8 -*-
import zipfile, os, sys
import numpy as np, rasterio
sys.stdout.reconfigure(encoding="utf-8")
Z = "C:/Users/marco/Downloads/31. Islas de calor AMVA.zip"
DEST = ("G:/Mi unidad/2.Consultoria/01_PAC_MEDELLIN_2026/2.Ejecución/C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA/P1_Caracterizacion_Socioeconomica_Ambiental/"
        "02_DOCUMENTOS_EN_ELABORACION/08_1_AMENAZAS/02_ISLAS_DE_CALOR_AMVA/01_DATOS_ORIGINALES")
os.makedirs(DEST, exist_ok=True)
z = zipfile.ZipFile(Z)
want = ["Isla de calor/Mediana_LST.tif", "Isla de calor/Mediana_LST_norm.tif", "Isla de calor/Hotspots_LST1.tif", "Isla de calor/Bajo_ndvi1.tif",
        "Isla de calor/Zonas_Interv1.tif", "Isla de calor/Mediana_LST.tif.aux.xml", "Isla de calor/Mediana_LST_norm.tif.aux.xml",
        "Isla de calor/Cartografia_mediana_LST_PAVACC.pdf", "Isla de calor/Cartografia_mediana_LST_normalizada_PAVACC.pdf",
        "Isla de calor/Cartografia_hotspotas_temperatura_superficial_PAVACC.pdf", "Isla de calor/Cartografia_zonas_intervencion_Isla_de_calor_PAVACC.pdf",
        "Isla de calor/Cartografia_NDVI_bajos_PAVACC.pdf"]
for n in want:
    out = os.path.join(DEST, os.path.basename(n))
    if not os.path.exists(out):
        with z.open(n) as src, open(out, "wb") as dst:
            dst.write(src.read())
print("extracted to", DEST, "| files:", len(os.listdir(DEST)))
for r in ("Mediana_LST.tif", "Mediana_LST_norm.tif", "Hotspots_LST1.tif", "Bajo_ndvi1.tif", "Zonas_Interv1.tif"):
    with rasterio.open(os.path.join(DEST, r)) as s:
        a = s.read(1)
        nd = s.nodata
        v = a[(a != nd) & np.isfinite(a)] if nd is not None else a[np.isfinite(a)]
        print(f"{r}: {s.shape} | res {s.res[0]:.1f} m | dtype {s.dtypes[0]} | nodata {nd} | bounds {[round(x) for x in s.bounds]}")
        print("    CRS:", (s.crs.to_string()[:110] if s.crs else None))
        print("    values: min %.3f  p5 %.3f  median %.3f  p95 %.3f  max %.3f | unique(sample) %d" % (v.min(), np.percentile(v, 5), np.median(v), np.percentile(v, 95), v.max(), len(np.unique(v[:200000]))))
