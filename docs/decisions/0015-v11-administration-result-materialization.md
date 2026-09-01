# ADR 0015: materialización administrativa v1.1

- **Estado:** aceptada solo como panel experimental
- **Fecha:** 2026-08-25

## Contexto

El piloto solo tenía dos controles manuales de *Online Service Index* (OSI),
Colombia y Estados Unidos. El resultado administrativo no podía incorporarse a
un panel multinacional, aunque la tabla oficial de la ONU contiene los 193
Estados Miembros.

## Decisión

Se materializa `ADM-RES-01` para los 38 miembros de la OCDE como control manual
versionado. La tabla se publica en PDF, por lo que se conserva la ruta de
adquisición `manual_control` en vez de fingir una descarga API. Cada dato queda
enlazado a la edición, URL y localizador de la tabla 7.

Se crea un panel experimental con OSI 2024 y el recurso condicional
`ADM-IN-02`, promedio 2019–2021. Sus 34 pares se pueden explorar técnicamente,
pero todos los gates oficiales continúan cerrados.

## Razones

El PDF oficial permite una transcripción verificable de una observación puntual
por país. El control de integridad mantiene los puntos ancla de Colombia y
Estados Unidos y la prueba no llama a la red. Aceptar manifiestos solo-manuales
es preferible a introducir una adquisición automática ficticia.

## Consecuencias

OSI refleja disponibilidad y calidad evaluada de servicios en línea; no mide
uso, conectividad efectiva, brecha territorial ni equidad. El insumo cubre
2019–2021 mientras el resultado es 2024, por lo que no se infiere causalidad
ni productividad. GF01 sigue siendo una proxy condicional y faltan roles de
acceso/equidad. La v1.1 no habilita IEE, publicación o ranking.
