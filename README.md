# Front Mission WonderSwan Color — English v0.35-TEST

Japanese to English fan translation of the Japanese WonderSwan Color game. This is a **public testing pre-release, not a formal RC or final translation**. The v0.35 change repairs secondary pointer tables without rewriting dialogue. Whole-game linguistic approval, a natural campaign through credits, remaining graphics classification and final presentation approval are open. See [validation](docs/VALIDATION.md).

## Apply the cumulative patch

Provide your own unmodified Japanese ROM locally. The project's reference filename is `Front Mission (2002-07-12)(Squaresoft)[SWJ-SQRC10].bin`; exact size and SHA-256 are decisive.

| Item | Size | SHA-256 | CRC32 / checksum |
| --- | ---: | --- | --- |
| Japanese original (documented; not supplied) | 8,388,608 | `d1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380` | BPS source CRC `2f9e2560` |
| `patches/v035_TEST_from_clean.bps` | 157,734 | `3834387947741d4ce57004d914a21021eea84138d44974735825ab300d99a954` | BPS CRC `7ad99dec` |
| Resulting v0.35 ROM (verified against private supplied copy; never distributed) | 8,388,608 | `bed365a706e13338c8bebc17723fc40f3804a114520524d3ad62f180d44f42c0` | CRC `e8daee38`; WonderSwan checksum `BE92` |

Apply that BPS **once directly to the clean original** using a compatible BPS patcher. The included patch tool is documented in its [CLI reference](vendor/17_WS_Patch_Tools_v0.1.1/docs/CLI_REFERENCE.md). Check the output SHA-256. The separate release BPS and repository BPS have identical bytes. Incremental patches in the source tree are not the public installation path.

## Build from available sources

The active Python 3 builder uses the standard library. It checks the private original ROM hash, applies the required v0.34 baseline IPS internally, then applies the bounded repair specification in `data/repair.json`. It refuses an unknown base and an existing output. The earlier translation is represented by a cumulative baseline patch and recovered historical sources; the older canonical editorial manifest has **not** been recovered. This procedure is a reproducible binary build with the available project inputs, not a claim that every old editorial decision has an independent source.

```sh
python3 tools/build_v035.py /private/clean-japanese.bin /private/Front_Mission_v035_TEST.wsc
python3 tools/audit_v035.py /private/clean-japanese.bin /private/Front_Mission_v035_TEST.wsc
python3 tools/validate_native_evidence.py
```

The audit rewrites QA reports and patches; use a working copy to preserve checked-in evidence. Windows launchers: `build_windows.bat "clean-japanese.bin" "Front_Mission_v035_TEST.wsc"` and `validate_windows.bat "clean-japanese.bin" "Front_Mission_v035_AUDIT.wsc"`. Linux syntax/JSON checks and checked-in evidence validation were run for this packaging. ROM-dependent reconstruction and BPS application were **NOT_RUN** here because the exact original ROM was unavailable. Windows and macOS were not run here. For optional native QA, provide Mesen 2.1.1 separately; the Unix capture wrapper also uses Pillow. See the [existing reproduction guide](docs/VALIDACION_EPILOGO_ES.md).

## Layout

| Path | Purpose |
| --- | --- |
| `tools/`, `data/`, Windows BAT files | Active builder, text codec, repair specification and audits. |
| `patches/baseline_v034_from_clean.ips` | Required input to rebuild v0.35 from the clean ROM. |
| `patches/v035_TEST_from_clean.bps` | Public cumulative patch; other patches serve historical/audit uses. |
| `qa/`, `docs/` | Reports, actual captures/traces and technical documentation. |
| `history/` | Prior source/assembly/graphics work and version-specific evidence. |
| `vendor/` | Source tools and their notices; no emulator binary. |
| `ORGANIZATION_MANIFEST.json` | Per-file origin and disposition. |

## Architecture and reverse-engineering findings

The main text pointer table starts at **ROM file offset `0x7427C0`**, with 3,358 entries. Each four-byte entry stores a little-endian offset and segment; `tools/common.py` defines the verified mapping to a ROM offset for segments `0x8000`–`0xF000`. This implementation mapping is not a general conversion between CPU, RAM and VRAM addresses. The historical audit separates 3,125 text/control entries, 231 preserved name-entry cells and two nested arrays.

For v0.35, arrays **3317** (`0x7CC124`, seven children) and **3339** (`0x7CC58C`, 18 children) receive same-bank near pointers and `FFFF` sentinels. Two overlapping dialogues are relocated; seven main-table aliases are updated; six children are copied into that bank. The reclaimed area is `0x7C9F48`–`0x7CA0D0` (393 bytes, 329 used). The builder checks allowed changes and recomputes the two-byte cartridge checksum. The archived audit reports 3,356 other text sequences and 2,972 graphics descriptors/payloads unchanged.

The native epilogue selects from a 39-index table at ROM file offset **`0x7EC6A8`**. The documented `E000:F9C5` instruction selects an index and `6000:CE20` reads the main table and calls a secondary renderer. The repaired legacy arrays were **not read on this observed epilogue route**; their other consumer is `NOT_IDENTIFIED`. The synthetic route writes event `0x58` in WRAM and clears the battle-update bit at WRAM `0x0900`; it does not inject text pointers or modify ROM bytes.

Earlier work moved bank-crossing record 1011 from `0x7BFFFB`–`0x7C0043` to `0x7C0000`; v0.33 changed word wrapping and glyph advances; v0.34 translated a compressed Sakata advertising graphic. Its descriptor is at `0x749BF6`, its stream `0x00DAEA`–`0x00ECA1`, and decoder `4000:6E86` writes 6,656 bytes to VRAM `0x6600`–`0x7FFF`. See the [finding inventory](docs/TECHNICAL_FINDINGS.md), [memory map](docs/MEMORY_MAP.csv) and [consumer table](docs/TEXT_CONSUMERS.csv) for version, provenance and certainty. The v0.32 binary-derived corpus is a recovered snapshot, **not** the missing editorial manifest.

## Validation and known issues

Archived evidence reports an exact cumulative BPS round trip, structural repair, and 25/25 requested epilogue subtitles captured under `SYNTHETIC_STATE`, with zero Japanese or unknown glyphs within those captions. This does not establish linguistic fidelity, global visual approval, natural completion, or absence of Japanese elsewhere. Later quality review in the project context identified remaining corrections; no later edits were merged into these v0.35 files. See [validation](docs/VALIDATION.md) for status and methods.

## Credits and licensing

Unofficial fan translation. The provided records do not establish a general translation license or named authorship, so neither is invented here. Game content has its own rights. Bundled `WS_Patch_Tools` has its own [MIT license](vendor/17_WS_Patch_Tools_v0.1.1/licenses/PROJECT_MIT.txt) and [source notice](vendor/17_WS_Patch_Tools_v0.1.1/SOURCE_ORIGIN.md). Mesen itself is not included. Existing credits and historical references remain in their respective files.
