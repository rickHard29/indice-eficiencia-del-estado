# ADR 0027: adopción condicional de equidad territorial de seguridad v2.3

- **Estado:** aprobado como subindicador condicional; puntaje bloqueado
- **Fecha:** 2026-09-02

## Contexto

La [ADR 0026](0026-v22-security-territorial-equity-screen.md) identificó una
medida abierta, armonizada y ponderable de disparidad territorial de homicidios.
La revisión confirmó 30 países OCDE con tres o más regiones TL2 y una pareja de
tasa de homicidios y población para 2021, incluidos Colombia y Estados Unidos.

## Decisión

Se adopta `SEG-EQ-01` como subindicador condicional de equidad territorial en
seguridad y justicia. La canalización descarga los dos extractos oficiales OCDE,
exige coincidencia exacta de regiones, país y año, y calcula:

```text
P90 ponderado por población(tasa de homicidios TL2)
− P10 ponderado por población(tasa de homicidios TL2)
```

El algoritmo toma el primer valor que alcanza cada porcentaje de población
acumulada. Su dirección es `lower`; una brecha menor representa mayor paridad
territorial. La máscara excluye Estonia, Islandia, Israel, Letonia, Lituania,
Luxemburgo, Nueva Zelanda y Eslovenia, sin imputación. Los controles de 2021 son
35,5 para Colombia y 6,1 para Estados Unidos.

## Consecuencias

El contrato guarda los bytes fuente, hashes y observaciones derivadas. Requiere un
mínimo de tres regiones por país y falla cerrada si baja de 30 países. Aunque la
fuente es pública y comparable en unidad, las divisiones TL2 no son equivalentes
en extensión o atribuciones administrativas. Por ello `score_eligible = false`:
la adopción no habilita puntajes, ranking, frontera ni IEE oficial.

El indicador mide dispersión territorial de homicidios, no acceso a justicia,
percepción de seguridad, eficacia institucional ni el promedio nacional de
homicidios. Cualquier cambio de año, geometría regional o transformación exige
una nueva decisión metodológica.
