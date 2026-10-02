# Evaluación de preparación para Release Candidate

Evaluación del 20 de septiembre de 2026: **v0.35-TEST es aceptable para pruebas
públicas, pero todavía no es un Release Candidate formal**.

La decisión usa los criterios de `WS_TRANSLATION_UNIVERSAL_RULES_v1.1.md`. Un RC
requiere construcción reproducible y estabilidad técnica, además de cierre de
contenido, revisión lingüística, cobertura representativa del final y ausencia
de regresiones críticas.

| Criterio | Evidencia actual | Decisión |
| --- | --- | --- |
| Construcción reproducible | ROM limpia y v0.34 producen el mismo SHA-256 | Cumplido |
| Checksum y tamaño | `BE92`, 8.388.608 bytes | Cumplido |
| BPS acumulativo verificado | Aplicación sobre la base exacta reproduce v0.35 | Cumplido |
| Integridad de texto/gráficos | 3.356 textos y 2.972 recursos preservados | Cumplido |
| Reparación de tablas secundarias | 25 destinos y dos terminadores válidos | Cumplido |
| Epílogo nativo solicitado | 25/25 textos visibles mediante estado sintético | Cumplido con límite |
| Prueba natural hasta créditos | No existe una partida completa documentada | Abierto |
| Revisión lingüística/terminológica | No aprobada; el epílogo contiene resúmenes breves | Abierto |
| Japonés confirmado pendiente = 0 | No se certifica para toda la ROM y sus gráficos | Abierto |
| Presentación final de créditos | La pantalla posterior a la firma no está aprobada | Abierto |

## Etiqueta recomendada

- Tag: `v0.35-TEST`
- Título: `Front Mission WSC English v0.35-TEST — Pre-RC testing build`
- Opción de GitHub: **marcar como pre-release**
- Activo principal: `Front_Mission_WSC_English_v0.35_TEST_Cumulative.bps`

La promoción a `v0.36-RC1` debería hacerse sólo después de cerrar los cuatro
puntos de `remaining_rc_gates` en `PROJECT_STATE.json` y repetir la reconstrucción,
la auditoría estática y una ruta natural completa.
