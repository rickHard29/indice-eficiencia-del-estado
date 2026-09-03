# Sensibilidad mixta TL2/TL3 de equidad de seguridad v2.9

La v2.9 materializa `SEG-EQ-02`, una sensibilidad de cobertura para seguridad y
justicia. Conserva el cálculo de v2.3 —brecha P90–P10 de homicidios ponderada por
población— pero usa TL3 únicamente donde el contrato TL2 no estaba disponible.
No reemplaza `SEG-EQ-01` y permanece fuera de puntajes, frontera, ranking e IEE.

## Diseño

| Grupo | Nivel | Países |
|---|---|---|
| Contrato base | TL2 | Los 30 países de `SEG-EQ-01` |
| Extensión de sensibilidad | TL3 | Estonia, Lituania y Eslovenia |
| Sin cobertura suficiente | — | Islandia, Israel, Letonia, Luxemburgo y Nueva Zelanda |

Cada país conserva un único nivel territorial. No se combinan regiones TL2 y TL3
dentro de un país; el manifiesto registra expresamente las tres excepciones TL3.
Una región debe tener tasa de homicidios y población positivas en 2021, y cada
país requiere tres o más parejas regionales.

## Materialización

La ejecución del 3 de septiembre de 2026 produjo 33 observaciones condicionales:

| País | Nivel | Regiones | Brecha |
|---|---|---:|---:|
| Colombia | TL2 | — | 35,5 |
| Estados Unidos | TL2 | — | 6,1 |
| Estonia | TL3 | 5 | 0,8 |
| Lituania | TL3 | 10 | 2,2 |
| Eslovenia | TL3 | 12 | 0,8 |

El archivo procesado tiene SHA-256
`48d2e1e2856373e6239dfbf19c8c2ff988a3ae95b357c58b16fa8793537c008b`.
Los extractos de homicidios y población tienen SHA-256
`8edaf4262a515ee41134eb45b50f2d670946e6de02bcf8d487b860f33c0adb74` y
`394dc2aabe8ca2ac49c946747adf3bf9831980b3ea686867c466214adac5ef20`.
Los archivos se conservan fuera de Git y el recibo registra las URLs oficiales.

## Interpretación y puerta de integración

Con `SEG-EQ-02`, resultado e insumo vigentes, la intersección de seguridad sube
de 26 a **29 países**. Aún no alcanza el mínimo de 30: Canadá sigue fuera mientras
su candidato de recurso CCOFOG no haya sido convertido y validado a PPA constante.

La sensibilidad no demuestra que una brecha TL3 sea igual a una brecha TL2. Las
unidades territoriales más pequeñas pueden modificar la dispersión observada. Por
eso `score_eligible = false` y cualquier comparación debe identificar el nivel
territorial usado; no se publica una frontera ni una medida de eficiencia.

## Reproducción

```bash
iee-download --manifest config/downloads_security_equity_v2.9.toml \
  --raw-dir data/raw/v29-equity \
  --processed data/processed/v29_equity.csv \
  --provenance data/interim/v29_equity.json
```

La decisión está en la [ADR 0032](decisions/0032-v29-security-equity-sensitivity.md).
