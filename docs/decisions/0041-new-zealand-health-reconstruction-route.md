# ADR 0041: ruta de reconstrucción para la mortalidad evitable de Nueva Zelanda

- **Estado:** candidata de investigación; no adoptada
- **Fecha:** 2026-09-04

## Contexto

Nueva Zelanda no completa `SAL-RES-01` en 2019–2021. La
[herramienta de mortalidad de Health New Zealand](https://www.tewhatuora.govt.nz/for-health-professionals/data-and-statistics/mortality/data-web-tool)
publica causas de defunción y desagregaciones demográficas, pero sus tasas se
estandarizan a la población mundial de la OMS. Además, la observación de 2021 se
señala como provisional.

El contrato OCDE usa causas prevenibles y tratables en menores de 75 años y tasas
estandarizadas a la población OCDE de 2015. La
[metodología de la OCDE](https://stats.oecd.org/wbos/fileview2.aspx?IDFile=41dfcc30-110a-4b7a-ac94-d6b8874e27cd)
publica ambos requisitos.

## Decisión

No copiar la tasa nacional publicada: su población estándar no es la misma. Se
abre una única ruta admisible, aún no materializada:

1. extraer defunciones nacionales por edad, sexo y causa ICD-10 para 2019–2021;
2. aplicar la lista conjunta OCDE/Eurostat de causas prevenibles y tratables;
3. recalcular la tasa con los pesos de población OCDE 2015;
4. conservar el estado provisional de 2021 y comprobar los resultados frente a la
   serie OCDE cuando ésta vuelva a publicar Nueva Zelanda.

## Consecuencias

- Nueva Zelanda no se incorpora todavía al panel de salud ni a la cohorte común.
- La ruta no requiere fuentes pagas, pero sí una extracción reproducible y una
  validación de equivalencia antes de cualquier integración.
- Si falla cualquiera de los cuatro controles, las observaciones se descartan y
  permanecen explícitamente ausentes.
