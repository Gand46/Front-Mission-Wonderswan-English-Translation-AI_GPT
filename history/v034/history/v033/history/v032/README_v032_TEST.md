# Front Mission WSC — v0.32-TEST

Continuación de v0.31, japonés → inglés. **Candidata, no release final:**
validación estática aprobada; emulación bloqueada antes del primer frame.
Este documento y `evidence/static_validation.json` prevalecen sobre el historial.

## Cambios implementados

- 16 glifos japoneses de atributos sustituidos por abreviaturas inglesas. Son
  recursos compartidos: afectan 464 entradas de la tabla principal, 463 destinos
  únicos. No son 464 diálogos nuevos.
- Cinco registros internos 2099–2103 traducidos como `test`. Se conservan nombre
  dinámico, dos puntos y salto de línea. Las terminaciones coloquiales de dos
  variantes japonesas se normalizan por tratarse de placeholders técnicos;
  su uso durante el juego sigue sin demostrarse.
- Corregido el cruce de banco heredado del registro 1011. Empezaba en
  `0x7BFFFB` y terminaba en `0x7C0043`; el lector usa un offset de 16 bits sin
  aumentar el segmento. Ahora empieza en `0x7C0000`, dentro de su propia reserva,
  sin tomar espacio supuesto libre. Texto equivalente abreviado:
  `USN Soldier:{BR}Unidentified Wanzer{BR}near the crash site.`
- Se conserva el motor Optical8, las fuentes latinas existentes y Name Entry.

| Japonés | Etiqueta inglesa | Significado |
| --- | --- | --- |
| 防 | DF | Defense |
| 攻 | AT | Attack |
| 重 | WT | Weight |
| 出 | PW | Power output |
| 弾 | AM | Ammo |
| 命 | AC | Accuracy |
| 移 | MV | Movement |
| 格 | ML | Melee |
| 近 | SR | Short range |
| 遠 | LR | Long range |
| 射程 | RG | Range, dos glifos |
| 回避 | EV | Evade, dos glifos |
| 対人 | AP | Anti-personnel, dos glifos |

## Aplicar y verificar

Requiere Python 3; aplicación, reconstrucción y pruebas básicas usan solamente
la biblioteca estándar. Pillow se necesita únicamente para regenerar las PNG.
No se distribuye una ROM comercial ni un ejecutable del emulador.

```bat
APPLY_FROM_CLEAN.bat "Front Mission Japan.wsc"
rem Alternativa: partir de la v0.31 canónica
APPLY_FROM_v031.bat "Front Mission v0.31.wsc" "FM_v032_TEST.wsc"
VALIDATE_STATIC.bat "Front Mission Japan.wsc" "FM_v032_TEST.wsc"
```

Los dos ejemplos de aplicación son alternativas. Por defecto, el primero genera
`Front_Mission_WSC_English_v0.32_TEST.wsc` junto al BAT. Usar ese nombre al validar
si no se eligió otro. No sobrescribe una salida existente.
Los IPS `v032_TEST_from_clean.ips` y `v032_TEST_from_v031.ips` también pueden
aplicarse con un parcheador IPS, comprobando siempre el hash de la base.

| Archivo | SHA-256 |
| --- | --- |
| ROM japonesa limpia, 8 MiB | `d1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380` |
| ROM v0.31 canónica | `76d30792f9e82c74291c28864cdf4a86ee4e3e21fe0c2792a8f099b087234f4d` |
| ROM v0.32-TEST esperada | `75ddcc0c9ac17d2d188a5312c205149288e7eb6f5c4f93e795238d97f6f74185` |

Checksum WonderSwan nuevo: `0x1D05`. Cambian 1.208 bytes respecto de v0.31.

## Resultado y alcance

19 pruebas unitarias aprobadas. Reconstrucción desde limpia y v0.31 idéntica;
IPS acumulativo y delta reconstruyen exactamente la misma ROM. Se comprueban
checksum, límites, terminadores, referencias conocidas y lista de áreas
autorizadas. Todos los textos de la tabla, salvo las seis entradas modificadas,
conservan sus bytes y destinos; los atributos cambian mediante arte compartido.
No quedan registros de texto de la tabla principal que crucen un banco.

En el ámbito decodificado de la tabla principal, excluyendo la cuadrícula de
nombres y las dos tablas binarias, no quedan caracteres japoneses reconocidos
ni códigos de glifo sin clasificar. **Esto NO equivale a un juego 100% traducido.**
No certifica texto dibujado en gráficos, operadores especiales FD, otras tablas,
todos los consumidores ni un recorrido completo.

Se inspeccionaron las vistas estáticas del atlas y ejemplos. Las nuevas etiquetas
caben en 8 px incluyendo sombra. Las PNG con `STATIC` NO son capturas del juego;
en los ejemplos se omiten operadores dinámicos FC/FD y no se certifica layout.

Mesen normal devolvió `XOpenDisplay failed` con la ROM de esta entrega: cero frames
y cero capturas runtime. Ver `evidence/runtime_result.json` y
`validation/QA_MESEN.md`. No se usa el PASS de 24.000 frames de v0.31 como prueba nueva.

## Pendientes que impiden considerarla final

1. Dos tablas near-pointer, índices 3317 y 3339, con 7 y 18 hijos: conservan
   referencias antiguas y centinelas alterados de `FFFF` a `FFC0`. Sus hijos
   tienen traducciones en la tabla principal, pero éstas fueron reubicadas.
   La búsqueda estática acotada no probó el consumidor ni sus reglas de banco.
   No se modifica esta estructura sin ese trazado. No son dos diálogos.
2. Cuadrícula Name Entry: 231 entradas preservadas intencionadamente. Su japonés
   sigue disponible; no se elimina la capacidad de introducir nombres japoneses.
3. QA visual y funcional en tiendas, Setup, armas, escenas tardías y ending.
4. Texto japonés original retenido sin referencias demostradas: presencia de
   bytes no equivale a texto pendiente alcanzable. No se borra como limpieza.

## Fuentes y continuidad

- `data/translations_v032.json`: decisiones nuevas editables y bytes originales.
- `tools/build_v032.py`: constructor reproducible y fuente de glifos 3×7.
- `data/binary_derived_corpus_v032.json`: los 3.358 registros recuperados de la
  ROM actual, incluyendo dos estructuras binarias separadas. Es una instantánea
  binaria, NO el manifiesto editorial original de las versiones recientes.
- `patches/`: base v0.31, acumulativo nuevo y delta nuevo.
- `history/`: paquete complementado anterior, fuentes históricas recuperadas y
  auditoría revisada v0.31. Los diagnósticos anteriores incorrectos se conservan
  como historia, no como instrucciones activas.

El manifiesto editorial canónico posterior a v0.13 no fue recuperado. La entrega
es autocontenida para reconstruir el binario y editar esta revisión, pero no se
afirma haber recuperado fuentes editoriales que no están disponibles.

Para volver atrás, reconstruir v0.31 desde una copia limpia con el acumulativo
histórico. No aplicar el delta nuevo a una ROM de otra versión.
