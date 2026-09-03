# ADR 0030: cribado de fuentes de recuperación de seguridad v2.7

- **Estado:** dos candidatas en verificación; ningún indicador adoptado
- **Fecha:** 2026-09-02

## Contexto

La ruta v2.6 requiere recuperar cuatro observaciones para alcanzar 30 países,
pero no permite sustituir gasto del gobierno general por presupuestos de alcance
menor. La OCDE confirma que su fuente COFOG no publica datos para Canadá, México,
Nueva Zelanda y Türkiye.

## Decisión

Se conserva la fuente OCDE como contrato vigente. La prueba de Eurostat se
descarta porque Bélgica no tiene víctimas de homicidio en los tres años; no se
sustituye por otras categorías jurídicas. Statistics Canada sí publica el
agregado CCOFOG de gobierno general canadiense y queda como única candidata en
verificación de conversión a PPA constante. Las referencias de México y Türkiye
no superan el control de alcance y quedan fuera de materialización.

## Consecuencias

La v2.5 permanece con 26 países. La ruta A no puede llegar al mínimo por sí sola
con la evidencia actual. Ninguna candidata genera puntaje, frontera, ranking ni
IEE; solo una extracción reproducible, la comparación de definiciones y pruebas
de regresión podrían justificar una nueva decisión de adopción.
