#!/bin/bash
# Regenera con ejes en km los mapas de 7.1 y 8.1 usando el entorno de mapas del proyecto (Python de Codex + .mapdeps).
B="C:/Users/marco/.codex/.chatgpt-projects/g-p-6a9707bd4d7881918247b690a771ddbd"
PYX="C:/Users/marco/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
export PYTHONPATH="$B/.mapdeps"
export MPLCONFIGDIR="$B/.mpl-p1"
export PYTHONIOENCODING=utf-8
SP="C:/Users/marco/AppData/Local/Temp/claude/G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude/446a2666-30c7-4c61-98e1-c82458a0665f/scratchpad/figuras_km"
export KM_OUT="$SP/salida"
R="C:/Users/marco/Documents/GitHub/PAC_2026_MED"
D="G:/Mi unidad/2.Consultoria/01_PAC_MEDELLIN_2026/2.Ejecución/C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA/P1_Caracterizacion_Socioeconomica_Ambiental/02_DOCUMENTOS_EN_ELABORACION"
corre() { echo "######## $1"; shift; "$PYX" "$SP/corre_en_km.py" "$@" 2>&1 | grep -v -E "Warning|warn" | tail -6; }

corre "dias calurosos" "$R/P1_08_1_AMENAZAS/CODIGO/mapa_dias_calurosos_referencia.py" "$KM_OUT"
corre "temperatura superficial" "$R/P1_08_1_AMENAZAS/CODIGO/mapas_temperatura_superficial.py" "$D/08_1_AMENAZAS/02_ISLAS_DE_CALOR_AMVA/02_DATOS_PREPARADOS" "$KM_OUT"
corre "riesgo precipitacion extrema" "C:/Users/marco/Downloads/PAC_2026_Referencias_7.1_8.1/8.1_script_mapa_riesgo_precip_extrema.py"
corre "riesgo escasez" "C:/Users/marco/Downloads/PAC_2026_Referencias_7.1_8.1/8.1_script_mapa_riesgo_escasez.py"
corre "diferencia 2040-2030" "$R/P1_08_1_AMENAZAS/DAGRD_SIATA_ESCENARIOS/mapa_diferencia_2040_2030.py"
corre "relieve (elevacion y pendiente)" "$R/12_RELIEVE_LAYOUT_POMCA.py"
corre "Koppen" "$R/publicar_koppen_medellin.py" "$D/07_1_CLIMA_RELIEVE"
corre "salud" "$R/P1_08_1_AMENAZAS/CODIGO/mapa_riesgo_salud_clima.py" "$KM_OUT"
echo FIN
