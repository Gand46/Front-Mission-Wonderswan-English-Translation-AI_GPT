# Reference / external projects

This package's IPS/BPS implementation is original MIT-licensed code. The
following projects are references or optional external engines and are not
bundled in this ZIP:

- Floating IPS / Flips: https://github.com/Sir-Walrus/Flips
  - pinned release: v198
  - release commit: `359d414cff73b3e0400871d3c288a59b36564834`
- xdelta: https://github.com/jmacd/xdelta
  - pinned release: v3.2.0 (2026-06-21)
  - release commit: `ff322e592383227b0d65ddfde7e0e5bbc504dc15`
  - official Linux x86_64 asset SHA-256:
    `480295c7a41fea6503659f19ddc61676c0df4834e2292846ba97de30c68c2397`

If you place the official xdelta3 executable at `vendor/bin/xdelta3`, this
package will use it automatically.
