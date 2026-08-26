# ADR 0013: cribado de frontera educativa v0.9

- **Estado:** rechazada como evidencia de eficiencia; conservar solo como diagnóstico de proxy
- **Fecha:** 2026-08-25

## Contexto

El puente v0.6 reúne aprendizaje armonizado de 2020 y el promedio 2019–2020 de
`EDU-IN-02`, una aproximación de gasto público educativo total por habitante en
PPA constante. Tiene 35 pares OCDE y supera el mínimo numérico de 30, pero su
denominador poblacional no equivale a estudiantes FTE y la fuente es condicional.

## Decisión

Se estimó una sola frontera cuantílica experimental, previamente especificada:
cuantil 0,90, recurso `log1p`, pendiente no decreciente y escala HCI técnica de
300 a 625. El ajuste devuelve pendiente cero. Por ello, los diagnósticos no se
interpretan como eficiencia de recursos y no se promueve `EDU-IN-02` a insumo
validado.

No se relaja la monotonicidad, no se elige un cuantil distinto después de ver el
resultado y no se usan los resultados para ranking. Acceso y equidad PISA 2022
siguen fuera hasta fijar un tratamiento temporal explícito.

## Consecuencias

La v0.9 confirma que cobertura suficiente no sustituye una definición de recursos
adecuada. El proyecto conserva el puente para auditoría, pero buscará una serie por
estudiante que incluya Colombia o una justificación metodológica independiente para
el denominador por habitante. El IEE oficial continúa nulo.
