# ADR 0041: ruta de reconstrucción para la mortalidad evitable de Nueva Zelanda

- **Estado:** lista para materialización; no adoptada
- **Fecha:** 2026-09-04

## Contexto

Nueva Zelanda no completa `SAL-RES-01` en 2019–2021. La
[herramienta de mortalidad de Health New Zealand](https://www.tewhatuora.govt.nz/for-health-professionals/data-and-statistics/mortality/data-web-tool)
publica causas de defunción y desagregaciones demográficas, pero sus tasas se
estandarizan a la población mundial de la OMS. La actualización oficial de marzo
de 2026 declara completos los datos de 2019–2021 y ofrece descargas con códigos
ICD, grupos de edad, sexo y denominadores de población.

El contrato OCDE usa causas prevenibles y tratables en menores de 75 años y tasas
estandarizadas a la población OCDE de 2015. La
[metodología de la OCDE](https://stats.oecd.org/wbos/fileview2.aspx?IDFile=41dfcc30-110a-4b7a-ac94-d6b8874e27cd)
publica ambos requisitos.

## Decisión

No copiar la tasa nacional publicada: su población estándar no es la misma. Se
abre una única ruta admisible, aún no materializada:

1. congelar la descarga oficial de defunciones por edad, sexo y causa ICD-10 para
   2019–2021, junto con su archivo de población;
2. aplicar la lista conjunta OCDE/Eurostat de causas prevenibles y tratables;
3. recalcular la tasa con los pesos de población OCDE 2015;
4. conservar el estado provisional de 2021 y comprobar los resultados frente a la
   serie OCDE cuando ésta vuelva a publicar Nueva Zelanda.

## Consecuencias

- Nueva Zelanda no se incorpora todavía al panel de salud ni a la cohorte común.
- La ruta no requiere fuentes pagas y ya tiene datos públicos suficientes para
  implementación; sigue requiriendo extracción reproducible y validación de
  equivalencia antes de cualquier integración.
- Si falla cualquiera de los cuatro controles, las observaciones se descartan y
  permanecen explícitamente ausentes.
