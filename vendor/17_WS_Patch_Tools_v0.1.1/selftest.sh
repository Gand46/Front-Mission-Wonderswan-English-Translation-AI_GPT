#!/usr/bin/env bash
export PYTHONDONTWRITEBYTECODE=1
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
python3 "$ROOT/tests/make_fixture.py" "$TMP"
for F in ips bps; do
  "$ROOT/run.sh" create --format "$F" "$TMP/source.bin" "$TMP/target.bin" "$TMP/p.$F" --metadata selftest --json > "$TMP/create-$F.json"
  "$ROOT/run.sh" info "$TMP/p.$F" --json > "$TMP/info-$F.json"
  "$ROOT/run.sh" apply "$TMP/p.$F" "$TMP/source.bin" "$TMP/out-$F.bin" --json >/dev/null
  cmp "$TMP/out-$F.bin" "$TMP/target.bin"
  "$ROOT/run.sh" verify "$TMP/p.$F" "$TMP/source.bin" "$TMP/target.bin" --json | grep -q 'true'
done
# Corrupt BPS CRC and ensure it is rejected.
cp "$TMP/p.bps" "$TMP/bad.bps"; python3 - "$TMP/bad.bps" <<'PYTEST'
import sys
p=sys.argv[1]; b=bytearray(open(p,'rb').read()); b[-1]^=1; open(p,'wb').write(b)
PYTEST
if "$ROOT/run.sh" apply "$TMP/bad.bps" "$TMP/source.bin" "$TMP/no.bin" --json >/dev/null 2>&1; then echo 'corrupt BPS unexpectedly accepted' >&2; exit 1; fi
"$ROOT/run.sh" backend --json | grep -q 'native'
export WS_XDELTA3_BIN="$ROOT/tests/fake_xdelta3.py"
"$ROOT/run.sh" backend --json | grep -q 'fake-selftest'
"$ROOT/run.sh" create --format xdelta "$TMP/source.bin" "$TMP/target.bin" "$TMP/p.xdelta" --json >/dev/null
"$ROOT/run.sh" apply "$TMP/p.xdelta" "$TMP/source.bin" "$TMP/out-xdelta.bin" --json >/dev/null
cmp "$TMP/out-xdelta.bin" "$TMP/target.bin"
"$ROOT/run.sh" verify "$TMP/p.xdelta" "$TMP/source.bin" "$TMP/target.bin" --json | grep -q 'true'
if find "$ROOT" -type d -name __pycache__ | grep -q .; then echo '__pycache__ created' >&2; exit 1; fi
echo 'WS_Patch_Tools selftest: PASS'
