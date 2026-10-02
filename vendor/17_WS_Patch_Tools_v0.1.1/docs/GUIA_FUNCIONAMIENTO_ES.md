# Guía 17 — WS Patch Tools

**Versión analizada:** 0.1.1  
**Fecha de validación:** 2026-09-02  
**Entorno:** Linux x86_64, Python 3.13.5  
**Objetivo:** uso automatizado/headless desde ChatGPT y desde la fuente del proyecto de traducción WonderSwan.


## Correcciones y empaquetado v0.1.1

- Desactivada la escritura de bytecode Python.
- Añadido `vendor/install_xdelta3_archive.sh`, que instala offline el asset Linux x86_64 oficial de xdelta3 3.2.0 desde un archivo local y exige su SHA-256 oficial antes de copiarlo a `vendor/bin/xdelta3`.
- IPS/BPS nativos no cambian y siguen funcionando completamente offline sin xdelta.

## 1. Qué hace

Frontend portable para crear, aplicar y verificar:

- IPS;
- BPS;
- xdelta/VCDIFF mediante backend externo.

IPS y BPS son implementaciones Python propias, offline.

## 2. Estado validado

**Estado: APROBADO; XDELTA EXTERNO NO DISPONIBLE EN ESTE HOST.**

Backend actual:

```json
{
  "ips": "native",
  "bps": "native",
  "xdelta3": {
    "available": false
  }
}
```

Pruebas:

- IPS create/apply/verify: PASS;
- BPS create/apply/verify: PASS;
- BPS corrupto: rechazado por CRC;
- prueba integrada 512 KiB: output SHA-256 idéntico al target;
- 100 casos aleatorios adicionales de tamaños/cambios distintos:
  - IPS round-trip: PASS;
  - BPS round-trip: PASS.

El self-test xdelta usa un backend simulado; no equivale a haber ejecutado el xdelta3 oficial.

## 3. Crear BPS

Formato recomendado para releases:

```bash
./run.sh create \
  --format bps \
  original.wsc \
  traducida.wsc \
  traduccion.bps \
  --metadata 'Project version 1.0' \
  --json
```

Verificar:

```bash
./run.sh verify \
  traduccion.bps \
  original.wsc \
  traducida.wsc \
  --json
```

Aplicar:

```bash
./run.sh apply \
  traduccion.bps \
  original.wsc \
  reconstruida.wsc \
  --json
```

## 4. Crear IPS

```bash
./run.sh create \
  --format ips \
  original.wsc \
  traducida.wsc \
  traduccion.ips \
  --json
```

IPS no tiene CRC interno equivalente a BPS, por lo que `verify` reconstruye y compara el resultado esperado.

## 5. Xdelta

Backend resolution:

```text
--xdelta-bin
WS_XDELTA3_BIN
vendor/bin/xdelta3
xdelta3 del sistema
```

Instalación portable futura:

```text
17_WS_Patch_Tools_v0.1.1/
└── vendor/
    └── bin/
        └── xdelta3
```

Después:

```bash
chmod +x vendor/bin/xdelta3
./run.sh backend --json
```

Crear:

```bash
./run.sh create \
  --format xdelta \
  original.wsc \
  traducida.wsc \
  traduccion.xdelta \
  --json
```

## 6. Implementación BPS

La implementación genera BPS estándar:

```text
BPS1
source size
target size
metadata
actions
source CRC32
target CRC32
patch CRC32
```

El creador actual usa principalmente:

```text
SourceRead
TargetRead
```

El aplicador admite también:

```text
SourceCopy
TargetCopy
```

## 7. Limitaciones

### 7.1 BPS válido pero no optimizado como Flips

Al no buscar coincidencias complejas con SourceCopy/TargetCopy durante creación, algunos parches serán más grandes que los producidos por Flips/beat.

Para distribución final donde el tamaño sea importante, comparar:

```text
WS_Patch_Tools BPS
vs
Flips BPS
```

cuando Flips esté disponible.

### 7.2 IPS y límite de 24 bits

La implementación rechaza targets `> 0xFFFFFF` bytes. Esto es conservador y puede impedir un caso límite cercano a 16 MiB.

Para ROMs grandes preferir BPS/xdelta.

### 7.3 Offset `EOF` en IPS

IPS clásico tiene una ambigüedad conocida alrededor del valor de offset cuyos tres bytes son ASCII `EOF`. No confiar en IPS como único formato de release para casos extremos.

### 7.4 xdelta

Sin xdelta3 real:

```text
create/apply xdelta
```

no funcionan.

## 8. Política de release recomendada

Generar:

```text
traduccion.bps    principal
traduccion.ips    compatibilidad si aplica
traduccion.xdelta opcional
SHA256SUMS
README
```

y siempre registrar SHA-256 de:

```text
ROM original soportada
ROM traducida
patch
```

## 9. Fuentes

- BPS specification: https://github.com/bates64/flips/blob/master/bps_spec.md
- Flips: https://github.com/Sir-Walrus/Flips
- xdelta: https://github.com/jmacd/xdelta
