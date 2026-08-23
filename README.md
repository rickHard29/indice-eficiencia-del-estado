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
```

## Estado

Versión metodológica `0.1-draft`. La estructura es funcional y ya cuenta con una
[evaluación reproducible de los 12 indicadores propuestos del piloto](docs/source-validation.md):
6 indicadores validados, 2 condicionales, 2 en reserva y 2 que requieren diseño.
Todavía no se ha calculado ni publicado un puntaje IEE.

La [canalización reproducible de datos](docs/data-pipeline.md) ya descarga y valida
7 series oficiales, conserva 2 controles manuales y deja 3 indicadores explícitamente
diferidos. Los datos reales y sus recibos permanecen fuera de Git.

## Principios

- Trazabilidad de las fuentes y transformaciones.
- Reproducibilidad de los cálculos.
- Separación entre datos originales, procesados y resultados.
- Comparación de resultados frente a recursos, no de resultados aislados.
- Análisis de sensibilidad antes de publicar rankings.
