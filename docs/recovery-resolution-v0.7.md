# Resolución de recuperación v0.7

**Estado:** ciclo técnico cerrado; no publicable como índice ni ranking.

La v0.7 resuelve las tres rutas que quedaron candidatas en v0.6. Resolver no
significa adoptar: una fuente solo se integra cuando conserva definición, ventana
y unidad comparables con el contrato existente.

| País | Evidencia contrastada | Decisión |
| --- | --- | --- |
| Australia | ABS informa 105.129 y 114.146 millones AUD de gasto operativo educativo para 2018-19 y 2019-20. Son ejercicios fiscales y gasto operativo de gobierno general, no la serie calendario UIS/WDI. | No adoptado: desfase fiscal y alcance. |
| Grecia | Eurostat COFOG GF09 informa 3,9% y 4,4% del PIB en 2019-2020. El dato base de 2019 equivale a 3,5506% del PIB PPA: una diferencia de 9,84%. | No adoptado: discontinuidad de definición sin puente oficial. |
| Alemania | Eurostat informa 231,41; 238,07; 252,54 para 2019-2021, mientras la serie OCDE existente informa 188 y 195 en 2019-2020 y carece de 2021. | No adoptado: definiciones no intercambiables. |

El recibo `iee-recovery-resolution` conserva ambas fuentes y bloquea toda adopción,
cambio de cohorte, puntaje y ranking. La cohorte común se mantiene en **24 de 30**.

## Cierre técnico

Las seis prioridades originales y las tres candidatas ya tienen una decisión
reproducible. Por ello se completa el ciclo técnico de recuperación v0.7. Esto no
equivale a una validación metodológica independiente ni habilita un ranking oficial:
la evidencia comparable todavía debe existir y superar la revisión abierta.

## Ejecución

```bash
iee-recovery-resolution \
  --config config/recovery_resolution_v0.7.toml \
  --output data/processed/recovery_resolution_v0.7.json
```
