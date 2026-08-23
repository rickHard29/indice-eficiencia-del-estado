# Metodología del Índice de Eficiencia del Estado

Versión `0.1-draft`.

## 1. Qué mide

El IEE mide la capacidad relativa de un Estado para convertir recursos públicos en resultados sociales y servicios de calidad, dadas condiciones estructurales comparables.

No mide el tamaño ideal del Estado, si un país gasta “mucho” o “poco”, el nivel de desarrollo por sí solo ni el efecto causal de una política específica. Un gasto alto no reduce mecánicamente el puntaje y un gasto bajo no lo aumenta.

## 2. Unidad de análisis

- País-año, usando gobierno general consolidado para evitar doble conteo.
- Recursos monetarios en PPA constante por habitante o población objetivo.
- Promedios móviles de tres años cuando la volatilidad lo justifique.
- Rezagos entre insumos y resultados definidos por sector.
- Comparación principal mediante una frontera global condicionada.

## 3. Dimensiones

El marco completo propone seis dimensiones:

1. Salud.
2. Educación.
3. Seguridad y justicia.
4. Protección social.
5. Infraestructura y servicios básicos.
6. Administración, recaudo y compras públicas.

El piloto comenzará con salud, educación, seguridad y justicia, y administración, sujetas a cobertura suficiente. Cada dimensión combina resultados finales, acceso o confiabilidad y equidad. Los indicadores de percepción nunca serán el único resultado de una dimensión.

## 4. Resultados y normalización

Todos los indicadores se orientan para que una puntuación mayor sea mejor y se llevan a una escala de 0 a 100 mediante límites técnicos fijos:

```text
puntaje = 100 × (valor − límite inferior) / (límite superior − límite inferior)
```

Los indicadores negativos invierten la escala. Los límites deben provenir de metas técnicas, compromisos internacionales o valores plausibles; no del mínimo y máximo de la muestra. Se congelan por un período definido para conservar comparabilidad temporal.

Composición provisional dentro de cada dimensión:

- 50 % calidad o resultado final.
- 25 % acceso, cobertura o confiabilidad.
- 25 % equidad territorial o socioeconómica.

Los bloques se combinan con media geométrica para limitar la compensación entre alta cobertura y mala calidad.

## 5. Insumos y contexto

Los insumos centrales son recursos efectivamente destinados a cada función: gasto consolidado en PPA por población objetivo, personal equivalente a tiempo completo y servicios del capital público cuando corresponda.

No se usarán cocientes simples resultado/gasto. El modelo considerará rendimientos decrecientes, rezagos, calidad y condiciones plausiblemente exógenas como estructura etaria, densidad, dispersión, geografía o desastres. Los recursos privados complementarios se controlarán para no atribuir al Estado resultados financiados por hogares.

Corrupción, calidad institucional, desigualdad actual o gasto/PIB no se usarán como controles si forman parte del desempeño que se quiere medir. El ingreso heredado se reservará para sensibilidad.

## 6. Frontera de eficiencia

Para cada dimensión se estimará una frontera condicional robusta, inicialmente el percentil 90 del resultado alcanzable con recursos y contexto comparables.

El puntaje sectorial será la cercanía a esa frontera, limitado a 100 para el índice. También se publicará la brecha en puntos de resultado. Se contrastará el modelo principal con percentiles 85 y 95, frontera estocástica y un método no paramétrico robusto.

## 7. Ponderación y agregación

Las dimensiones activas tendrán igual peso en la versión inicial. El puntaje general usará media geométrica ponderada. Como sensibilidad se publicarán media aritmética y pesos alternativos de ±25 %.

El IEE siempre se mostrará junto con:

1. Nivel de resultados.
2. Intensidad de recursos.
3. Eficiencia relativa.
4. Calidad y cobertura de datos.

Así, un país con pocos recursos y resultados igualmente bajos no se describirá como de alto desempeño, aunque esté cerca de su frontera condicionada.

## 8. Datos faltantes

- Nunca sustituir faltantes por cero.
- Interpolar solo brechas de hasta dos años y nunca sobre rupturas conocidas.
- Reponderar únicamente dentro del mismo bloque.
- Exigir al menos 75 % del peso previsto de una dimensión y representación de todos sus bloques obligatorios.
- Marcar como provisional cualquier índice con cobertura incompleta.
- Usar imputación múltiple solo para sensibilidad e intervalos, no para el puntaje principal.

## 9. Incertidumbre y validación

Se publicarán intervalos del 90 %, sensibilidad a pesos, rezagos, controles, límites y método de frontera. Cuando los intervalos se superpongan se usarán grupos de desempeño en lugar de rankings exactos.

Las validaciones incluirán observaciones extremas, estabilidad temporal, doble conteo, auditorías externas y comprobación de que el IEE no tenga una relación mecánica fuerte con gasto público/PIB o tamaño del empleo estatal.

## 10. Salvaguardas

- Es un índice relativo y condicionado, no causal.
- Un puntaje alto no implica que deba reducirse el gasto.
- Un puntaje bajo no demuestra corrupción ni identifica por sí solo desperdicio.
- Las comparaciones deben usar la misma versión, ventana temporal y cobertura.
- Los resultados nacionales pueden ocultar desigualdades territoriales.
- El índice no se publicará sin resultados, recursos y calidad de datos.

## 11. Decisiones abiertas

- Universo inicial de países.
- Indicadores y fuentes armonizadas por dimensión.
- Límites técnicos de normalización.
- Rezagos sectoriales.
- Frontera cuantílica frente a frontera estocástica.
- Controles estructurales mínimos.
- Umbrales definitivos de cobertura.
- Frontera fija o móvil en el tiempo.
- Tratamiento de sostenibilidad fiscal y ambiental.
- Publicación de ranking o únicamente grupos estadísticamente distinguibles.
