# Núcleo común de resultados v1.0

**Estado:** cobertura de resultados; no es un índice de eficiencia ni un ranking  
**Fecha:** 2026-09-05

## Propósito

El proyecto conserva una cohorte completa de 24 países, que exige resultado,
recurso y el rol de acceso o equidad correspondiente. En paralelo, este artefacto
identifica los países que sí tienen los **cuatro resultados comparables** ya
validados: educación, salud, administración pública y seguridad y justicia.

La intersección contiene **33 de los 38 países OCDE**: AUS, AUT, CAN, CHE, CHL,
COL, CRI, CZE, DNK, ESP, EST, FIN, FRA, GBR, GRC, HUN, IRL, ISL, ISR, ITA, JPN,
KOR, LTU, LUX, LVA, MEX, NLD, POL, SVK, SVN, SWE, TUR y USA.

## Qué permite y qué no permite

Este núcleo permite analizar cobertura y consistencia de los resultados en un
universo de más de 30 países. No incorpora los recursos, el acceso ni la equidad
territorial requeridos para hablar de eficiencia. En consecuencia:

- no calcula un puntaje IEE;
- no calcula una frontera;
- no publica un ranking; y
- no reemplaza la cohorte común completa de 24 países.

## Control reproducible

`iee-outcomes-core-cohort` lee los cuatro paneles existentes, exige que cada
resultado esté presente y conserva el hash de cada archivo. El recibo
`data/processed/outcomes_core_cohort_v1.json` solo se emite si coincide
exactamente con la membresía declarada de 33 países. Cualquier pérdida o adición
de cobertura obliga a revisar el corte antes de volver a publicarlo.
