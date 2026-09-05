# Ranking exploratorio de resultados v0.1

**Estado:** publicable como experimento; no es el IEE oficial  
**Fecha:** 2026-09-05

## Qué compara

Este artefacto ordena los **33 países** con resultado disponible en educación,
salud, administración pública y seguridad y justicia. Es una comparación
exploratoria de resultados observados; no estima eficiencia estatal.

## Método fijo

1. Cada resultado se ordena dentro de los mismos 33 países.
2. La mejor posición de cada dimensión recibe 100 y la última 0; los empates
   reciben el promedio de sus posiciones.
3. El puntaje exploratorio es la media simple de las cuatro posiciones
   normalizadas, con peso de 25 % por dimensión.
4. Las posiciones se presentan por puntaje descendente; el código ISO3 solo
   ordena visualmente los empates.

El recibo `data/processed/results_ranking_v0.1.json` fija los hashes de los
cuatro paneles fuente, cada valor, cada posición normalizada y el puntaje.

## Archivos públicos reutilizables

La publicación incluye [puntajes exploratorios por país](publication/results-ranking-v0.1.csv)
y [rangos de estabilidad](publication/results-ranking-stability-v0.1.csv). Ambos
archivos indican en cada fila que se trata de un ranking exploratorio de
resultados y no del IEE oficial.

## Límites explícitos

Este ranking no incluye recursos, acceso ni equidad; tampoco aplica una frontera
de eficiencia. Por lo tanto:

- no se denomina Índice de Eficiencia del Estado;
- no tiene puntaje IEE oficial;
- no habilita afirmaciones causales sobre gestión pública; y
- no reemplaza la cohorte completa actual de 24 países.

La publicación busca hacer discutibles los datos y el método, no convertir una
comparación provisional en una evaluación definitiva de gobiernos.
