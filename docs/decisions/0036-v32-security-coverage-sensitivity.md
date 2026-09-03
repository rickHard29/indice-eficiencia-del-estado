# ADR 0036: sensibilidad multifuente alcanza 30 países

- **Estado:** materializada como sensibilidad experimental
- **Fecha:** 2026-09-03

## Contexto

La seguridad tenía 29 países completos bajo SEG-EQ-02. Canadá contaba con un
complemento de insumo reproducible, pero debía combinarse sin ocultar su
procedencia distinta.

## Decisión

Se crea SEG-IN-04 como complemento explícito: 34 países de la OCDE y Canadá de
Statistics Canada. La integración v3.2 usa SEG-EQ-02 y alcanza 30 países
completos, manteniendo el resultado experimental y los contratos históricos
intactos.

## Consecuencias

Se elimina el bloqueo puramente numérico de la sensibilidad de seguridad. No se
elimina el bloqueo metodológico para estimar eficiencia o publicar rankings.
