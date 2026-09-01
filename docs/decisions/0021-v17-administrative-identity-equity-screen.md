# ADR 0021: cribado de equidad de identidad administrativa v1.7

- **Estado:** candidata de equidad; requiere enmienda metodológica
- **Fecha:** 2026-09-01

## Contexto

La administración ya cuenta con un resultado digital (`ADM-RES-01`), un
subindicador condicional de carga de trámites empresariales (`ADM-ACC-02`) y un
insumo condicional. Falta un rol de equidad. La fuente debe ser abierta,
comparable para Colombia y Estados Unidos y cubrir al menos 30 países del marco
OCDE-38.

## Decisión

Se evaluó ID4D--Global Findex 2025 del Banco Mundial. Sus indicadores
`ID.OWN.TOTL.FE.ZS` y `ID.OWN.TOTL.MA.ZS` informan el porcentaje de mujeres y de
hombres de 15 años o más con identidad oficial. Se propone como candidata
`ADM-EQ-02` la diferencia absoluta en puntos porcentuales entre ambos valores:

```text
brecha de identidad por sexo = |cobertura de hombres − cobertura de mujeres|
```

Menor brecha significa mayor paridad. En 2024 la brecha es 0,995574 p.p. en
Colombia (97,904212 % mujeres; 98,899786 % hombres) y 2,916416 p.p. en Estados
Unidos (88,340335 % mujeres; 91,256751 % hombres). La serie está completa para
34 de 38 miembros OCDE; faltan Australia, Estonia, Luxemburgo y República
Eslovaca. Supera el mínimo técnico de 30 observaciones.

## Consecuencias

La métrica observa una desigualdad concreta de un requisito para acceder a
servicios, beneficios y transacciones. Es gratuita, pública y tiene
desagregación simétrica para ambos grupos. No se adopta todavía porque sustituye
la idea inicial de disparidad territorial por una brecha de género y su población
es la de personas de 15 años o más, distinta de los establecimientos privados de
`ADM-ACC-02`.

La cobertura de identidad es alta en buena parte del marco, por lo que la brecha
puede saturarse; debe conservarse como un indicador de paridad, no de calidad
general de los trámites. No abre un puntaje ni una frontera.

Fuentes: [catálogo ID4D](https://datacatalog.worldbank.org/search/dataset/0040787/identification-for-development-id4d-global-dataset), [API mujeres](https://api.worldbank.org/v2/country/COL;USA/indicator/ID.OWN.TOTL.FE.ZS?format=json) y [API hombres](https://api.worldbank.org/v2/country/COL;USA/indicator/ID.OWN.TOTL.MA.ZS?format=json).
