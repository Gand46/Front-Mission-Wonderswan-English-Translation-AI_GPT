"""Small ROM and IPS helpers used by the active v0.35 toolchain."""

from __future__ import annotations

import hashlib


CLEAN_SHA256 = "d1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380"
POINTER_TABLE = 0x7427C0
TEXT_COUNT = 3358


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_ips(base: bytes, patch: bytes) -> bytes:
    if patch[:5] != b"PATCH":
        raise ValueError("Invalid IPS header")
    out = bytearray(base)
    position = 5
    while True:
        if position + 3 > len(patch):
            raise ValueError("Truncated IPS patch")
        if patch[position : position + 3] == b"EOF":
            if position + 3 != len(patch):
                raise ValueError("Unexpected IPS trailer")
            return bytes(out)
        offset = int.from_bytes(patch[position : position + 3], "big")
        position += 3
        if position + 2 > len(patch):
            raise ValueError("Truncated IPS record size")
        length = int.from_bytes(patch[position : position + 2], "big")
        position += 2
        if length:
            data = patch[position : position + length]
            position += length
            if len(data) != length:
                raise ValueError("Truncated IPS record")
        else:
            if position + 3 > len(patch):
                raise ValueError("Truncated IPS RLE record")
            length = int.from_bytes(patch[position : position + 2], "big")
            data = bytes([patch[position + 2]]) * length
            position += 3
        if offset + length > len(out):
            raise ValueError("IPS record exceeds the ROM")
        out[offset : offset + length] = data


def make_ips(base: bytes, modified: bytes) -> bytes:
    if len(base) != len(modified):
        raise ValueError("ROM size changed")
    out = bytearray(b"PATCH")
    position = 0
    while position < len(base):
        if base[position] == modified[position]:
            position += 1
            continue
        start = position
        if start == 0x454F46:  # Reserved IPS EOF offset.
            start -= 1
        while (
            position < len(base)
            and base[position] != modified[position]
            and position - start < 65535
        ):
            position += 1
        data = modified[start:position]
        out += start.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    return bytes(out + b"EOF")


def text_target(rom: bytes, index: int) -> int:
    pointer = POINTER_TABLE + 4 * index
    offset = int.from_bytes(rom[pointer : pointer + 2], "little")
    segment = int.from_bytes(rom[pointer + 2 : pointer + 4], "little")
    if segment not in range(0x8000, 0x10000, 0x1000):
        raise ValueError(f"Unexpected segment for text {index}: 0x{segment:04X}")
    return 0x700000 + (segment >> 12) * 0x10000 + offset
