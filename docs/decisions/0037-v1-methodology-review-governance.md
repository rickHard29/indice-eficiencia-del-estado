# ADR 0037: gobernanza de revisión metodológica v1

- **Estado:** adoptado como procedimiento de revisión
- **Fecha:** 2026-09-04

## Contexto

El repositorio del IEE ya es público y puede recibir comentarios sobre el método.
Sin un registro común, las recomendaciones podrían confundirse con aprobaciones o
perder su relación con el contrato técnico que deben modificar.

## Decisión

Se adopta el registro `M-01` a `M-06` como único punto de control de decisiones
metodológicas v1. Cada cambio propuesto debe vincularse a uno de esos IDs y
terminar en una ADR de aceptación o rechazo. La aceptación exige fundamento,
contrato actualizado, prueba automatizada y documentación; ninguna respuesta en
GitHub aprueba por sí sola una regla ni habilita un ranking.

## Consecuencias

La revisión abierta puede avanzar sin costo y de forma trazable. El método v1
sigue sin congelarse mientras alguna decisión permanezca abierta. Esta ADR regula
el proceso de revisión, no decide ventanas, pesos, normalización ni fuentes.
