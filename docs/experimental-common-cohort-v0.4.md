# Cohorte común exploratoria v0.4: 24 países

**Estado:** habilita análisis experimental de cohorte; no habilita IEE oficial
ni ranking oficial.  
**Fecha:** 2026-09-05

## Decisión de alcance

La v0.4 crea un contrato **nuevo y separado** para trabajar con los 24 países
que tienen evidencia completa en las cuatro dimensiones. No modifica el mínimo
predeclarado de 30 de la metodología v1 ni reemplaza el corte v0.3. Así se evita
presentar una regla posterior como si hubiera sido la regla original.

La cohorte exploratoria es: AUT, CHE, CHL, COL, CRI, CZE, DNK, ESP, EST, FIN,
FRA, GBR, HUN, IRL, ITA, JPN, KOR, LTU, NLD, POL, SVK, SVN, SWE y USA.

## Qué habilita

- Análisis descriptivo y de sensibilidad con exactamente estos 24 países.
- Comparación de cobertura entre las cuatro dimensiones bajo contratos ya
  documentados.
- Preparación de una futura visualización experimental con su advertencia de
  alcance.

## Qué permanece bloqueado

- Puntaje o ranking que se denomine IEE oficial.
- Cambiar la metodología v1 o declarar que el umbral vigente es 24.
- Incorporar observaciones condicionales, imputadas o de otro constructo.

El recibo de v0.4 mantiene `official_iee_score`, `ranking` y
`publication_eligible` vacíos o falsos. La única puerta que abre es la de
cohorte experimental: 24 miembros observados frente a mínimo 24.

## Reproducción

```bash
iee-experimental-cohort \
  --config config/experimental_cohort_v0.4.toml \
  --output data/processed/experimental_cohort_v0.4.json
```

## Relación con v1

El umbral de 30 sigue siendo la regla de preparación para una comparación
agregada de la metodología v1. La revisión pública conserva la tarea de decidir
si los contratos alternativos de salud, educación o seguridad son aceptables
para ampliar esa versión futura.
