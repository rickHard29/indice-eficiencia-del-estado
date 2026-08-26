# ADR 0011: cribado de equidad en salud v0.7

- **Estado:** rechazada para el panel OCDE actual; conservar como candidata en reserva
- **Fecha:** 2026-08-25

## Contexto

Salud contaba con un resultado y una medida de acceso, pero no con un indicador
de equidad. Se evaluó el indicador de dificultad financiera de la OMS conforme a
la definición revisada en 2025 del ODS 3.8.2. La fuente publica el porcentaje de
la población con gasto directo en salud superior al 40 % de su presupuesto
discrecional y permite desagregarlo por quintil de riqueza.

El contraste natural sería la diferencia `Q1 - Q5`, en puntos porcentuales,
entre el quintil con menor riqueza y el de mayor riqueza, usando únicamente pares
del mismo país y año. Colombia tiene un par en 2021 y Estados Unidos en 2023.

## Evidencia

La descarga oficial contiene los cinco quintiles para 32 de los 38 miembros de la
OCDE en al menos un año. Al imponer una observación no anterior a 2010 quedan 25
países; desde 2015 quedan 21; desde 2019, 16. Por tanto, ninguna ventana reciente
respeta la regla mínima de 30 países de la v0.2.

Las estimaciones proceden de encuestas de presupuestos o ingresos-gastos de los
hogares y sus años no están sincronizados. La propia OMS también advierte que una
persona que no utiliza servicios por barreras de acceso puede tener gasto cero;
ello puede subestimar la dificultad financiera medida por gasto directo.

## Decisión

No se materializa una serie `SAL-EQ-02`, no se amplía el panel de frontera y no
se cambia el umbral de cobertura para acomodar la fuente. La candidata permanece
documentada como reserva. Sus datos no deben convertirse en un ranking ni en un
puntaje de salud.

La candidata podrá reabrirse únicamente si una actualización ofrece al menos 30
pares Q1/Q5 dentro de una ventana temporal definida, incluye Colombia y Estados
Unidos y fija antes de puntuar la dirección/transformación de la brecha y el
tratamiento del sesgo por gasto cero.

## Fuentes

- [OMS: definición y limitaciones de dificultad financiera, ODS 3.8.2](https://www.who.int/data/gho/data/themes/topics/topic-details/GHO/financial-hardship-in-health-and-components-sdg-3.8.2-2025-definition)
- [OMS GHO: indicador por quintil de riqueza](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/financial-hardship-----of-population--by-consumption-or-income-quintile)
- [API GHO: observaciones de población](https://ghoapi.azureedge.net/api/FINANCIALHARDSHIP_PROPORTIONOFPOP)
