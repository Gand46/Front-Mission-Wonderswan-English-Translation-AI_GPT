# Visualización reproducible de ROMs con Mesen 2.1.1 — v1.1.0

Este paquete ejecuta Mesen en Linux y genera capturas auténticas de ROMs. Incluye dos modos:

1. `capture`: ejecuta `--testRunner`, captura el framebuffer mediante Lua y no necesita `DISPLAY`.
2. `gui`: abre la interfaz con un `DISPLAY` verificado o con Xvfb.

El paquete no incluye Mesen ni ROMs. Use su ZIP de Mesen 2.1.1 y sus propias ROMs.

## Corrección del perfil portátil

Se comprobó mediante una prueba A/B que, sin `settings.json` junto a `Mesen`, el ejecutable intenta inicializar X11 y termina con `XOpenDisplay failed` antes de producir una captura. Con el perfil mínimo `{}`, la misma orden `--testRunner` funciona sin `DISPLAY`.

`prepare` crea el perfil. Desde v1.1.0, `capture` y `gui` también lo restauran automáticamente si falta. Un perfil existente pero inválido se rechaza y no se sobrescribe.

## Inicio rápido

```bash
./scripts/prepare_mesen.sh \
  --zip /ruta/Mesen_2.1.1_Linux_x64.zip \
  --dest .tools/mesen-2.1.1

./scripts/probe_mesen.sh \
  --mesen .tools/mesen-2.1.1/Mesen \
  --rom /ruta/juego.wsc

./scripts/preview_rom.sh \
  --mesen .tools/mesen-2.1.1/Mesen \
  --rom /ruta/juego.wsc \
  --output previews/boot.png \
  --frame 180 --timeout 30 --normalize-wonderswan
```

`probe --rom` hace una prueba activa: carga la ROM, ejecuta un fotograma y exige salida 0. Sin `--rom`, sólo informa si están presentes el ELF de 64 bits y el perfil; `test_runner_ready_without_display` queda en `null` porque no se ejecutó Mesen.

La captura genera:

- `boot.png`: captura final decodificada y validada completamente.
- `boot.raw.png`: original 237×144, si se normalizó a 224×144.
- `boot.json`: hashes, dimensiones, comando, timeout y código de salida.
- `boot.log`: salida de Mesen.

## Protección contra bloqueos

Mesen usa su límite interno `--timeout`. Python añade un supervisor mediante `--timeout-grace` (5 segundos por defecto), ejecuta Mesen en una sesión separada y termina el grupo completo de procesos si se agota el plazo. El JSON distingue `mesen_internal_likely` y `python_supervisor`.

Para añadir un segundo límite desde la shell:

```bash
timeout -k 2 40 ./scripts/preview_rom.sh \
  --mesen .tools/mesen-2.1.1/Mesen --rom juego.wsc \
  --output previews/boot.png --timeout 30
```

## Garantías de v1.1.0

- Decodifica el PNG completo con Pillow; una firma o IHDR truncados no pasan.
- Sólo normaliza 224×144 o el formato comprobado de Mesen 237×144.
- Valida todas las rutas auxiliares antes de borrar archivos con `--overwrite`.
- Conserva salida parcial en timeouts y siempre intenta escribir log y JSON.
- Comprueba el formato ELF antes de declarar prerrequisitos disponibles.
- Registra el comando exacto en el reporte.
- Limita a cinco segundos la consulta auxiliar a `g++` y `xdpyinfo`.

`passed=true` acredita carga, ejecución, salida 0 y PNG válido. No acredita traducción completa, audio, controles ni gameplay. Para esos objetivos se necesitan Lua de recorrido, entradas y aserciones específicas.

## Lua personalizado

El Lua debe leer `MESEN_CAPTURE_PATH`, escribir `emu.takeScreenshot()` en binario y terminar con `emu.stop(0)` o un código de error. Use `emu.eventType.inputPolled` para controles y `emu.eventType.endFrame` para checkpoints. No use `emu.exit()` con Mesen 2.1.1.

```bash
./scripts/preview_rom.sh \
  --mesen .tools/mesen-2.1.1/Mesen --rom juego.wsc \
  --lua pruebas/ruta.lua --output previews/ruta.png
```

## GUI

```bash
./scripts/run_mesen_gui.sh \
  --mesen .tools/mesen-2.1.1/Mesen --rom juego.wsc --xvfb auto
```

La GUI espera hasta cerrarse. Agregue `--timeout 120` para limitarla. Si faltan `xdpyinfo`, DISPLAY verificable, Xvfb o permisos de socket X11, el diagnóstico informa el bloqueo.

## Pruebas del paquete

```bash
MESEN_TEMP_DIR=/dev/shm python3 tests/selftest.py
```

`MESEN_TEMP_DIR` es opcional y permite dirigir archivos temporales a un volumen con espacio. Consulte `validation/VALIDATION.md` para la evidencia real de v1.1.0.
