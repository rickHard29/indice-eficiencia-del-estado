# ADR 0009: roles educativos PISA para acceso y equidad

- **Estado:** aceptada para panel de calidad; no habilita eficiencia ni publicación
- **Fecha:** 2026-08-25

## Contexto

La finalización de primaria de UNESCO UIS no cubre suficientemente OCDE-38: solo 25
países tienen observación y Estados Unidos no tiene dato. No puede funcionar como
rol comparable de acceso en esta versión.

PISA 2022 publica en un único libro oficial el `Coverage Index 3` (tabla I.B1.4.1) y
la brecha de rendimiento entre cuartiles socioeconómicos (tabla I.B1.4.3). Ambas
medidas usan la misma población de referencia de 15 años y permiten conservar las
cautelas de muestreo de la OCDE.

## Decisión

Se adopta `EDU-ACC-02` como proxy validada de acceso para PISA 2022 y se amplía
`EDU-EQ-01` desde el control bilateral al panel oficial automatizado. El libro XLSX
se descarga mediante su enlace permanente OCDE, se lee sin dependencias externas y
se guarda con hash y URL final en la procedencia.

El universo base sigue siendo OCDE-38. No se recorta para borrar faltantes: acceso
tiene una máscara de 37 países (sin Luxemburgo) y equidad una de 36 (sin Costa Rica
ni Luxemburgo). Los asteriscos de la OCDE se convierten en
`source:sampling_caution` y nunca se eliminan por defecto.

## Consecuencias

Educación dispone ahora de resultado, acceso y equidad en una intersección de 36
países. Ello permite describir perfiles de calidad/cobertura y preparar una futura
regla temporal explícita. No autoriza una frontera ni un IEE: el resultado es de
2020, PISA es de 2022 y el insumo educativo aún no es compatible para ajustar
recursos.
