# ADR 0038: Canadá no se incorpora al insumo administrativo con CCOFOG agregado

- **Estado:** resuelto; candidata rechazada
- **Fecha:** 2026-09-04

## Contexto

El faltante canadiense del insumo `ADM-IN-02` impide que administración complete
la ventana común 2019–2021. El contrato vigente requiere el gasto operativo de
servicios públicos generales: compensación de empleados (`D1`) más consumo
intermedio (`P2`) en `S13/GF01`, normalizado por PIB y población.

Statistics Canada ofrece dos piezas oficiales y abiertas:

1. la [tabla 10-10-0024-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1010002401), que clasifica el gasto del gobierno general por función CCOFOG y componente de gobierno; y
2. su [guía del sistema canadiense de cuentas macroeconómicas](https://www150.statcan.gc.ca/n1/pub/13-606-g/2016001/article/14624-eng.htm), que distingue los componentes económicos del gasto —compensación de empleados y uso de bienes y servicios— de los gastos por función.

## Decisión

No incorporar Canadá usando el agregado CCOFOG de “servicios públicos
generales”. La fuente funcional no publica el cruce que permita seleccionar solo
`D1 + P2` dentro de `GF01`. Usar el total funcional mezclaría recursos
operativos con otras partidas, entre ellas intereses y transferencias, y cambiaría
el constructo del insumo.

## Consecuencias

- Administración conserva su cobertura vigente y la cohorte común permanece en
  24 de 30 países mínimos.
- No se modifica ningún puntaje, frontera, ranking ni elegibilidad de
  publicación.
- Una futura candidata solo podrá entrar si publica ese cruce, o si una revisión
  metodológica aprueba explícitamente un cambio de contrato y vuelve a validar
  todos los países afectados.
