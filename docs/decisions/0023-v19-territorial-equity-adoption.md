# ADR 0023: adopción condicional de equidad territorial administrativa v1.9

- **Estado:** aprobado como subindicador condicional; puntaje bloqueado
- **Fecha:** 2026-09-01

## Contexto

La [ADR 0022](0022-v18-administrative-territorial-equity-screen.md) identificó
una medida abierta y territorialmente desagregada para el rol de equidad de
administración. Mide la diferencia absoluta entre la cobertura de identidad
oficial rural y urbana para personas de 15 años o más. La pareja de series cubre
34 miembros del marco OCDE-38, incluidos Colombia y Estados Unidos.

## Decisión

Se adopta `ADM-EQ-03` como subindicador condicional de equidad territorial. El
contrato descarga las dos series de la API del Banco Mundial, exige la misma
pareja país-año y calcula:

```text
|cobertura urbana − cobertura rural|
```

La dirección es `lower`: una brecha menor implica mayor paridad territorial. La
máscara excluye de forma explícita Australia, Estonia, Luxemburgo y República
Eslovaca, sin imputarlas. Colombia tiene 1,367093 p.p. y Estados Unidos 7,452805
p.p. en 2024.

## Consecuencias

La fuente es pública, gratuita y reproducible. El contrato conserva los bytes
de ambas series y la procedencia de la transformación. `score_eligible = false`;
no se habilitan puntajes, ranking, frontera ni un IEE oficial.

La serie mide igualdad territorial de un requisito habilitante, no uso efectivo,
tiempo, terminación o calidad de los trámites. Su población de referencia es
personas de 15 años o más y no representa a empresas. Cualquier ampliación a
desigualdad municipal o a experiencia de servicio exige una fuente y una decisión
metodológica adicionales.

Fuentes: [catálogo ID4D](https://id4d.worldbank.org/global-dataset), [serie urbana](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/ID.OWN.TOTL.UR.ZS?format=json&date=2024&per_page=100) y [serie rural](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/ID.OWN.TOTL.RU.ZS?format=json&date=2024&per_page=100).
