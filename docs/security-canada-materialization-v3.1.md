# Materialización del complemento canadiense de seguridad v3.1

**Estado:** sensibilidad de insumo materializada; no integrada al panel  
**Fecha:** 2026-09-03

## Resultado

La candidata validada en v3.0 se ejecutó como una adquisición reproducible
independiente. Produce tres observaciones de SEG-IN-03 para Canadá:

| Año | Dólares internacionales constantes de 2021 por habitante |
| ---: | ---: |
| 2019 | 1008,452640893214656668833594 |
| 2020 | 987,6415616677451160511751931 |
| 2021 | 1010,478883929813639176074892 |

El archivo procesado tiene SHA-256
b37ddd0c530e8b7e60121ee3d89517eb269ef0aa779c6c42040d9741d0279559.

## Contrato

La nueva serie usa CCOFOG 703 del gobierno general consolidado de Statistics
Canada, PIB nominal canadiense y PIB por habitante PPA constante 2021 del Banco
Mundial. El manifiesto y catálogo están en:

- config/downloads_security_canada_v3.1.toml;
- config/security_canada_sources_v3.1.toml.

La conversión se prueba automáticamente, exige la fila CCOFOG exacta y conserva
los hashes de los tres recursos descargados. SEG-IN-03 permanece condicional y
no puede alimentar un puntaje directamente.

## Límite de integración

SEG-IN-03 no reemplaza SEG-IN-02. Los 34 países de la OCDE usan la serie
histórica y Canadá usa un complemento nacional compatible pero distinto. Antes
de calcular la sensibilidad de 30 países se creará una capa de combinación que
registre, país por país, qué fuente respalda cada observación. Esa trazabilidad
evita convertir una mejora de cobertura en una sustitución silenciosa.
