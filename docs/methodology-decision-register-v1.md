# Registro de decisiones metodológicas IEE v1

**Estado:** abierto a revisión; ninguna decisión de este registro está congelada.

Este registro separa preguntas metodológicas de cambios de código o de fuentes.
Una decisión solo cambia de estado cuando se publica su fundamento, se actualizan
los contratos afectados y pasan las pruebas correspondientes.

| ID | Decisión | Estado actual | Evidencia mínima para cerrar |
| --- | --- | --- | --- |
| M-01 | Ventana temporal y rezagos entre resultado y recurso | Abierta | Regla por dimensión, justificación causal y prueba de sensibilidad predefinida |
| M-02 | Cohorte común, mínimo y exclusiones | Abierta | Universo fijado, regla previa a resultados y demostración de cobertura comparable |
| M-03 | Normalización y tratamiento de valores extremos | Abierta | Especificación reproducible y comparación de escenarios sin escoger por resultado |
| M-04 | Función de acceso, equidad y contexto | Abierta | Regla explícita: requisito, ajuste o reporte paralelo; nunca suma automática |
| M-05 | Pesos o alternativa a pesos fijos | Abierta | Fundamentación, sensibilidad y regla para no compensar déficits graves |
| M-06 | Admisión de insumos condicionales | Abierta | Definición, unidad, ventana, cobertura y equivalencia demostrada frente al contrato |

## Estados permitidos

- **Abierta:** requiere aporte o análisis adicional.
- **Requiere más evidencia:** una propuesta fue analizada pero no cumple todavía
  el umbral indicado.
- **Aceptada:** cuenta con ADR, contrato actualizado, pruebas y documentación.
- **Rechazada:** se conserva la justificación y no altera el método.

## Ruta de revisión

Los aportes se reciben en la [consulta metodológica pública](https://github.com/rickHard29/indice-eficiencia-del-estado/issues/1).
La propuesta debe indicar el ID de esta tabla, el fundamento verificable y el
impacto esperado. Una conversación no habilita puntuaciones ni rankings.

El estado de `M-01` a `M-06` bloquea la congelación de la metodología v1. La
cohorte común y las fuentes se siguen auditando en paralelo, pero no se adopta una
regla después de mirar posiciones agregadas.
