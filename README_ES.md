# Front Mission WSC — traducción inglesa v0.35-TEST

Estado de publicación: **pre-RC listo para pruebas**. El código, la construcción,
el parche acumulativo y las reparaciones estructurales son reproducibles. Esta
versión todavía no debe etiquetarse como Release Candidate formal porque siguen
abiertas la revisión lingüística global, una partida natural completa hasta los
créditos y la clasificación final de algunos gráficos y candidatos japoneses.

| Área | Estado verificado |
| --- | --- |
| Construcción desde la ROM japonesa exacta | PASS, resultado byte a byte reproducible |
| BPS acumulativo | PASS, aplicación comprobada contra la ROM v0.35 |
| Checksum WonderSwan | `BE92` |
| Tablas secundarias 3317 y 3339 | PASS estructural, 25 hijos y dos terminadores |
| Epílogo nativo, 25 subtítulos solicitados | PASS mediante `SYNTHETIC_STATE`, 25/25 capturas |
| Japonés o glifos desconocidos en esos 25 subtítulos | 0 / 0 |
| Ruta inicial y regresiones controladas | PASS |
| Campaña natural completa, créditos y aprobación lingüística | Pendiente |
| Ausencia de japonés en toda la ROM | No certificada |

La evaluación completa de los criterios está en
[`docs/ESTADO_PRE_RC_ES.md`](docs/ESTADO_PRE_RC_ES.md). La validación técnica del
epílogo está en [`docs/VALIDACION_EPILOGO_ES.md`](docs/VALIDACION_EPILOGO_ES.md).

## Aplicar el parche

Usa `patches/v035_TEST_from_clean.bps` sobre esta base exacta:

- Nombre de referencia: `Front Mission (2002-07-12)(Squaresoft)[SWJ-SQRC10].bin`
- Tamaño: **8.388.608 bytes**
- SHA-256: `d1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380`

Resultado esperado:

- SHA-256: `bed365a706e13338c8bebc17723fc40f3804a114520524d3ad62f180d44f42c0`
- Checksum interno: `BE92`
- Tamaño: **8.388.608 bytes**

El repositorio no contiene la ROM comercial. El BPS acumulativo es el activo
recomendado para la pre-release `v0.35-TEST`; aplica un solo parche.

## Construir y validar

Requiere Python 3. No requiere ensamblador para reconstruir v0.35.

En Windows:

```bat
build_windows.bat "ROM_original.bin" "Front_Mission_v035_TEST.wsc"
validate_windows.bat "ROM_original.bin" "Front_Mission_v035_AUDIT.wsc"
```

En Linux o macOS:

```sh
python3 tools/build_v035.py ROM_original.bin Front_Mission_v035_TEST.wsc
python3 tools/audit_v035.py ROM_original.bin Front_Mission_v035_TEST.wsc
python3 tools/validate_native_evidence.py
```

El constructor acepta la ROM japonesa limpia o la v0.34 canónica, rechaza una
base distinta y no sobrescribe el destino. La auditoría comprueba conservación
de 3.356 secuencias de texto, 2.972 recursos gráficos, las cuatro variantes de
parche y la reconstrucción exacta.

## Repetir el epílogo con Mesen

Se validó con Mesen 2.1.1 y `mesen_visualization_source_v1.1.0`:

```sh
python3 tools/run_native.py \
  --mesen /ruta/a/Mesen \
  --rom Front_Mission_v035_TEST.wsc \
  --out qa/repeticion_epilogo
```

La prueba activa el evento nativo `0x58` mediante estado sintético después del
arranque. No sustituye punteros, no modifica la ROM y deja toda intervención en
`trace.tsv`. Esto valida el controlador real del epílogo, pero no equivale a
terminar una partida completa.

## Continuar la traducción

- `data/repair.json`: reparación activa de v0.35.
- `tools/`: constructor, decodificador y validadores vigentes.
- `patches/`: BPS/IPS acumulativos e incrementales, más la base v0.34.
- `qa/`: informes y evidencia Mesen vigente.
- `history/`: fuentes acumulativas v0.32–v0.34 y auditorías históricas.
- `vendor/`: herramientas BPS y envoltorio Mesen con sus licencias propias.

Antes de promover una versión a RC, resuelve y documenta los puntos de
`PROJECT_STATE.json`, vuelve a construir desde la ROM limpia y actualiza los
hashes. Las incidencias visuales deberían incluir captura, escena, texto
esperado, método de acceso y, cuando exista, save state reproducible.
