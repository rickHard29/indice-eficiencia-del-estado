# ADR 0025: protocolo candidato de acceso administrativo por pasaporte v2.1

- **Estado:** protocolo de diseño; sin indicador ni puntaje
- **Fecha:** 2026-09-01

## Contexto

`ADM-ACC-01` requiere una medida ciudadana de acceso a un trámite. La expedición
o renovación regular de pasaporte es una candidata útil porque es un servicio
nacional presente en Colombia y Estados Unidos, con información pública sobre
sus pasos y tiempos.

Sin embargo, las cifras publicadas no son equivalentes: Colombia informa entrega
en 24 horas hábiles en Bogotá y 48 horas en gobernaciones **después del pago**;
Estados Unidos informa un intervalo de procesamiento por agencias o centros,
que comienza una vez reciben la solicitud y excluye el correo. Ninguna cifra
incluye de forma equivalente la espera de cita, preparación documental y entrega
física. No se pueden restar ni puntuar como si fueran el mismo tiempo.

## Decisión

Se define un protocolo, no una serie. La futura comparación debe restringirse a
personas adultas, solicitud o renovación regular, trámite doméstico,
documentación completa, modalidad no expedita y un mismo año de observación.

La métrica admisible será el tiempo mediano desde que el solicitante puede
presentar la solicitud completa hasta que el documento está disponible para
recoger o es entregado, separado en cuatro componentes:

1. disponibilidad de cita o canal de presentación;
2. verificación y aceptación de requisitos;
3. producción y decisión administrativa;
4. entrega o disponibilidad final.

Cada componente deberá provenir de una estadística operativa oficial con fecha,
universo, percentil o media y definición publicada. Se informarán tiempo total,
componentes faltantes, costo obligatorio y proporción de solicitudes digitales
cuando estén disponibles. Una ausencia no se imputará como cero.

## Consecuencias

No se crea `ADM-ACC-03` ni se actualiza el catálogo. Las promesas de servicio
actuales sirven para localizar datos, no para comparar desempeño. Una futura
serie solo podrá entrar como condicional si ambos países publican el mismo
inicio, fin y estadístico de tiempo; para puntuar requerirá además cobertura
internacional compatible o una decisión explícita de análisis bilateral separado.

La declaración de renta se descarta como primera ruta: el IRS publica una carga
anual agregada de preparación y presentación, mientras que la información abierta
colombiana disponible describe volumen y canal de presentación, no una carga de
tiempo equivalente para personas naturales.

Fuentes: [Cancillería de Colombia](https://cancilleria.gov.co/atencion-y-servicio-al-ciudadano/tramites-y-servicios/pasaportes), [U.S. Department of State](https://travel.state.gov/en/passports/apply/help/processing-time.html) y [IRS, carga tributaria individual](https://www.irs.gov/privacy-disclosure/irs-privacy-policy).
