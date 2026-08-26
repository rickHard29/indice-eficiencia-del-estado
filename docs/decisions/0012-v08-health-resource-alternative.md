# ADR 0012: alternativa directa de recursos sanitarios v0.8

- **Estado:** aceptada como sensibilidad experimental condicional
- **Fecha:** 2026-08-25

## Contexto

`SAL-IN-02` aproxima gasto público sanitario real multiplicando el porcentaje del
PIB de GHED por PIB per cápita PPA constante. Su cobertura OCDE es completa, pero
usa el deflactor general del PIB, no uno específico de salud.

La OCDE publica una alternativa directa bajo SHA 2011: gasto sanitario en
esquemas gubernamentales u obligatorios (`HF1`), PPA por persona a precios
constantes de 2020. La consulta tiene cobertura completa 2019–2023 para los 38
miembros OCDE, incluidos Colombia y Estados Unidos.

## Decisión

Se materializa `SAL-IN-03` como insumo alternativo para análisis de sensibilidad.
Permanece `conditional` y no se puntúa por sí mismo. La v0.8 no reemplaza ni
recalifica `SAL-IN-02`, y mantiene bloqueados el IEE oficial, los rankings y toda
publicación de eficiencia.

## Razones

La nueva serie resuelve el defecto principal de precios de la proxy: la OCDE la
difunde en PPA y precios constantes, sin una multiplicación por PIB. Sin embargo,
`HF1` incluye tanto esquemas gubernamentales como seguros contributivos obligatorios.
Eso mide recursos canalizados por arreglos públicos u obligatorios, no exactamente
el gasto del gobierno general de GHED. También cubre gasto sanitario corriente y
excluye formación de capital.

## Consecuencias

Una futura frontera sanitaria debe publicar ambas especificaciones por separado y
comparar estabilidad de muestra, orden y sensibilidad; no puede elegir la más
favorable después de ver resultados. Para aprobar una como insumo oficial aún se
requiere decidir si el concepto de recursos del Estado incluye el seguro obligatorio
y fijar el tratamiento de inversión de capital.

La primera ejecución muestra que reemplazar la proxy por HF1 mueve los diagnósticos
experimentales de Colombia y Estados Unidos. Esta sensibilidad confirma que ninguna
de las dos especificaciones puede promoverse de forma oportunista a resultado
oficial.

## Fuentes

- [OCDE: gasto sanitario, definición y financiación](https://www.oecd.org/en/data/indicators/health-spending.html)
- [OCDE: clasificación SHA de HF.1](https://www.oecd.org/en/publications/best-practice-in-institutionalising-health-accounts_cf997130-en/full-report/key-classifications-of-the-system-of-health-accounts-2011_a2857acf.html)
- [OCDE Data Explorer: Health expenditure and financing](https://data-explorer.oecd.org/vis?bp=true&df%5Bag%5D=OECD.ELS.HD&df%5Bds%5D=dsDisseminateFinalDMZ&df%5Bid%5D=DSD_SHA%40DF_SHA&df%5Bvs%5D=1.1&dq=.A.EXP_HEALTH.USD_PPP_PS._T.._T.._T...&fc=Topic&fs%5B0%5D=Topic%2C1%7CHealth%23HEA%23%7CHealth+expenditure+and+financing%23HEA_EXP%23&pd=2022%2C&pg=0&snb=4&to%5BTIME_PERIOD%5D=false&vw=tb)
