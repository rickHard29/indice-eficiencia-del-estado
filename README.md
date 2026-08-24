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

## Principios

- Trazabilidad de las fuentes y transformaciones.
- Reproducibilidad de los cálculos.
- Separación entre datos originales, procesados y resultados.
- Comparación de resultados frente a recursos, no de resultados aislados.
- Análisis de sensibilidad antes de publicar rankings.
