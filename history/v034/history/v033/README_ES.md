# Front Mission WSC — v0.33-TEST

Corrección del espaciado y del salto automático por palabras. Fecha: 2026-09-20.

## Aplicar la corrección

Elige **un solo parche**, según tu ROM de entrada:

| Archivo | Entrada exacta |
| --- | --- |
| `patches/v033_TEST_from_clean.bps` | ROM japonesa original, sin parches; opción recomendada |
| `patches/v033_TEST_from_v032.bps` | v0.32-TEST RC3 canónica |
| Los archivos `.ips` equivalentes | Las mismas bases; IPS no verifica por sí solo la identidad de entrada |

No apliques el parche acumulativo encima de v0.32 ni combines el acumulativo con el delta.
Trabaja sobre una copia. El paquete no incluye la ROM comercial ni las ROM de pruebas.

SHA-256 de entrada original:
`d1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380`

SHA-256 de entrada v0.32-TEST RC3:
`75ddcc0c9ac17d2d188a5312c205149288e7eb6f5c4f93e795238d97f6f74185`

SHA-256 de salida v0.33-TEST:
`6c722fe5f3bbe7bf6ec371bc54a4ba801806e2c829b6ac72406b30445dd5ed41`

Tamaño: 8,388,608 bytes. Checksum interno: `8369`.

También puedes construirla con Python 3, sin instalar ensamblador:

```bat
build_windows.bat "ROM_original.bin" "Front_Mission_v033_TEST.wsc"
```

```sh
python3 tools/build_v033.py ROM_original.bin Front_Mission_v033_TEST.wsc
```

El constructor acepta la ROM original o v0.32-TEST RC3 y rechaza otras bases.
Inicia de nuevo el emulador con la ROM nueva. Para validar código modificado, no
uses un estado rápido capturado dentro de una rutina de texto de otra versión.
La compatibilidad de todos los estados rápidos anteriores no está certificada.

## Qué cambia

- El segundo motor seguía avanzando 12 píxeles por carácter aunque los glifos se
  habían reducido. Ahora usa 8 píxeles y 4 para los alias estrechos.
- Ambos motores miden la palabra siguiente antes de imprimir su espacio. Si no
  cabe, trasladan la palabra a la línea o página siguiente mediante las rutinas
  originales. Se respetan las capacidades existentes de 176 y 120 píxeles.
- Se preserva el comportamiento protegido de la cuadrícula de nombres. Durante
  la expansión de nombres dinámicos FC no se consumen espacios del texto principal.
- No se abreviaron frases, no se cambiaron traducciones, fuentes ni punteros.
  La diferencia frente a v0.32 es de 450 bytes de código/checksum.

Las frases `Avenge her death?` y `Join us. You may` se muestran completas en las
pruebas del segundo motor. La corrección no consiste en cambiar solo esos registros.

## Validación y alcance

Consulta `QA_ES.md`, los JSON, los registros y las capturas en `qa/`.
Mesen se ejecutó mediante `mesen_visualization_source_v1.1.0` y la excepción
headless `--testRunner` previamente autorizada. Hay un recorrido sin inyecciones,
pruebas de punteros controladas y pruebas sintéticas, claramente separadas.

**Esta es una versión TEST, no una aprobación del juego completo.** No se llegó
naturalmente a la escena tardía de Olson: se reprodujeron sus textos en el motor
real durante una escena accesible. Las tablas anidadas 3317 y 3339 siguen pendientes
de investigación y no se alteraron. Tampoco se certifican todos los menús, escenas,
estados guardados, gráficos con texto ni hardware real.

Una palabra individual más ancha que su ventana conserva un corte de emergencia;
no puede garantizarse que quepa sin un cambio editorial o de diseño. El escáner no
atraviesa los controles FC/FD/F8–FF para predecir expansiones de ancho variable.
Esos casos requieren QA específica. Los saltos explícitos del guion se conservan.

## Fuentes y reproducción

`source/wordwrap.s` es el ensamblador nuevo; `source/bank76.bin` contiene su salida
enlazada, no una ROM. Para regenerarla con GNU binutils desde esta carpeta:

```sh
as --32 -o wordwrap.o source/wordwrap.s
ld -m elf_i386 -Ttext=0 --entry=0 -o wordwrap.elf wordwrap.o
objcopy -O binary -j .text wordwrap.elf source/bank76.bin
```

No uses `objcopy` directamente sobre el objeto sin enlazar: quedarían relocalizaciones.
El bloque nuevo ocupa `76:FEA4–FFBE`; las sustituciones están enumeradas en el
constructor y en `qa/build_report.json`. Se verificó que el espacio era relleno FF.

Para verificar la compilación y regenerar BPS/IPS:

```sh
python3 tools/validate_release.py ROM_original.bin Front_Mission_v033_TEST.wsc
```

Incluye las fuentes disponibles de v0.32 y su corpus recuperado de binario en
`history/v032`, el parche base acumulativo, las fuentes nuevas y las herramientas
de parches/Mesen. El corpus recuperado **no sustituye al manifiesto editorial
original ausente de las versiones anteriores**. Las notas antiguas de `history/`
describen su momento histórico; la validación vigente es la de `qa/`.

El reglamento adjunto se conserva como referencia. Su exigencia de BPS acumulativo
y separación entre validación estática, visual y de ejecución se aplicó a la entrega.
