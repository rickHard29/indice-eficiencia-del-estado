# Recursos de salud v0.8

Corte de validación: **25 de agosto de 2026**.

La v0.8 incorpora `SAL-IN-03` como alternativa experimental al proxy `SAL-IN-02`.
Usa el flujo oficial de la OCDE de gasto sanitario y financiación bajo el Sistema de
Cuentas de Salud (SHA 2011): gasto (`EXP_HEALTH`) financiado por esquemas
gubernamentales u obligatorios (`HF1`), en dólares estadounidenses por persona PPA
constantes de 2020 (`USD_PPP_PS`, base de precios `Q`).

## Cobertura y puntos de control

La consulta congelada contiene los 38 miembros OCDE y los cinco años 2019–2023
para cada uno. No se imputa ningún año ni país.

| País | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---:|---:|---:|---:|---:|
| Colombia | 1.053,406 | 1.067,002 | 1.253,923 | 1.107,703 | 1.177,410 |
| Estados Unidos | 9.130,785 | 10.183,869 | 10.027,034 | 9.833,002 | 10.078,994 |

La serie resulta directamente comparable en volumen y evita usar el deflactor
general del PIB de `SAL-IN-02`. No se debe mezclar su base 2020 con la base 2021
del proxy anterior en una misma columna: cada alternativa mantiene su propia
unidad y procedencia.

## Contraste con el proxy anterior

En los 38 países y cada año 2019–2023, la correlación de rangos con `SAL-IN-02`
está entre 0,938 y 0,959; la correlación lineal de los logaritmos está entre 0,967
y 0,975. Es una comprobación de estabilidad de orden, no prueba de equivalencia.
En 2023, `SAL-IN-03`/`SAL-IN-02` es 1,115 en Colombia y 1,505 en Estados Unidos.
La diferencia refleja tanto una base de precios distinta como el alcance financiero.

## Límite y uso permitido

`HF1` suma esquemas gubernamentales y seguros contributivos obligatorios. Por eso
es un recurso de salud movilizado de manera pública u obligatoria, no una medida
idéntica de gasto del gobierno general. La OCDE también define el gasto como
consumo final de bienes y servicios sanitarios, excluyendo inversión de capital.

La serie queda `conditional`, con `score_eligible = false`. Puede usarse para una
sensibilidad de frontera sanitaria, pero no habilita un IEE oficial, un ranking ni
la promoción automática de `SAL-IN-02`.

## Sensibilidad de frontera

Con la misma ventana de resultado (mortalidad evitable media 2019–2021), los 34
pares completos pasan el mínimo experimental de 30. La frontera cuantílica al
90 %, con `log1p` del insumo y las mismas cotas provisionales del resultado,
se ejecutó únicamente como contraste de especificación.

El diagnóstico cambia al sustituir `SAL-IN-02` por `SAL-IN-03`: Colombia pasa de
48,97 a 51,99 y Estados Unidos de 48,80 a 46,44 en la salida experimental. Esos
valores no son puntajes IEE ni deben usarse como ranking: sus intervalos bootstrap
se superponen y el cambio muestra que la conclusión depende materialmente de la
definición del recurso. El recibo conserva el panel (`815550…f2eb`) y los modelos
(`724780…768d`) completos fuera de Git, junto con sus hashes.

## Ejecución

```bash
iee-download \
  --manifest config/downloads_health_v0.8.toml \
  --raw-dir data/raw/official-v0.8 \
  --processed data/processed/v08_health_input.csv \
  --provenance data/interim/v08_health_input_provenance.json
```

La definición del alcance y la decisión de uso están en la
[ADR 0012](decisions/0012-v08-health-resource-alternative.md).
