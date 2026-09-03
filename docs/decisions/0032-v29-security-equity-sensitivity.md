# ADR 0032: sensibilidad mixta TL2/TL3 de seguridad v2.9

- **Estado:** materializada como sensibilidad condicional; contrato base intacto
- **Fecha:** 2026-09-03

## Contexto

La v2.8 identificó tres países con datos TL3 completos, pero no con datos TL2
suficientes. El usuario autorizó evaluar la extensión exclusivamente como una
sensibilidad separada.

## Decisión

Se crea `SEG-EQ-02` con 30 países TL2 y Estonia, Lituania y Eslovenia a nivel
TL3. El adaptador exige un nivel territorial explícito por país, parejas
homicidio--población del mismo año y al menos tres regiones. La serie se publica
con `score_eligible = false` y no sustituye a `SEG-EQ-01`.

## Consecuencias

La sensibilidad cubre 33 países de equidad pero eleva la intersección completa
solo a 29, porque Canadá aún carece de un insumo validado. Mezclar niveles puede
afectar la magnitud de las brechas, de modo que ni la nueva serie ni su cobertura
habilitan una frontera, ranking o IEE oficial.
