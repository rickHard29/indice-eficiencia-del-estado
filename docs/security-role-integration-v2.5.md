# Integración de roles de seguridad y justicia v2.5

La v2.5 reúne los tres roles disponibles de seguridad y justicia en una sola
máscara de cobertura: resultado (`SEG-RES-01`), equidad territorial
(`SEG-EQ-01`) y recurso público (`SEG-IN-02`). No calcula eficiencia, un
puntaje, una frontera ni un ranking.

## Contrato

| Rol | Indicador y ventana | Estado | Regla de inclusión |
|---|---|---|---|
| Resultado | Homicidios intencionales, media 2019–2021 | Validado | Tres años observados y comparables |
| Equidad | Brecha territorial P90–P10, 2021 | Condicional | Una observación regional TL2 válida |
| Insumo | GF03 × PIB pc PPA, media 2019–2021 | Condicional | Tres años observados y comparables |

Cada país debe completar los tres roles. La integración conserva el universo
OCDE-38, no imputa faltantes y requiere por lo menos 30 países completos para
pasar su puerta de cobertura. Cumplir esa puerta tampoco habilitaría un IEE:
el resultado solo demuestra que la muestra permitiría una revisión metodológica
posterior.

## Materialización del 2 de septiembre de 2026

La intersección efectiva es de **26 de 38** países, por debajo del mínimo de 30.
Quedan dentro Australia, Austria, Suiza, Chile, Colombia, Costa Rica, Chequia,
Alemania, Dinamarca, España, Finlandia, Francia, Reino Unido, Grecia, Hungría,
Irlanda, Italia, Japón, Corea, Países Bajos, Noruega, Polonia, Portugal,
Eslovaquia, Suecia y Estados Unidos.

Los 12 faltantes se identifican sin sustituir datos: Bélgica no completa el
resultado 2019–2021; Canadá, México y Turquía no completan el insumo; Estonia,
Islandia, Israel, Letonia, Lituania, Luxemburgo y Eslovenia no tienen la medida
regional de equidad; y Nueva Zelanda carece de equidad e insumo.

Por tanto, la puerta queda cerrada: `integration_sample_eligible = false`,
`experimental_frontier_eligible = false` y `official_iee_score = null`.

Los snapshots usados tuvieron estos SHA-256:

| Snapshot | SHA-256 |
|---|---|
| Resultados v0.3 | `6d71bddd2660c37471baf3f18d0b0906dea2661a181773a88682a342e257683f` |
| Insumos v0.2 | `69f1ebdcbd7991e855f8e3fce1690bd041a7a53b00c825525a203cff74258d6c` |
| Equidad v2.3 | `49e176bb600f16c0c37caac02d7efda1603f6106170c2bf645977aae685920a0` |
| Panel integrado | `110fe1baed7625ab449ee91dae59f15db2705fd6b25ad8a6ebf6d30846a1271b` |

Los datos y recibos se mantienen fuera de Git. La configuración, el código, las
pruebas y esta documentación permiten reconstruir el diagnóstico.

## Reproducción

```bash
iee-download --manifest config/downloads_results_v0.3.toml \
  --raw-dir data/raw/v25-results \
  --processed data/processed/v25_results.csv \
  --provenance data/interim/v25_results.json

iee-download --manifest config/downloads_inputs_v0.2.toml \
  --raw-dir data/raw/v25-inputs \
  --processed data/processed/v25_inputs.csv \
  --provenance data/interim/v25_inputs.json

iee-download --manifest config/downloads_security_equity_v2.3.toml \
  --raw-dir data/raw/v25-equity \
  --processed data/processed/v25_equity.csv \
  --provenance data/interim/v25_equity.json

iee-security-integration
```

La decisión metodológica correspondiente es la
[ADR 0028](decisions/0028-v25-security-role-integration.md).
