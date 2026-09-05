# Sensibilidad del ranking exploratorio de resultados v0.1

**Estado:** control de robustez exploratorio; no es el IEE oficial  
**Fecha:** 2026-09-05

## Pregunta que responde

El ranking exploratorio de resultados v0.1 usa cuatro dimensiones con el mismo
peso: educación, salud, administración pública y seguridad y justicia. Esta
prueba pregunta cuánto cambia una posición si se elimina **una** de esas
dimensiones y se reparte el peso por igual entre las tres restantes.

## Procedimiento fijo

Se calculan cinco escenarios para los mismos 33 países:

1. el ranking base con las cuatro dimensiones;
2. un recálculo sin educación;
3. un recálculo sin salud;
4. un recálculo sin administración; y
5. un recálculo sin seguridad y justicia.

Para cada país se informa la mejor y la peor posición en los cuatro recálculos
que omiten una dimensión, además de la amplitud entre ambas. Los puntajes se
derivan de las posiciones normalizadas ya fijadas en el recibo del ranking
v0.1. Los empates de los recálculos se ordenan visualmente por código ISO3.

El recibo `data/processed/results_ranking_sensitivity_v0.1.json` conserva el
hash del ranking de entrada y todas las posiciones de cada escenario.

## Interpretación correcta

Una amplitud pequeña indica que la posición mostrada no depende mucho de
retirar una sola dimensión. Una amplitud grande señala que la posición merece
lectura cautelosa y revisión de los resultados que la componen.

Esto **no** es un intervalo estadístico, una estimación de causalidad ni una
medida de incertidumbre muestral. Tampoco incorpora recursos, acceso o equidad,
ni una frontera de eficiencia. Por ello no habilita un ranking ni un puntaje
oficial del Índice de Eficiencia del Estado.
