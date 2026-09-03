# Cribado de fuentes para recuperar seguridad v2.7

La v2.7 evalúa fuentes públicas para la ruta A de recuperación de cobertura. Es
un cribado documental: ninguna candidata cambia todavía `SEG-RES-01`,
`SEG-IN-02`, el catálogo ni la muestra v2.5.

## Hallazgo de origen

La falta del insumo no proviene de una descarga incompleta. La OCDE señala que
los datos de gasto COFOG de primer nivel no están disponibles para Canadá,
México, Nueva Zelanda y Türkiye en *Government at a Glance 2025*. Esto confirma
que no debe reintentarse el mismo extractor como si fuera un error técnico.

## Resultado: Bélgica

| Fuente candidata | Cobertura y definición | Estado |
|---|---|---|
| Eurostat, `crim_hom_soff` | La API pública identifica la categoría ICCS0101, pero Bélgica no aporta observaciones de víctimas para 2019–2021; solo aparecen sospechosos, procesados o condenados. | **Descartada** |

Eurostat define homicidio intencional como muerte ilícita causada
deliberadamente y enumera inclusiones y exclusiones. Sin embargo, esa definición
no basta: la combinación belga de víctima, total y tasa por 100.000 no tiene
valores en los tres años requeridos. No se sustituye el resultado por sospechosos,
procesados o condenados porque cambiaría la población medida.

## Insumo: tres países prioritarios

| País | Fuente candidata | Evaluación | Estado |
|---|---|---|---|
| Canadá | Statistics Canada, tabla 10-10-0005-01 | CCOFOG consolidado, anual desde 2008, publicado con licencia abierta. El extracto contiene el agregado `Public order and safety [703]` del gobierno general consolidado: CAD 40,517 millones (2019), 40,543 millones (2020) y 44,958 millones (2021). | **Candidata condicionada** |
| México | SHCP/INEGI, clasificación funcional | La evidencia localizada describe gasto programable/federal o inversión, no gasto del gobierno general homologable a GF03. | **No apta por ahora** |
| Türkiye | TÜİK | La documentación confirma uso de COFOG en compilación nacional, pero no se encontró una serie abierta de gasto del gobierno general por función para 2019–2021. | **Sin serie verificable** |

El manual GFS del FMI reconoce la función 703 (*public order and safety*) y la
utilidad de COFOG para comparaciones internacionales. Eso respalda usar la
correspondencia funcional como criterio, pero no convierte automáticamente datos
nacionales de presupuesto en una observación comparable.

## Decisión operativa

La siguiente iteración solo puede materializar una prueba acotada y gratuita:

1. Extraer de Statistics Canada el agregado consolidado CCOFOG equivalente a
   orden público y seguridad para 2019–2021 y verificar su mapeo, cobertura y
   conversión a PPA constante.

La candidata canadiense debe convertir gasto nominal en dólares canadienses a
proporción del PIB nominal y luego a PPA constante por habitante. Esa operación
debe conservar los tres años, la cobertura de gobierno general y recibos de todas
las dependencias antes de recibir un nuevo identificador. No se adoptará una
fuente para México o Türkiye mientras no cubra gobierno
general, tenga función documentada comparable y permita una descarga
reproducible. Esa restricción evita elevar la muestra mezclando presupuestos
federales con gasto general de otros países.

## Resultado del cribado

La ruta A no puede alcanzar 30 países con las fuentes revisadas: Canadá es el
único candidato que pasa disponibilidad y alcance; Bélgica falla cobertura del
resultado y México/Türkiye fallan el alcance verificable. La investigación debe
mantener esta candidata aislada y pasar al cribado de una alternativa de equidad
territorial (ruta B), salvo que aparezcan nuevas fuentes oficiales equivalentes
para los tres faltantes restantes.

## Fuentes oficiales

- [OECD, gasto por función COFOG 2025](https://www.oecd.org/en/publications/2025/06/government-at-a-glance-2025_70e14c6c/full-report/government-expenditure-by-function-cofog_d2b167d4.html)
- [Eurostat, metadatos de crimen y justicia](https://ec.europa.eu/eurostat/cache/metadata/en/crim_sims.htm)
- [Statistics Canada, CCOFOG consolidado](https://open.canada.ca/data/en/dataset/399fa7e0-8900-42db-8f34-7849fc2f647f)
- [FMI, clasificación funcional del gasto](https://www.imf.org/external/pubs/ft/gfs/manual/pdf/all.pdf)
- [FMI, evaluación de estadísticas fiscales de México](https://www.imf.org/-/media/files/publications/cr/2021/english/1mexea2021004.pdf)
- [TÜİK, PIB anual 2021](https://veriportali.tuik.gov.tr/Bulten/Index?p=Yillik-Gayrisafi-Yurt-Ici-Hasila-2021-45834)

La decisión correspondiente se conserva en la
[ADR 0030](decisions/0030-v27-security-source-screen.md).
