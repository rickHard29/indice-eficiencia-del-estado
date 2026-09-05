# Cierre de la cohorte común actual v1.0

**Estado:** corte experimental reproducible; no habilita publicación de un IEE ni ranking  
**Fecha:** 2026-09-05

## Qué quedó terminado

La cohorte común vigente queda cerrada en **24 de los 38 países OCDE**:
AUT, CHE, CHL, COL, CRI, CZE, DNK, ESP, EST, FIN, FRA, GBR, HUN, IRL, ITA,
JPN, KOR, LTU, NLD, POL, SVK, SVN, SWE y USA.

El cierre fija esa membresía, el mínimo predeclarado de 30 países y los hashes
del recibo de cohorte y del paquete de revisión. Así, una modificación futura
de una fuente o de un panel no podrá presentar como el mismo corte los datos de
una cohorte diferente.

## Control ejecutable

`iee-current-cohort-release` genera
`data/processed/current_cohort_release_v1.json`. El recibo solo se emite si:

- la intersección calculada coincide exactamente con los 24 países declarados;
- los cuatro paneles de dimensión siguen siendo los que originaron el recibo;
- el paquete de revisión está disponible y aún no declara aprobación; y
- los puntajes, el IEE oficial y el ranking permanecen nulos.

Esto completa el corte actual como artefacto trazable, no como una tabla de
posiciones.

## Relación con la recuperación de cobertura

Los cinco hitos de la ruta v0.9 se cierran como un ciclo de evaluación de
fuentes: una ruta puede terminar en candidata reproducible o en rechazo
documentado. La revisión de las alternativas para Alemania, Noruega y Portugal
confirma que la serie OCDE no tiene la ventana completa 2019–2021; la serie
europea publicada no se intercambia porque usa otra definición y
estandarización. Nueva Zelanda tampoco ofrece ya la descarga pública de los
microdatos necesarios para reconstruir la medida.

Por ello el ciclo de recuperación no incorpora observaciones, no cambia la
cohorte de 24 países y no adelanta la publicación de un ranking. La próxima
ampliación solo podrá producirse cuando exista una fuente gratuita que supere
las mismas puertas de cobertura, causas, denominador, estándar y trazabilidad.
