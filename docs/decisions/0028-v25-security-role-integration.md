# ADR 0028: integración de los roles de seguridad v2.5

- **Estado:** aprobado como diagnóstico de cobertura; eficiencia bloqueada
- **Fecha:** 2026-09-02

## Contexto

Seguridad y justicia ya contaba con un resultado nacional validado, una proxy de
recurso condicional y una medida territorial de equidad condicional. Antes de
probar cualquier relación entre ellos era necesario verificar que compartieran
países y ventanas sin sustituir observaciones faltantes.

## Decisión

Se crea `security_role_integration_v2.5.toml` y un proceso que valida recibos,
hashes, universo OCDE-38 e identidad de cada fuente. El proceso promedia 2019–
2021 para resultado e insumo y toma 2021 para equidad. Publica una máscara por
país, una puerta de cobertura y procedencia, no una estimación.

La ejecución obtuvo 26 países con los tres roles, frente a un mínimo de 30. El
proceso bloquea explícitamente una frontera experimental, ranking y puntaje IEE.

## Consecuencias

La intersección revela que los 33 pares de la sensibilidad v1.0 no son una
muestra suficiente cuando se añade equidad territorial. No se cambia la ventana,
no se elimina el rol de equidad y no se rellena ningún faltante para alcanzar el
umbral. Cualquier propuesta posterior debe ampliar comparabilidad de datos o
justificar una nueva arquitectura metodológica antes de estimar eficiencia.
