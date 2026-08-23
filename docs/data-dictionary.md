# Diccionario de datos

## Identificadores mínimos

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `entity` | texto | Código estable del país o territorio. |
| `period` | entero | Año de referencia. |
| `indicator_id` | texto | Identificador versionado del indicador. |
| `value` | número | Valor observado antes de normalizar. |
| `direction` | texto | `higher` si un valor mayor es mejor; `lower` en caso contrario. |
| `source_id` | texto | Identificador de la fuente y extracción. |

Las unidades, transformaciones, reglas de imputación y licencias se registrarán en el inventario maestro de indicadores.
