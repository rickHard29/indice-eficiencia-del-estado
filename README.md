# Índice de Eficiencia del Estado (IEE)

Proyecto para construir un índice internacional comparable y reproducible sobre la capacidad del Estado para transformar recursos públicos en resultados sociales e institucionales.

El IEE no premia automáticamente un Estado pequeño ni castiga uno grande: compara resultados con recursos, cobertura, calidad y contexto.

## Componentes

- Google Drive y Google Sheets: fuentes, datos de trabajo e inventario de indicadores.
- Google Docs: metodología viva y decisiones pendientes.
- GitHub: código, configuraciones, pruebas y control de versiones.

## Estructura

```text
config/          Parámetros metodológicos versionados
data/            Esquemas y muestras sintéticas; nunca datos restringidos
docs/            Metodología técnica y decisiones
src/iee/         Código del índice
tests/           Pruebas automatizadas
```

## Inicio rápido

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
iee-download
iee-score
```

## Estado

Versión metodológica `0.1-draft`. La estructura es funcional y ya cuenta con una
[evaluación reproducible de los 12 indicadores propuestos del piloto](docs/source-validation.md):
6 indicadores validados, 2 condicionales, 2 en reserva y 2 que requieren diseño.
Todavía no se ha calculado ni publicado un puntaje IEE.

La [canalización reproducible de datos](docs/data-pipeline.md) ya descarga y valida
7 series oficiales, incorpora 2 controles manuales versionados y deja 3 indicadores
explícitamente diferidos. Los datos reales y sus recibos permanecen fuera de Git.

El [diagnóstico experimental v0.1](docs/experimental-scoring-v0.1.md) ya prueba
normalización, agregación, sensibilidad y procedencia con el snapshot bilateral.
El sistema mantiene el IEE oficial nulo y bloquea publicación y ranking porque aún
faltan insumos compatibles, roles obligatorios y un universo multinacional.

La [v0.2 ya congela un universo de 38 miembros de la OCDE](docs/universe-v0.2.md)
y exige muestras separadas por dimensión. La ampliación permite auditar cobertura
multinacional sin seleccionar países por sus faltantes, pero todavía no levanta los
bloqueos metodológicos del IEE oficial.

También existe una [canalización v0.2 de insumos comparables](docs/input-proxies-v0.2.md)
que convierte las cuatro funciones a PPA constante de 2021 por habitante. Las
series siguen siendo proxies condicionales hasta validar deflactores, vintages y
rezagos sectoriales.

La v0.3 ya inició con un [panel multinacional reproducible de resultados](docs/decisions/0005-v03-frontier-experimental-panel.md)
para los 38 países OCDE. Es la base de una futura frontera experimental por
dimensión; no habilita todavía un IEE, ranking ni publicación de eficiencia.

Sobre ese panel, la [frontera cuantílica experimental v0.3](docs/decisions/0006-v03-experimental-quantile-frontier.md)
estima únicamente las dimensiones que superan el mínimo de 30 pares completos,
con sensibilidad e intervalos reproducibles. Todos sus resultados continúan
marcados como experimentales y el IEE oficial permanece nulo.

La [v0.4 añade un panel de contexto estructural](docs/structural-controls-v0.4.md)
para probar controles demográficos y de concentración espacial. Es una base para
sensibilidades futuras, no un cambio automático de la frontera ni del IEE.

Las [sensibilidades de contexto v0.4](docs/context-sensitivity-v0.4.md) ya comparan
esos controles por separado contra la frontera experimental. Siguen bloqueadas para
publicación y sirven para detectar fragilidad de especificación.

La [v0.5 materializa los roles educativos](docs/education-roles-v0.5.md) de
resultado, acceso y equidad para OCDE-38, con máscaras explícitas para los faltantes
PISA y cautelas de muestreo por país. Es un panel de calidad/cobertura: por el
desfase 2020–2022 y la ausencia de un insumo educativo final, no habilita todavía
eficiencia, ranking ni IEE oficial.

## Principios

- Trazabilidad de las fuentes y transformaciones.
- Reproducibilidad de los cálculos.
- Separación entre datos originales, procesados y resultados.
- Comparación de resultados frente a recursos, no de resultados aislados.
- Análisis de sensibilidad antes de publicar rankings.
