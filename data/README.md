# Política de datos

Este directorio solo versiona esquemas, manifiestos y muestras sintéticas.

- `raw/`, `interim/` y `processed/` están excluidos de Git.
- Los archivos reales permanecen en Google Drive con su control de acceso original.
- Cada extracción debe registrar fuente, fecha de corte, licencia, versión y suma SHA-256.
- Las muestras publicadas aquí no deben contener datos personales ni restringidos.

La canalización oficial escribe en:

- `raw/official/<sha256>.<formato>`: respuestas originales inmutables.
- `interim/pilot_provenance.json`: recibo completo de adquisición y transformación.
- `processed/pilot_observations.csv`: observaciones normalizadas.

La ampliación multinacional v0.2 escribe, por separado:

- `raw/official-v0.2/<sha256>.<formato>`: componentes oficiales inmutables;
- `interim/v02_input_provenance.json`: universo, máscaras, vintages y hashes;
- `processed/v02_input_proxies.csv`: cuatro proxies condicionales en PPA constante.

La primera entrega de resultados v0.3 escribe, por separado:

- `raw/official-v0.3/<sha256>.<formato>`: respuestas oficiales inmutables;
- `interim/v03_result_provenance.json`: recibo con el corte y vintages por país;
- `processed/v03_result_observations.csv`: resultados observados sin imputación.

El panel de frontera experimental v0.3 añade:

- `processed/v03_frontier_panel.csv`: pares resultado–insumo con ventanas completas;
- `processed/v03_frontier_gates.csv`: cobertura y bloqueo por dimensión;
- `interim/v03_frontier_provenance.json`: hashes de ambos snapshots y del panel.

Estas salidas no contienen un IEE ni un ranking: sus insumos continúan condicionales.

La estimación experimental v0.3 produce:

- `processed/v03_experimental_frontier_estimates.csv`: perfiles y brechas por país;
- `processed/v03_experimental_frontier_models.csv`: parámetros y gates por dimensión;
- `processed/v03_experimental_frontier_sensitivity.csv`: cuantiles 85, 90 y 95;
- `interim/v03_experimental_frontier_provenance.json`: método, hashes y bloqueos.

Uso y controles: [`docs/data-pipeline.md`](../docs/data-pipeline.md).
