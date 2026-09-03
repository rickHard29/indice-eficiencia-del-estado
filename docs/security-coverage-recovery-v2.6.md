# Recuperación de cobertura de seguridad v2.6

Este documento prioriza la siguiente búsqueda de datos para seguridad y justicia
a partir del diagnóstico v2.5. No incorpora indicadores, no cambia ventanas y no
autoriza una estimación de eficiencia.

## Evidencia del cuello de botella

La intersección actual contiene 26 países, cuatro menos que el mínimo de 30.
La revisión del snapshot del 2 de septiembre de 2026 separa los faltantes así:

| Falta | Países | Qué muestran los datos actuales |
|---|---|---|
| Resultado 2019–2021 | Bélgica | La serie de homicidios contiene 2021, pero no 2019 ni 2020. |
| Insumo 2019–2021 | Canadá, México, Nueva Zelanda, Türkiye | La extracción pública GF03 de la OCDE no contiene ninguna observación para esos países en 2019–2023. |
| Equidad territorial 2021 | Estonia, Islandia, Israel, Letonia, Lituania, Luxemburgo, Nueva Zelanda y Eslovenia | La fuente regional TL2 no cumple el contrato de `SEG-EQ-01`. |

Por eso no se trata de elegir otra ventana después de ver la muestra: cambiar
solo años no crea datos de insumo para los cuatro países ni una observación
regional de equidad para los ocho países.

## Rutas mínimas hacia 30 países

| Ruta | Recuperación necesaria | Riesgo metodológico |
|---|---|---|
| A | Bélgica en resultado + Canadá, México y Türkiye en insumo | Cambia o complementa dos fuentes, pero no el rol de equidad. |
| B | Cuatro de los ocho faltantes de equidad | Requiere una alternativa territorial comparable y puede cambiar el constructo. |
| C | Bélgica + uno de los tres insumos recuperables + dos coberturas de equidad | Mezcla tres cambios; exige la mayor disciplina de comparabilidad. |

Nueva Zelanda no aporta a la recuperación mínima mientras siga faltando tanto
equidad como insumo. No se considera una prioridad inicial.

## Protocolo de investigación sin costo

Cada fuente candidata debe ser pública, reutilizable y aportar datos descargables
para todos los países que promete. Antes de editar el catálogo debe superar, por
este orden:

1. Identidad: organismo productor, código de serie, definición, unidad y año.
2. Cobertura: países completos, observaciones por año y regla explícita para
   faltantes; sin estimación ni reemplazo silencioso.
3. Comparabilidad: misma función gubernamental para el insumo o misma geografía
   subnacional y denominador poblacional para equidad.
4. Reproducibilidad: URL estable, bytes originales, hash y adaptación verificable.
5. Decisión: cribado separado y prueba de regresión antes de que una candidata
   pueda sustituir o complementar una fuente vigente.

La investigación debe preservar `SEG-EQ-01`, `SEG-IN-02` y `SEG-RES-01` como
contratos históricos. Una alternativa recibe un identificador nuevo; no se
sobrescriben definiciones para elevar artificialmente la cobertura.

## Prioridad recomendada

Primero se debe cribar una alternativa pública para el **insumo de Canadá, México
y Türkiye** que mantenga la función COFOG/GF03 o una correspondencia funcional
documentada. Recuperar los tres, junto con una fuente verificable para el
resultado belga, elevaría la muestra a 30 sin rediseñar el indicador territorial.

En paralelo, se puede investigar cobertura territorial de equidad, pero solo
como candidata nueva: la falta de tres o más regiones TL2 suele reflejar tamaño
territorial o disponibilidad estadística, no un error que se pueda corregir con
la tasa nacional.

La siguiente acción es un cribado de fuentes oficiales gratuitas para la ruta A;
si ninguna conserva la definición, se registra el bloqueo y se pasa a la ruta B.
