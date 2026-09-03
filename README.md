# Índice de Eficiencia del Estado (IEE)

Proyecto para construir un índice internacional comparable y reproducible sobre la capacidad del Estado para transformar recursos públicos en resultados sociales e institucionales.

El IEE no premia automáticamente un Estado pequeño ni castiga uno grande: compara resultados con recursos, cobertura, calidad y contexto.

## Componentes

- Google Drive y Google Sheets: fuentes, datos de trabajo e inventario de indicadores.
- Google Docs: metodología viva y decisiones pendientes.
- GitHub: código, configuraciones, pruebas y control de versiones.

## Estructura

```text
config/          Parámetros metodológicos versionados
data/            Esquemas y muestras sintéticas; nunca datos restringidos
docs/            Metodología técnica y decisiones
src/iee/         Código del índice
tests/           Pruebas automatizadas
```

## Inicio rápido

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
iee-download
iee-score
```

## Estado

Versión metodológica `0.1-draft`. La estructura es funcional y ya cuenta con una
[evaluación reproducible de los 14 indicadores propuestos del piloto](docs/source-validation.md):
6 indicadores validados, 5 condicionales, 2 en reserva y 1 que requiere diseño.
Todavía no se ha calculado ni publicado un puntaje IEE.

La [canalización reproducible de datos](docs/data-pipeline.md) ya descarga y valida
7 series oficiales, incorpora 2 controles manuales versionados y deja 5 indicadores
explícitamente diferidos. Los datos reales y sus recibos permanecen fuera de Git.

El [diagnóstico experimental v0.1](docs/experimental-scoring-v0.1.md) ya prueba
normalización, agregación, sensibilidad y procedencia con el snapshot bilateral.
El sistema mantiene el IEE oficial nulo y bloquea publicación y ranking porque aún
faltan insumos compatibles, roles obligatorios y un universo multinacional.

La [v0.2 ya congela un universo de 38 miembros de la OCDE](docs/universe-v0.2.md)
y exige muestras separadas por dimensión. La ampliación permite auditar cobertura
multinacional sin seleccionar países por sus faltantes, pero todavía no levanta los
bloqueos metodológicos del IEE oficial.

También existe una [canalización v0.2 de insumos comparables](docs/input-proxies-v0.2.md)
que convierte las cuatro funciones a PPA constante de 2021 por habitante. Las
series siguen siendo proxies condicionales hasta validar deflactores, vintages y
rezagos sectoriales.

La v0.3 ya inició con un [panel multinacional reproducible de resultados](docs/decisions/0005-v03-frontier-experimental-panel.md)
para los 38 países OCDE. Es la base de una futura frontera experimental por
dimensión; no habilita todavía un IEE, ranking ni publicación de eficiencia.

Sobre ese panel, la [frontera cuantílica experimental v0.3](docs/decisions/0006-v03-experimental-quantile-frontier.md)
estima únicamente las dimensiones que superan el mínimo de 30 pares completos,
con sensibilidad e intervalos reproducibles. Todos sus resultados continúan
marcados como experimentales y el IEE oficial permanece nulo.

La [v0.4 añade un panel de contexto estructural](docs/structural-controls-v0.4.md)
para probar controles demográficos y de concentración espacial. Es una base para
sensibilidades futuras, no un cambio automático de la frontera ni del IEE.

Las [sensibilidades de contexto v0.4](docs/context-sensitivity-v0.4.md) ya comparan
esos controles por separado contra la frontera experimental. Siguen bloqueadas para
publicación y sirven para detectar fragilidad de especificación.

La [v0.5 materializa los roles educativos](docs/education-roles-v0.5.md) de
resultado, acceso y equidad para OCDE-38, con máscaras explícitas para los faltantes
PISA y cautelas de muestreo por país. Es un panel de calidad/cobertura: por el
desfase 2020–2022 y la ausencia de un insumo educativo final, no habilita todavía
eficiencia, ranking ni IEE oficial.

La v0.6 añade un [puente reproducible de recursos educativos](docs/education-resource-bridge-v0.6.md):
35 pares entre aprendizaje 2020 y gasto aproximado 2019–2020, incluidos Colombia y
Estados Unidos. La proxy es condicional y el panel bloquea explícitamente cualquier
frontera o publicación de eficiencia.

La v0.8 añade una [alternativa directa de recursos sanitarios](docs/health-resources-v0.8.md):
gasto bajo esquemas gubernamentales u obligatorios, en PPA constante y con cobertura
OCDE-38. Sirve para contrastar la proxy sanitaria anterior; ambas definiciones siguen
siendo condicionales y toda frontera, ranking e IEE oficial permanecen bloqueados.

La v0.9 aplica ese mismo control a educación y encuentra una
[frontera plana](docs/education-frontier-v0.9.md) con el puente de gasto por
habitante. El resultado descarta interpretarla como eficiencia de recursos y
mantiene el insumo como contexto condicional.

La v1.0 añade una [sensibilidad temporal de seguridad y justicia](docs/security-frontier-v1.0.md):
alinea recursos y homicidios en 2019–2021 para recuperar 33 pares observados. Es
una prueba de cobertura y rezago; conserva el carácter condicional del insumo y no
habilita eficiencia oficial, ranking ni IEE.

La v1.6 incorpora un [subindicador condicional de carga regulatoria empresarial](docs/administration-access-v1.6.md)
para los 38 países OCDE. Mide tiempo de alta gerencia en requisitos estatales y
conserva explícitamente su población empresarial; no puntúa ni habilita el IEE.

La v1.9 incorpora una [brecha territorial condicional de identidad oficial](docs/administration-equity-v1.9.md)
para 34 países OCDE. Compara la cobertura rural y urbana de personas de 15 años o
más; mide un requisito de acceso y no habilita puntajes, ranking ni IEE.

La v2.3 incorpora una [brecha territorial condicional en seguridad y justicia](docs/security-equity-v2.3.md): P90–P10 de homicidios regionales TL2, ponderada
por población, para 30 países OCDE. La serie queda fuera de puntajes, ranking,
frontera e IEE oficial.

La v2.5 [integra los tres roles disponibles de seguridad](docs/security-role-integration-v2.5.md)
en una máscara de cobertura. La intersección alcanza 26 de 38 países, bajo el
mínimo de 30; por ello no se estima eficiencia ni se habilita frontera, ranking o IEE.
La [ruta v2.6 de recuperación de cobertura](docs/security-coverage-recovery-v2.6.md)
separa los faltantes por rol y exige fuentes públicas nuevas sin reemplazar los
contratos históricos ni rellenar datos.
El [cribado v2.7](docs/security-source-screen-v2.7.md) confirma que la ausencia
de cuatro países en el COFOG de la OCDE es estructural y deja solo dos candidatas
en verificación, sin adoptar datos nuevos.
El [cribado TL3 v2.8](docs/security-equity-tl3-screen-v2.8.md) encuentra tres
países adicionales en la fuente regional OCDE, pero los conserva como sensibilidad
porque mezclar niveles TL2 y TL3 cambiaría el constructo de equidad territorial.
La [v2.9 materializa esa sensibilidad](docs/security-equity-sensitivity-v2.9.md)
para 33 países con una máscara territorial explícita; la intersección de seguridad
sube a 29, pero mantiene bloqueados la frontera, los rankings y el IEE.

El [protocolo de lanzamiento del IEE v1](docs/iee-v1-launch-protocol.md) distingue
el tablero de trazabilidad, un corte experimental y un ranking oficial. Ningún
ranking podrá publicarse hasta cerrar las puertas de método, cobertura comparable,
roles completos, reproducibilidad, sensibilidades y revisión abierta.

La [validación canadiense v3.0](docs/security-canada-validation-v3.0.md) confirma
una fuente gratuita y trazable para recuperar el insumo faltante de Canadá. Es
una candidata aislada: su integración debe conservar los contratos históricos y
volver a comprobar la muestra antes de cualquier estimación.
La [materialización v3.1](docs/security-canada-materialization-v3.1.md) ya
produce las tres observaciones canadienses con recibos y pruebas; todavía no
cambia la puerta 29/30 hasta combinar ambas procedencias de forma explícita.
La [sensibilidad v3.2](docs/security-coverage-sensitivity-v3.2.md) realiza esa
combinación con procedencia por país y alcanza 30 países completos para seguridad;
permanece experimental y no habilita fronteras, rankings ni IEE oficial.

El [paquete de preparación experimental v0.2](docs/experimental-release-v0.2.md)
reúne las cuatro puertas experimentales que ya superan 30 países dentro del
universo OCDE-38. Conserva los contratos separados y publica hashes de sus puertas:
es un corte de evidencia reproducible, no una agregación, puntaje ni ranking.

## Principios

- Trazabilidad de las fuentes y transformaciones.
- Reproducibilidad de los cálculos.
- Separación entre datos originales, procesados y resultados.
- Comparación de resultados frente a recursos, no de resultados aislados.
- Análisis de sensibilidad antes de publicar rankings.
