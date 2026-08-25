# Puente de recursos educativos v0.6

La v0.6 prepara un panel trazable entre aprendizaje y recursos educativos. No estima
frontera, eficiencia, ranking ni IEE oficial.

## Decisión de fuentes

| Candidato | Unidad | Cobertura relevante | Decisión |
| --- | --- | --- | --- |
| OCDE Education at a Glance: gasto del gobierno general por estudiante FTE, PPA constante 2020 | USD PPA por estudiante | No contiene observación vigente para Colombia | Rechazado como insumo central |
| `EDU-IN-02`: UIS `% PIB` × PIB per cápita PPA constante | USD internacionales constantes 2021 por habitante | 35/38 para 2019–2020, incluye COL y USA | Puente condicional, no insumo final |

La primera alternativa es conceptualmente preferible porque su denominador es el
estudiante FTE. Su falta de Colombia impediría el objeto central del proyecto y no
se corrige con imputación. La fuente se conserva como contraste metodológico.

La segunda alternativa ya estaba materializada en v0.2. Mide gasto público total de
educación aproximado por habitante, por lo que no se presenta como gasto por alumno
ni se habilita para ajustar eficiencia.

## Contrato temporal y cobertura

| Componente | Regla |
| --- | --- |
| Resultado | `EDU-RES-01`, punto observado en 2020 |
| Recurso | `EDU-IN-02`, promedio de 2019 y 2020 |
| Países con par completo | 35/38 |
| Faltantes del puente | Australia, Grecia y México |
| Mínimo experimental | 30 países |
| Colombia / Estados Unidos | Incluidos |

El promedio 2019–2020 evita usar gasto posterior al resultado HCI 2020 y recupera
Colombia, que no tiene la ventana 2019–2021 completa. El panel resultante contiene
35 pares: supera el mínimo numérico, pero `input_conditional` mantiene falsos los
gates de eficiencia y publicación.

Los roles PISA de acceso y equidad de 2022 permanecen en v0.5 y no se agregan al
ajuste de recursos: primero debe aprobarse una regla explícita sobre el desfase entre
HCI 2020 y PISA 2022.

## Reproducción

```bash
iee-frontier-panel \
  --config config/frontier_panel_v0.6.toml \
  --result-observations data/processed/v03_result_observations.csv \
  --result-provenance data/interim/v03_result_provenance.json \
  --input-observations data/processed/v02_input_proxies.csv \
  --input-provenance data/interim/v02_input_provenance.json \
  --panel-output data/processed/v06_education_resource_panel.csv \
  --gates-output data/processed/v06_education_resource_gates.csv \
  --provenance-output data/interim/v06_education_resource_provenance.json
```

El [explorador oficial OCDE](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.EDU.IMEP&df%5Bid%5D=DSD_EAG_UOE_FIN%40DF_UOE_INDIC_FIN_PERSTUD&df%5Bvs%5D=3.1)
describe el dataset directo por estudiante FTE y su distinción por fuente de gasto,
precio y nivel educativo.
