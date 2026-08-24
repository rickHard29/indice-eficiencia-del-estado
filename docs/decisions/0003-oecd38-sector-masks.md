# ADR 0003: congelar OCDE-38 y usar muestras por dimensión

- **Estado:** aceptada para la ingeniería v0.2
- **Fecha:** 2026-08-24

## Contexto

El piloto bilateral no permite estimar una frontera. Una intersección completa de
todos los indicadores tampoco es una solución: dentro de los 38 miembros de la
OCDE deja solo 29 países y selecciona la muestra en función de los faltantes.

## Decisión

La v0.2 congela como universo base los 38 miembros de la OCDE registrados el 24 de
agosto de 2026. Colombia y Estados Unidos pertenecen al mismo marco institucional y
las fuentes OCDE cubren una parte suficiente de sus pares.

La muestra de estimación se construirá por dimensión, nunca como una intersección
general:

- el universo base no se recorta por disponibilidad ni por desempeño;
- cada indicador exige su ventana completa, salvo una excepción metodológica
  versionada;
- los países ausentes se conservan en la máscara como no elegibles, no como ceros;
- cada dimensión debe conservar al menos 30 países elegibles;
- las observaciones con cautelas se retienen y se identifican;
- la imputación no puede hacer que una muestra pase el umbral de publicación.

La expansión a los ocho candidatos de adhesión se mantiene únicamente como
sensibilidad. No puede sustituir el universo base sin validar fuentes, insumos y
comparabilidad institucional para cada candidato.

## Consecuencias

Salud, educación, seguridad y administración pueden superar individualmente el
umbral numérico con varias series existentes. Eso no habilita un IEE: siguen
faltando roles obligatorios, insumos compatibles y un protocolo de frontera con
incertidumbre.

Los resultados v0.2 deberán describirse como comparaciones relativas al marco
OCDE, no como una frontera global. Cualquier dimensión que caiga por debajo de 30
países permanecerá bloqueada aunque las demás sí alcancen el mínimo.

La configuración ejecutable está en
[`config/country_universe_v0.2.toml`](../../config/country_universe_v0.2.toml).
