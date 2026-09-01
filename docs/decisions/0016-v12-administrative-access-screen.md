# ADR 0016: cribado de acceso administrativo v1.2

- **Estado:** rechazada como sustituto de acceso; retenida como referencia de participación
- **Fecha:** 2026-09-01

## Contexto

Tras materializar el resultado administrativo OSI en v1.1, faltaba un indicador
internacional armonizado para el bloque obligatorio de acceso, cobertura o
confiabilidad. Se evaluaron dos candidatos de gobierno digital.

## Decisión

El *E-Participation Index* (EPI) 2024 de Naciones Unidas no se incorpora como
`ADM-ACC-01`. Cubre los 38 miembros de la OCDE y ambos países de control —0,7397
para Colombia y 0,9452 para Estados Unidos—, pero sus componentes son
e-información, e-consulta y e-toma de decisiones. Mide la oferta de mecanismos
de participación ciudadana, no el acceso efectivo, tiempo o finalización de un
trámite administrativo.

El *Digital Government Index* (DGI) 2023 de la OCDE tampoco sustituye ese bloque:
mide madurez de políticas y capacidades institucionales. Además, la edición no
incluye a Estados Unidos, por lo que falla el requisito mínimo bilateral del
piloto.

## Razones

El marco del IEE reserva el segundo bloque para acceso, cobertura o confiabilidad
del servicio. Renombrar participación o capacidad institucional como acceso
introduciría un error de constructo y duplicaría parcialmente la evaluación de
oferta digital ya capturada por OSI.

## Consecuencias

Administración conserva solo el resultado `ADM-RES-01`; no alcanza los roles
obligatorios y permanece fuera de cualquier IEE oficial. La próxima búsqueda
debe exigir una medida multinacional observable de uso, finalización, tiempo de
respuesta o accesibilidad de transacciones públicas, con cobertura de Colombia,
Estados Unidos y al menos 30 países para una frontera experimental.

Fuentes: [apéndice técnico ONU, tabla 9](https://desapublications.un.org/sites/default/files/publications/2024-10/Technical%20Appendix%20%28Web%20version%29%2030102024.pdf) y [DGI 2023 de la OCDE](https://www.oecd.org/en/publications/2023-oecd-digital-government-index_1a89ed5e-en.html).
