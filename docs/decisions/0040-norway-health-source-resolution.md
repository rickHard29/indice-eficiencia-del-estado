# ADR 0040: Noruega no se incorpora con la serie europea de mortalidad evitable

- **Estado:** resuelto; candidata rechazada
- **Fecha:** 2026-09-04

## Contexto

Noruega no tiene una ventana completa de `SAL-RES-01` para 2019–2021. Eurostat
sí publica, en `sdg_03_42`, la mortalidad evitable total estandarizada de 172,27
(2019), 171,75 (2020) y 169,48 (2021) por cada 100.000 personas menores de 75
años.

## Decisión

No incorporar esos valores. Son la misma definición y serie de Eurostat evaluada
en los ADR [0039](0039-portugal-health-source-resolution.md) y en la resolución
v0.7 para Alemania. La comparación alemana demostró que, aunque la etiqueta sea
análoga, no existe un puente validado con la lista de causas y estandarización de
`SAL-RES-01` de la OCDE.

## Consecuencias

- Noruega sigue incompleta en salud; el panel queda en 34 países completos.
- No cambian la cohorte común de 24/30, los puntajes ni la elegibilidad de
  publicación.
- La fuente solo podrá usarse si una revisión metodológica aprueba y valida un
  contrato común para todos los países, no como excepción nacional.
