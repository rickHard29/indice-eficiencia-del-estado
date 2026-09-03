# Paquete de preparación experimental v0.2

**Estado:** experimental; no habilita publicación ni ranking  
**Fecha:** 2026-09-03

## Qué publica esta versión

Esta versión reúne en un único recibo reproducible las puertas de cobertura ya
superadas por las cuatro dimensiones del IEE dentro del universo OCDE-38. Cada
evidencia conserva su propio contrato, periodo y definición; el paquete no las
convierte en un puntaje común.

| Dimensión | Evidencia incluida | Países completos | Uso permitido |
| --- | --- | ---: | --- |
| Educación | Sensibilidad de recurso v0.9 | 35 / 38 | Prueba de cobertura experimental |
| Salud | Sensibilidad de recurso v0.8 | 34 / 38 | Prueba de cobertura experimental |
| Administración pública | Sensibilidad de resultado y proxy v1.1 | 34 / 38 | Prueba de cobertura experimental |
| Seguridad y justicia | Máscara de tres roles multifuente v3.2 | 30 / 38 | Prueba de cobertura de roles |

El manifiesto `config/experimental_release_v0.2.toml` y el comando
`iee-experimental-release` verifican esos cuatro archivos de puerta, guardan sus
hashes y generan `data/processed/experimental_release_v0.2.json`.

## Lo que esta versión no hace

- No calcula una eficiencia por país.
- No normaliza ni agrega dimensiones.
- No define una cohorte común para una comparación agregada.
- No publica puntajes, posiciones ni un ranking.
- No habilita el IEE oficial.

Una dimensión puede superar el mínimo de su propia sensibilidad y, aun así, no
ser directamente agregable con otra. La seguridad v3.2, por ejemplo, demuestra
que existen 30 países con los tres roles observados bajo una combinación
multifuente; no sustituye su sensibilidad temporal v1.0 ni estima una frontera.

## Bloqueos que se conservan

El recibo declara explícitamente cuatro bloqueos: metodología v1 sin congelar,
ausencia de cohorte común predeclarada, insumos condicionales y revisión
metodológica abierta pendiente. Cualquiera de ellos basta para mantener nulos el
puntaje IEE y el ranking.

La siguiente unidad de trabajo es definir el contrato común de un corte
experimental —periodos, reglas de exclusión, normalización y tratamiento de los
roles— antes de observar posiciones agregadas.
