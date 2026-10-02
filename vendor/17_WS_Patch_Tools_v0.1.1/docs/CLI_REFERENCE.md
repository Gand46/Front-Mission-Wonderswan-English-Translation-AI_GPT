# CLI reference

- `backend [--json]`
- `info PATCH [--json]`
- `create --format ips|bps|xdelta SOURCE TARGET PATCH [--metadata TEXT] [--json]`
- `apply PATCH SOURCE OUTPUT [--format auto|ips|bps|xdelta] [--json]`
- `verify PATCH SOURCE TARGET [--format auto|ips|bps|xdelta] [--json]`

Backend resolution for xdelta3: `--xdelta-bin`, `WS_XDELTA3_BIN`,
`vendor/bin/xdelta3`, system `xdelta3`.
