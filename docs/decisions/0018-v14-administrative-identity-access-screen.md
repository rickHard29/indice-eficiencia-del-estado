# ADR 0018: cribado de identidad y uso digital administrativo v1.4

- **Estado:** candidata de prerrequisito de acceso; no adoptada en el índice
- **Fecha:** 2026-09-01

## Contexto

El proyecto conserva la comparación Colombia--Estados Unidos y solo puede usar
fuentes abiertas, gratuitas y reutilizables. Tras descartar las encuestas de
satisfacción por cobertura bilateral, se evaluó el módulo ID4D--Global Findex
2025 del Banco Mundial, que publica datos nacionales de 2024 y está disponible
bajo CC BY 4.0.

## Decisión

La pregunta `con30g` de Global Findex mide directamente si una persona accedió
a servicios gubernamentales o buscó información gubernamental en línea durante
los últimos tres meses. Es una medida de uso, pero su cobertura OCDE es solo de
cuatro países (Colombia, Costa Rica, México y Türkiye) y no tiene observación
para Estados Unidos. Queda rechazada como medida bilateral de uso.

El indicador `used_eid_s` registra el uso de una identidad digital en teléfono
o computador para confirmar identidad en línea. Es más específico aún, pero
solo cubre 28 de los 38 miembros OCDE; Estados Unidos tiene observación y
Colombia no. También queda rechazado por cobertura.

El indicador `ID.OWN.TOTL.ZS` mide la proporción de personas de 15 años o más
con identidad oficial. Tiene datos en 2024 para Colombia (98,3836 %), Estados
Unidos (89,7975 %) y 34 de los 38 miembros OCDE; faltan Australia, Estonia,
Luxemburgo y República Eslovaca. Además publica las mismas desagregaciones por
sexo, ingreso y zona rural/urbana para esos 34 países. Se conserva como
`ADM-ID-01`, candidata a **prerrequisito de acceso**, no como sustituto de
`ADM-ACC-01`.

## Consecuencias

La identidad oficial es una puerta de entrada a servicios, beneficios y
transacciones, pero no observa una solicitud administrativa, su tiempo ni su
finalización. Por ello no se cambia la definición vigente de `ADM-ACC-01` ni se
produce un puntaje. Si más adelante se adopta `ADM-ID-01`, requerirá una
enmienda metodológica explícita que lo describa como cobertura habilitante y un
control de saturación, no como desempeño del trámite.

El conjunto ID4D aporta una posible vía abierta para examinar equidad de acceso,
pero no completa por sí solo el bloque administrativo: persiste la ausencia de
una medida internacional armonizada de experiencia o finalización de trámites.

Fuentes: [catálogo ID4D del Banco Mundial](https://datacatalog.worldbank.org/search/dataset/0040787/identification-for-development-id4d-global-dataset), [datos ID4D](https://id4d.worldbank.org/global-dataset), [API de identidad oficial](https://api.worldbank.org/v2/country/COL;USA/indicator/ID.OWN.TOTL.ZS?format=json), [API de uso de identidad digital](https://api.worldbank.org/v2/country/COL;USA/indicator/used_eid_s?format=json) y [API de uso de servicios o información gubernamental en línea](https://api.worldbank.org/v2/country/COL;USA/indicator/con30g?format=json).
