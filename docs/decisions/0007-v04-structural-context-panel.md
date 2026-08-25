# ADR 0007: panel de contexto estructural v0.4

- **Estado:** aceptada para experimentación, no para publicación
- **Fecha:** 2026-08-25

## Contexto

La v0.3 estima una frontera experimental de resultado frente a recursos, pero no
incluye todavía las condiciones estructurales mínimas previstas por la metodología.
Con 34 pares en las dimensiones estimables no es defendible introducir muchos
regresores de forma conjunta ni seleccionar controles según el resultado obtenido.

## Decisión

La v0.4 materializa, separada de resultados e insumos, una canasta mínima de dos
controles transversales oficiales para los 38 miembros de la OCDE entre 2010 y 2023:

1. `CTX-AGE-01`: razón de dependencia etaria (`SP.POP.DPND`), de UN WPP vía WDI;
2. `CTX-DENS-01`: densidad poblacional (`EN.POP.DNST`), de FAO/WDI.

Ambos se conservan con `direction = input` y `score_eligible = false`: no son
resultados, no son recursos y nunca puntúan. La dependencia etaria se mantiene en
escala lineal; la densidad usa `log1p` si llega a modelarse. La población rural no
entra a esta canasta porque su definición es nacional y no es suficientemente
armonizada para funcionar como control principal.

La siguiente etapa deberá fijar por dimensión, antes de ejecutar modelos, si se usa
un control, ambos por separado como sensibilidad o ninguno. No se permiten modelos
con los dos controles añadidos automáticamente ni se levanta ningún gate oficial.

## Consecuencias

El proyecto gana una base reproducible para probar sensibilidad al contexto sin
convertir correlaciones en causalidad. Salud, educación, seguridad y administración
conservan los bloqueos ya publicados; el IEE oficial, los rankings y la publicación
siguen nulos o falsos.
