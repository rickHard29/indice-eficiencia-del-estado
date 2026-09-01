# ADR 0026: cribado de equidad territorial en seguridad y justicia v2.2

- **Estado:** candidata de equidad territorial; pendiente de adopción
- **Fecha:** 2026-09-01

## Contexto

El rol `SEG-EQ-01` requiere observar desigualdad territorial en seguridad y
justicia, no solamente el resultado nacional de homicidios. La revisión anterior
lo mantenía como `design_required` por falta de una serie internacional
armonizada que pudiera agregarse con una ponderación explícita por población.

## Hallazgo y protocolo candidato

La OCDE publica tasas anuales de homicidio intencional a nivel TL2 en su conjunto
*Safety -- Regions* y población TL2 en *Demography -- Regions*. Ambos conjuntos
son públicos, descargables y usan la misma geografía regional de la OCDE. Para el
corte común de 2021 se propone calcular, por país:

```text
brecha territorial = P90 ponderado por población(tasa regional de homicidios)
                      − P10 ponderado por población(tasa regional de homicidios)
```

La dirección es `lower`: una menor distancia entre las zonas que concentran el
10 % y el 90 % de la población indica mayor paridad territorial de seguridad.
La ponderación evita que departamentos o estados pequeños pesen igual que zonas
mucho más pobladas. Solo se incluiría un país con tres o más regiones TL2 y con
ambas observaciones en el mismo año; no se imputan faltantes.

El corte cubre exactamente 30 integrantes de la OCDE: Australia, Austria,
Bélgica, Canadá, Suiza, Chile, Colombia, Costa Rica, Chequia, Alemania,
Dinamarca, España, Finlandia, Francia, Reino Unido, Grecia, Hungría, Irlanda,
Italia, Japón, Corea, México, Países Bajos, Noruega, Polonia, Portugal,
República Eslovaca, Suecia, Türkiye y Estados Unidos. Se excluyen Estonia,
Islandia, Israel, Lituania, Luxemburgo, Letonia, Nueva Zelanda y Eslovenia.

Los puntos de control son 35,5 homicidios por 100.000 habitantes para Colombia y
6,1 para Estados Unidos. La medida describe dispersión territorial de la tasa,
no el nivel nacional de homicidios, acceso a justicia, percepción de seguridad ni
la eficacia de policía o tribunales.

## Decisión

Se registra `SEG-EQ-01` como candidata y se conserva el protocolo completo para
una posterior adopción. La decisión no materializa datos, no modifica el
catálogo ejecutable y no habilita puntaje, ranking, frontera ni IEE oficial.

## Consecuencias y resguardos

La fuente y las unidades son comparables, pero la cobertura queda exactamente en
el mínimo de 30 y las unidades TL2 tienen distinta extensión, población y función
administrativa entre países. Antes de adoptar hay que fijar en código el método
de cuantil ponderado, la máscara de ocho exclusiones y controles de regresión
para Colombia y Estados Unidos. Si la cobertura baja de 30 en una actualización,
el indicador deberá fallar cerrado y permanecer fuera de cualquier resultado.

Fuentes: [Safety -- Regions, OCDE](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.CFE.EDS&df%5Bds%5D=dsDisseminateFinalDMZ&df%5Bid%5D=DSD_REG_SOC%40DF_SAFETY&df%5Bvs%5D=2.2), [Demography -- Regions, OCDE](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.CFE.EDS&df%5Bds%5D=dsDisseminateFinalDMZ&df%5Bid%5D=DSD_REG_DEMO%40DF_DEMO&df%5Bvs%5D=2.4), [extracto de homicidios TL2](https://sdmx.oecd.org/public/rest/data/OECD.CFE.EDS,DSD_REG_SOC%40DF_SAFETY,/A.TL2...HOMIC...CS_10P5PS?startPeriod=2021&endPeriod=2021&dimensionAtObservation=AllDimensions&format=csvfile) y [extracto de población TL2](https://sdmx.oecd.org/public/rest/data/OECD.CFE.EDS,DSD_REG_DEMO%40DF_DEMO,/A.TL2...POP._T._T.PS?startPeriod=2021&endPeriod=2021&dimensionAtObservation=AllDimensions&format=csvfile).
