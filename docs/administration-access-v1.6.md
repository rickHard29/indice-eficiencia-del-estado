# Acceso administrativo empresarial v1.6

La v1.6 materializa `ADM-ACC-02` como subindicador condicional. Mide el tiempo
semanal que la alta gerencia de empresas privadas dedica a requisitos estatales.
No representa la experiencia de hogares ni completa el rol ciudadano pendiente.

## Contrato de datos

| Elemento | Regla |
|---|---|
| Fuente | Banco Mundial, *Enterprise Surveys*, `IC.GOV.DURS.ZS` |
| Universo | 38 miembros OCDE |
| Ventana de consulta | 2020--2025 |
| Cobertura | 38 de 38; 37 últimas observaciones entre 2023--2025 y Luxemburgo en 2020 |
| Dirección | Menor es mejor |
| Puntaje | Bloqueado (`score_eligible = false`) |
| Uso autorizado | Diagnóstico de carga regulatoria empresarial |

Los resultados se escriben localmente en `data/processed/` y `data/interim/`;
los bytes originales y sus hashes se conservan fuera de Git en `data/raw/`.
La ejecución no habilita una clasificación de países ni modifica el IEE oficial.

## Verificación de materialización

La ejecución de control del 1 de septiembre de 2026 obtuvo 50 observaciones
históricas para los 38 países, con SHA-256 de salida
`11db1d92534519201fbe13028985993020119d57e751792a3ce32b588e06ff9e` y SHA-256
del recurso original `7fb1951fb99955a1481c1347f27444ca56935be112d69794d93fe3fc079bca21`.
Los puntos de control son Colombia 2023 (26,16919518 %) y Estados Unidos 2024
(5,754378796 %). Ambos permanecen `conditional` y `score_eligible = false`.
