# ADR 0005: panel de resultados v0.3 antes de estimar una frontera

- **Estado:** aceptada
- **Fecha:** 2026-08-24

## Contexto

La v0.2 ya entrega insumos en PPA constante por habitante y un marco fijo de 38
miembros de la OCDE. Aún no existe un panel reproducible de resultados para ese
marco. Los roles de equidad de educación y los resultados administrativos de 38
países requieren una adquisición manual auditable; los roles obligatorios de
seguridad y administración siguen incompletos.

## Decisión

La primera entrega de v0.3 descarga y normaliza cuatro resultados con API oficial:

- mortalidad evitable (`SAL-RES-01`);
- cobertura sanitaria universal (`SAL-ACC-01`);
- aprendizaje armonizado (`EDU-RES-01`);
- homicidios intencionales (`SEG-RES-01`).

El manifiesto conserva los 38 miembros OCDE, incluso si una ventana posterior deja
un país fuera de la muestra de una dimensión. La descarga solo exige al menos una
observación histórica por país; la elegibilidad exige después la ventana completa
congelada. No se imputan ceros, no se mezclan vintages en silencio y no se generan
filas ficticias.

Los cuatro indicadores son resultados validados, pero el artefacto todavía no
estima eficiencia ni publica ranking. La frontera experimental solo se implementará
cuando pueda recibir, por dimensión, el resultado elegido, el insumo v0.2 y una
máscara de ventana explícita.

## Consecuencias

La v0.3 separa claramente tres estados:

1. datos descargados y auditables;
2. muestra suficiente para experimentar por dimensión;
3. dimensión habilitada para un IEE oficial.

El segundo estado no implica el tercero. Salud y educación seguirán bloqueadas por
roles obligatorios faltantes; seguridad y administración, además, por diseño de
roles. Los insumos v0.2 permanecen condicionales y no activan el IEE oficial.
