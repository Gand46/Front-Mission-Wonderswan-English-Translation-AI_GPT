# Changelog

## v0.35-TEST — pre-release package

- Repairs secondary near-pointer tables 3317 and 3339 with 25 English targets
  and two valid `FFFF` sentinels.
- Relocates two complete dialogues and seven aliases without changing their text.
- Adds six same-bank copies required by the 16-bit table format.
- Preserves all other 3,356 main text byte sequences and 2,972 graphics
  descriptors/payloads.
- Verifies cumulative and incremental BPS/IPS patches and an exact rebuild from
  both the clean Japanese ROM and canonical v0.34.
- Adds native epilogue QA: its real controller selects all 39 indices; the 25
  requested translated subtitles are captured with no Japanese/unknown glyphs
  and no observed clipping under a documented synthetic state.
- Cleans the GitHub source tree: no ROM, no caches, no redundant historical ZIPs;
  active build and QA dependencies are available from repository-root paths.
- Classifies the publication as a testing-ready pre-RC. Linguistic approval,
  natural full-game completion, complete credits QA, and final graphics coverage
  remain open.

The ROM bytes and release patch are unchanged by the repository cleanup and the
native epilogue validation.
