#!/usr/bin/env python3
"""Validate the compact, checked-in Mesen evidence for the native epilogue."""

from __future__ import annotations

import json
import hashlib
import struct
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "epilogue_native"
RUN = QA / "isolated_v035"
EXPECTED_ROM = "bed365a706e13338c8bebc17723fc40f3804a114520524d3ad62f180d44f42c0"
REQUESTED = list(range(3318, 3325)) + list(range(3340, 3358))
ALL_NATIVE = list(range(3318, 3339)) + list(range(3340, 3358))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def png_geometry(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise AssertionError(f"Invalid PNG: {path}")
    return struct.unpack(">II", data[16:24])


def main() -> None:
    summary = load(QA / "native_validation.json")
    run = load(RUN / "final.lua.json")
    isolated = next(item for item in summary["runs"] if item["name"] == "isolated_v035")
    assert isolated["capture_metadata_sha256"] == hashlib.sha256((RUN / "final.json").read_bytes()).hexdigest()

    assert summary["rom_sha256"] == EXPECTED_ROM
    assert summary["rom_modified"] is False
    assert summary["classification"] == "SYNTHETIC_STATE"
    assert summary["requested_text_records"] == len(REQUESTED)
    assert summary["requested_japanese_glyphs"] == 0
    assert summary["requested_unknown_glyphs"] == 0
    assert summary["legacy_tables_read_by_native_ending"] is False
    assert summary["legacy_tables_structurally_valid"] is True
    assert summary["natural_campaign_completion_proven"] is False
    assert summary["linguistic_accuracy_approved"] is False

    records = {row["index"]: row for row in summary["records"]}
    assert sorted(records) == REQUESTED
    for index, row in records.items():
        assert row["japanese_glyphs"] == 0, index
        assert row["unknown_glyphs"] == 0, index
        assert row["terminated"] is True, index
        assert row["secondary_copy_matches"] is True, index
        images = list(RUN.glob(f"text_{index:04d}_frame_*.png"))
        assert images, f"Missing screenshot for record {index}"
        assert all(png_geometry(path) == (237, 144) for path in images)

    assert run["classification"] == "SYNTHETIC_STATE"
    assert run["frames"] == 36000
    assert run["activation_event"] == 88
    assert run["rom_modified"] is False
    assert run["text_pointer_injection"] is False
    assert run["legacy_root_reads"] == [0, 0]
    native = {int(key) for key, value in run["native_index_reads"].items() if value}
    assert native == set(ALL_NATIVE)
    assert set(REQUESTED) <= {int(key) for key, value in run["main_reads"].items() if value}

    trace_counts = Counter()
    for number, line in enumerate((RUN / "trace.tsv").read_text(encoding="utf-8").splitlines()):
        if number == 0:
            assert line == "frame\tkind\taddress\tvalue\tcs\tip"
            continue
        columns = line.split("\t")
        if len(columns) > 1:
            trace_counts[columns[1]] += 1
    assert trace_counts["native_index"] == 39
    assert trace_counts["WRAM_WRITE_EVENT_58"] == 1
    assert trace_counts["WRAM_CLEAR_BATTLE_UPDATE_BIT"] == 1
    assert trace_counts["native_init"] == 1

    assert png_geometry(QA / "native_25_records.png") == (1185, 850)
    assert png_geometry(RUN / "final.png") == (224, 144)
    print("NATIVE EPILOGUE EVIDENCE: PASS")
    print("Classification: SYNTHETIC_STATE")
    print("Native indices: 39/39; requested records: 25/25")
    print("Japanese/unknown glyphs in requested records: 0/0")
    print("Natural campaign completion and linguistic approval: not claimed")


if __name__ == "__main__":
    main()
