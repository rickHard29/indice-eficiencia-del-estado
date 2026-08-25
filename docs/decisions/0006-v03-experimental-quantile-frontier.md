# ADR 0006: frontera cuantílica experimental restringida

- **Estado:** aceptada para experimentación, no para publicación
- **Fecha:** 2026-08-24

## Contexto

El panel v0.3 tiene 34 pares completos en salud, 34 en educación, 29 en seguridad
y ninguno en administración. La metodología exige al menos 30 países por dimensión,
rendimientos decrecientes, sensibilidad e intervalos. Los insumos siguen siendo
proxies `conditional` y todavía no existen controles estructurales armonizados.

## Decisión

La v0.3 estima únicamente salud y educación con una regresión cuantílica lineal del
resultado normalizado sobre `log1p(insumo)`. La pendiente se restringe a ser no
negativa: una mayor disponibilidad de recursos no puede reducir el resultado
alcanzable. La frontera base usa el percentil 90 y las sensibilidades usan 85 y 95.
Para evitar cruces, las predicciones de sensibilidad se ordenan por cuantíl y se
anclan al p90; la estimación base nunca se modifica.

El ajuste minimiza exactamente la pérdida pinball mediante enumeración de los
vértices del problema de dos parámetros. Esta implementación no requiere una
dependencia estadística externa y aplica una regla de desempate determinista. Los
intervalos del 90 % se obtienen con 200 remuestras bootstrap y semilla congelada.

El valor experimental se calcula como:

```text
eficiencia experimental = min(100, 100 × resultado normalizado / frontera p90)
brecha de resultado = max(0, frontera p90 − resultado normalizado)
```

No se estima seguridad porque sus 29 pares no alcanzan el mínimo; administración
carece de resultado multinacional materializado. Colombia no recibe estimación de
educación porque su ventana 2019–2021 del insumo no está completa. Ninguno de estos
faltantes se imputa.

## Salvaguardas

- `official_iee_score` permanece nulo en todas las salidas;
- `official_frontier_eligible`, publicación y ranking permanecen falsos;
- cada resultado se etiqueta `resource_only_frontier` e `input_conditional`;
- una pendiente cero se marca `flat_frontier` y no se interpreta como prueba causal;
- los límites provisionales de mortalidad y homicidios conservan su advertencia;
- los hashes del panel, los gates y su procedencia deben coincidir antes de estimar;
- ante errores controlados, las cuatro salidas se restauran como conjunto; una
  interrupción abrupta puede dejar una generación mixta, que se detecta verificando
  el recibo y los hashes de salida antes de consumirla.

## Consecuencias

La v0.3 permite auditar el comportamiento de una frontera real sin presentar sus
números como un índice terminado. Para levantar los bloqueos se necesitan controles
estructurales, validación externa de las proxies de insumo, roles obligatorios,
pruebas con métodos alternativos y un protocolo de interpretación pública.
