# Diagnóstico experimental v0.1

## Dictamen

Esta fase prueba la mecánica de normalización, agregación, trazabilidad y
sensibilidad con el snapshot bilateral del piloto. **No calcula un Índice de
Eficiencia del Estado, no estima eficiencia y no habilita un ranking.**

La configuración ejecutable es
[`config/scoring_experiment.toml`](../config/scoring_experiment.toml). El motor
verifica el hash del snapshot y de su recibo de ingestión antes de calcular. Las
cinco salidas se publican como una unidad: si falla una escritura, se restaura el
conjunto anterior.

## Por qué el IEE oficial queda nulo

Los bloqueos son deliberados y auditables:

- ninguna de las cuatro dimensiones tiene todavía un insumo público compatible
  habilitado;
- salud y educación cubren 75 % de los roles planificados, mientras seguridad y
  administración cubren 50 %;
- faltan roles obligatorios en todas las dimensiones;
- dos países no permiten estimar la frontera internacional prevista; la prueba
  fija un mínimo futuro de 30;
- existen límites provisionales y sensibilidad material a la ventana de salud y
  al tratamiento de la brecha PISA.

Por eso `official_iee_score` permanece vacío, `publication_eligible=false` y
`ranking_eligible=false`. Los insumos condicionales o en reserva se exportan solo
como contexto y nunca entran en el compuesto diagnóstico.

## Ventanas congeladas

| Indicador | Regla temporal | Normalización diagnóstica |
| --- | --- | --- |
| `SAL-RES-01` | promedio 2019–2021 | lineal, menor es mejor, 0–500 provisional |
| `SAL-ACC-01` | 2021 | lineal, mayor es mejor, escala natural 0–100 |
| `EDU-RES-01` | 2020 | lineal, mayor es mejor, escala técnica 300–625 |
| `EDU-EQ-01` | 2022 | lineal, menor es mejor, 0–150 provisional |
| `SEG-RES-01` | promedio 2021–2023 | `log1p` del promedio, menor es mejor, 0–50 provisional |
| `ADM-RES-01` | 2024 | lineal, mayor es mejor, escala natural 0–1 |

El rango 300–625 de aprendizaje armonizado sigue la escala técnica publicada
por el [Banco Mundial](https://humancapital.worldbank.org/hciplus/insights/indicators_responsible_gap/).
La mortalidad evitable conserva la definición oficial de la
[OCDE](https://www.oecd.org/en/publications/health-at-a-glance-2023_7a7afb35-en/full-report/avoidable-mortality-preventable-and-treatable_e7407977.html),
pero su límite 0–500 es solo una prueba de estrés. El OSI proviene de la
[Encuesta de Gobierno Electrónico 2024 de Naciones Unidas](https://publicadministration.desa.un.org/publications/un-e-government-survey-2024-0).

Los roles disponibles se reponderan exclusivamente para probar la tubería. Los
pesos de referencia son resultado 50 %, acceso 25 % y equidad 25 %. Las cuatro
dimensiones conservan 25 % cada una y usan media geométrica ponderada. Esta
reponderación es una excepción experimental; no satisface las reglas del IEE.

## Resultado de control

Con el snapshot cuyo SHA-256 comienza por `8209f9ca`, la ejecución de control
produce los siguientes valores. Deben leerse como comprobaciones internas de la
canalización, no como resultados publicables ni posiciones relativas.

| País | Salud | Educación | Seguridad | Administración | Compuesto diagnóstico |
| --- | ---: | ---: | ---: | ---: | ---: |
| Colombia | 45,36 | 39,89 | 16,99 | 75,21 | 39,00 |
| Estados Unidos | 48,43 | 51,41 | 49,26 | 91,36 | 57,86 |

El compuesto mezcla observaciones de 2021 a 2024 y no representa un país-año.
La observación PISA de Estados Unidos conserva una advertencia de muestreo.

## Sensibilidad obligatoria

La ejecución calcula catorce escenarios además de la base:

1. media aritmética en lugar de geométrica;
2. peso de resultado −25 % y +25 %;
3. mortalidad evitable prepandemia, promedio 2017–2019, manteniendo UHC 2021;
4. límite superior de mortalidad evitable de 400 y 600;
5. límite superior de brecha PISA de 110, 120 y 200 puntos;
6. límite superior de homicidios de 30 y 75;
7. exclusión global de una serie si su observación seleccionada tiene advertencia
   de muestreo, para conservar el mismo conjunto de indicadores en ambos países;
8. homicidios con promedio 2021–2023 lineal y con punto 2023 más `log1p`, para
   separar el efecto de suavizar la serie del efecto de transformar su asimetría.

La ventana prepandemia cambia la señal bilateral de salud: Colombia obtiene 58,86
y Estados Unidos 56,78, frente a 45,36 y 48,43 en la base 2019–2021. En educación,
el límite de brecha PISA también cambia la magnitud y puede cambiar la señal. Estas
pruebas confirman que aún no debe publicarse un agregado. En seguridad, sustituir
`log1p` por una regla lineal mueve el compuesto diagnóstico aproximadamente 12,00
puntos en Colombia y 8,90 en Estados Unidos, otra sensibilidad material.

## Ejecución y salidas

```bash
python -m pip install -e .
iee-score
```

El comando produce:

- `iee_experimental_indicator_scores.csv`: valores seleccionados, transformados y
  normalizados;
- `iee_experimental_dimension_diagnostics.csv`: dimensiones y compuesto con los
  bloqueos explícitos;
- `iee_experimental_sensitivity.csv`: escenario, valor base y diferencia;
- `iee_experimental_input_context.csv`: insumos no puntuados y su razón de reserva;
- `iee_experimental_provenance.json`: hashes, ventanas, conteos y gate de publicación.

Los resultados son regenerables y permanecen fuera de Git. Git conserva el código,
la configuración, las pruebas y esta especificación.

## Condiciones para una versión publicable

Antes de calcular un IEE se debe ampliar el universo internacional, resolver los
insumos a precios constantes, completar los roles obligatorios, definir rezagos,
validar límites con la distribución multinacional, estimar la frontera y aprobar el
protocolo de incertidumbre. Cumplir solo el umbral numérico de cobertura no elimina
los demás bloqueos.
