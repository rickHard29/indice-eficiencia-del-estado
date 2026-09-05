# Cribado Educación v2: ventanas UIS de gasto educativo

**Estado:** rechazada como ampliación común; no modifica la cohorte  
**Fecha:** 2026-09-05

## Pregunta

¿Una ventana de dos años distinta para `EDU-IN-02` permite incluir a Australia y
Grecia sin perder comparabilidad temporal ni países completos actuales?

## Extracción reproducible

Se consultó el indicador público UIS `XGDP.FSGOV` —gasto gubernamental en
educación como porcentaje del PIB— para los 38 países OCDE y los años 2018 a
2021. La respuesta registra como fuente las entregas nacionales a la recolección
conjunta UNESCO-OCDE-Eurostat (UOE). El archivo descargado tiene SHA-256
`73827a1a332e0f02882acd40dab889de728f21701541addd3f6745141df82edd`.

Consulta exacta:

`https://api.uis.unesco.org/api/public/data/indicators?indicator=XGDP.FSGOV&start=2018&end=2021`

## Cobertura observada

| Ventana | Países con ambos años | Ausencias en OCDE-38 | Decisión |
| --- | ---: | --- | --- |
| 2018–2019 | 36 | Australia, México | No recupera Australia; México sigue incompleto en otras dimensiones. |
| 2019–2020 (vigente) | 35 | Australia, Grecia, México | Mantiene la ventana pre/contemporánea al resultado HCI 2020, pero no amplía la cohorte. |
| 2020–2021 | 36 | Colombia, Grecia | Recupera Australia, pero pierde Colombia y usa 2021, posterior al resultado HCI 2020. |

Australia publica 2020 y 2021; Grecia, 2018 y 2019. No comparten una ventana
consecutiva de dos años en este corte. Colombia tiene 2018–2020, no 2021.

## Decisión

No se cambia `EDU-IN-02` de 2019–2020 a otra ventana. Las alternativas no
incorporan simultáneamente Australia y Grecia, y la ventana 2020–2021 rompe la
regla temporal que evita usar un recurso posterior al resultado de 2020.

La serie UIS conserva su papel de proxy condicional: no habilita eficiencia,
puntajes ni ranking. Cualquier Educación v2 deberá usar una fuente común con
ventana anterior o contemporánea al resultado, cobertura suficiente y el mismo
calendario estadístico para todos los países incluidos.

## Referencias

- [Documentación de la API UIS](https://api.uis.unesco.org/api/public/documentation)
- [Definición UIS del gasto gubernamental en educación como porcentaje del PIB](https://uis.unesco.org/en/glossary-term/government-expenditure-education-gdp)
