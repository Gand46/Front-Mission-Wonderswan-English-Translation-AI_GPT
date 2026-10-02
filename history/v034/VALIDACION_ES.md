# Validación y pendientes — v0.34-TEST

## Hallazgo y corrección

La captura aportada muestra `新発売!!`, literalmente un anuncio de lanzamiento
o novedad a la venta. En el contexto publicitario de Sakata, `NEW RELEASE!!`
conserva esa función y las dos exclamaciones. No añade especificaciones ni cambia
precio, alcance, potencia o munición. Revisión lingüística y visual aprobadas
**para este lema**, no para la traducción completa.

La familia usa diez registros gráficos, índices 13–22 de la tabla `0x749B90`.
Sakata es el índice 17: descriptor `0x749BF6`, bloque `0x00DAEA–0x00ECA1`.
Se descomprime a 6656 bytes en VRAM `0x6600–0x7FFF`.
El mapa de tiles es el recurso 12. La rutina de RLE se identificó en `0x746E86`.

El nuevo flujo ocupa 4521 de los 4535 bytes disponibles: no requiere mover el
recurso, extender la ROM ni tocar los vecinos. Se actualiza su longitud, se rellena
el resto del bloque y se recalcula el checksum. La lista de rangos permitidos
solo incluye ese bloque, el campo de longitud y el checksum.

## Pruebas realizadas

1. Reproducción natural del fallo en v0.33, sin entradas de mando ni memoria
   alterada. Captura: `qa/before/sakata_v033_NATURAL.png`.
2. Rastreo del lector de recursos y de su rutina de descompresión. Datos en
   `qa/consumer_trace/`.
3. Recorrido natural de 15000 frames con v0.34 usando Mesen y
   `mesen_visualization_source_v1.1.0`. Capturas de los diez anuncios; todos sus
   descriptores fueron leídos. No se usaron inyecciones de texto/estado.
4. Comparación antes/después: diferencia limitada al lema; resto de la pantalla
   idéntico. Captura corregida: `qa/ads_after/ad_17_frame_10500_NATURAL.png`.
5. Comparación exacta entre el recurso descomprimido de la ROM y la VRAM capturada.
6. Vectores de prueba independientes para los opcodes RLE 77/88/99/AA/BB/CC/DD/EE,
   literales escapados, repeticiones y secuencias de palabras con desbordamiento.
7. Construcción desde ROM original y desde v0.33 idéntica; aplicación de cuatro
   parches BPS/IPS acumulativos/incrementales idéntica al resultado del constructor.

No se modificó código de ejecución; las correcciones tipográficas de v0.33 se
preservan byte por byte. No se repitió una partida completa para un cambio gráfico
local. `passed` en los informes de Mesen solo indica ejecución/captura correcta;
la inspección visual se documenta por separado.

## Anuncios revisados visualmente

| Recurso | Marca | Lema final |
| --- | --- | --- |
| 13 | Vantam | State Of The Art |
| 14 | Vince | The Cutting Edge |
| 15 | Leonora | Grab yours before they sell out |
| 16 | Jade Metal | It's New! |
| 17 | Sakata | **NEW RELEASE!!** |
| 18 | Schnecke | The Cutting Edge |
| 19 | Diable Avionics | Action at its Best |
| 20 | Iguchi | Now on Sale! |
| 21 | Challenge Bold | IT'S HOT! |
| 22 | Taureau | The Latest Technology |

Los nueve lemas preexistentes se preservan; esta tabla registra lo observado,
no una nueva revisión editorial de su estilo. No se observó clipping del lema nuevo.

## Dónde podría quedar japonés

- **Gráficos fuera de la familia revisada.** La tabla inventariada tiene 1616
  descriptores. Se identificaron 134 flujos que cumplen estrictamente la estructura
  RLE. No todos son texto: incluyen mapas, efectos, retratos y datos gráficos.
- **Otros sistemas de texto.** Los dos arreglos anidados 3317 y 3339 tienen 25
  hijos y problemas históricos de referencias/terminación. No deben repararse
  apuntándolos a cadenas vecinas sin identificar su consumidor.
- **Datos originales retenidos.** El barrido reconoce 744 cadenas japonesas
  originales todavía presentes y 22 coincidencias de bytes con forma de puntero
  fuera de la tabla principal. Pueden ser datos sin uso o coincidencias en código;
  no son 744 diálogos pendientes demostrados.
- **Selección de nombre.** Se conserva la cuadrícula de caracteres. El barrido
  separa sus 231 entradas del texto de juego para no contarlas como traducciones
  pendientes ni eliminarlas por accidente.

La tabla principal contiene 3358 entradas: 3125 de texto/control, 231 de cuadrícula
y 2 arreglos pendientes. En las 3125 entradas, el codec y el mapa de glifos actuales
no detectan japonés ni glifos sin clasificar fuera de los símbolos ya identificados.
Esto no evalúa automáticamente la fidelidad lingüística de cada frase.

Como ampliación gráfica se inspeccionaron mosaicos de los recursos 3, 7, 10, 32,
33, 40 y 1214: mapa, localidades latinas, cabecera publicitaria y elementos de UI.
No se observó japonés en esas inspecciones. Las láminas de `qa/static_tiles/`
son datos extraídos reorganizados para revisión, **no capturas de gameplay** ni
certificación de todas las combinaciones de tiles posibles.

Los informes completos son `qa/main_text_audit.json`,
`qa/graphics_resource_inventory.json`, `qa/retained_original_text_candidates.json`,
`qa/retained_text_pointer_candidates.json` y `qa/audit_summary.json`.
La conclusión global sigue siendo **NOT_APPROVED_GLOBAL_COVERAGE_INCOMPLETE**.

## Repetir la prueba natural

Desde la carpeta del paquete, con tu ejecutable Mesen y la ROM construida:

```sh
python3 history/v033/vendor/mesen_visualization_source_v1.1.0/scripts/mesen_visual.py capture --mesen /ruta/Mesen --rom /ruta/Front_Mission_v034_TEST.wsc --lua qa/advertisements.lua --output qa/ads_after/final.png --timeout 50 --timeout-grace 5 --normalize-wonderswan
python3 tools/validate_runtime.py /ruta/Front_Mission_v034_TEST.wsc
```

Trabaja sobre una copia del paquete para preservar la evidencia entregada.
La segunda orden necesita Pillow. La primera genera temporalmente
`sakata_vram.bin`, que no se distribuye en el ZIP: su hash y comparación quedan
registrados en `qa/runtime_validation.json`.

Las herramientas Mesen se incluyen con sus fuentes; el ejecutable comercial del
juego no se distribuye. Mesen usado: SHA-256
`ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`.
Se utilizó el modo `--testRunner` autorizado anteriormente.

## Próximo cierre de cobertura

Prioridad 1: rastrear consumidores de las dos tablas anidadas y de las referencias
residuales. Prioridad 2: clasificar los demás recursos gráficos y ensamblar las
pantallas que contengan letras. Prioridad 3: validación contextual de los textos
restantes mediante recorridos y checkpoints acotados. No declarar 100 % antes de
cerrar estas áreas y la revisión lingüística global.
