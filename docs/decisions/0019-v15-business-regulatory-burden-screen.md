# ADR 0019: cribado de carga regulatoria empresarial v1.5

- **Estado:** candidata condicional de acceso administrativo; no adoptada en el índice
- **Fecha:** 2026-09-01

## Contexto

La búsqueda se limita a datos abiertos, gratuitos y reutilizables que preserven
la comparación Colombia--Estados Unidos. El rol `ADM-ACC-01` sigue sin una
medida internacional de experiencia ciudadana, tiempo y finalización de trámites.

## Decisión

Se evaluó el indicador del Banco Mundial `IC.GOV.DURS.ZS`, procedente de las
*Enterprise Surveys*: porcentaje promedio del tiempo semanal de la alta gerencia
dedicado a requisitos estatales. La definición incluye impuestos, aduanas,
regulación laboral, licencias, registros, interacción con funcionarios y
formularios. Por tanto registra una carga de cumplimiento reportada por quienes
usan trámites, no una evaluación normativa ni un índice de capacidad digital.

La serie tiene cobertura para los 38 miembros OCDE usando la observación más
reciente disponible entre 2020 y 2025; 37 observaciones corresponden a
2023--2025 y Luxemburgo a 2020. Colombia registra 26,1692 % en 2023 y Estados
Unidos 5,7544 % en 2024. El valor menor representa menor carga administrativa.
Los datos y sus agregados se publican bajo CC BY 4.0.

Se conserva como `ADM-ACC-02`, candidata condicional de acceso administrativo
en el ámbito empresarial. No se sustituye `ADM-ACC-01`, ni se incorpora al
catálogo ejecutable o a un puntaje, hasta resolver la diferencia de población.

## Consecuencias

La fuente satisface las condiciones de costo, trazabilidad, cobertura bilateral
y tamaño de referencia. También se acerca más al objetivo original de tiempo de
trámite que OSI, EPI, identidad o los indicadores de satisfacción.

Sin embargo, el encuestado es la alta gerencia de establecimientos privados;
no representa a hogares, usuarios de beneficios ni personas que realizan
trámites civiles. Adoptarla requeriría definir expresamente que la eficiencia
administrativa incluye la carga regulatoria de empresas y mantener el rótulo de
población empresarial. No aporta por sí sola un indicador de equidad ni resuelve
la finalización de trámites.

Fuentes: [metadato del indicador](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/IC.GOV.DURS.ZS), [API para Colombia y Estados Unidos](https://api.worldbank.org/v2/country/COL;USA/indicator/IC.GOV.DURS.ZS?format=json) y [datos de Enterprise Surveys](https://www.enterprisesurveys.org/en/data).
