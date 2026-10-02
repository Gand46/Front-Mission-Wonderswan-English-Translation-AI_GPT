#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARC="${1:-}"
EXPECTED="480295c7a41fea6503659f19ddc61676c0df4834e2292846ba97de30c68c2397"
if [[ -z "$ARC" || ! -f "$ARC" ]]; then
  echo "Usage: $0 /path/to/xdelta3-3.2.0-linux-x86_64.tar.gz" >&2
  exit 2
fi
ACTUAL="$(sha256sum "$ARC" | awk '{print $1}')"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "SHA-256 mismatch: expected $EXPECTED got $ACTUAL" >&2
  exit 3
fi
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
tar -xzf "$ARC" -C "$TMP"
BIN="$(find "$TMP" -type f -name xdelta3 -perm -111 | head -n1 || true)"
if [[ -z "$BIN" ]]; then echo "xdelta3 executable not found in archive" >&2; exit 4; fi
install -m 0755 "$BIN" "$ROOT/vendor/bin/xdelta3"
"$ROOT/vendor/bin/xdelta3" -V | head -n1
"$ROOT/run.sh" backend --json
