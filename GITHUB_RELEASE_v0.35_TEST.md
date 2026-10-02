# Front Mission WSC English v0.35-TEST — Pre-RC testing build

This pre-release contains the latest cumulative English patch. It is ready for
broader technical and playtesting feedback, but it is not yet a formal Release
Candidate.

## Verified

- Reproducible 8 MiB output from the exact clean Japanese ROM.
- Cumulative BPS round trip and WonderSwan checksum `BE92`.
- Structural repair of secondary tables 3317/3339.
- Native epilogue controller coverage for the 25 requested translated subtitles:
  25/25 captured, with zero Japanese or unknown glyphs in those records.
- Preservation checks for 3,356 other text sequences and 2,972 graphics resources.

## Still open before RC

- Natural full-game playthrough through the complete credits.
- Whole-project linguistic and terminology approval.
- Final classification/translation of remaining graphics and Japanese candidates.
- Approval of the presentation after the epilogue signature.

## Patch base

Apply `Front_Mission_WSC_English_v0.35_TEST_Cumulative.bps` to the exact 8 MiB
Japanese ROM with SHA-256:

`d1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380`

Expected patched SHA-256:

`bed365a706e13338c8bebc17723fc40f3804a114520524d3ad62f180d44f42c0`

No ROM image is included.
