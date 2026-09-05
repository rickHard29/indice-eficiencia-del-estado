# Ruta de recuperación verificable v0.9

**Estado:** activa  
**Corte inicial:** 2026-09-05  
**Alcance:** recuperación de evidencia y cálculos candidatos; no habilita un
ranking ni modifica la cohorte común sin validación independiente.

## Meta

Convertir las ausencias prioritarias en decisiones auditables. Cada ruta debe
terminar en uno de estos estados explícitos:

1. candidato reproducible, con fuente congelada, transformación verificable y
   controles de equivalencia pendientes o superados;
2. fuente rechazada, con una razón comprobable de incompatibilidad de concepto,
   universo, ventana o unidad; o
3. ruta aún abierta, con la evidencia faltante y el siguiente paso definidos.

La primera implementación concreta es `SAL-RES-01` para Nueva Zelanda. Sus
datos de defunciones y población son públicos, pero la tasa nacional usa una
población estándar distinta de la exigida por la OCDE; por eso se reconstruirá
desde conteos, causas ICD-10 y denominadores, sin copiar la tasa publicada.

## Hitos verificables

| Hito | Evidencia de cierre | Estado inicial |
| --- | --- | --- |
| 1. Priorizar y cualificar rutas | Contratos, fuentes y criterios de admisibilidad documentados | Hecho |
| 2. Congelar evidencia neozelandesa | Archivos crudos, fecha, URL, licencia y SHA-256 registrados | Pendiente |
| 3. Materializar candidato sanitario | Transformación por ICD/edad, pesos OCDE 2015 y salida determinista | Pendiente |
| 4. Ejecutar puertas de validación | Pruebas de alcance, ventana, denominador, estándar y comparación externa | Pendiente |
| 5. Sincronizar revisión pública | Paquete de revisión y tablero actualizados con estado y procedencia | Pendiente |

**Avance de la ruta v0.9: 1 de 5 hitos (20%).** El primer hito cuenta solamente
la definición reproducible de la ruta, no la recuperación de ningún dato.

## Puertas obligatorias para adoptar una observación

Un candidato no entra al panel, a la cohorte común ni a una puntuación hasta que
demuestre simultáneamente:

- cobertura de 2019, 2020 y 2021;
- causas prevenibles y tratables bajo la lista conjunta OCDE/Eurostat;
- población menor de 75 años y denominadores coherentes;
- estandarización con la población total OCDE de 2015;
- trazabilidad de archivos, transformaciones, pruebas y resultado; y
- revisión metodológica registrada.

Una falla deja el valor como ausente. No se imputan datos ni se sustituye una
tasa con definición diferente.

## Resultado esperado

Al terminar v0.9 habrá más evidencia utilizable y una explicación comprobable
para cada ruta prioritaria; podría aumentar la cobertura, pero no se fija ni se
promete ese resultado. El ranking oficial seguirá bloqueado mientras la cohorte
común no alcance el mínimo predeclarado de 30 países y se cumplan las demás
puertas de método.

## Referencias de la primera ruta

- [Herramienta de mortalidad de Health New Zealand](https://www.tewhatuora.govt.nz/for-health-professionals/data-and-statistics/mortality/data-web-tool)
- [Metodología OCDE de mortalidad evitable](https://stats.oecd.org/wbos/fileview2.aspx?IDFile=41dfcc30-110a-4b7a-ac94-d6b8874e27cd)
- [Lista conjunta OCDE/Eurostat de causas evitables](https://www.oecd.org/content/dam/oecd/en/data/datasets/oecd-health-statistics/avoidable-mortality-2019-joint-oecd-eurostat-list-preventable-treatable-causes-of-death.pdf)
