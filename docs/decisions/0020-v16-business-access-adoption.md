# ADR 0020: adopción condicional de acceso administrativo empresarial v1.6

- **Estado:** aceptada como subindicador condicional; no apta para puntaje
- **Fecha:** 2026-09-01

## Decisión

Se adopta `ADM-ACC-02`, carga regulatoria de trámites empresariales, desde el
indicador abierto `IC.GOV.DURS.ZS` de *Enterprise Surveys* del Banco Mundial.
La serie queda en sentido inverso: menos porcentaje del tiempo semanal de alta
gerencia dedicado a impuestos, aduanas, regulación laboral, licencias, registros,
funcionarios y formularios es mejor.

La adquisición v1.6 congela el marco OECD-38, la consulta API, la ventana
2020--2025, la condición de una observación por país y los puntos de control de
Colombia (2023, 26,1692 %) y Estados Unidos (2024, 5,7544 %). Su elegibilidad de
puntaje permanece falsa y el estado de fuente es `conditional`.

## Consecuencias

El IEE cuenta ahora con un subindicador reproducible de fricción administrativa
para empresas. No lo interpreta como experiencia de hogares ni como medida de
finalización de todos los trámites, no lo combina aún con identidad oficial y no
abre una frontera, ranking o IEE oficial. Cualquier panel futuro debe declarar
la ventana asíncrona y que Luxemburgo conserva una observación de 2020.

La fuente es pública y gratuita; no se incorporan licencias ni datos de pago.

Véase el [cribado v1.5](0019-v15-business-regulatory-burden-screen.md), el
[metadato oficial](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/IC.GOV.DURS.ZS) y la [consulta API](https://api.worldbank.org/v2/country/COL;USA/indicator/IC.GOV.DURS.ZS?format=json).
