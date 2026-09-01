# ADR 0022: cribado de equidad territorial administrativa v1.8

- **Estado:** candidata de equidad territorial; pendiente de adopción
- **Fecha:** 2026-09-01

## Contexto

El marco metodológico requiere que el rol de equidad administrativa observe una
desigualdad territorial o socioeconómica. La candidata previa `ADM-EQ-02` mide
paridad por sexo de un requisito de acceso y, por tanto, no debe sustituir sin
más la noción territorial original. Se requiere una serie abierta, bilateral y
con al menos 30 observaciones del marco OCDE-38.

## Decisión

Se evaluó nuevamente ID4D--Global Findex 2025 del Banco Mundial, esta vez con
los indicadores `ID.OWN.TOTL.RU.ZS` e `ID.OWN.TOTL.UR.ZS`. Informan el
porcentaje de población de 15 años o más con identidad oficial, respectivamente
en zonas rurales y urbanas. Se propone como candidata `ADM-EQ-03` la diferencia
absoluta en puntos porcentuales:

```text
brecha territorial de identidad = |cobertura urbana − cobertura rural|
```

Una menor brecha significa mayor paridad territorial del requisito de identidad.
En 2024 Colombia registra 97,536758 % rural y 98,903851 % urbana: una brecha de
1,367093 p.p. Estados Unidos registra 86,129917 % rural y 93,582721 % urbana:
una brecha de 7,452805 p.p. La pareja de series cubre 34 de los 38 miembros de
la OCDE; faltan Australia, Estonia, Luxemburgo y República Eslovaca. Cumple el
mínimo técnico de 30 observaciones.

## Consecuencias

La candidata preserva el sentido territorial previsto para el rol de equidad y
usa una fuente pública, gratuita y reproducible. Mide un requisito para acceder
a servicios, beneficios y transacciones; no mide la finalización, el tiempo ni
la calidad del trámite. Tampoco sustituye la atención de desigualdades entre
municipios ni otros factores territoriales más finos.

La identidad oficial presenta niveles altos en buena parte del marco, por lo que
la brecha puede saturarse. Antes de incorporarla al catálogo debe decidirse su
rol exacto y materializarse un contrato que calcule la diferencia absoluta,
mantenga la máscara de 34 países y bloquee puntajes y frontera hasta validar el
panel. Esta ADR no activa ningún puntaje ni ranking.

Fuentes: [catálogo ID4D](https://datacatalog.worldbank.org/search/dataset/0040787/identification-for-development-id4d-global-dataset), [API rural](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/ID.OWN.TOTL.RU.ZS?format=json&date=2024&per_page=100) y [API urbana](https://api.worldbank.org/v2/country/COL%3BUSA/indicator/ID.OWN.TOTL.UR.ZS?format=json&date=2024&per_page=100).
