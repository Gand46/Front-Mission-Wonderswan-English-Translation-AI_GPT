# Front Mission WSC — v0.34-TEST

**Corregido:** el anuncio de Sakata EGRET AVM-12A mostraba `新発売!!`.
Ahora muestra **NEW RELEASE!!**. Era texto dibujado dentro de un gráfico
comprimido, independiente de la tabla principal de diálogos.

## Instalar

Aplica **un solo** parche:

| Parche | Base |
| --- | --- |
| `patches/v034_TEST_from_clean.bps` | ROM japonesa original; recomendado y acumulativo |
| `patches/v034_TEST_from_v033.bps` | v0.33-TEST canónica |
| IPS equivalentes | Las mismas bases; no verifican la base mediante CRC |

El acumulativo ya incluye las correcciones anteriores. No apliques ambos parches.
También puedes construir con Python 3, sin ensamblador ni librerías adicionales:

```bat
build_windows.bat "ROM_original.bin" "Front_Mission_v034_TEST.wsc"
```

```sh
python3 tools/build_v034.py ROM_original.bin Front_Mission_v034_TEST.wsc
```

Base original: `Front Mission (2002-07-12)(Squaresoft)[SWJ-SQRC10].bin`,
8,388,608 bytes, SHA-256:
`d1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380`.

Base v0.33-TEST SHA-256:
`6c722fe5f3bbe7bf6ec371bc54a4ba801806e2c829b6ac72406b30445dd5ed41`.

Salida v0.34-TEST: 8,388,608 bytes, checksum `B9F6`, SHA-256:
`4d6a19c8a69c61edf92ccab3c17ec007f942faec66e6ffe7b68bdbb98450b263`.

No se distribuye la ROM comercial. El BPS acumulativo y el constructor producen
el mismo resultado a partir de la base indicada.

## Resultado de la auditoría

| Ámbito | Resultado |
| --- | --- |
| 10 anuncios de la familia | Revisados en la secuencia natural de Mesen; ninguno conserva japonés visible |
| 3125 entradas principales de texto/control | Sin japonés detectado por el codec y mapa de glifos conocidos |
| 231 entradas de selección de nombre | Preservadas intencionalmente; no se cuentan como diálogos pendientes |
| 1616 recursos gráficos | Inventariados; 134 candidatos RLE estrictos. Inventario no equivale a revisión visual completa |
| Gráficos de UI/localidades examinados | Sin japonés observado en la inspección de tiles; ver alcance en `VALIDACION_ES.md` |
| Tablas 3317 y 3339, 25 hijos | **NEEDS_CONTEXT / NEEDS_CONSUMER_TRACE**; siguen sin aprobación |
| 744 cadenas japonesas originales retenidas y 22 coincidencias de posibles punteros externos | Existencia en bytes confirmada; uso visible no demostrado |

**No se certifica que toda la ROM esté libre de japonés.** El cero solo aplica
a los ámbitos indicados. Los gráficos aún no revisados, los consumidores de las
tablas pendientes y el contenido original residual requieren investigación.

## Qué se preserva

Precio `F$ 540 ~`, arma, estadísticas, marca y fondo del anuncio. El rótulo rojo
es la notación monetaria estilizada, no otro lema japonés. Los otros nueve anuncios
no cambian. Tampoco cambia código, tablas de diálogos, cuadrícula de nombres ni
el ajuste de palabras de v0.33.

La comparación natural antes/después limita las diferencias visuales al rectángulo
del lema: `(55,123)–(168,141)`, extremo final exclusivo. La descompresión de la ROM
coincide exactamente con el bloque gráfico leído de VRAM en Mesen.

## Fuentes y validación

- `data/sakata_caption.json`: traducción, contexto y píxeles indexados editables.
- `tools/resources.py`: codec RLE derivado del consumidor real `4000:6E86`.
- `tools/build_v034.py`: inserción, límites, checksum y validación de vecinos.
- `tools/audit_v034.py`: barridos, inventario y creación/verificación BPS/IPS.
- `qa/advertisements.lua`: recorrido natural reproducible; sin inyecciones.
- `qa/ads_after/`: diez capturas reales de Mesen.
- `history/v033/`: fuentes y evidencia acumuladas, incluidas las etapas anteriores.

El arte se generó como píxeles nativos usando Nimbus Sans Bold Italic a 14 px y
la paleta existente. La fuente del sistema no es necesaria para compilar: la máscara
final está incluida. `tools/make_caption.py` permite regenerarla opcionalmente con
Pillow y el archivo de fuente indicado por el usuario.

El historial conserva los datos recuperados de binario; no sustituye al manifiesto
editorial original ausente de versiones antiguas. Las notas históricas de QA
describen sus respectivas versiones. Consulta los informes de la raíz para v0.34.

Reproducir auditoría y parches:

```sh
python3 tools/audit_v034.py ROM_original.bin Front_Mission_v034_TEST.wsc
python3 -m unittest discover -s tools -p "test_*.py" -v
```
