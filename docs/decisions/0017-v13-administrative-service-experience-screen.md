# ADR 0017: cribado de experiencia administrativa v1.3

- **Estado:** rechazada para el piloto bilateral por cobertura
- **Fecha:** 2026-09-01

## Contexto

V1.2 confirmó que participación y capacidad digital no sustituyen el acceso
efectivo a los trámites. Se evaluaron las dos fuentes internacionales más
directas de experiencia de usuarios de servicios administrativos.

## Decisión

El indicador ODS `16.6.2`, “proporción de la población satisfecha con su última
experiencia de servicios públicos”, no se materializa como `ADM-ACC-01`. Es el
constructo adecuado: el metadato contempla acceso, oportunidad, información y
calidad, y permite desagregaciones. Sin embargo, la extracción oficial actual
del subindicador de **servicios gubernamentales** contiene 37 países y no tiene
observación para Colombia ni Estados Unidos.

La *Survey on Drivers of Trust in Public Institutions* de la OCDE mide
satisfacción de usuarios recientes de servicios administrativos y es también un
constructo adecuado. La ronda 2023 cubre 30 países y la 2025, 33; Estados Unidos
no participa en ninguna de ellas. Por tanto, ambas rutas fallan el requisito
bilateral del piloto aun antes de aplicar el mínimo de frontera.

## Consecuencias

`ADM-ACC-01` continúa en estado `design_required`. No se infieren datos desde
la satisfacción sanitaria disponible ni se combina la encuesta OCDE con una
medición nacional estadounidense: eso rompería definición, población y modo de
recolección.

Para continuar se necesita una decisión explícita entre: conservar Colombia y
Estados Unidos como requisito y buscar una fuente global adicional —posiblemente
con licencia—, o permitir un análisis administrativo separado para el subconjunto
de países que sí reporta experiencia de servicio. Ninguna alternativa habilita
por sí sola un IEE oficial mientras falte el bloque de equidad y el insumo siga
siendo condicional.

Fuentes: [metadato ODS 16.6.2](https://unstats.un.org/sdgs/metadata/files/Metadata-16-06-02.pdf), [API global ODS 16.6.2](https://unstats.un.org/SDGAPI/v1/sdg/Indicator/Data?indicator=16.6.2&pageSize=1000) y [encuesta OCDE 2025](https://www.oecd.org/en/publications/2026/06/results-of-the-2025-oecd-survey-on-drivers-of-trust-in-public-institutions_96323a65/full-report/drivers-of-trust-over-time-lessons-from-the-third-wave-of-the-oecd-trust-survey_440749ab.html).
