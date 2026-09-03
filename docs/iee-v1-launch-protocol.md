# Protocolo de lanzamiento del IEE v1

**Estado:** propuesta operativa; no habilita un ranking  
**Fecha:** 2026-09-03

## Propósito

Este protocolo separa tres productos que no deben confundirse:

1. **Tablero público de trazabilidad:** evidencia, cobertura, decisiones y
   bloqueos del proyecto.
2. **Corte experimental:** resultados reproducibles con advertencias, sin
   presentarse como ranking oficial.
3. **IEE v1 oficial:** publicación estable del proyecto, con metodología,
   evidencia y controles completos.

“Oficial” significa oficial dentro del proyecto IEE. No implica aprobación,
representación o certificación de ningún gobierno, organismo internacional o
fuente de datos.

## Reglas de publicación

El tablero puede publicarse mientras muestre claramente que:

- no existen puntajes IEE oficiales;
- una evidencia por dimensión no equivale a un puntaje general;
- las sensibilidades TL2/TL3 permanecen separadas del contrato base;
- cada afirmación de cobertura identifica su universo, corte y limitación.

Un corte experimental solo podrá difundirse cuando se publique junto con el
hash de sus entradas, el código, el universo de comparación, sus exclusiones y
un aviso visible de que no es un ranking oficial.

## Puertas del IEE v1 oficial

El ranking oficial queda bloqueado hasta cumplir todas las puertas siguientes.

| Puerta | Evidencia exigida | Estado al 2026-09-03 |
| --- | --- | --- |
| Método congelado | Especificación v1, pesos, normalización y reglas de imputación versionadas | Pendiente |
| Cohorte comparable | Mismo universo y al menos 30 países elegibles por cada componente incluido | En curso |
| Roles completos | Recursos, resultados, acceso/equidad y contexto documentados para cada dimensión incluida | En curso |
| Reproducibilidad | Recibos de fuentes, hashes, pruebas y ejecución repetible del corte | Parcialmente listo |
| Sensibilidades separadas | Resultados TL2/TL3 y otras alternativas reportados sin alterar el resultado base | Listo para seguridad |
| Revisión abierta | Ventana pública para comentarios metodológicos y registro de respuestas | Pendiente |
| Paquete de publicación | Metodología, datos permitidos, limitaciones y glosario publicados en una versión etiquetada | Pendiente |

Una puerta fallida bloquea el ranking. No se compensa una falta de cobertura con
un indicador atractivo, una visualización convincente o un mayor número de
pruebas automatizadas.

## Orden de trabajo

1. Completar la cobertura común de las dimensiones y documentar los faltantes.
2. Congelar el contrato metodológico v1 antes de mirar posiciones agregadas.
3. Generar un corte experimental reproducible y separar cada sensibilidad.
4. Abrir una revisión metodológica sin costo mediante el repositorio público.
5. Corregir o documentar las observaciones, etiquetar la versión y, solo
   entonces, evaluar la publicación del IEE v1 oficial.

## Regla de comunicación

Hasta que todas las puertas estén cerradas, se usará la expresión
**“tablero de trazabilidad”** o **“corte experimental”**. Se evitarán frases
como “mejor Estado”, “peor Estado”, “puesto” o “ranking IEE” para los resultados
en desarrollo.
