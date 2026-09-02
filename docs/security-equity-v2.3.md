# Equidad territorial en seguridad y justicia v2.3

`SEG-EQ-01` mide la dispersión territorial de la tasa de homicidios intencionales
en regiones TL2 de la OCDE. Es un subindicador condicional: se materializa para
diagnóstico, pero no se usa en puntajes, ranking, frontera ni IEE oficial.

## Contrato de datos

| Elemento | Regla |
|---|---|
| Fuentes | OCDE, *Safety -- Regions* y *Demography -- Regions* |
| Corte | 2021, único año común del contrato |
| Unidad base | Homicidios intencionales por 100.000 habitantes, TL2 |
| Transformación | `P90 ponderado − P10 ponderado` por población TL2 |
| Dirección | Menor es mejor |
| Cobertura | 30 de 38 países OCDE; sin imputación |
| Puntaje | Bloqueado (`score_eligible = false`) |

Para cada país se ordenan las tasas regionales de menor a mayor. El cuantil
ponderado es la primera tasa cuya población acumulada alcanza 10 % o 90 % de la
población TL2 observada. La diferencia se expresa en homicidios por 100.000
habitantes. Cada país debe aportar al menos tres regiones y las parejas
región--población deben corresponder al mismo año.

Se excluyen Estonia, Islandia, Israel, Letonia, Lituania, Luxemburgo, Nueva
Zelanda y Eslovenia. Una actualización que reduzca la muestra por debajo de 30
debe fallar cerrada; no se reemplazan datos regionales por la tasa nacional.

## Puntos de control

| País | P10 ponderado | P90 ponderado | Brecha |
|---|---:|---:|---:|
| Colombia | 14,0 | 49,5 | 35,5 |
| Estados Unidos | 4,1 | 10,2 | 6,1 |

## Límites de interpretación

La medida compara dispersión territorial dentro de cada país, no su tasa nacional
promedio. Las regiones TL2 tienen tamaño, población y atribuciones administrativas
distintos entre países; por ello el indicador es condicional y conserva el bloqueo
de puntuación. No mide acceso a justicia, percepción de seguridad, denuncias ni
eficacia de la policía o los tribunales.

## Verificación de materialización

La ejecución de control del 2 de septiembre de 2026 obtuvo 30 observaciones
derivadas. El archivo procesado tiene SHA-256
`49e176bb600f16c0c37caac02d7efda1603f6106170c2bf645977aae685920a0`.
Los recursos originales de homicidios y población tienen, respectivamente,
SHA-256 `f12a73d9d60d8a89b48017ccf4b1f7425e11e6d025f726ac6d772ff837bf5db1`
y `cef59f118c57d8fda15e8e00f17f7005e832bb9287446ab074e9097059356900`.
Los bytes se mantienen fuera de Git y el recibo de procedencia registra ambas
URLs oficiales.

La decisión de adopción está en la
[ADR 0027](decisions/0027-v23-security-territorial-equity-adoption.md).
