# Universo multinacional v0.2

Corte de validación: **24 de agosto de 2026**.

## Marco base

La v0.2 usa los 38 miembros enumerados por la
[OCDE](https://www.oecd.org/en/about/members-partners.html). El marco incluye a
Colombia y Estados Unidos y permanece fijo aunque una fuente omita países. Las
muestras se determinan por dimensión y se publican como máscaras explícitas.

La definición ejecutable está en
[`config/country_universe_v0.2.toml`](../config/country_universe_v0.2.toml). Su hash,
los 38 países y las máscaras de adquisición se incorporan al recibo de procedencia;
si divergen del manifiesto, la canalización falla antes de descargar o escribir.

Este marco permite una comparación **relativa a la OCDE**. No representa todavía
la frontera global prevista por la metodología completa.

## Cobertura de resultados ya validados

| Indicador | Ventana | Elegibles | Falta de ventana completa |
|---|---:|---:|---|
| Mortalidad evitable | Media 2019–2021 | 34/38 | DEU, NOR, NZL, PRT |
| Cobertura sanitaria universal | 2021 | 38/38 | Ninguno |
| Aprendizaje armonizado | 2020 | 38/38 | Ninguno |
| Brecha socioeconómica PISA | 2022 | 37/38 | CRI |
| Homicidios intencionales | Media 2021–2023 | 32/38 | BEL, GBR, ISR, LUX, NZL, PRT |
| Servicios públicos en línea | 2024 | 38/38 | Ninguno |

La advertencia muestral de PISA se conserva para AUS, CAN, DNK, GBR, IRL, LVA,
NLD, NZL y USA. La exclusión de esas observaciones solo puede evaluarse como una
sensibilidad global y simétrica.

## Regla de elegibilidad

Una dimensión puede preparar una estimación únicamente cuando:

1. su muestra observada contiene al menos 30 países;
2. están representados todos los roles obligatorios;
3. existe un insumo en PPA constante compatible;
4. la ventana y el rezago están congelados;
5. ninguna imputación es necesaria para cruzar el umbral.

Cumplir el primer punto no compensa el incumplimiento de los otros cuatro. Por eso
este inventario amplía la capacidad de análisis, pero mantiene nulos el IEE oficial,
la publicación y el ranking.
