# Sensibilidad de contexto v0.4

Esta etapa compara la frontera experimental base con dos especificaciones
condicionadas, una por control estructural. No elige una especificación ganadora ni
crea un IEE oficial.

| Escenario | Control | Ventana | Transformación |
|---|---|---|---|
| Base | Ninguno | — | — |
| `CTX-AGE-01` | Dependencia etaria | 2019–2021 | Lineal |
| `CTX-DENS-01` | Densidad poblacional | 2019–2021 | `log1p` |

Los escenarios se ejecutan por separado para salud y educación, que tienen 34 pares
completos. Seguridad y administración permanecen fuera: no alcanzan su gate de
muestra o no tienen resultado multinacional materializado.

## Ejecución

```bash
iee-context-sensitivity \
  --config config/context_sensitivity_v0.4.toml \
  --panel data/processed/v03_frontier_panel.csv \
  --gates data/processed/v03_frontier_gates.csv \
  --panel-provenance data/interim/v03_frontier_provenance.json \
  --context data/processed/v04_context_observations.csv \
  --context-provenance data/interim/v04_context_provenance.json
```

El comando publica una comparación por país, dimensión y control, más cuatro
modelos. Las sensibilidades no llevan intervalos nuevos, por lo que sirven para
detectar fragilidad de especificación, no para declarar diferencias entre países.
Cada salida mantiene `official_iee_score` nulo, `ranking_blocked` y
`context_control_not_causal`.

La primera corrida muestra cambios reducidos con dependencia etaria y cambios
materiales al condicionar salud por densidad. Esa diferencia confirma que la
densidad no debe adoptarse automáticamente como control principal; requiere
validación externa y un protocolo de incertidumbre antes de cualquier uso estable.
