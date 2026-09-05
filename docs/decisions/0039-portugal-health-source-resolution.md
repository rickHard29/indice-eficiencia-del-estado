# ADR 0039: Portugal no se incorpora con la serie europea de mortalidad evitable

- **Estado:** resuelto; candidata rechazada
- **Fecha:** 2026-09-04

## Contexto

Portugal queda fuera del panel sanitario porque `SAL-RES-01` no contiene una
ventana completa 2019–2021. La base de Eurostat `sdg_03_42` sí publica una serie
nacional anual de mortalidad evitable estandarizada: 214,65 (2019), 224,82
(2020) y 230,42 (2021) por cada 100.000 personas menores de 75 años.

Eurostat define esa medida como el total de mortalidad prevenible y tratable. Su
[metadato](https://ec.europa.eu/eurostat/cache/metadata/en/sdg_03_42_esmsip2.htm)
confirma la cobertura, unidad y periodicidad; la
[documentación de causas de muerte](https://ec.europa.eu/eurostat/cache/metadata/en/hlth_cdeath_sims.htm)
confirma que se trata de tasas estandarizadas basadas en certificados de defunción.

## Decisión

No materializar Portugal desde `sdg_03_42`. La misma serie europea fue evaluada
para Alemania en la resolución v0.7: arroja 231,41 (2019), 238,07 (2020) y
252,54 (2021), mientras que el contrato `SAL-RES-01` de la OCDE contiene 188 y
195 para los años comparables. Sin un puente que demuestre igualdad entre ambas
listas de causas y estandarizaciones, sustituir la serie faltante cambiaría el
constructo de forma silenciosa.

## Consecuencias

- Portugal conserva el faltante de resultado sanitario y el panel permanece en
  34 países completos.
- No cambia la cohorte común de 24/30, ningún puntaje ni ninguna puerta de
  publicación.
- Esta decisión extiende al nuevo país el mismo control de equivalencia aplicado
  a Alemania; no convierte la ausencia de datos en un cero ni en una imputación.
