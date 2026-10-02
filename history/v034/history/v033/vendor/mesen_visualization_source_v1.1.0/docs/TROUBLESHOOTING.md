# Diagnóstico de Mesen 2.1.1 — v1.1.0

## `XOpenDisplay failed` al usar `--testRunner`

Ejecute `capture`: desde v1.1.0 crea automáticamente `settings.json` con `{}` si falta. Si el perfil existe pero su JSON no es un objeto, la herramienta lo rechaza para no destruir una configuración existente.

Compruebe activamente el modo sin pantalla con:

```bash
./scripts/probe_mesen.sh --mesen /ruta/Mesen --rom /ruta/juego.wsc
```

## `MesenCore.so: file too short`

La autoextracción del ejecutable fue interrumpida, normalmente por falta de espacio. Retire únicamente los archivos parciales de esa instalación, asegure espacio suficiente y prepare una copia limpia de Mesen. No atribuya este error a la ROM.

## `Cannot establish any listening sockets`

La GUI no puede crear sockets X11. Use `capture`, reutilice un `DISPLAY` funcional o cambie a un entorno que permita X11. `--testRunner` con perfil portátil no requiere esos sockets.

## Timeout

El reporte usa:

- `timeout_source: mesen_internal_likely`: Mesen terminó con 255 sin captura al alcanzar probablemente su límite.
- `timeout_source: python_supervisor`: el supervisor agotó el plazo, terminó el grupo de procesos y conservó la salida parcial.

Aumente `--timeout` para recorridos largos; mantenga un `--timeout-grace` pequeño.

## PNG rechazado

La v1.1.0 abre, verifica y decodifica el archivo entero. Un PNG truncado o corrupto produce `passed=false`. La normalización automática sólo acepta 237×144 y entrega 224×144; conserva el original como `*.raw.png`.

## `--overwrite` rechazado

Alguna salida (`.png`, `.raw.png`, `.json`, `.lua.json` o `.log`) coincide con Mesen, perfil, ROM o Lua. Cambie el nombre base de `--output`; la herramienta se niega a borrar una entrada.

## Diferenciar entorno y ROM

| Evidencia | Interpretación |
|---|---|
| Perfil ausente y `XOpenDisplay failed` | Fallo de inicialización; `capture` debe restaurar `{}` |
| `MesenCore.so` vacío o truncado | Instalación incompleta o falta de espacio |
| `probe --rom` con salida 0 | Mesen cargó y ejecutó la ROM sin DISPLAY |
| PNG válido, proceso 0 y `passed=true` | Captura técnica completada |
| `passed=false` con mapper en log | El núcleo cargó la ROM; revise Lua, timeout o escenario |
