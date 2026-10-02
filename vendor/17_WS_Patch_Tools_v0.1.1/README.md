# WS Patch Tools v0.1.1

**Guía completa en español:** `GUIA_FUNCIONAMIENTO_ES.md`
Portable IPS/BPS/xdelta patch frontend for ROM translation releases.
IPS and BPS creation/application are native Python implementations; xdelta3 is
an optional external backend.

```bash
./selftest.sh
./run.sh create --format bps original.wsc translated.wsc patch.bps --json
./run.sh apply patch.bps original.wsc rebuilt.wsc --json
./run.sh verify patch.bps original.wsc translated.wsc --json
./run.sh create --format ips original.wsc translated.wsc patch.ips --json
./run.sh backend --json
```
