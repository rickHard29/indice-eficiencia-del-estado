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
| SAL-EQ-02 (candidata v0.7) | Brecha de dificultad financiera por quintil | Rechazada v0.7 | 1,40 p.p. (2021) | 26,53 p.p. (2023) |
| SAL-IN-01 | Gasto público en salud por habitante, PPA | Condicional | 1.226,42 (2024) | 7.269,29 (2023) |
| EDU-RES-01 | Puntaje armonizado de aprendizaje | Validado | 419,03 (2020) | 511,80 (2020) |
| EDU-EQ-01 | Brecha PISA por nivel socioeconómico | Validado | 79 (2022) | 102 (2022) |
| EDU-IN-01 | Gasto público por estudiante de primaria | Reserva | 1.817,85 (1999) | 15.989,62 (2021) |
| SEG-RES-01 | Homicidios intencionales por 100.000 habitantes | Validado | 24,91 (2023) | 5,76 (2023) |
| SEG-EQ-01 | Disparidad territorial en seguridad y justicia | Requiere diseño | — | — |
| SEG-IN-01 | Gasto en orden público y seguridad por habitante | Reserva | 430,63 (2024) | 1.551,23 (2024) |
| ADM-RES-01 | Índice de servicios públicos en línea | Validado | 0,7521 (2024) | 0,9136 (2024) |
| ADM-ACC-01 | Tiempo y finalización de transacciones públicas | Requiere diseño | — | — |
| ADM-ACC-02 | Carga regulatoria de trámites empresariales | Condicional; subindicador empresarial v1.6 | 26,1692 % (2023) | 5,7544 % (2024) |
| ADM-EPI-01 (candidata v1.2) | Participación electrónica | Rechazada v1.2 como acceso | 0,7397 (2024) | 0,9452 (2024) |
| ADM-SAT-01 (candidata v1.3) | Satisfacción con último servicio gubernamental | Rechazada v1.3 por cobertura | — | — |
| ADM-ID-01 (candidata v1.4) | Identidad oficial como prerrequisito de acceso | En evaluación metodológica | 98,3836 % (2024) | 89,7975 % (2024) |
| ADM-IN-01 | Recursos operativos de servicios públicos generales | Condicional | 1,844 % (2024) | 1,512 % (2024) |

Resumen del catálogo del piloto: **6 validados, 3 condicionales, 2 en reserva y
2 que requieren diseño**. La candidata SAL-EQ-02 no se materializa en el catálogo
ni cambia esos conteos.
Un indicador condicional tiene fuente y cobertura utilizables, pero necesita una
decisión de transformación o definición antes de entrar al modelo. Una reserva no
cumple hoy la comparabilidad requerida.

### Cribado v1.2: participación no equivale a acceso administrativo

La tabla 9 del [apéndice técnico oficial de la Encuesta de Gobierno Electrónico
2024 de la ONU](https://desapublications.un.org/sites/default/files/publications/2024-10/Technical%20Appendix%20%28Web%20version%29%2030102024.pdf)
ofrece el *E-Participation Index* (EPI) para los 38 países OCDE. Colombia tiene
0,7397 y Estados Unidos 0,9452. La cobertura es suficiente, pero el índice se
compone de e-información, e-consulta y e-toma de decisiones: describe mecanismos
institucionales de participación, no la experiencia de completar un trámite, su
tiempo de respuesta, uso efectivo ni accesibilidad para grupos distintos.

Por ello `ADM-EPI-01` queda rechazada como sustituto de `ADM-ACC-01`; puede
servir más adelante como referencia de participación cívica, sin puntaje ni
reponderación. El *Digital Government Index* 2023 de la OCDE también se descartó
como alternativa: es una medida de capacidades y políticas y su edición no
incluye a Estados Unidos. La decisión completa está en la
[ADR 0016](decisions/0016-v12-administrative-access-screen.md).

### Cribado v1.3: experiencia de servicio sin cobertura bilateral

El indicador ODS 16.6.2 es metodológicamente pertinente porque pregunta por la
satisfacción con la última experiencia de servicio y su metadato contempla
atributos como acceso, oportunidad e información. La descarga oficial del
subindicador de servicios gubernamentales contiene 37 países, pero no una
observación para Colombia ni Estados Unidos. La fuente de [datos ODS de la
ONU](https://unstats.un.org/SDGAPI/v1/sdg/Indicator/Data?indicator=16.6.2&pageSize=1000)
no permite entonces sostener el piloto bilateral.

La encuesta de confianza de la OCDE, que sí pregunta por satisfacción de usuarios
recientes de servicios administrativos, confirma el mismo tipo de constructo;
sin embargo, Estados Unidos no participó en sus rondas 2023 (30 países) ni 2025
(33 países). `ADM-SAT-01` queda rechazada por cobertura, no por definición. Se
prohíbe mezclarla con encuestas nacionales no armonizadas. Véase la
[ADR 0017](decisions/0017-v13-administrative-service-experience-screen.md).

### Cribado v1.4: identidad como prerrequisito, no como trámite completado

El módulo ID4D--Global Findex 2025 del Banco Mundial es abierto y entrega una
medida de identidad oficial con cobertura de 34 de los 38 países OCDE, incluidos
Colombia y Estados Unidos, además de cortes por sexo, ingreso y zona. Es una
fuente útil para estudiar el requisito de poder acreditar identidad, que habilita
servicios y beneficios, pero no mide el tiempo ni la finalización de un trámite.
Por eso `ADM-ID-01` se conserva en evaluación y no cambia `ADM-ACC-01`.

Las dos variables de uso más directas del mismo módulo no resuelven el problema:
la de acceso reciente a servicios o información gubernamental en línea no cubre
Estados Unidos, y la de uso de identidad digital no cubre Colombia. Sus
coberturas OCDE son respectivamente cuatro y 28 países. La decisión completa y
los códigos de API están en la
[ADR 0018](decisions/0018-v14-administrative-identity-access-screen.md).

### Cribado v1.5: tiempo reportado de cumplimiento regulatorio empresarial

La serie abierta `IC.GOV.DURS.ZS` de *Enterprise Surveys* mide el porcentaje
del tiempo semanal de alta gerencia dedicado a impuestos, aduanas, regulación
laboral, licencias, registros, funcionarios y formularios. Cubre los 38 países
OCDE con su última observación entre 2020 y 2025; 37 están entre 2023 y 2025.
Colombia registra 26,1692 % en 2023 y Estados Unidos 5,7544 % en 2024.

Es una candidata más próxima al tiempo efectivo de trámites, pero representa a
establecimientos privados y no a toda la población. Con la aprobación v1.6,
`ADM-ACC-02` se adopta como subindicador condicional empresarial: no reemplaza el
rol ciudadano pendiente, no puntúa y no habilita resultados oficiales. La
[ADR 0020](decisions/0020-v16-business-access-adoption.md) conserva el contrato
ejecutable y sus límites.

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

### Equidad: brecha de dificultad financiera por quintil

La definición revisada en 2025 del indicador ODS 3.8.2 de la OMS mide la
proporción de población cuyo gasto directo en salud supera el 40 % de su
presupuesto discrecional. La [API oficial de la OMS](https://ghoapi.azureedge.net/api/FINANCIALHARDSHIP_PROPORTIONOFPOP)
publica observaciones por quintil de riqueza, con las que se puede construir una
diferencia de puntos porcentuales entre el primer y el quinto quintil como
candidata de desigualdad.
Los puntos de control más recientes son 1,40 p.p. para Colombia (2021) y 26,53
p.p. para Estados Unidos (2023), calculados como `Q1 - Q5` a partir de las
observaciones de cada país y año.

La candidata queda rechazada en v0.7 y no se incorpora al panel ni al catálogo.
Solo 32 de los
38 países OCDE tienen ambos quintiles en algún año; la cobertura baja a 25 desde
2010, 21 desde 2015 y 16 desde 2019. No alcanza el mínimo de 30 países con una
vintage razonable. Además, la OMS advierte que las personas que no superan las
barreras de acceso pueden registrar gasto cero, subestimando la dificultad
financiera. Antes de reabrirla se requiere una ventana temporal que conserve al
menos 30 países y una decisión explícita sobre la transformación de la brecha y
ese sesgo de acceso.

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

La fuente legible por máquina de los 12 indicadores del piloto es
[`config/pilot_sources.toml`](../config/pilot_sources.toml). La candidata no
materializada SAL-EQ-02 queda registrada en la [decisión v0.7](decisions/0011-v07-health-equity-screen.md).
