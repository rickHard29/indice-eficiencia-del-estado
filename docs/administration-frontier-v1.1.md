# Panel administrativo v1.1

Corte de ejecución: **25 de agosto de 2026**.

La v1.1 materializa por primera vez el resultado administrativo para los 38
miembros de la OCDE. No calcula un IEE, no publica una clasificación y no
convierte el resultado en una medida oficial de eficiencia.

## Fuente y materialización

El resultado `ADM-RES-01` es el *Online Service Index* (OSI) de la Encuesta de
Gobierno Electrónico 2024 de Naciones Unidas. La [tabla 7 del apéndice técnico
oficial](https://desapublications.un.org/sites/default/files/publications/2024-10/Technical%20Appendix%20%28Web%20version%29%2030102024.pdf)
se publica como PDF, no como una API estable. Por ello se transcribieron y
versionaron los 38 valores de la columna **OSI 2024** en
`config/admin_manual_controls_v1.1.toml`.

La transcripción se prueba sin conexión, conserva URL, edición, localizador y
hash del archivo de controles. Colombia (0,7521) y Estados Unidos (0,9136)
reproducen los controles ya validados. El anexo de la ONU enumera la tabla en
las páginas PDF 36–45; no mide uso efectivo de los servicios ni desigualdad de
acceso digital.

## Panel experimental

| Elemento | Regla |
|---|---|
| Resultado | `ADM-RES-01`, OSI, punto 2024, escala natural 0–1 |
| Recurso | `ADM-IN-02`, proxy operativo COFOG GF01, promedio 2019–2021 |
| Muestra | 34 de 38 miembros OCDE; faltan Canadá, México, Nueva Zelanda y Turquía en el recurso |
| Modelo | Frontera cuantílica lineal monótona, cuantil 0,90 y `log1p` del recurso |
| Estado | Experimental; resultado oficial, publicación y ranking: nulos/bloqueados |

Los 34 pares superan el mínimo técnico de 30, pero la distancia temporal entre
el recurso 2019–2021 y el resultado 2024 se declara explícitamente. El recurso
es condicional: excluye intereses y transferencias, pero GF01 continúa siendo
una proxy amplia de administración pública y se convierte con el deflactor
general del PIB. Tampoco existe aquí un rol internacional armonizado de acceso
o equidad.

El modelo entrega una pendiente positiva (4,1438 por `log1p` del recurso) y
perfiles internos. Esos perfiles solo describen el ajuste de este proxy y esta
ventana; no son puntajes de eficiencia estatal ni una comparación que pueda
publicarse.

## Artefactos reproducibles

- `config/downloads_admin_v1.1.toml` y `config/admin_manual_controls_v1.1.toml`:
  panel de resultado y su control PDF.
- `config/frontier_panel_v1.1.toml`: contrato del panel de 38 países.
- `config/frontier_estimator_v1.1.toml`: hashes del panel y de sus salidas.
- `data/processed/admin_v11_observations.csv` y `data/interim/admin_v11_provenance.json`:
  snapshot local ignorado por Git, regenerable sin red.

La decisión metodológica correspondiente está en la
[ADR 0015](decisions/0015-v11-administration-result-materialization.md).
