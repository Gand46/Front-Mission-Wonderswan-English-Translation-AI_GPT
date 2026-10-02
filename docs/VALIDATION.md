# Validation and known issues

The packaged assets remain **v0.35-TEST public testing pre-release**. This packaging compared the attached BPS, release ZIP BPS and source BPS byte for byte; verified the BPS1 self CRC32, source/target sizes and CRC fields; and compared the private patched-ROM copy in the supplied FULL archive to the documented target SHA-256, CRC32 and checksum. That ROM is excluded from both deliverables. A matching target copy does not prove a fresh rebuild or BPS application from the clean original.

| Area | Status | Boundary |
| --- | --- | --- |
| Three cumulative BPS copies | PASS in this packaging | Identical SHA-256 3834387947741d4ce57004d914a21021eea84138d44974735825ab300d99a954. |
| BPS1 integrity | PASS in this packaging | Header and patch CRC32 verified; source/target CRC fields inspected. |
| Private target-copy identity | PASS in this packaging | 8 MiB, expected SHA-256 and CRC32 e8daee38, cartridge BE92; ROM not distributed. |
| New build and BPS round trip from clean original | NOT_RUN here | Original Japanese ROM unavailable; archived qa/static_validation.json records earlier PASS. |
| Structural repair | PASS archived | 25 children, two FFFF sentinels, allowed ranges; no wording edits. |
| Native ending captions | PASS_SYNTHETIC archived | SYNTHETIC_STATE; 25 requested records, 0 Japanese/unknown glyphs within these captures. Not a natural or linguistic PASS. |
| Whole-game linguistic quality | FAIL_CORRECTIONS_REQUIRED | Later review in project context identifies 10/14 epilogue dialogues and 25 ending fragments requiring corrections; those separate review files were not attached here. |
| Full visual approval, natural ending/credits | NOT_VALIDATED | No continuous natural playthrough through credits or global inspection. |
| All Japanese text/graphics resolved | NOT_VALIDATED | Bounded scans and graphics inventories do not establish whole-game coverage. |

Known limits: one overwide word can split; dynamic name expansion and narrow windows need contextual QA; other consumers of the repaired near arrays remain unknown; post-signature and credits presentation is unapproved. See original version-scoped reports in docs/ESTADO_PRE_RC_ES.md, docs/VALIDACION_EPILOGO_ES.md, history/v034/VALIDACION_ES.md and history/v034/history/v033/QA_ES.md. Personal local paths were redacted in metadata only; the stored native metadata hash was updated. Screenshots, trace data, ROM target and BPS bytes were unchanged.
