# Validación de la candidata canadiense de seguridad v3.0

**Estado:** candidata verificada; aún no integrada  
**Fecha de consulta:** 2026-09-03

## Propósito

Esta revisión verifica que Canadá puede aportar un insumo de seguridad y justicia
compatible con la definición funcional usada en el IEE. No cambia el contrato
base SEG-IN-02, no altera la muestra v2.9 y no habilita una frontera ni un
ranking.

## Fuente primaria

Statistics Canada publica la tabla abierta
[10-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1010000501):
*Consolidated Canadian general government, expenses by function*. Se seleccionó
la fila:

- componente: Consolidated Canadian general government;
- CCOFOG: Public order and safety [703];
- unidad: dólares canadienses;
- escala: millones;
- vector: v107022154.

La clasificación canadiense define CCOFOG 703 como orden público y seguridad e
incluye policía, bomberos, tribunales, prisiones, I+D y funciones no clasificadas
en otra parte. Es la correspondencia funcional más próxima a GF03 de la OCDE.

| Año | Valor nominal (millones CAD) |
| ---: | ---: |
| 2019 | 40.517 |
| 2020 | 40.543 |
| 2021 | 44.958 |

El archivo descargado de la tabla tuvo SHA-256
0ef8b51bdd71944a6539f6bd25026d81581ba5c8586b347b2ba537794e9389ca.

## Conversión propuesta

Para mantener la unidad del insumo vigente se usará, por cada año:

\[
\frac{\text{CCOFOG 703 en CAD}}{\text{PIB nominal canadiense en CAD}}
\times \text{PIB por habitante PPA constante 2021}.
\]

Los denominadores propuestos son dos series públicas del Banco Mundial:
[PIB en moneda local corriente](https://api.worldbank.org/v2/country/CAN/indicator/NY.GDP.MKTP.CN?format=json&date=2019%3A2021&per_page=100)
y [PIB por habitante PPA constante de 2021](https://api.worldbank.org/v2/country/CAN/indicator/NY.GDP.PCAP.PP.KD?format=json&date=2019%3A2021&per_page=100).

Con el corte consultado, la transformación arroja aproximadamente 1.008,5;
987,6; y 1.010,5 dólares internacionales constantes por habitante para 2019,
2020 y 2021, respectivamente. Son resultados de validación; no se incorporan
aún como observaciones IEE.

## Decisión

La fuente supera identidad, cobertura temporal y correspondencia funcional como
**candidata condicionada**. La siguiente iteración deberá crear un identificador
de complemento propio, guardar los tres recursos y sus recibos, probar la
conversión y volver a calcular la máscara de seguridad con SEG-EQ-02.

Si ese complemento se reproduce sin cambiar contratos históricos, Canadá llevaría
la intersección de la sensibilidad de seguridad de 29 a 30 países. Aun así, el
resultado seguiría siendo experimental: la mezcla territorial TL2/TL3 y el
insumo condicional impiden llamar al resultado ranking oficial.
