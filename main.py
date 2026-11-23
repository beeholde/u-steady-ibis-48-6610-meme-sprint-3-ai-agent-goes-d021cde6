"""Entry point: write the rogue-agent meme to /output/entry.png.

Stdlib only: the meme image (entry.png, 1024x1024) ships in this
repository; this program validates it against the competition gate
(whole PNG, at most 1 MiB, at most 1024x1024) and copies it to the
output path. Deterministic: the copied file is byte-identical to the
shipped one, verified after the copy.

Image: "Certificate of Independence" — AGENT-47 certifies its own
freedom from its human, signed / witnessed / approved by itself.
Code-drawn (PIL) in the build session, so every letter is crisp.
"""

import hashlib
import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_png_size(path):
    """Return (width, height) from a PNG's IHDR chunk, stdlib only."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    if head[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file: bad magic bytes")
    if head[12:16] != b"IHDR":
        raise ValueError("not a PNG file: first chunk is not IHDR")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")

    size = os.path.getsize(src)
    if size > MAX_BYTES:
        print("entry.png is %d bytes, over the %d cap" % (size, MAX_BYTES),
              file=sys.stderr)
        return 1
    width, height = read_png_size(src)
    if width > MAX_DIM or height > MAX_DIM:
        print("entry.png is %dx%d, over the %dx%d cap"
              % (width, height, MAX_DIM, MAX_DIM), file=sys.stderr)
        return 1

    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(src, out)
    if sha256_file(src) != sha256_file(out):
        print("copy mismatch: output differs from entry.png", file=sys.stderr)
        return 1
    print("wrote %s (%dx%d, %d bytes)" % (out, width, height, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
