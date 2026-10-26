#!/bin/bash
# Parte del lote que usa el Python de QGIS (osgeo): mapas del POMCA y mapas de amenaza v2 (capa oficial del DAP).
SPK="C:/Users/marco/AppData/Local/Temp/claude/G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude/446a2666-30c7-4c61-98e1-c82458a0665f/scratchpad/figuras_km"
SPV="C:/Users/marco/AppData/Local/Temp/claude/G--Mi-unidad-1-Investigaci-n-Hidrometereologia-NPP-VS-PET-P-Claude/446a2666-30c7-4c61-98e1-c82458a0665f/scratchpad/v2_amenazas"
D="G:/Mi unidad/2.Consultoria/01_PAC_MEDELLIN_2026/2.Ejecución/C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA/P1_Caracterizacion_Socioeconomica_Ambiental/02_DOCUMENTOS_EN_ELABORACION"
export KM_OUT="$SPK/salida"
echo "### POMCA"
"/c/Program Files/QGIS 3.44.14/bin/python-qgis-ltr.bat" "$SPK/corre_en_km.py" "$SPK/pomca_arbol/07_POMCA_RIO_ABURRA/recortar_pomca_medellin.py" 2>&1 | grep -c "km ->"
echo "### amenaza v2"
export V2_PREP="$D/08_1_AMENAZAS/05_POT2026_AMENAZAS_OFICIAL_V2/02_DATOS_PREPARADOS/pot2026_amenazas_oficial_v2_9377.gpkg"
export V2_FIGS="$SPK/amenaza_v2"
unset V2_ONLY
"/c/Program Files/QGIS 3.44.14/bin/python-qgis-ltr.bat" "$SPV/mapas_amenaza_pot2026_v2.py" 2>&1 | grep -E "^saved|Error|Traceback" | cut -c1-120
echo FIN_QGIS
