# ADR 0031: cribado de equidad territorial TL3 de seguridad v2.8

- **Estado:** sensibilidad candidata; adopción bloqueada
- **Fecha:** 2026-09-02

## Contexto

`SEG-EQ-01` usa brechas de homicidios TL2 y deja ocho países fuera del contrato.
La fuente regional OCDE también contiene niveles TL3 para parte de esos países.

## Decisión

Se prueban los pares TL3 de 2021 sin alterar el indicador vigente. Estonia,
Lituania y Eslovenia pasan los controles de tres o más regiones y parejas de
homicidio/población; Letonia, Islandia, Israel, Luxemburgo y Nueva Zelanda no.
Los tres valores quedan como candidatos de sensibilidad, no como observaciones
de `SEG-EQ-01`.

## Consecuencias

Mezclar TL2 y TL3 cambiaría el nivel territorial de medición y puede afectar la
magnitud de la brecha. Cualquier adopción requiere una nueva definición, máscara
por nivel y prueba de estabilidad sobre países con ambos niveles. La muestra
integrada mantiene 26 países y todos los bloqueos del IEE siguen vigentes.
