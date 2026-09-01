# Equidad territorial administrativa v1.9

`ADM-EQ-03` es un subindicador condicional que mide la brecha absoluta de
cobertura de identidad oficial entre zonas rurales y urbanas para la población
de 15 años o más. Usa los indicadores abiertos `ID.OWN.TOTL.UR.ZS` y
`ID.OWN.TOTL.RU.ZS` de ID4D--Global Findex 2025 del Banco Mundial.

## Contrato

La descarga reproduce un único corte de 2024 para 34 países OCDE. Excluye
Australia, Estonia, Luxemburgo y República Eslovaca por falta de la pareja
rural-urbana. Para cada país se requiere el mismo año en ambas series y se
calcula:

```text
brecha territorial = |porcentaje urbano − porcentaje rural|
```

El archivo procesado se etiqueta como `derived`, con dirección `lower` y
`score_eligible = false`. Se conserva la respuesta original de cada serie y un
recibo con hashes. El mínimo de 34 países supera el umbral técnico de 30, pero
no autoriza una frontera mientras la metodología general mantenga el bloqueo.

## Controles de 2024

| País | Rural | Urbana | Brecha absoluta |
|---|---:|---:|---:|
| Colombia | 97,536758 % | 98,903851 % | 1,367093 p.p. |
| Estados Unidos | 86,129917 % | 93,582721 % | 7,452805 p.p. |

## Límite de interpretación

La medida aproxima igualdad territorial de un requisito para acceder a servicios
o beneficios. No es un indicador de uso, tiempo de respuesta, terminación,
satisfacción ni diferencias entre municipios. Tampoco describe la carga
administrativa de empresas, que sigue separada en `ADM-ACC-02`.

La decisión de adopción y sus resguardos están en la
[ADR 0023](decisions/0023-v19-territorial-equity-adoption.md).
