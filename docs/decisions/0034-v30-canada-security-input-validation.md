# ADR 0034: validación de candidata canadiense para insumo de seguridad

- **Estado:** candidata aceptada para integración aislada
- **Fecha:** 2026-09-03

## Contexto

La sensibilidad SEG-EQ-02 alcanza 29 países completos y Canadá es el único
faltante que puede recuperar la cobertura mínima de 30 sin sustituir la
definición de equidad territorial. La tabla 10-10-0005-01 de Statistics Canada
fue identificada en v2.7, pero aún faltaba verificar sus observaciones exactas.

## Decisión

Se valida CCOFOG 703 del gobierno general consolidado de Canadá para 2019–2021
como candidata condicionada. Su integración deberá ser un complemento nuevo,
con conversión explícita mediante PIB nominal en CAD y PIB por habitante PPA
constante; no se editará SEG-IN-02 ni se sustituirá la fuente de la OCDE.

## Consecuencias

La próxima implementación puede probar una muestra de 30 países para la
sensibilidad mixta, manteniendo bloqueados la frontera, el ranking y el IEE
oficial. Si falla la reproducción o la comparabilidad, la cobertura permanece en
29 y el contrato histórico no cambia.
