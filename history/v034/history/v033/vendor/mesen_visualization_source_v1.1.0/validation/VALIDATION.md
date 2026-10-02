# Validación de mesen_visualization_source v1.1.0

Fecha: 2026-09-05. Linux x86_64, Mesen 2.1.1, sin `DISPLAY`.

## Causa confirmada

Se ejecutó la misma ROM sintética, el mismo Lua y el mismo Mesen cambiando sólo el perfil portátil:

| Condición | Salida | Captura |
|---|---:|---|
| Sin `settings.json` | -6, `XOpenDisplay failed` | No |
| Con `settings.json` = `{}` | 0 | Sí, 237×144 |

Esto confirma que el perfil mínimo evita la inicialización gráfica que bloqueaba `--testRunner` en este entorno. La prueba externa no demuestra por sí sola qué componente interno de Mesen toma cada decisión de arranque.

## Integración v1.1.0

Se retiró `settings.json` de una instalación limpia y se ejecutó `capture`. La herramienta recreó el perfil automáticamente y completó:

- ROM sintética WSC: 131.072 bytes.
- 120 fotogramas sin `DISPLAY`.
- Código de salida: 0.
- Tiempo: 0,621 s.
- Captura Mesen: 237×144.
- Captura normalizada: 224×144.
- SHA-256 Mesen: `ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`.
- SHA-256 ROM: `4dd47a784e4f019bc15b9dc7e023fa713d52342d03f4728ed195db7f4e043ffe`.
- SHA-256 PNG normalizado: `274cb6ccbf1534ef871e84040afb36ca5833bd26214891e22a008ee26b0e4438`.
- SHA-256 PNG bruto: `44083e24000feb17bda027ca694edbdb2b8c4f87a7ac2e8ce87c4dcc3307c40b`.

`probe --rom` ejecutó activamente la misma ROM sin `DISPLAY`, imprimió el mapper y devolvió `test_runner_ready_without_display: true` con salida 0.

El timeout real con límite interno de un segundo devolvió 255, `passed: false`, `timed_out: true` y `timeout_source: mesen_internal_likely`.

## Regresiones

Siete pruebas automatizadas pasaron:

1. PNG completo se decodifica.
2. PNG truncado se rechaza también desde `capture`.
3. `capture` restaura el perfil mínimo.
4. Geometría desconocida no se recorta.
5. Una colisión de salida no elimina el Lua de entrada.
6. Un archivo con permiso de ejecución pero sin formato ELF se rechaza.
7. El supervisor termina un proceso bloqueado, conserva su salida y devuelve 124.

También pasaron `py_compile`, la sintaxis de los cuatro wrappers Bash y la verificación de `SHA256SUMS` del paquete final.

## Límites

La ROM sintética valida carga, render y captura. No valida gameplay, audio, controles, traducción ni una ROM comercial. La GUI no pudo probarse en este entorno porque no existen `DISPLAY`/Xvfb y los sockets Unix X11 están bloqueados; el modo `--testRunner` no los necesita.
