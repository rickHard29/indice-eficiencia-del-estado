# Cribado TL3 para equidad territorial de seguridad v2.8

La v2.8 evalúa si el conjunto público *Safety -- Regions* de la OCDE puede
ampliar `SEG-EQ-01` con regiones TL3 para los países que no completaron el
contrato TL2. No adopta datos, no modifica `SEG-EQ-01` y no habilita eficiencia.

## Prueba de disponibilidad

Se descargaron los extractos OCDE de homicidios y población de 2021 sin fijar
nivel territorial. Se conservaron pares de la misma región, país y año, y se
aplicó el mismo cuantil ponderado por población de v2.3.

| País | Regiones TL3 emparejadas | P10 | P90 | Brecha P90–P10 | Resultado |
|---|---:|---:|---:|---:|---|
| Estonia | 5 | 0,7 | 1,5 | 0,8 | Candidata |
| Lituania | 10 | 0,9 | 3,1 | 2,2 | Candidata |
| Eslovenia | 12 | 0,0 | 0,8 | 0,8 | Candidata |
| Letonia | 2 | — | — | — | Rechazada: menos de 3 regiones |
| Islandia | 0 TL3 | — | — | — | Rechazada: sin unidad TL3 publicada |
| Israel | 0 | — | — | — | Rechazada: sin observaciones publicadas |
| Luxemburgo | 1 | — | — | — | Rechazada: menos de 3 regiones |
| Nueva Zelanda | 0 | — | — | — | Rechazada: sin observaciones publicadas |

Los tres casos candidatos satisfacen el control de parejas homicidio--población
y el mínimo de tres regiones. Junto con la candidata canadiense de recursos,
elevarían la intersección de v2.5 de 26 a **30 países**.

## Bloqueo de adopción

El indicador vigente utiliza TL2 en todos sus países. Las regiones TL3 son más
pequeñas y, por esa sola diferencia de nivel, una brecha P90–P10 TL3 no es
numéricamente equivalente a una brecha TL2. Incorporarlas directamente al mismo
indicador reduciría artificialmente o ampliaría la dispersión según la geometría
administrativa de cada país.

Por ello estos tres valores solo pueden formar una sensibilidad nueva, por
ejemplo `SEG-EQ-02`, con tres condiciones previas:

1. Definir explícitamente la mezcla TL2/TL3 y sus límites de interpretación.
2. Mantener una máscara que identifique el nivel territorial de cada país.
3. Probar la estabilidad de los países que sí disponen de ambos niveles antes de
   considerar cualquier integración de cobertura.

El mínimo de 30 no es autorización para relajar comparabilidad. La candidata de
Canadá tampoco se adopta hasta validar su conversión a PPA constante. Por tanto,
la puerta de v2.5 sigue cerrada.

## Fuentes

- [OECD Safety -- Regions](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.CFE.EDS&df%5Bds%5D=DisseminateFinalDMZ&df%5Bid%5D=DSD_REG_SOC%40DF_SAFETY)
- [OECD Demography -- Regions](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.CFE.EDS&df%5Bds%5D=dsDisseminateFinalDMZ&df%5Bid%5D=DSD_REG_DEMO%40DF_DEMO)

La decisión se documenta en la
[ADR 0031](decisions/0031-v28-security-equity-tl3-screen.md).
