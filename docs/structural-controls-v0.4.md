# Controles estructurales v0.4

La v0.4 descarga un panel de contexto transversal. Está diseñado para análisis de
sensibilidad de la frontera experimental, no para producir una puntuación ni abrir
elegibilidad oficial.

| ID | Control | Fuente primaria | Transformación prevista | Cobertura congelada |
|---|---|---|---|---:|
| `CTX-AGE-01` | Dependencia etaria | UN WPP vía WDI | lineal | 38/38, 2010–2023 |
| `CTX-DENS-01` | Densidad poblacional | FAO/WDI | `log1p` | 38/38, 2010–2023 |

La [dependencia etaria](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SP.POP.DPND)
es la razón entre personas menores de 15 o mayores de 64 años y la población de
15–64 años. Es un indicador de composición poblacional, no de dependencia económica
observada. La [densidad poblacional](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/EN.POP.DNST)
divide la población de mitad de año por el área terrestre; es una medida nacional
gruesa de concentración espacial, no de accesibilidad local.

## Ejecución

```bash
iee-download \
  --manifest config/downloads_context_v0.4.toml \
  --raw-dir data/raw/official-v0.4 \
  --processed data/processed/v04_context_observations.csv \
  --provenance data/interim/v04_context_provenance.json
```

El recibo y el CSV conservan los hashes, los años más recientes, las observaciones
por país y la versión de los dos contratos. Antes de integrarlos a cualquier
frontera, el modelo debe declarar expresamente el control, transformación, ventana,
dimensión y análisis de sensibilidad.
