# Control de cohorte común experimental v0.3

**Estado:** experimental; no habilita puntajes, agregación ni publicación  
**Fecha:** 2026-09-03

## Resultado del control

Las cuatro dimensiones tienen cortes propios de 30 o más países, pero su
intersección actual contiene **24 de 38 países**. Por tanto, una comparación
agregada experimental sigue bloqueada por el mínimo predeclarado de 30 países.

La cohorte común actual es: AUT, CHE, CHL, COL, CRI, CZE, DNK, ESP, EST, FIN,
FRA, GBR, HUN, IRL, ITA, JPN, KOR, LTU, NLD, POL, SVK, SVN, SWE y USA.

Esto es un diagnóstico de comparabilidad, no una selección de países para
favorecer resultados ni un ranking.

## Control reproducible

`config/experimental_cohort_v0.3.toml` fija el universo OCDE-38, los cuatro
paneles fuente y la regla de pertenencia de cada uno. El comando
`iee-experimental-cohort` calcula la intersección, lista faltantes por dimensión
y conserva un hash de cada panel de entrada.

El recibo generado mantiene nulos el puntaje, el ranking y la elegibilidad de
publicación. Si la intersección llega a 30, el recibo seguirá bloqueando la
agregación mientras no exista una metodología v1 congelada, los insumos sigan
condicionales y la revisión metodológica esté pendiente.

## Implicación operativa

La ruta de mayor impacto no es diseñar una visualización de posiciones. Es
recuperar, verificar y documentar seis países adicionales con roles y periodos
compatibles, empezando por las ausencias que se repiten entre los paneles. Cada
recuperación debe volver a ejecutar este control antes de proponerse para una
cohorte común.
