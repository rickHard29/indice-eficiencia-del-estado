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

Uso y controles: [`docs/data-pipeline.md`](../docs/data-pipeline.md).
