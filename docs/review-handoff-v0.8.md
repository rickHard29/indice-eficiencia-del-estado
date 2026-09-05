# Entrega para revisión abierta v0.8

**Estado:** preparado para recibir revisión; no es aprobación metodológica.

Este paquete permite que una revisión externa examine decisiones del IEE sin
necesitar herramientas pagas ni acceso a datos privados. Las plantillas del
repositorio separan dos flujos: revisión metodológica y propuesta de evidencia.

## Alcance de la revisión

| Flujo | Lo que debe aportar | Lo que no puede hacer |
| --- | --- | --- |
| Metodología | Regla concreta, fundamento verificable e impacto en comparabilidad | Congelar el método por sí sola o pedir un ranking |
| Evidencia | Fuente pública, definición, unidad, años, cobertura y puente de equivalencia | Imputar faltantes o sustituir una serie sin validación |

## Preguntas prioritarias

1. ¿Qué regla temporal hace comparables resultado y recurso en cada dimensión?
2. ¿Cómo deben funcionar acceso, equidad y contexto antes de cualquier agregado?
3. ¿Qué requisito adicional permite aceptar un recurso actualmente condicional?
4. ¿Qué umbral y sensibilidad son defendibles para una cohorte común?

## Proceso de decisión

Cada aporte se registra como uno de estos estados: `aceptado`, `rechazado` o
`requiere más evidencia`. Una aceptación debe actualizar el contrato, las pruebas,
la documentación y el control de cohorte; no basta con una conversación. Hasta
entonces siguen nulos el puntaje oficial y el ranking.

## Uso

Al habilitar la revisión en GitHub, las personas revisoras pueden abrir una de las
dos plantillas en `.github/ISSUE_TEMPLATE/`. La prioridad actual es recuperar
evidencia comparable para los seis países fuera de la cohorte común, no discutir
posiciones de países.
