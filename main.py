#!/usr/bin/env python3
"""Entry for news-image-20261122: copy the drawn broadsheet to the output.

The picture itself is drawn by tools/make_image.py into assets/entry.png
(a 1024x1024 PNG, well under 1 MiB). This program only copies those exact
bytes to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the
grader), after checking the file really is a whole, valid PNG of the size
the bounty allows. No network, no clock, no randomness: every run writes
identical bytes.
"""

import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "assets", "entry.png")
MAX_BYTES = 1_048_576
MAX_SIDE = 1024

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"entry: invalid image: {message}", file=sys.stderr)
    sys.exit(1)


def read_png(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        fail(f"file is {len(data)} bytes, over the {MAX_BYTES} byte limit")
    if data[:8] != PNG_MAGIC:
        fail("does not start with the PNG signature")
    pos = 8
    first = True
    width = height = None
    bit_depth = colour_type = None
    idat_parts = []
    saw_iend = False
    while pos + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 12 + length
        if end > len(data):
            fail(f"chunk {kind!r} runs past the end of the file")
        body = data[pos + 8:pos + 8 + length]
        stored_crc, = struct.unpack(">I", data[pos + 8 + length:end])
        if zlib.crc32(kind + body) & 0xFFFFFFFF != stored_crc:
            fail(f"chunk {kind!r} has a bad CRC")
        if first:
            if kind != b"IHDR":
                fail("first chunk is not IHDR")
            if length != 13:
                fail("IHDR is not 13 bytes")
            width, height, depth, ctype = struct.unpack(">IIBB", body[:10])
            if width > MAX_SIDE or height > MAX_SIDE:
                fail(f"image is {width}x{height}, over {MAX_SIDE}x{MAX_SIDE}")
            if width == 0 or height == 0:
                fail("image has a zero dimension")
            if ctype not in (0, 2, 3, 4, 6):
                fail(f"unknown PNG colour type {ctype}")
            bit_depth, colour_type = depth, ctype
            first = False
        if kind == b"IDAT":
            idat_parts.append(body)
        if kind == b"IEND":
            if length != 0:
                fail("IEND carries data")
            if end != len(data):
                fail("bytes follow the IEND chunk")
            saw_iend = True
            break
        pos = end
    if first:
        fail("no IHDR chunk found")
    if not saw_iend:
        fail("no IEND chunk found")
    if not idat_parts:
        fail("no IDAT chunk found")
    # The pixel data must inflate to exactly what the header promises:
    # one filter byte plus one row of samples per scanline.
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour_type]
    bits_per_pixel = channels * bit_depth
    row_bytes = (width * bits_per_pixel + 7) // 8
    try:
        raw = zlib.decompress(b"".join(idat_parts))
    except zlib.error as exc:
        fail(f"IDAT data does not inflate: {exc}")
    if len(raw) != height * (1 + row_bytes):
        fail(f"inflated image data is {len(raw)} bytes, expected "
             f"{height * (1 + row_bytes)}")
    return data, width, height


def main():
    data, width, height = read_png(SOURCE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    with open(dest, "wb") as handle:
        handle.write(data)
    print(f"entry: wrote {dest} ({width}x{height}, {len(data)} bytes)")


if __name__ == "__main__":
    main()
