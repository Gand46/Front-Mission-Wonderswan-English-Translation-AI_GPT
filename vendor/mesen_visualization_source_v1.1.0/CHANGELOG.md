# Cambios

## 1.1.0 — 2026-09-05

- Restaura automáticamente el perfil portátil `{}` en `capture` y `gui`.
- Agrega diagnóstico activo `probe --rom` y validación ELF estática.
- Valida y decodifica completamente los PNG mediante Pillow.
- Impide colisiones entre todas las entradas y salidas auxiliares.
- Añade supervisor de procesos, cierre del grupo completo y registro de timeouts.
- Registra el comando ejecutado y una causa explícita si falta la captura.
- Restringe la normalización al formato WonderSwan comprobado 237×144.
- Agrega seis pruebas de regresión y documentación actualizada.
