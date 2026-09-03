# ADR 0035: materialización aislada del complemento canadiense

- **Estado:** implementado; pendiente de integración trazable
- **Fecha:** 2026-09-03

## Contexto

La validación v3.0 confirmó una fuente canadiense apta para prueba, pero el
panel vigente solo reconoce SEG-IN-02 y no debe mezclar procedencias sin
declararlo.

## Decisión

Se materializa SEG-IN-03 en un manifiesto independiente y se conserva separado
de SEG-IN-02. La próxima capa de integración deberá declarar la procedencia por
país y mantener el resultado como sensibilidad experimental.

## Consecuencias

Canadá ya cuenta con una observación reproducible para los tres años requeridos.
La muestra de seguridad sigue publicada como 29/30 hasta que la combinación sea
auditada y vuelva a calcularse la puerta de cobertura.
