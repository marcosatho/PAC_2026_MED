# Notas de trabajo — P2 prospectiva climática (2026-10-26, noche)

Reglas del encargo: borrador estructural ≥20 págs (con figuras); 3 fases (fuentes y acuerdos / datos y evidencias / conclusiones);
no tocar archivos del PAC (solo lectura); no descargar datos nuevos (dejar trazabilidad); citar como en el P1 (RT docx "(2)");
lenguaje técnico pero universal; avanzar sin pausas.

## Rutas (todas leídas, nada modificado)
- BASE P1: G:\Mi unidad\2.Consultoria\01_PAC_MEDELLIN_2026\2.Ejecución\C1_01_EVIDENCIA_DIAGNOSTICO_PROSPECTIVA\P1_Caracterizacion_Socioeconomica_Ambiental
- Datos SIATA ya locales: BASE\02_DOCUMENTOS_EN_ELABORACION\08_1_AMENAZAS\01_DAGRD_SIATA_ESCENARIOS\01_DATOS_ORIGINALES\Archivos_Soporte\{1_Precip_media,2_Temper_media,3_Precip_extrema,4_Num_dias_Tmax,5_Susc_Incendios,6_RTI,7_Probabilidad_excedencia,8_IndiceRiesgo,9_IA_CWSI_Antioquia,10_IA_Medellin,11_T2_ETP,12_RAIN_ETR}
- Límites Medellín: BASE\02_DOCUMENTOS_EN_ELABORACION\07_1_CLIMA_RELIEVE\03_DATOS_PREPARADOS\20260910\limites_medellin_9377.gpkg (capas limite_medellin, comunas_corregimientos) y *_4326.geojson
- UdeA gdb extraída en scratch p2\udea_gdb (de Downloads\OneDrive_1_21-10-2026.zip); rasterio abre rasters con OpenFileGDB (GDAL 3.12.4)
- Python: codex python.exe + sys.path.append(scratchpad\libs) (matplotlib, shapely, pyproj, pyshp instalados solo en scratch)
- OneDrive personal Alcaldía (1044100469): Doc_Cambio climático MED/{...}; solo listado leído por REST; sin descargas.

## SIATA 2019 (PDF = BP\SIATA_2019_Convenio_DAGRD_Escenarios_Clima.pdf; págs. = visor PDF; impresa = PDF−5)
- Conv. Interadmin. 4600082037/2019; presentado a AMVA y DAGRD; nov-2019. (p.1–2)
- 3 horizontes: 1990-2000 (ref.), 2030-2040, 2040-2050; "año climatológico representativo" de 10 años del MCG por década (p.8)
- RCP4.5 (IPCC 2014) "moderado"; CCSM4 (CMIP5), 0,9424°×1,25° (104×138 km); dominios WRF 12/3/1 km (Colombia / Antioquia / Valle de Aburrá); salida horaria 1 km (p.9, 15)
- CMIP6 no usado: aún en liberación (p.9)
- Incoherencia IDEAM 2.ª vs 3.ª comunicación en Antioquia: −30 % vs +30 % precip. 2011-2040 (p.12)
- Validación contra radar Santa Elena (≈6 años) (p.18)
- T media: casco urbano 19–21 °C en 1990-2000; Medellín ≈21 °C; +1,05 °C zona urbana y +0,9 laderas 2030-40; +1,05–1,2 °C 2040-50 (p.19–20)
- Precip. media: leve disminución NE (Barbosa, Girardota, Copacabana) 2–6 mm/día; centro y suroeste sin cambios representativos (p.21)
- Precip. extrema P90/P95 horaria: disminuye Barbosa/Girardota; se intensifica en los demás; señal más intensa a 2040; zonas al occidente del casco urbano disminuyen (p.22)
- Días > umbrales 28/29/30 °C: ≈150 días/año >29 °C hacia 2040-50 sobre Medellín (p.26); máx. diaria sube ≈0,5 °C 2030→2040 (p.26-27); contraste casco urbano vs. promedio municipal >5 °C al mediodía-tarde (p.26)
- Amenazas: índice R (Moreno 2006: R = P3 + 0,5·P15 − 75) movimientos en masa; RTI avenidas torrenciales (Jan 2018; Guerrero y Giraldo 2019); precip. extrema para inundaciones; modelo bayesiano SIATA incendios (>5000 eventos) (p.30–38); no son mapas de zonificación de amenaza (p.28)
- Palmitas–San Cristóbal: mayor aumento R90/R95 (p.41); RTI90 sube en Doña María oriental, bajo río Medellín, Palmitas (p.42); incendios: sin cambio generalizado; sube cerca del casco urbano (p.46)
- Conclusiones/limitaciones: un año climatológico/década, un solo escenario, resolución >100 km de partida; sin variabilidad interanual/ENSO (p.48–50)

## UdeA 2026a (PDF = BP\UdeA_2026a_Escenarios_cambio_climatico_CCMED.pdf; impresa = PDF−1)
- Contrato 4600105139/2025 (26/06/2025–26/03/2026), SMA Medellín–UdeA (p.1)
- 19 modelos NEX-GDDP-CMIP6 (0,25°; Thrasher 2022; reducción estadística) + 7 HighResMIP (hist-1950, HighresFuture≈SSP5-8.5 hasta 2050) (p.23–26)
- Obs.: CHIRTS (0,05°, 1983-2016) y CHIRPS v2 (1981-2014) (p.26); índices ETCCDI (TX95p, TN95p, WSDI; RX1day, R95p, R99p, CWD, INT, DSL, CDD, SPI3, HY-INT, PRCPTOT) + compuestos CDHE/CHEE (p.28–35)
- SSP1-2.6, 2-4.5, 3-7.0, 5-8.5; horizontes 2021-2050 y 2071-2100; referencia 1981-2010 (P) y 1983-2010 (T) (p.36–37)
- Región 1 = Antioquia (9,07–5,21°N; 77,43–73,57°W), Región 2 = 5,5–7°N, 76–75°W (p.22, 37–38)
- Desempeño: correlaciones débiles-moderadas en índices de T; Taylor skill <0,4; sesgos importantes en P (p.39, 115)
- Tabla 5 (SSP3-7.0, Antioquia; p.117): SPI3 ↓ (−0,05/−0,1 corto; −0,1/−0,25 largo); CDD +1–2 d (DEF) corto, +1–3 largo; DSL sin cambio corto, +0,5–1 largo; RX1day +2–3 mm corto, +5–10 mm largo; R95p +30–50 mm (MAM) corto, +50–80 largo; R99p +15–30 corto, +30–50 largo; INT +0,5–1 mm/día corto, +0,5–2 largo; CWD −2–4 d corto, −2–6 largo; WSDI +100–600 d corto, +1000–2000 d largo; TX95p +10–30 % días corto, +60–75 % largo; TN95p +10–30 % corto, +75–95 % largo
- Mensaje: alta confianza en el signo: "lloverá más duro y hará más calor" (p.118); acuerdo >80 % en TX95p, TN95p, WSDI; TN95p>TX95p (más noches cálidas); sin señal clara en CDD/DSL corto plazo; SPI3 sin acuerdo; RX1day/R95p/R99p/INT aumento con alta confianza; CHEE aumenta con alto acuerdo (p.115–116)
- gdb (Downloads zip): rasters AMN_* a 27,6 km (0,25°) por modelo (BCC-CSM2-MR, CanESM5, KACE-1-0-G, MPI-ESM1-2-HR) SSP3-7.0 2021-2050: TN95p (trimestral), R95p, R99p, INT, CWD, RX1day (cambios anuales)

## IDEAM
- 2015 (Tercera Comunicación; PDF = Downloads\undp-co-escenarioscambioclima_departamental-2015.pdf; 60 págs.): 16 MCG CMIP5, REA, 4 RCP, ref. 1976-2005, periodos 2011-2040/2041-2070/2071-2100; ficha Antioquia (PDF p.24): ΔT +0,8/+1,4/+2,2 °C; ΔP +4,88/+6,91/+9,30 %; mayores aumentos de P en Valle de Aburrá, Occidente y Suroeste; fin de siglo +9,3 % (p.24)
  -> El texto del equipo PAC dice +0,86 °C y 4,7 % (2011-2040): NO coincide con la ficha de 2015 (0,8 y 4,88). Verificar en TCNCC 2017.
- 2024 (Cuarta Comunicación; PDF = Downloads\escenarios_de_cambio_de_la_cuarta_comunicacion_de_colombia.pdf; 194 págs.; cítese: Ideam 2024): 25 modelos CMIP6 (NEX-GDDP, 25 km) → cubo de datos 10×10 km 1981-2020 (1753 est. P; 215 Tmed; 151 Tmax; 204 Tmin; CHIRPS, MERRA); HR de CHIRTS; viento y radiación de ERA5; BC factores mensuales; ponderación por correlación (t de Student, 95 %); SSP1-2.6/2-4.5/3-7.0/5-8.5 (SSP4-6.0 omitido); periodos 2021-2040/2041-2060/2061-2080/2081-2100 vs 1981-2010; 7 variables; anual, trimestral, mensual (p.20–46)
  - Precip. anual 2021-2040: cambios dentro del rango normal (~10 %), >10–20 % en el centro de la región Andina; reducciones SSP5-8.5 en Caribe/Orinoquia (p.46)
  - Tmed 2021-2040: +0,5–2 °C país; mayores en Catatumbo (p.52); Tmín 2021-2040 +0,4–2 °C, mayores en centro de la región Andina (p.50); Tmáx +0,4–2 °C (p.48)
  - HR: reducciones 0,5–2 % en gran parte del país 2021-2040 (p.54); viento: reducciones 0,2–1 m/s, regiones Andina/Pacífica a fin de siglo (p.56); radiación: +3–10 W/m² 2021-2040 (p.58)
  - Cap. final p.190: "posiblemente se incrementen la intensidad y la frecuencia de los eventos extremos" (deducción de cambios mensuales; no hay índices de extremos)
- Metodología (NT IDEAM-2023-001; GCI-G004 de 25/03/2026): por leer

## Texto del equipo PAC (a verificar)
- "CCSM4 SIATA 2019 RCP4.5" ✔ (SIATA p.9, 15); "TCNCC 2017 Antioquia 2011-2040 +0,86 °C y 4,7 %" ✘ no hallado (ficha 2015: 0,8 °C / 4,88 %)
- "IDEAM 2024 nuevas variables (humedad, viento, radiación)" ✔ ; "proyectan mayor frecuencia de eventos extremos" ≈ solo inferencia en p.190, no índices
- "AMVA 2021-2040 precip +10–20 %, T +1–1,5 °C" : por verificar en mapas Fig. 4.2/4.5 (lectura visual)

## Estado final (26-oct-2026, madrugada)
- Documento: C:\Users\marco\Downloads\P2_prospectiva_climatica\P2_Prospectiva_climatica_borrador_v0.1.docx (20 figuras, 10 tablas; PyMuPDF no pagina bien docx: sin imágenes ni tablas; conviene revisar en Word).
- Hallazgos de verificación: ver LEEME_primero.md (texto del equipo: lluvia 10–20 % no se sostiene sobre Medellín; "sustancialmente más alta" no se sostiene en temperatura; 0,86 °C / 4,7 % por verificar; errata 1940–1950 en el Anexo 14, p. 21).
- SIATA: ráster de temperatura en kelvin; lluvia mensual = un año simulado por década (ruido). Ráster ya estaban en el Drive del P1.
- UdeA gdb: 4 celdas (0,25°) tocan el Distrito; AMN_* solo SSP3-7.0 2021-2050 con 4 modelos.
- IDEAM 2024: lectura de clases de color (±0,15°); 90 % de las 112 combinaciones mantienen clase dominante con ventana ±0,30°.
