# Contributing

Use `PROJECT_STATE.json` as the current source of truth. Historical reports may
describe defects that v0.35 already repaired.

For a text or layout change:

1. Record the entry, scene, original bytes, intended text, and available space.
2. Keep control codes and pointer ownership explicit; do not treat unproven free
   bytes as available storage.
3. Rebuild from the exact clean ROM with `tools/build_v035.py`.
4. Run `tools/audit_v035.py` and `tools/validate_native_evidence.py`.
5. Test the affected scene in Mesen and attach screenshots plus a reproducible
   route or save state.
6. Update `PROJECT_STATE.json`, `CHANGELOG.md`, and release hashes.

Bug reports should identify the v0.35 ROM SHA-256, emulator/version, access
method, exact scene, observed text, expected text, and a screenshot. Do not
attach commercial ROM images.
