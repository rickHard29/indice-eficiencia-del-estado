# Cribado Salud v2: serie Eurostat de mortalidad evitable

**Estado:** rechazada como reemplazo común; no modifica la cohorte  
**Fecha:** 2026-09-05

## Pregunta

¿La serie Eurostat `sdg_03_42` puede sustituir `SAL-RES-01` para toda la
cohorte OCDE-38 y completar Alemania, Noruega y Portugal sin excepciones por
país?

## Extracción reproducible

Se consultó la API oficial de Eurostat para 2019, 2020 y 2021:

`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_03_42?lang=en&time=2019&time=2020&time=2021`

Se usó `mortalit=TOTAL`, `sex=T`, `icd10=TOTAL` y `unit=RT`: tasa anual
estandarizada de mortalidad evitable total por 100.000 personas menores de 75
años. El archivo descargado tiene SHA-256
`15bd88e82b65e242469ba275a1f49527b7b8d7be1d1fcf81342802577afbcd4d`.

## Resultado de cobertura y equivalencia

- La serie entrega los tres años para **26** miembros de la OCDE: AUT, BEL,
  CHE, CZE, DEU, DNK, ESP, EST, FIN, FRA, GRC, HUN, IRL, ISL, ITA, LTU, LUX,
  LVA, NLD, NOR, POL, PRT, SVK, SVN, SWE y TUR.
- Solo **23** de ellos tienen al mismo tiempo la ventana completa en
  `SAL-RES-01` de la OCDE.
- En esos 23 países, el promedio 2019–2021 de Eurostat menos el de la OCDE
  varía de **26,78 a 96,27** muertes por 100.000; su promedio es **52,37**.

Por ejemplo, Austria registra 225,13; 235,44; 244,51 en Eurostat frente a 183;
191; 198 en la OCDE. La diferencia no permite tratar ambos resultados como la
misma escala intercambiable sin un puente metodológico validado.

## Decisión

La fuente no se adopta como `SAL-RES-02` ni como complemento para Alemania,
Noruega o Portugal:

1. no cubre de forma común los 38 países OCDE; y
2. no coincide numéricamente con la serie vigente en el solapamiento.

Puede conservarse como evidencia de sensibilidad europea, siempre fuera de la
cohorte IEE, puntajes y rankings. La siguiente búsqueda de Salud v2 debe partir
de una fuente internacional común, o de una reconstrucción trazable que cubra
los 38 países bajo una única lista de causas y población estándar.

## Referencias

- [API de Eurostat](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started/api)
- [Metadatos de mortalidad prevenible y tratable](https://ec.europa.eu/eurostat/cache/metadata/en/sdg_03_42_esmsip2.htm)
- [Lista conjunta OCDE-Eurostat](https://www.oecd.org/content/dam/oecd/en/data/datasets/oecd-health-statistics/avoidable-mortality-2019-joint-oecd-eurostat-list-preventable-treatable-causes-of-death.pdf)
