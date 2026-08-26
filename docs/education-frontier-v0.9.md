# Sensibilidad de frontera educativa v0.9

Corte de ejecución: **25 de agosto de 2026**.

La v0.9 somete al puente educativo v0.6 a la misma frontera cuantílica
experimental usada en salud. No calcula un IEE oficial, no publica ranking y no
agrega los roles PISA de acceso y equidad de 2022.

## Contrato congelado

| Elemento | Regla |
|---|---|
| Resultado | `EDU-RES-01`, aprendizaje armonizado HCI, punto 2020 |
| Recurso | `EDU-IN-02`, gasto público educativo aproximado por habitante, media 2019–2020 |
| Muestra completa | 35 de 38 países OCDE; faltan Australia, Grecia y México |
| Modelo | Frontera cuantílica lineal monótona, cuantil 0,90, `log1p` del recurso |
| Resultado oficial | Nulo; publicación y ranking bloqueados |

El recurso permanece anterior o contemporáneo al resultado. PISA 2022 no entra en
esta estimación: su desfase con HCI 2020 debe resolverse antes de construir una
dimensión educativa completa.

## Hallazgo

La estimación converge en una frontera plana: intercepto 71,9994 y pendiente 0.
Por tanto, dentro de esta muestra y con esta proxy, el modelo no identifica una
relación positiva monótona entre el recurso por habitante y el aprendizaje.

Los diagnósticos que produce no son eficiencia ajustada por recursos: al ser plana
la frontera, dependen esencialmente de la normalización del resultado HCI. Por
ejemplo, Colombia obtiene 50,87 (IC bootstrap 50,07–66,38) y Estados Unidos 90,51
(87,09–95,69), pero esos números no deben interpretarse como una comparación de
eficiencia ni como ranking.

## Decisión de uso

`EDU-IN-02` sigue disponible como puente de cobertura y contexto, pero v0.9
rechaza usarlo para afirmar eficiencia educativa en esta frontera. El resultado
plano es evidencia contra promover la proxy por habitante como insumo final, no
una razón para retirar la restricción monótona ni para seleccionar otra
especificación después de observar los datos.

La salida reproducible conserva 35 pares, un modelo y 105 filas de sensibilidad;
los artefactos de datos y los hashes viven fuera de Git. La decisión completa está
en la [ADR 0013](decisions/0013-v09-education-frontier-screen.md).

La alternativa conceptual preferida —gasto de gobierno general por estudiante FTE
en PPA constante— continúa sin una observación vigente de Colombia. Su estado y
la fuente oficial están documentados en el [puente v0.6](education-resource-bridge-v0.6.md).
