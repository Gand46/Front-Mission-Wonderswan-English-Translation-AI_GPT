# Prueba pendiente en Mesen

Esta entrega NO tiene un PASS de emulación. El intento Linux con la ROM exacta
terminó antes del primer frame: `XOpenDisplay failed`. No se ha utilizado
`--testRunner`, tal como exige el handoff. El PASS histórico de v0.31 no se
transfiere a v0.32-TEST.

## Ruta acotada

1. Aplicar la candidata y verificar SHA-256 con `VALIDATE_STATIC.bat`.
2. Abrir la ROM en la interfaz normal de Mesen 2.1.1, desde reinicio limpio.
3. Crear una carpeta nueva para capturas. Editar `out` en
   `mesen_v032_smoke_24000.lua` con su ruta absoluta; en Windows usar `/`.
4. Abrir el script mediante Script Window y ejecutarlo. La ruta deriva del Lua
   histórico, pero esta revisión NO se ha podido ejecutar en este entorno.
5. El script se detiene a los 24.000 frames. Si no progresa en diez minutos,
   detenerlo y conservar log/capturas. No repetir indefinidamente.
6. `completed.txt` acredita sólo que los callbacks llegaron al límite; NO
   demuestra ausencia de cuelgues lógicos, corrección de textos o de escenas.

## Comprobaciones dirigidas necesarias

| Pantalla / registro | Qué comprobar |
| --- | --- |
| Tienda / partes: 137, 138, 139 | DF, PW, WT, MV y HP, números intactos, sin solapamientos |
| Ordenador: 496 | ML, SR, LR y EV, legibles a escala nativa |
| Arma: 545 | AT, AC, RG, AM; conservar multiplicador y guion FD, infinito |
| Armas antipersona | AP y comportamiento de la etiqueta compuesta |
| Diálogo 1011 | Soldado USN, texto completo después del cambio de banco |
| Name Entry | Cuadrícula japonesa y avance de 12 px sin cambios |
| Prueba interna: 2099–2103 | `test` sólo si se demuestra un consumidor; no inventar una escena |
| Ending: tablas 3317 y 3339 | Trazar consumidor y banco; 25 hijos, referencias antiguas y centinelas dañados |

Si una escena no se alcanza naturalmente, usar un savestate conocido o trazado
de consumidor. No realizar escrituras WRAM o reemplazos de punteros a ciegas.
La ruta temprana no sustituye tiendas, menús, escenas tardías ni créditos.
Conservar hash de ROM, versión de Mesen, estado inicial, ruta de acceso y capturas.
