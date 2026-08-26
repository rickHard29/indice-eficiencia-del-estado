# ADR 0014: sensibilidad temporal de seguridad y justicia v1.0

- **Estado:** aceptada solo como sensibilidad experimental
- **Fecha:** 2026-08-25

## Contexto

La configuración v0.3 combina homicidios 2021–2023 con recursos 2019–2021. Solo
29 países tienen ese par completo, menos del mínimo experimental de 30. Se evaluó
la ventana alternativa 2019–2021 para ambos componentes antes de estimar la
frontera; conserva 33 pares, incluidos Colombia y Estados Unidos.

## Decisión

Se materializa y estima la sensibilidad v1.0 con media 2019–2021, cuantil 0,90,
`log1p` y monotonicidad no decreciente. La ventana original 2021–2023 se conserva
sin cambios como referencia y no se sobrescribe ni se declara inválida.

La nueva estimación permanece experimental. No abre los gates de eficiencia,
publicación, ranking o IEE oficial.

## Razones

La alineación temporal elimina una causa conocida de pérdida de cobertura y supera
el umbral numérico. No basta para una conclusión: 2020–2021 contiene un choque
excepcional, GF03 no identifica únicamente policía y el insumo se deriva con el
deflactor general del PIB. Seguridad y justicia sigue sin un indicador de equidad
internacional armonizado.

## Consecuencias

La futura metodología debe comparar de forma predefinida ambas ventanas o justificar
un rezago sectorial, y no elegir según el perfil que favorezca a un país. Hasta que
eso ocurra, los perfiles v1.0 son solo diagnósticos reproducibles.
