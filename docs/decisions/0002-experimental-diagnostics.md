# ADR 0002: calcular diagnósticos sin publicar un IEE

- **Estado:** aceptada
- **Fecha:** 2026-08-24

## Contexto

El snapshot bilateral ya materializa seis indicadores elegibles y tres insumos de
contexto. Sin embargo, los insumos no son compatibles con el ajuste de eficiencia,
faltan roles obligatorios y dos países no bastan para estimar una frontera.

## Decisión

Implementar una versión `0.1-experimental` que pruebe selección temporal,
normalización, agregación, sensibilidad y procedencia. El motor debe fallar cerrado:

- `official_iee_score` siempre es nulo;
- publicación y ranking siempre están bloqueados;
- los insumos incompatibles solo se exportan como contexto;
- toda salida se etiqueta `experimental_only` y `not_efficiency_score`;
- el hash del snapshot debe coincidir con la configuración y el recibo de ingestión;
- el esquema, los países y el hash del catálogo del recibo deben coincidir con la
  configuración, y cada serie debe conservar unidad, fuente y código oficiales;
- las salidas relacionadas se publican juntas o no se publica ninguna.

## Consecuencias

La tubería se puede probar de extremo a extremo sin adelantar una conclusión
metodológica. Los números resultantes sirven para detectar decisiones sensibles,
pero no pueden citarse como IEE, eficiencia estatal, clasificación ni país ganador.

La siguiente versión exige universo multinacional, insumos compatibles, cobertura
completa y protocolo de incertidumbre antes de levantar los bloqueos.
