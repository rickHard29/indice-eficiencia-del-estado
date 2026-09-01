# ADR 0024: recribado de acceso administrativo ciudadano v2.0

- **Estado:** sin fuente adoptable; `ADM-ACC-01` continúa requiriendo diseño
- **Fecha:** 2026-09-01

## Contexto

Tras completar el subindicador territorial `ADM-EQ-03`, se revisaron fuentes
abiertas recientes que pudieran medir el acceso o la experiencia de personas con
servicios administrativos, manteniendo la comparación Colombia--Estados Unidos
y una muestra OCDE de al menos 30 países.

## Decisión

No se identifica una fuente que cumpla simultáneamente el constructo, la
cobertura bilateral y la comparabilidad.

- La pregunta `con30g` de Global Findex sigue siendo una medida directa de uso
  reciente: acceder a servicios gubernamentales o buscar información
  gubernamental en línea. Pero no tiene una observación estadounidense y su
  cobertura OCDE es de cuatro países; no puede materializar `ADM-ACC-01`.
- El indicador ODS 16.6.2 sigue siendo la mejor medida armonizada de experiencia
  de servicio, pero el subindicador de servicios gubernamentales no cubre ni
  Colombia ni Estados Unidos.
- La *Serving Citizens Survey* de la OCDE 2024/2025 publica información sobre
  arreglos, objetivos y sistemas gubernamentales de medición. Es útil para
  describir capacidad de gestión, pero responde funcionarios y no mide tiempo,
  finalización o experiencia de usuarios. Tampoco ofrece el panel bilateral
  ciudadano que requiere el índice.

## Consecuencias

`ADM-ACC-01` se mantiene como `design_required`. No se mezclan encuestas
nacionales ni se convierte una encuesta a funcionarios, participación electrónica
o disponibilidad digital en una medida de acceso ciudadano. `ADM-ACC-02` sigue
siendo únicamente la carga regulatoria de empresas y no sustituye este rol.

La siguiente vía válida es diseñar un protocolo de comparación de trámites
específicos con fuentes abiertas de ambos países, definiendo previamente la
transacción, población, pasos, tiempo, costo, año y regla de agregación. Ese
protocolo será una serie nueva y no un reemplazo silencioso con proxies.

Fuentes: [Global Findex](https://www.worldbank.org/en/publication/globalfindex/download-data), [metadato ODS 16.6.2](https://unstats.un.org/sdgs/metadata/files/Metadata-16-06-02.pdf) y [OECD Government at a Glance 2025](https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/measurement-engagement-and-improvement-of-public-administrative-services_3b589a5f.html).
