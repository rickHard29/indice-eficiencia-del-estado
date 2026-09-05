# Ruta de completitud de cohorte v1.0

**Estado:** diseño metodológico pendiente; no adopta datos ni cambia la cohorte  
**Fecha:** 2026-09-05

## Punto de partida comprobado

La cohorte completa actual contiene 24 de los 38 países OCDE. Para alcanzar el
mínimo predeclarado de 30 hacen falta seis países que cuenten simultáneamente con
resultado, recurso y acceso o equidad en las cuatro dimensiones.

Las once ausencias con un único componente faltante ya fueron contrastadas con
fuentes gratuitas. Ninguna puede incorporarse como excepción nacional bajo el
contrato actual: faltan años, la unidad territorial es insuficiente, o la fuente
mide un constructo distinto. Este documento no reabre esas decisiones ni rellena
valores ausentes.

## Qué tendría que cambiar para llegar a 30

La única vía que conserva la comparabilidad es evaluar contratos alternativos
aplicados de forma uniforme a toda la cohorte, antes de incorporar a cualquier
país. Las tres líneas mínimas son:

| Línea | Países potencialmente recuperables | Requisito no negociable | Estado |
| --- | --- | --- | --- |
| Salud v2 | Alemania, Noruega y Portugal | Reconstruir o adoptar una única serie común para los 38 países, con lista de causas, edad y estandarización demostrablemente equivalentes | Pendiente de prueba de equivalencia |
| Educación v2 | Australia y Grecia | Recalibrar una fuente y una ventana comunes para los 38 países; no mezclar ejercicios fiscales nacionales con series calendario | Pendiente de diseño de ventana común |
| Equidad de seguridad v3 | Islandia, Israel, Luxemburgo o Letonia | Definir un indicador territorial alternativo que mida inequidad para todos los países; no reducir el mínimo regional ni asignar cero a países con una región | Sin candidata adoptable |

La primera línea podría ampliar Salud en tres países; la segunda, Educación en
dos. Aun así faltaría al menos una recuperación desde una definición de equidad
territorial común y válida. Por ello no es responsable prometer que la cohorte
alcanzará 30 solo por cambiar de fuente.

## Puertas del rediseño

Cada línea debe superar estas puertas antes de convertirse en un panel nuevo:

1. Cobertura completa y reproducible para los 38 países, o una máscara pública
   que documente toda ausencia.
2. Misma definición, unidad, población, frecuencia y ventana para todos los
   países incluidos.
3. Comparación de solapamiento contra la serie actual en los países con ambas
   fuentes; diferencias, rupturas y revisiones quedan publicadas.
4. Reejecución de los controles de roles y de la intersección común sin puntaje
   ni ranking.
5. Revisión metodológica independiente antes de sustituir el contrato vigente.

Una fuente que falle cualquiera de estas puertas queda como sensibilidad o se
rechaza. El corte vigente de 24 países se conserva intacto.

## Primer experimento propuesto: Salud v2

La lista conjunta de mortalidad evitable de la OCDE y Eurostat ofrece una base
conceptual para evaluar una serie común, pero no constituye por sí sola un puente
de valores. El experimento deberá descargar la misma variante para todos los
países disponibles, congelar la extracción y verificar:

- causas prevenibles y tratables incluidas;
- población menor de 75 años;
- método de estandarización;
- años 2019, 2020 y 2021; y
- comportamiento frente a la serie `SAL-RES-01` en los países con ambas.

Solo después de esa prueba se decidirá si existe un contrato `SAL-RES-02` común.
No se usarán los valores europeos exclusivamente para Alemania, Noruega o
Portugal.

## Actualización de cribado v1.1

El cribado uniforme posterior encontró cobertura 38/38 para esperanza de vida
al nacer del Banco Mundial en 2019–2021, pero la medida es longevidad general y
no mortalidad evitable. La correlación observada con el recurso vigente no
autoriza un reemplazo conceptual. El candidato educativo de OCDE de 2019 cubre
Australia y Grecia, pero pierde Costa Rica y Suiza; por tanto no mejora la
cohorte. La alternativa de seguridad por sexo añade Israel y Letonia, pero mide
otra forma de equidad. El detalle reproducible y las decisiones están en
[cribado de completitud v1.1](cohort-completion-feasibility-v1.1.md).

## Referencias públicas

- [Lista conjunta OCDE-Eurostat de causas prevenibles y tratables](https://www.oecd.org/content/dam/oecd/en/data/datasets/oecd-health-statistics/avoidable-mortality-2019-joint-oecd-eurostat-list-preventable-treatable-causes-of-death.pdf)
- [Metadatos Eurostat de causas de defunción](https://ec.europa.eu/eurostat/cache/metadata/en/hlth_cdeath_sims.htm)
- [Metadatos Eurostat de crimen y justicia](https://ec.europa.eu/eurostat/cache/metadata/en/crim_sims.htm)
