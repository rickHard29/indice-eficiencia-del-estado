# Sensibilidad temporal de seguridad y justicia v1.0

Corte de ejecución: **25 de agosto de 2026**.

La v1.0 prueba una sola alternativa temporal al panel de seguridad v0.3. La
ventana original de homicidios 2021–2023 conserva 29 pares y queda bajo el mínimo
de 30. Esta sensibilidad alinea resultado e insumo en 2019–2021; no reemplaza la
ventana original.

## Contrato

| Elemento | Regla |
|---|---|
| Resultado | `SEG-RES-01`, homicidios intencionales, media 2019–2021 |
| Recurso | `SEG-IN-02`, GF03 como proporción del PIB × PIB pc PPA constante, media 2019–2021 |
| Muestra | 33 de 38 países OCDE; faltan Bélgica, Canadá, México, Nueva Zelanda y Turquía |
| Modelo | Frontera cuantílica lineal monótona, cuantil 0,90, `log1p` del recurso y resultado |
| Resultado oficial | Nulo; publicación y ranking bloqueados |

Colombia y Estados Unidos están incluidos. No hay imputación: cada país necesita
los tres años de ambas series para entrar en la muestra.

## Hallazgo

La ventana alineada alcanza el mínimo experimental y produce una pendiente positiva
de 0,5461. Sin embargo, no es una medida publicable de eficiencia. El recurso
`SEG-IN-02` sigue siendo condicional y agrupa policía, bomberos, tribunales y
prisiones; además deriva volumen con el deflactor general del PIB. La ventana
incluye los años 2020–2021, afectados por el choque pandémico.

El modelo genera 33 perfiles y 99 filas de sensibilidad. Sus números internos son
diagnósticos: Colombia y Estados Unidos, por ejemplo, no deben compararse como un
ranking porque aún faltan un rol de equidad, un insumo final y una prueba de
estabilidad frente a la ventana 2021–2023.

## Decisión de uso

La v1.0 demuestra que el bloqueo previo era principalmente de cobertura temporal,
no de ausencia total de datos. Mantiene ambos paneles: 2021–2023 como referencia
más reciente bloqueada por muestra, y 2019–2021 como sensibilidad alineada. Ninguno
habilita un IEE oficial ni permite reemplazar la ventana después de observar el
resultado.

La decisión se detalla en la [ADR 0014](decisions/0014-v10-security-temporal-sensitivity.md).
