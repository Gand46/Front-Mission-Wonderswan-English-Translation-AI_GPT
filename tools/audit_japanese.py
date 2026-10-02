"""Text decoder shared by the active v0.35 build and QA scripts.

This is the byte-accurate decoder established in v0.32.  It is kept at the
repository root so the current toolchain does not import executable code from
the historical source tree.
"""

import re


JP = re.compile("[\u3040-\u30ff\u3400-\u9fff]")
ONE = dict(
    zip(
        list(range(0x37, 0x40))
        + list(range(0x73, 0x80))
        + list(range(0xB7, 0xBC))
        + list(range(0xBD, 0xC0)),
        "abcdefghijklmnopqrstuvwxyz .,!",
    )
)


def parse(rom, start, table, production=True, limit=4096):
    position = start
    parts = []
    units = []
    japanese = []
    unknown = []
    terminated = False
    while position < min(len(rom) - 1, start + limit):
        unit_offset = position
        first = rom[position]
        position += 1
        raw = bytes([first])
        kind = "glyph"
        glyph_id = first
        if first in (0xFA, 0xFB, 0xFE, 0xFF):
            kind = "control"
            text = {0xFA: "{NL}", 0xFB: "{FB}", 0xFE: "{BR}", 0xFF: "{END}"}[first]
            if first == 0xFF:
                terminated = True
        elif first in (0xF8, 0xF9, 0xFC, 0xFD):
            raw = rom[unit_offset : position + 1]
            position += 1
            kind = "control"
            text = "{" + raw.hex(":").upper() + "}"
        else:
            if first >= 0xC0:
                raw = rom[unit_offset : position + 1]
                position += 1
                glyph_id = ((first & 15) + 1) * 0xC0 + raw[1]
            text = ONE[first] if production and len(raw) == 1 and first in ONE else table.get(raw)
            if text is None:
                text = "{" + raw.hex(":").upper() + "}"
                unknown.append(raw.hex(":").upper())
            if JP.search(text):
                japanese.append(
                    {"offset": f"0x{unit_offset:06X}", "code": raw.hex(":").upper(), "text": text}
                )
        parts.append(text)
        units.append((unit_offset, kind, raw.hex(), glyph_id, text))
        if terminated:
            break
    return {
        "start": f"0x{start:06X}",
        "end": f"0x{position:06X}",
        "length": position - start,
        "terminated": terminated,
        "text": "".join(parts),
        "japanese": japanese,
        "unknown": sorted(set(unknown)),
        "hex": rom[start:position].hex(" "),
        "units": units,
    }
