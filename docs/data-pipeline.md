# Canalización reproducible de datos del piloto

La primera canalización del IEE descarga, valida y normaliza fuentes oficiales para
Colombia y Estados Unidos. No calcula puntuaciones: su única función es producir una
base trazable y detenerse si la fuente cambia de forma material.

La extensión v0.2 usa el mismo motor para los cuatro insumos multinacionales. Su
manifiesto referencia el universo OCDE-38, aplica máscaras de 38 o 34 países y deriva
PPA constante de 2021 por habitante. Véase
[`docs/input-proxies-v0.2.md`](input-proxies-v0.2.md).

La primera entrega v0.3 materializa, por separado, un panel de cuatro resultados
validados para el mismo marco OCDE-38. La decisión y sus límites se documentan en
[`ADR 0005`](decisions/0005-v03-frontier-experimental-panel.md).

## Cobertura

El manifiesto [`config/downloads.toml`](../config/downloads.toml) asigna una ruta de
adquisición a los 12 indicadores propuestos:

- **7 automáticos:** mortalidad evitable, cobertura sanitaria universal, gasto
  público en salud, aprendizaje armonizado, homicidios, gasto en seguridad por
  habitante en PPA y recursos operativos administrativos.
- **2 controles manuales versionados:** brecha PISA por nivel socioeconómico y
  Online Service Index. Sus cuatro valores se incorporan a la salida normalizada
  desde [`config/manual_controls.toml`](../config/manual_controls.toml), con fuente,
  edición, localizador y estado de calidad. No se presentan como descargas de API.
- **3 diferidos:** gasto educativo por estudiante, disparidad territorial de
  violencia y finalización de trámites. El primero está en reserva por cobertura; los
  otros dos requieren diseño.

Que una serie pueda descargarse no significa que pueda puntuar. `score_eligible`
separa la adquisición técnica del dictamen metodológico. Los insumos condicionales o
en reserva se conservan para análisis, pero nunca entran silenciosamente al índice.

## Ejecución

Desde la raíz del repositorio:

```bash
python -m pip install -e .
iee-download
```

Sin instalar el comando:

```bash
PYTHONPATH=src python -m iee.download
```

Las rutas se pueden modificar:

```bash
iee-download \
  --manifest config/downloads.toml \
  --raw-dir data/raw/official \
  --processed data/processed/pilot_observations.csv \
  --provenance data/interim/pilot_provenance.json
```

Para el panel multinacional de resultados v0.3:

```bash
iee-download \
  --manifest config/downloads_results_v0.3.toml \
  --raw-dir data/raw/official-v0.3 \
  --processed data/processed/v03_result_observations.csv \
  --provenance data/interim/v03_result_provenance.json
```

## Salidas

### Datos crudos

Cada respuesta original se guarda en `data/raw/official/` con su SHA-256 como nombre.
Dos respuestas con los mismos bytes comparten archivo; cualquier revisión produce un
hash diferente.

### Observaciones normalizadas

`data/processed/pilot_observations.csv` usa UTF-8, terminador LF y orden estable por
país, año e indicador. Reúne 7 series automáticas y 2 controles manuales. Los valores
se calculan con `Decimal`, sin redondeo intermedio, y `observation_kind` conserva la
diferencia entre `reported`, `derived` y `manual_control`.

El CSV y su recibo de procedencia se preparan juntos. Si falla la publicación de
cualquiera de los dos, la canalización restaura la pareja anterior; los recursos
crudos ya verificados pueden permanecer en la caché por ser inmutables y direccionados
por contenido.

### Procedencia

`data/interim/pilot_provenance.json` registra:

- URL solicitada y URL final.
- tipo de contenido, tamaño, ETag y Last-Modified cuando existen;
- SHA-256 y ruta de cada respuesta cruda;
- hashes del catálogo y del manifiesto;
- hash, versión, fecha de validación e identificadores del manifiesto de controles
  manuales;
- número de observaciones y último año/valor por país;
- SHA-256 de la salida normalizada;
- fecha UTC de la ejecución.

Las tres rutas están excluidas de Git. El repositorio conserva código, manifiestos y
pruebas; los snapshots de datos deben archivarse en el almacenamiento de datos del
proyecto.

## Controles que detienen la ejecución

La canalización falla antes de publicar las salidas cuando encuentra:

- un indicador, fuente, estado o unidad que difiere del catálogo metodológico;
- una URL primaria o dependiente que difiere del catálogo congelado;
- un universo o una máscara de países que difiere del manifiesto;
- una ruta de salida que pueda sobrescribir una entrada o un recurso crudo;
- un país, año, valor o URL manual que difiere del catálogo metodológico;
- una respuesta paginada incompleta, vacía, XML en lugar de CSV o con columnas
  faltantes;
- un país inesperado, una clave país-año duplicada o cobertura insuficiente;
- un último año distinto del validado;
- un último valor fuera de la tolerancia explícita;
- `NaN`, infinito, denominador cero, moneda incompatible o componentes incompletos;
- una unión imperfecta de gasto, PPA y población.

No se exige un panel balanceado ni el mismo último año para ambos países. Los
faltantes nunca se convierten en cero.

## Derivaciones actuales

### Seguridad y justicia

```text
gasto GF03 por habitante PPA =
    gasto nominal × 10^UNIT_MULT / factor PPA / población
```

Los tres componentes deben coincidir exactamente en país y año. Esta serie sigue en
reserva porque usa PPA corriente y combina tres datasets.

### Administración

```text
recursos operativos (% PIB) = 100 × (D1 + P2 en S13/GF01) / B1GQ
```

La salida conserva `provisional` cuando cualquiera de sus componentes tiene la
bandera OECD `P`. En la ejecución de control, esto aplica a Colombia en 2023 y 2024
por el estado provisional del PIB.

## Pruebas

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Las pruebas no usan internet: inyectan respuestas pequeñas y verifican parseo,
hashes, cobertura desigual por país, derivaciones, orden estable y escritura
transaccional.
