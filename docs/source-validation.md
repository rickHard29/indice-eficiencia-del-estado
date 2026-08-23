# Validación de fuentes del piloto Colombia–Estados Unidos

Corte de validación: **23 de agosto de 2026**. Esta revisión determina, para cada
indicador propuesto, si existen una definición, un código oficial y cobertura
bilateral suficientes antes de descargar el panel o calcular el IEE. Los valores aquí
registrados son puntos de control, no un resultado del índice.

## Dictamen

| ID | Indicador propuesto | Estado | Colombia | Estados Unidos |
|---|---|---|---:|---:|
| SAL-RES-01 | Mortalidad evitable | Validado | 419,0 (2021) | 312,0 (2022) |
| SAL-ACC-01 | Cobertura de servicios esenciales de salud | Validado | 82 (2023) | 88 (2023) |
| SAL-IN-01 | Gasto público en salud por habitante, PPA | Condicional | 1.226,42 (2024) | 7.269,29 (2023) |
| EDU-RES-01 | Puntaje armonizado de aprendizaje | Validado | 419,03 (2020) | 511,80 (2020) |
| EDU-EQ-01 | Brecha PISA por nivel socioeconómico | Validado | 79 (2022) | 102 (2022) |
| EDU-IN-01 | Gasto público por estudiante de primaria | Reserva | 1.817,85 (1999) | 15.989,62 (2021) |
| SEG-RES-01 | Homicidios intencionales por 100.000 habitantes | Validado | 24,91 (2023) | 5,76 (2023) |
| SEG-EQ-01 | Disparidad territorial en seguridad y justicia | Requiere diseño | — | — |
| SEG-IN-01 | Gasto en orden público y seguridad por habitante | Reserva | 430,63 (2024) | 1.551,23 (2024) |
| ADM-RES-01 | Índice de servicios públicos en línea | Validado | 0,7521 (2024) | 0,9136 (2024) |
| ADM-ACC-01 | Tiempo y finalización de transacciones públicas | Requiere diseño | — | — |
| ADM-IN-01 | Recursos operativos de servicios públicos generales | Condicional | 1,844 % (2024) | 1,512 % (2024) |

Resumen: **6 validados, 2 condicionales, 2 en reserva y 2 que requieren diseño**.
Un indicador condicional tiene fuente y cobertura utilizables, pero necesita una
decisión de transformación o definición antes de entrar al modelo. Una reserva no
cumple hoy la comparabilidad requerida.

## Salud

### Resultado: mortalidad evitable

La serie bilateral de la OECD usa el código `AVM`, unidad `DT_10P5HB`, población
total y estandarización `STANDARD`. La medida combina mortalidad prevenible y
tratable según la lista OECD/Eurostat 2022. La [consulta SDMX exacta](https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_STAT@DF_AM,1.0/COL+USA.A.AVM.DT_10P5HB._T._T._Z._Z.STANDARD._Z._Z._Z._Z?startPeriod=2010&endPeriod=2022&dimensionAtObservation=AllDimensions&format=csvfile)
devuelve 419 para Colombia en 2021 y 312 para Estados Unidos en 2022. Es válida para
el piloto bilateral, no como cobertura mundial. Se aplicará promedio móvil y una
prueba de sensibilidad que excluya los años más afectados por la pandemia.

### Acceso: cobertura sanitaria universal

El código vigente es `SH_UHC_SCI`; el código histórico
`SH.UHC.SRVS.CV.XD` no debe utilizarse. La [API oficial del Banco Mundial](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/SH_UHC_SCI?format=json&per_page=200)
contiene 24 observaciones anuales para ambos países entre 2000 y 2023. Es un índice
de 0 a 100 construido por la OMS con 14 indicadores trazadores; por ello no se debe
interpretar como porcentaje literal de personas atendidas.

### Insumo: gasto público en salud

`SH.XPD.GHED.PP.CD`, de la [Global Health Expenditure Database](https://data.worldbank.org/indicator/SH.XPD.GHED.PP.CD),
tiene buena cobertura bilateral y mide PPA corriente por habitante. Queda
condicionado porque el modelo exige recursos en PPA constante. Antes de descargar
el panel debe fijarse el año base y el deflactor; no se mezclarán niveles corrientes
con resultados de otros años.

## Educación

### Resultado: aprendizaje armonizado

La serie `HD.HCI.HLOS`, fuente 63 del Banco Mundial, expresa los resultados en
unidades equivalentes a TIMSS. La [consulta oficial](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/HD.HCI.HLOS?format=json&per_page=100&source=63)
arroja 419,03 para Colombia y 511,80 para Estados Unidos en 2020. La serie es
periódica y escasa: solo se usarán años observados o ventanas explícitas, nunca una
interpolación anual larga.

### Equidad: brecha socioeconómica PISA

La [tabla I.B1.4.3 de PISA 2022](https://www.oecd.org/en/publications/pisa-2022-results-volume-i_53f23881-en/full-report/results-for-countries-and-economies_360c8f67.html)
reporta la diferencia de desempeño en matemáticas entre el cuartil superior e
inferior del índice ESCS: 79 puntos en Colombia y 102 en Estados Unidos. Menor es
mejor. Debe conservarse la advertencia de muestreo publicada para Estados Unidos y
limitar la inferencia a estudiantes de 15 años participantes en PISA.

### Insumo: gasto por estudiante

UNESCO UIS sí publica la definición deseada, código
`XUNIT.PPPCONST.1.FSGOV.FFNTR`, en su [descarga oficial SDG 4 de febrero de 2026](https://download.uis.unesco.org/bdds/202602/SDG.zip).
Sin embargo, la última observación colombiana es de 1999 y la estadounidense de
2021. La serie queda en reserva. Ni gasto como porcentaje del PIB per cápita ni
COFOG educación por habitante sustituyen correctamente el gasto por estudiante.

## Seguridad y justicia

### Resultado: homicidios intencionales

La serie UNODC distribuida en WDI, código `VC.IHR.PSRC.P5`, tiene cobertura
colombiana continua de 1990 a 2023 y cobertura estadounidense con vacíos en
2003–2005. La [consulta bilateral](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/VC.IHR.PSRC.P5?format=json&date=1990%3A2025&per_page=2000)
devuelve 24,91 y 5,76 víctimas por 100.000 habitantes en 2023. Se usará promedio
móvil de tres años o `log1p` y se conservará la [definición ODS 16.1.1](https://unstats.un.org/sdgs/metadata/files/Metadata-16-01-01.pdf).

### Equidad territorial

No se identificó una fuente internacional que armonice una medida subnacional
equivalente para ambos países. El indicador requiere un protocolo propio de
agregación desde fuentes territoriales, con definiciones compatibles y ponderación
por población. No entra al piloto hasta diseñar y probar ese protocolo.

### Insumo: gasto en orden público y seguridad

OECD COFOG `GF03` es comparable y cubre policía, bomberos, tribunales y prisiones,
pero el valor por habitante en PPA es una serie derivada. La [consulta de gasto
nominal](https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NASEC10@DF_TABLE11,1.1/A.COL+USA.S13._Z.D.OTE._Z.GF03.XDC.S.V.N.T1100?startPeriod=2009&endPeriod=2024&dimensionAtObservation=AllDimensions&format=csvfile)
se combina con las consultas WDI de [`PA.NUS.PPP`](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/PA.NUS.PPP?format=json&date=2024&per_page=200)
y [`SP.POP.TOTL`](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/SP.POP.TOTL?format=json&date=2024&per_page=200)
así:

```text
PPA corriente por habitante = gasto GF03 × 1.000.000 / factor PPA / población
```

Los controles de 2024 son 430,63 para Colombia y 1.551,23 para Estados Unidos.
Queda en reserva —y no solo condicional— porque, a diferencia del gasto sanitario,
no es una serie final directa: exige unir tres datasets, fijar precios constantes y
documentar el tratamiento de las revisiones de cuentas nacionales.

## Administración

### Resultado: servicios públicos en línea

El Online Service Index (OSI) de UN DESA es bienal, cubre los 193 Estados miembros
y usa una escala de 0 a 1. El [anexo oficial de la encuesta 2024](https://desapublications.un.org/file/20866/download)
reporta 0,7521 para Colombia y 0,9136 para Estados Unidos. Mide oferta y madurez de
servicios digitales, no uso efectivo, costo, tiempo ni satisfacción. Se prefiere al
EGDI para evitar doble conteo de capital humano e infraestructura.

### Acceso y finalización de trámites

No se encontró una serie bilateral armonizada de tiempo y finalización efectiva de
transacciones públicas. WGI Government Effectiveness es una percepción institucional
agregada y no sustituye esta medida. Se mantendrá solo como contraste, usando la
[revisión WGI 2025](https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators)
y sus errores estándar.

### Insumo: recursos operativos administrativos

La proxy provisional usa únicamente series OECD y calcula:

```text
100 × (compensación de empleados D1 + consumo intermedio P2 en S13/GF01) / PIB B1GQ
```

La [consulta funcional D1 y P2](https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NASEC10@DF_TABLE11,1.1/A.COL+USA.S13._Z.D.D1+P2._Z.GF01.XDC.S.V.N.T1100?startPeriod=2009&endPeriod=2024&dimensionAtObservation=AllDimensions&format=csvfile)
y la [consulta de PIB nominal](https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE,2.0/A.COL+USA.S1.S1.B1GQ._Z._Z._Z.XDC.V.N.T0102?startPeriod=2009&endPeriod=2024&dimensionAtObservation=AllDimensions&format=csvfile)
producen 1,844 % para Colombia y 1,512 % para Estados Unidos en 2024. Es preferible
al GF01 total porque excluye intereses y transferencias, aunque todavía incluye
funciones generales heterogéneas. Queda condicional hasta decidir si se modifica la
definición metodológica o se convierte a una medida de volumen por habitante.

## Reglas para la siguiente fase

1. Congelar los códigos, consultas y fecha de descarga en cada versión de datos.
2. No imputar los indicadores en reserva ni los que requieren diseño.
3. Resolver PPA constante para los insumos de salud y seguridad.
4. Probar la proxy administrativa con promedio 2022–2024 y compararla con WGI solo
   como sensibilidad.
5. No calcular un puntaje general hasta que cada dimensión cumpla el umbral de
   cobertura y cuente con un insumo compatible.

La fuente legible por máquina de este inventario es
[`config/pilot_sources.toml`](../config/pilot_sources.toml).
