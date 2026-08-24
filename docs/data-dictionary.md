# Diccionario de datos

## Identificadores mínimos

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `entity` | texto | Código estable del país o territorio. |
| `period` | entero | Año de referencia. |
| `indicator_id` | texto | Identificador versionado del indicador. |
| `value` | número | Valor observado antes de normalizar. |
| `direction` | texto | `higher`, `lower` o `input`; un insumo no se puntúa directamente. |
| `source_id` | texto | Identificador de la fuente y extracción. |

## Campos de trazabilidad de la canalización

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `unit` | texto | Unidad exacta registrada en el catálogo metodológico. |
| `series_code` | texto | Código o fórmula oficial de la serie. |
| `source_status` | texto | `validated`, `conditional` o `reserve`. |
| `score_eligible` | booleano | Indica si la observación puede entrar al cálculo actual. |
| `observation_status` | texto | Estado observado, incluido `provisional` cuando corresponda. |
| `observation_kind` | texto | `reported` para dato directo, `derived` para una transformación o `manual_control` para una transcripción oficial versionada. |
| `resource_id` | texto | Clave del recurso en `config/downloads.toml` o `config/manual_controls.toml`. |

Las unidades, transformaciones, reglas de imputación y licencias se registran en el
inventario maestro y en el recibo JSON de cada ejecución.

## Campos del diagnóstico experimental

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `diagnostic_score` | número 0–100 | Perfil normalizado o agregado de ingeniería; no mide eficiencia. |
| `lower_bound`, `upper_bound` | número | Límites congelados usados en la normalización diagnóstica. |
| `bound_status` | texto | `natural_scale`, `technical_scale` o `provisional`. |
| `bound_reference` | texto | Justificación o referencia versionada del par de límites. |
| `official_iee_score` | nulo | Gate explícito: no existe puntaje oficial en esta fase. |
| `coverage` | proporción | Peso de roles o dimensiones que tienen diagnóstico disponible. |
| `available_roles` | lista | Roles usados solo en el diagnóstico experimental. |
| `missing_roles` | lista | Roles obligatorios ausentes. |
| `input_compatible` | booleano | Si existe un insumo habilitado para ajustar recursos. |
| `frontier_eligible` | booleano | Si el universo alcanza el mínimo para estimar una frontera. |
| `publication_eligible` | booleano | Gate de publicación; permanece falso en v0.1. |
| `flags` | lista | Cautelas y bloqueos legibles por máquina. |

Los archivos y la semántica completa se describen en
[`docs/experimental-scoring-v0.1.md`](experimental-scoring-v0.1.md).
