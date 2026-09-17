# Precipitación: alcance y reservas

CHIRPS combina estimaciones satelitales y estaciones. Aceptación exploratoria por concordancia de orden de magnitud reportada por el usuario; fuentes externas todavía sin incorporar. No constituye validación cuantitativa local. Posibles sesgos espaciales y temporales, especialmente en terreno montañoso. El suavizado no mejora la resolución efectiva de 0,05°.

Se requiere incorporar la referencia externa consultada por el usuario y contrastar con estaciones para validar cuantitativamente.

El filtro gaussiano usa el entorno regional antes del recorte; maneja NoData mediante pesos normalizados y exige soporte completo en Medellín. Los píxeles se identifican en la cuadrícula geográfica original y se proyectan a EPSG:9377 para intersección y área. La máscara del ráster suavizado usa el centro de cada celda de representación.

## Próxima fase

Primero se auditará si las descargas CHIRPS disponibles son pentadales o mensuales. La clasificación Niño/Niña/neutral mediante ONI y confirmación por periodo móvil requiere conservar la dimensión mensual o agregar explícitamente las pentadas a meses, hasta 2025.

Productos previstos: mapas por fase ENSO; serie temporal anual por fase; precipitación municipal ponderada con `exact_extract`, `P = sum(Pi * Ai) / sum(Ai)`; y ficha de minería del paper de E. Aristizábal.

El mapa gaussiano de referencia debe usar el ráster regional completo y superponer el límite municipal. El ráster municipal enmascarado puede producir bordes escalonados de `NoData` y no debe usarse para diagnosticar cobertura regional.
