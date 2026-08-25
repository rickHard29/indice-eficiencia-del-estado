# ADR 0010: puente de recursos educativos v0.6

- **Estado:** aceptada como preparación condicional; eficiencia y publicación bloqueadas
- **Fecha:** 2026-08-25

## Contexto

Educación v0.5 ya tiene resultado, acceso y equidad, pero no un recurso sectorial
final con denominador por estudiante. La serie directa más adecuada de Education at
a Glance combina gasto de gobierno general, estudiante FTE y PPA constante; sin
embargo, su versión vigente no publica Colombia.

La proxy v0.2 `EDU-IN-02` combina la proporción UIS de gasto público educativo y
PIB per cápita PPA constante. Está disponible para Colombia y Estados Unidos, pero
su denominador es población total y usa el deflactor general del PIB.

## Decisión

Se rechaza la serie EAG como insumo principal por ausencia de Colombia, sin
imputarla ni sustituirla silenciosamente. Se materializa un panel puente con HCI
2020 y el promedio `EDU-IN-02` de 2019–2020. Esta ventana es anterior o
contemporánea al resultado y mantiene 35 pares OCDE, incluidos Colombia y Estados
Unidos.

El contrato declara `input_status_required = "conditional"`. Aunque el tamaño de
muestra excede 30, el panel solo sirve para auditar cobertura y sensibilidad de
recursos; no pasa a la estimación de frontera.

## Consecuencias

El proyecto conserva una ruta reproducible de preparación mientras busca una fuente
por estudiante que incluya Colombia o una justificación metodológica para usar un
denominador poblacional. Acceso/equidad PISA 2022 siguen separados hasta decidir el
tratamiento de desfases temporales. El IEE oficial y los rankings permanecen nulos.
