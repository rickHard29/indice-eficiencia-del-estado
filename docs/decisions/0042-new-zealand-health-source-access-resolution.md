# ADR 0042: resolución de acceso a la fuente sanitaria neozelandesa

- **Estado:** cerrada sin adopción
- **Fecha:** 2026-09-05

## Verificación

La [herramienta oficial de mortalidad de Health New Zealand](https://tewhatuora.shinyapps.io/mortality-web-tool/)
confirma que los registros de 2019–2021 se consideran completos y explica que
hay clasificaciones ICD de tres caracteres en los conjuntos de datos. Al revisar
su sección de descargas, la propia herramienta informa que las opciones cambiaron
en julio de 2025 y que los datos que antes estaban disponibles deben solicitarse
al equipo de datos.

La interfaz permite descargar su diccionario ICD, pero no ofrece el archivo
completo necesario para cruzar causa, edad, sexo, año y denominador. Una tabla
visible o una tasa nacional estandarizada a la población mundial de la OMS no
pueden reemplazar esa base: `SAL-RES-01` exige recomputar con causas OCDE/Eurostat
y la población estándar OCDE de 2015.

## Decisión

Se descarta esta ruta como recuperación gratuita y automática. No se envía una
solicitud individual, porque el proyecto no presupone pagos por extracciones ni
puede afirmar que el resultado sería público, completo o reutilizable.

La ruta solo se reabre si Health New Zealand publica directamente los archivos
requeridos bajo una licencia reutilizable o si otra fuente pública demuestra la
misma cobertura, causas, edades y estándar de población.

## Consecuencias

- Nueva Zelanda permanece ausente para `SAL-RES-01` y no cambia la cohorte común.
- Se conserva el criterio de no sustituir definiciones incompatibles.
- El cierre libera la prioridad para rutas cuya evidencia pueda recuperarse sin
  costo y con trazabilidad completa.
