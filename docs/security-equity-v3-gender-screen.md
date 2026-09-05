# Cribado Seguridad v3: equidad por sexo en homicidios

**Estado:** candidata de sensibilidad; no adopta datos ni modifica la cohorte  
**Fecha:** 2026-09-05

## Propuesta evaluada

Evaluar una medida de equidad de seguridad basada en la disparidad por sexo entre
las tasas de víctimas de homicidio: media 2019–2021 de
`abs(log(tasa masculina / tasa femenina))`. Un valor menor representa menor
brecha relativa entre sexos. La fuente es la misma serie internacional
UNODC/Banco Mundial ya usada para el resultado de homicidios.

Esta medida es una alternativa de **equidad por sexo**; no es una medida de
equidad territorial y no puede reemplazarla sin revisión metodológica.

## Extracción reproducible

Se descargaron para los 38 países OCDE y 2019–2021:

- `VC.IHR.PSRC.FE.P5`, víctimas mujeres por 100.000 mujeres;
- `VC.IHR.PSRC.MA.P5`, víctimas hombres por 100.000 hombres.

Los archivos tienen SHA-256
`57c313ebbee42c2531d99b1f621d221ff8c5fa9e13cd2aade2675399f6afd4f2`
y `c8b39351702e11d2bb01d67f24ee2b76173220a6d49c75729e512f8e1f16629c`,
respectivamente.

## Resultado del cribado

- **35 de 38** países tienen ambas tasas en los tres años.
- Bélgica, Islandia y Luxemburgo siguen sin ventana completa.
- No hay valores cero o negativos entre las 35 observaciones completas, por lo
  que la transformación logarítmica no requiere imputación.
- La brecha media resultante está entre 0,110 y 2,494. Israel registra 1,708 y
  Letonia 0,363.

Al combinar esa cobertura con el resultado y el recurso de Seguridad v3.2, el
panel de seguridad pasaría de **30 a 32** países. Los dos países adicionales
serían Israel y Letonia.

## Decisión

No se adopta `SEG-EQ-03` todavía. Aunque su fuente es internacional, gratuita y
reproducible, cambiaría el objeto medido de dispersión territorial a disparidad
por sexo. Antes de cualquier integración se requiere:

1. revisión conceptual independiente de que la dimensión de equidad admita esta
   perspectiva;
2. prueba de sensibilidad contra la medida territorial donde ambas existan;
3. publicación de una máscara que no mezcle ambas medidas dentro del mismo
   indicador; y
4. nueva evaluación de la cohorte completa sin puntajes ni ranking.

## Referencias

- [Tasa de homicidios intencionales, hombres](https://data.worldbank.org/indicator/VC.IHR.PSRC.MA.P5)
- [Tasa de homicidios intencionales, mujeres](https://data.worldbank.org/indicator/VC.IHR.PSRC.FE.P5)
- [Portal de datos de homicidio UNODC](https://data.unodc.org/dp-intentional-homicide-victims)
