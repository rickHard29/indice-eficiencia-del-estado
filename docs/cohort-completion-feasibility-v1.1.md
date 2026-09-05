# Cribado de completitud de cohorte v1.1

**Estado:** evidencia de factibilidad; no adopta datos ni modifica la cohorte  
**Fecha:** 2026-09-05

## Propósito y regla de decisión

Este cribado prueba contratos alternativos aplicados a todo el universo
OCDE-38. No incorpora un país por excepción y no recalcula puntajes ni ranking.
Una ruta sólo puede pasar a diseño metodológico si cubre de forma reproducible
la misma ventana para todos los países que conservaría el nuevo contrato, y si
su definición puede defenderse como sustituto de la función que hoy cumple.

La cohorte común vigente continúa en **24 de 38** países y el mínimo
predeclarado es 30.

## Resultados de las tres rutas

| Ruta uniforme comprobada | Ventana | Cobertura observada | Comparación con el contrato actual | Decisión |
| --- | --- | ---: | --- | --- |
| Salud: esperanza de vida al nacer, total (`SP.DYN.LE00.IN`) | 2019–2021 | 38/38 | Correlación de Pearson -0,9683 con mortalidad evitable en los 34 países con ambas series | Candidata conceptual, no sustituto automático |
| Educación: gasto total por estudiante equivalente a tiempo completo, OCDE EAG C1.1 | 2019 | 36/38 | Añade Australia y Grecia, pero Costa Rica y Suiza quedan sin dato | Rechazada como reemplazo común |
| Seguridad: brecha por sexo en tasas de homicidio | 2019–2021 | 35/38 | Añade Israel y Letonia frente a la equidad territorial; Bélgica, Islandia y Luxemburgo siguen incompletos | Candidata de sensibilidad, no sustituto automático |

### Salud: cobertura suficiente, significado distinto

La extracción del Banco Mundial contiene los años 2019, 2020 y 2021 para los
38 países. El archivo de respuesta quedó identificado por SHA-256
`6404d372988d14e4491f03d92f03cd75e2b0af281d50d2daa1e980238dfdcfc7`.

La serie mide longevidad general al nacer; el contrato vigente mide mortalidad
evitable, con causas, edad y estandarización definidos. La alta relación
empírica en la superposición no hace los conceptos equivalentes. Esta ruta
podría recuperar Alemania, Noruega y Portugal, pero sólo después de una decisión
metodológica explícita que cambie el objeto de la dimensión de salud.

### Educación: no pasa la puerta de cobertura

La tabla C1.1 de *Education at a Glance 2022* reporta gasto por estudiante en
2019 para Australia y Grecia, pero marca como ausentes a Costa Rica y Suiza.
El PDF fuente tuvo SHA-256
`fa071d6e6cbfaede61696d1591e11b17dd59bd778a3e98bb0b01bdb3c7290976`.

Además de no mejorar la intersección, el candidato cambia el denominador de
gasto público respecto del PIB a gasto por estudiante. No se incorporará a la
cohorte ni se usará para rellenar Australia o Grecia.

### Seguridad: sólo sensibilidad declarada

La brecha de homicidios por sexo mantiene una ventana 2019–2021 para 35 países
y tiene trazabilidad separada en
[el cribado de seguridad v3](security-equity-v3-gender-screen.md). No mide
distribución territorial, así que no puede mezclarse con la equidad territorial
dentro de un mismo índice.

## Conclusión operativa

No existe todavía una combinación de los contratos alternativos probados que
eleve responsablemente la cohorte común a 30. La opción con cobertura total
(salud) exige una revisión de constructo; la ruta educativa falla cobertura y
la de seguridad es una sensibilidad de otro objeto de equidad.

El siguiente trabajo útil es una revisión metodológica abierta de la candidata
de salud. Debe decidir si la dimensión acepta longevidad general como un nuevo
contrato común, antes de producir un panel, una cohorte o un ranking nuevos.

## Fuentes públicas

- [Banco Mundial: esperanza de vida al nacer, total](https://data.worldbank.org/indicator/SP.DYN.LE00.IN)
- [OCDE: Education at a Glance 2022, tabla C1.1](https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/10/education-at-a-glance-2022_4aad242c/3197152b-en.pdf)
- [Banco Mundial: tasa de homicidios de víctimas mujeres](https://data.worldbank.org/indicator/VC.IHR.PSRC.FE.P5)
- [Banco Mundial: tasa de homicidios de víctimas hombres](https://data.worldbank.org/indicator/VC.IHR.PSRC.MA.P5)
