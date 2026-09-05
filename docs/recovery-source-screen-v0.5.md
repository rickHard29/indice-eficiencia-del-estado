# Cribado de fuentes de recuperación v0.5

**Estado:** control de admisibilidad; no recupera observaciones  
**Fecha:** 2026-09-03

El cribado revisó las seis candidaturas de primera ola contra la fuente oficial y
el contrato vigente. Ninguna se adopta por ahora: hacerlo reduciría la exigencia
de ventana completa, cambiaría el constructo o relajaría la regla territorial.

| País | Faltante | Resultado del cribado |
| --- | --- | --- |
| Australia | Gasto educativo 2019–2020 | No adoptado: 2019 es nulo. |
| Bélgica | Homicidios 2019–2021 | No adoptado: 2019 y 2020 son nulos. |
| Canadá | Proxy administrativo | No adoptado: la tabla pública CCOFOG no cruza función y componente económico; no aísla D1+P2 dentro de GF01. |
| Alemania | Mortalidad evitable 2019–2021 | No adoptado: 2021 no está disponible. |
| Grecia | Gasto educativo 2019–2020 | No adoptado: 2020 es nulo. |
| Islandia | Equidad territorial de seguridad | No adoptado: solo hay dos regiones TL2 y el contrato exige tres. |

El resultado es valioso aunque no incremente la cohorte: confirma que el
siguiente trabajo necesita fuentes alternativas genuinamente comparables o una
revisión metodológica explícita, no imputaciones ni sustituciones silenciosas.

`iee-recovery-source-screen` genera un recibo con cada decisión y conserva el
puntaje, el ranking y la elegibilidad de publicación en nulo.

La validación posterior de Canadá está documentada en el
[ADR 0038](decisions/0038-canada-administration-source-resolution.md): Statistics
Canada publica ambas clasificaciones, pero no su cruce público necesario para
reconstruir el insumo operacional sin incluir intereses, transferencias u otros
gastos ajenos al contrato.
