# Prioridades de recuperación de cohorte v0.3

**Estado:** plan de cobertura experimental; no estima desempeño  
**Fecha:** 2026-09-03

El control de cohorte v0.3 identifica una intersección de 24 países y una meta
mínima de 30. Hay once candidaturas con un solo componente faltante. La primera
ola propuesta toma seis de ellas en orden determinista por cantidad de faltantes
y código de país; no las elige por sus resultados.

| País | Componente que falta | Acción requerida |
| --- | --- | --- |
| AUS | Educación | Verificar una observación compatible de resultado/recurso bajo el contrato v0.9. |
| BEL | Seguridad y justicia | Verificar resultado, equidad e insumo bajo la sensibilidad multifuente v3.2. |
| CAN | Administración pública | Verificar una observación compatible de resultado/proxy bajo el contrato v1.1. |
| DEU | Salud | Verificar una observación compatible de resultado/recurso bajo el contrato v0.8. |
| GRC | Educación | Verificar una observación compatible de resultado/recurso bajo el contrato v0.9. |
| ISL | Seguridad y justicia | Verificar resultado, equidad e insumo bajo la sensibilidad multifuente v3.2. |

El comando `iee-cohort-recovery` lee el recibo de cohorte, conserva su hash y
emite estas prioridades de manera determinista. No descarga datos, no rellena
faltantes y no altera ningún corte previo.

Solo después de recuperar y validar cada componente se vuelve a ejecutar el
control de cohorte. Alcanzar 30 países abre únicamente la posibilidad de diseñar
un corte agregado experimental; no habilita un ranking ni el IEE oficial.
