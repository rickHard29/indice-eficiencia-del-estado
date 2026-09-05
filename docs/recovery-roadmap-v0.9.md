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
| 2. Resolver disponibilidad neozelandesa | Archivos crudos congelados **o** bloqueo de acceso documentado | Hecho: la descarga completa ya no es pública |
| 3. Resolver materialización sanitaria | Transformación por ICD/edad, pesos OCDE 2015 y salida determinista **o** indisponibilidad de los archivos crudos documentada | Hecho: Nueva Zelanda no ofrece la descarga pública necesaria; no se materializa ni adopta un sustituto |
| 4. Ejecutar puertas de validación | Pruebas de alcance, ventana, denominador, estándar y comparación externa sobre cada fuente evaluada | Hecho: las series OCDE incompletas y la alternativa Eurostat no superan la puerta de ventana/equivalencia |
| 5. Sincronizar revisión pública | Paquete de revisión y tablero actualizados con estado y procedencia | Hecho: corte común v1.0 y documentación de resoluciones integrados |

**Avance de la ruta v0.9: 5 de 5 hitos (100%).** Se completó el ciclo de
evaluación, no una ampliación artificial de la cobertura. El segundo y tercer
hitos resolvieron que Nueva Zelanda no puede reconstruirse con archivos crudos
públicos; el cuarto comprobó que las series publicadas para Alemania, Noruega y
Portugal no son intercambiables con el contrato vigente. El quinto deja ese
resultado y el corte común de 24 países en el paquete de revisión, sin
convertirlo en una puntuación o ranking.

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
