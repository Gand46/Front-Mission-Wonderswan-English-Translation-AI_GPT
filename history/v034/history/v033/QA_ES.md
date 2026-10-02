# Validación v0.33-TEST

## Resultado

Corrección integrada y casos examinados aprobados. No se declara aprobación global.

| Comprobación | Evidencia | Resultado y límite |
| --- | --- | --- |
| Construcción desde original y v0.32 | `qa/static_validation.json` | Salidas idénticas; checksum correcto; bases incorrectas rechazadas |
| BPS/IPS acumulativos y delta | mismo informe | Cuatro aplicaciones reconstruyen exactamente la ROM final |
| Integridad del contenido | mismo informe | 3358 entradas/tablas del corpus y fuentes sin cambios; 231 entradas de cuadrícula preservadas |
| Recorrido sin inyección | `qa/route/` | 24000 frames; capturas de entrada de nombre y combate; no es una partida completa |
| Frases reportadas, segundo motor | `qa/secondary/` | Registros 2817 y 2821 completos; punteros sustituidos en ejecución, ROM sin modificar |
| Regresión del primer motor | `qa/primary/` | Ocho registros: 137, 138, 139, 496, 545, 486, 1011 y 2099; sustitución controlada |
| Comparación A/B con v0.32 | `qa/before_v032/` frente a `qa/secondary/` | Mismo script y textos: v0.32 corta `deat` y `ma`; v0.33 muestra las frases completas |
| Nombre FC y glifos FD, segundo motor | `qa/secondary_controls/` | Registros 956 y 545; nombre Lloyd, texto siguiente y atributos legibles |
| Salto automático sin saltos manuales | `qa/stress/` | Texto sintético largo en ambos motores; palabras enteras al pasar de línea y página |
| Rama de ventana estrecha | `qa/stress_narrow/` | Modo 120 px forzado en WRAM, texto sintético; palabras enteras; no prueba natural de una ventana estrecha |

Las pruebas de ejecución terminaron con código 0 y sin timeout. El valor `passed`
de los informes de captura certifica la ejecución/captura, no por sí solo la calidad
de la traducción. Las capturas indicadas se revisaron visualmente por separado.
Los registros pueden contener avisos de lectura de memoria no inicializada del
emulador; no se interpretan como una garantía de ausencia total de errores.
También se repitieron las 19 pruebas unitarias heredadas del parser, IPS y
fuentes: todas pasaron. Son comprobaciones auxiliares, no un test del CPU nuevo.

## Capturas principales

- `qa/secondary/record_2817_age_0480_CONTROLLED.png`: `Olson: / Avenge her death?`.
- `qa/secondary/record_2821_age_0480_CONTROLLED.png`: `Olson: / Join us. You may`.
- `qa/secondary/record_2821_age_0980_CONTROLLED.png`: `find the pilot / who killed her.`.
- `qa/secondary/record_2821_age_1480_CONTROLLED.png`: cierre `What do you say?`.
- `qa/stress/stress_0983_age_0620_SYNTHETIC.png`: ventana ancha, `Alpha beta gamma delta / epsilon zeta eta theta`.
- `qa/stress/stress_0955_age_0620_SYNTHETIC.png`: mismas palabras y `iota kappa.` en el primer motor.
- `qa/stress/stress_0984_age_0620_SYNTHETIC.png`: 22 letras a 8 px, salto antes de `W`.
- `qa/stress_narrow/stress_0983_age_0620_SYNTHETIC.png`: `Alpha beta gamma / delta epsilon`.
- `qa/stress_narrow/stress_0983_age_1270_SYNTHETIC.png`: `zeta eta theta / iota kappa.`.

Los retratos, fondos y contextos de las capturas CONTROLLED no son prueba de haber
alcanzado las escenas originales. Después del último registro controlado algunos
scripts siguen capturando el recorrido; solo las capturas listadas evidencian el caso.
El desplazamiento de una línea de la página anterior es el comportamiento del juego,
no una duplicación del guion por el parche.

## Repetir Mesen

Requiere un ejecutable Mesen compatible aportado por el usuario. No se incluye.
Ejecuta desde la carpeta del paquete y cambia las rutas por las de tu sistema:

```sh
python3 vendor/mesen_visualization_source_v1.1.0/scripts/mesen_visual.py capture --mesen /ruta/Mesen --rom /ruta/Front_Mission_v033_TEST.wsc --lua qa/reported_secondary.lua --output /ruta/resultados/secondary/final.png --timeout 50 --timeout-grace 5 --normalize-wonderswan
```

Para el recorrido usa `qa/route_24000.lua` y timeout 60. Para el primer motor usa
`qa/controlled_renderer_wordaware.lua`. Para FC/FD usa `qa/secondary_controls.lua`.
La salida debe estar en una carpeta nueva para conservar la evidencia anterior.

Las pruebas sintéticas necesitan una ROM temporal distinta, jamás la ROM de juego:

```sh
python3 qa/make_stress_rom.py /ruta/Front_Mission_v033_TEST.wsc /ruta/SYNTHETIC_ONLY.wsc
```

Con esa ROM usa `qa/stress.lua` o `qa/stress_narrow.lua`. El segundo modifica un
byte WRAM para seleccionar la rama estrecha. `qa/prepare_variants.py` regenera
ambas variantes controladas desde sus scripts base.

SHA-256 de Mesen usado:
`ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`.

SHA-256 de ROM sintética final:
`6db27465dac4bac82cd327eb228279764e02bbed2f9a346b7f3abe9559d5966e`.

## Pendientes conservados

Reproducir naturalmente la escena de Olson con una partida guardada; recorrer
los demás contextos de ventana; probar expansiones FC/FD cerca del borde;
investigar las tablas anidadas 3317 y 3339 (25 hijos); revisar texto gráfico y
resto del juego. No se cambió contenido pendiente ajeno a esta corrección.
