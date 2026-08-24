# ADR 0004: armonizar insumos con proxies PPA constantes

- **Estado:** aceptada como proxy condicional para v0.2
- **Fecha:** 2026-08-24

## Contexto

Los insumos del piloto estaban expresados en PPA corriente o porcentaje del PIB y
no podían alimentar una frontera comparable en el tiempo. Las cuatro dimensiones
necesitan una unidad común de volumen por habitante.

## Decisión

La v0.2 deriva insumos en dólares internacionales constantes de 2021 por habitante:

```text
insumo constante pc = participación del gasto en el PIB / 100
                      × PIB pc PPA constante de 2021
```

Salud usa el porcentaje GHED de gasto público sanitario; educación usa gasto
público educativo total; seguridad usa COFOG GF03; administración calcula primero
la participación de D1 + P2 en S13/GF01 respecto al PIB nominal.

Los cuatro resultados se mantienen `conditional`. La conversión usa el deflactor
general del PIB, no un índice de precios sectorial. Por ello automatizar y auditar
la serie no equivale todavía a aprobarla para una frontera oficial.

Educación se expresa por habitante. No se divide gasto educativo total por población
en edad primaria porque el numerador incluye todos los niveles. Una serie directa
por alumno equivalente a tiempo completo se reservará para sensibilidad.

## Consecuencias

La canalización puede producir un panel común de 34 países para las cuatro proxies;
CAN, MEX, NZL y TUR quedan fuera de las funciones COFOG disponibles. Salud y
educación conservan cobertura para los 38 países del marco.

Los vintages desiguales se registran y nunca se completan con cero. Para levantar el
estado condicional se requiere contrastar estas proxies con volúmenes sectoriales
directos, fijar rezagos y comprobar sensibilidad al deflactor.
