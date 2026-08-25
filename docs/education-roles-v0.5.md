# Roles de educación v0.5

La v0.5 materializa un panel reproducible de los tres roles de calidad educativa
para los 38 miembros de la OCDE. Es una mejora de cobertura y trazabilidad; no
calcula eficiencia, una frontera, un ranking ni un IEE oficial.

## Series

| Rol | Indicador | Año | Países con dato | Fuente |
| --- | --- | ---: | ---: | --- |
| Resultado | `EDU-RES-01`: aprendizaje armonizado | 2020 | 38/38 | Banco Mundial, HCI |
| Acceso | `EDU-ACC-02`: Coverage Index 3 | 2022 | 37/38 | OCDE, PISA 2022, tabla I.B1.4.1 |
| Equidad | `EDU-EQ-01`: brecha ESCS en matemáticas | 2022 | 36/38 | OCDE, PISA 2022, tabla I.B1.4.3 |

El `Coverage Index 3` (CI3) es la proporción de toda la población nacional de 15
años representada por la muestra PISA. Su denominador incluye jóvenes no
escolarizados; por tanto, es una proxy de acceso y permanencia en secundaria, no una
tasa de graduación ni de matrícula general.

La brecha ESCS es la diferencia de puntos de matemáticas entre el cuartil superior y
el inferior del índice socioeconómico PISA; menor es mejor. Las dos medidas PISA
describen estudiantes de 15 años y no deben extrapolarse a todo el sistema educativo.

## Máscaras y cautelas

- Acceso: Luxemburgo no tiene valor PISA 2022; quedan 37 observaciones.
- Equidad: Costa Rica y Luxemburgo no tienen estimación; quedan 36 observaciones.
- Las observaciones de Australia, Canadá, Dinamarca, Irlanda, Letonia, Países Bajos,
  Nueva Zelanda, Reino Unido y Estados Unidos preservan
  `source:sampling_caution`, tal como las marca la OCDE.

Las tres series se solapan en 36 países. Esa muestra supera el mínimo metodológico
de 30 países para una futura exploración por dimensión, pero la v0.5 no la ejecuta.

## Desfase temporal y bloqueo de eficiencia

El resultado HCI se observa en 2020 y los roles PISA en 2022. Esta diferencia queda
explícita en cada fila y no se trata como si fuera una medición simultánea. Además,
el insumo educativo comparable continúa siendo una proxy condicional, no un recurso
sectorial final por estudiante. Por ambos motivos el panel solo habilita perfiles de
cobertura/calidad; no ajusta resultados por recursos ni publica eficiencia.

## Reproducción

```bash
iee-download \
  --manifest config/downloads_education_v0.5.toml \
  --raw-dir data/raw/v05_education \
  --processed data/processed/v05_education_observations.csv \
  --provenance data/interim/v05_education_provenance.json
```

El adaptador `oecd_pisa_xlsx` lee directamente el libro XLSX oficial de la OCDE con
biblioteca estándar de Python. La hoja, columnas y nombres de países se congelan en
el manifiesto; la ejecución falla si faltan países o cambian los puntos de control de
Colombia y Estados Unidos.
