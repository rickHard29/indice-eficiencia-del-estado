# Insumos públicos comparables v0.2

Corte de validación: **24 de agosto de 2026**.

La canalización v0.2 armoniza los cuatro insumos en **dólares internacionales
constantes de 2021 por habitante**. Los datos fuente siguen siendo oficiales y cada
producto conserva los hashes de sus componentes.

| ID | Dimensión | Construcción | Cobertura | Estado |
|---|---|---|---:|---|
| `SAL-IN-02` | Salud | GHED `% PIB` × PIB pc PPA constante | 38/38 | Condicional |
| `EDU-IN-02` | Educación | UIS `% PIB` × PIB pc PPA constante | 38/38, vintages desiguales | Condicional |
| `SEG-IN-02` | Seguridad | COFOG GF03 `% PIB` × PIB pc PPA constante | 34/38 | Condicional |
| `ADM-IN-02` | Administración | `(D1 + P2) / PIB` × PIB pc PPA constante | 34/38 | Condicional |

Los cuatro países sin cobertura COFOG común son CAN, MEX, NZL y TUR. No se eliminan
del universo: quedan registrados de forma explícita en la máscara y la procedencia,
sin crear filas ficticias ni valores cero.

## Ejecución

```bash
iee-download \
  --manifest config/downloads_inputs_v0.2.toml \
  --raw-dir data/raw/official-v0.2 \
  --processed data/processed/v02_input_proxies.csv \
  --provenance data/interim/v02_input_provenance.json
```

La ejecución realiza nueve solicitudes y conserva siete respuestas crudas únicas
por hash. Antes de descargar, exige que el manifiesto coincida exactamente con el
catálogo de URLs y con
[`country_universe_v0.2.toml`](../config/country_universe_v0.2.toml). Después verifica
entidades, categorías, unidades y checkpoints de Colombia y Estados Unidos, calcula
con `Decimal` y publica datos y procedencia como una pareja atómica.

El recibo conserva, por indicador, países incluidos y excluidos, conteo por país,
año más reciente y `vintage_age` respecto de 2023. En educación, por ejemplo, el
último dato de Colombia tiene antigüedad 3 y el de Estados Unidos 2; esa diferencia
no se imputa ni se oculta.

## Límites

- El deflactor del PIB no reproduce precios específicos de salud, educación,
  seguridad o administración.
- GF03 abarca policía, bomberos, tribunales y prisiones; no es solo policía.
- GF01 con D1 + P2 es una proxy operativa amplia y no identifica exclusivamente
  recaudo, compras o trámites.
- La educación no forma un panel balanceado 2019–2023. La antigüedad del último dato
  debe entrar como bandera, nunca como interpolación silenciosa.

Estas series resuelven la unidad técnica y permiten análisis de sensibilidad, pero
no levantan por sí solas el bloqueo del IEE oficial.
