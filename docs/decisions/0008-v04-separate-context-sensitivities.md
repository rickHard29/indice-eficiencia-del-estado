# ADR 0008: sensibilidades de contexto por separado

- **Estado:** aceptada para experimentación, no para publicación
- **Fecha:** 2026-08-25

## Contexto

La v0.4 ya materializó dos controles estructurales completos para OCDE-38. Las
muestras experimentales de salud y educación tienen 34 pares; añadir ambos controles
simultáneamente elevaría el número de parámetros sin una muestra que justifique esa
especificación. Seguridad y administración continúan bloqueadas antes de llegar a
esta decisión.

## Decisión

Para cada dimensión experimentalmente elegible, se comparan tres fronteras p90:

1. la frontera base: resultado frente a `log1p(insumo)`;
2. una sensibilidad que añade solo dependencia etaria;
3. una sensibilidad que añade solo densidad transformada con `log1p`.

La pendiente del recurso continúa restringida a ser no negativa. El coeficiente del
control queda libre y se interpreta exclusivamente como ajuste estadístico local,
no como efecto causal. La salida publica el cambio frente a la eficiencia base y no
estima intervalos nuevos para estas sensibilidades exploratorias.

No se combinan los dos controles, no se selecciona el escenario que favorezca a un
país y no se calcula `official_iee_score`. Cualquier salida conserva los flags de
experimentación, incertidumbre no estimada, ranking bloqueado y sensibilidad de
contexto.

## Consecuencias

El proyecto puede cuantificar si la señal base es sensible a una condición
demográfica o espacial, sin presentar el modelo condicionado como definitivo. La
adopción de un control principal requerirá una decisión posterior por dimensión,
validación externa y un protocolo de incertidumbre.
