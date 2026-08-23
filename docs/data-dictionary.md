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
