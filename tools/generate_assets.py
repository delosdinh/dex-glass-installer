#!/usr/bin/env python3
"""Generate original lightweight Kodi skin PNGs with no third-party dependencies.

Run from repository root:
    python tools/generate_assets.py

Textures are intended for an independent skin using kodi/Includes_DexGlass.xml.
No Dex Hub, Applify/Pyrus or Apple assets are included.
"""
from pathlib import Path
import math
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "media" / "dexglass"


def png(path, width, height, pixel):
    """Save an RGBA PNG using the Python standard library."""
    data = bytearray()
    for y in range(height):
        data.append(0)  # PNG filter: None
        for x in range(width):
            data.extend(pixel(x, y))
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) +
                     chunk(b"IDAT", zlib.compress(bytes(data), 8)) + chunk(b"IEND", b""))


def scrim(x, y):
    """Full-bleed black veil, stronger left/bottom and transparent to right."""
    horiz = max(0, 1 - x / 1920)
    bottom = max(0, (y - 420) / 660)
    alpha = int(min(240, 25 + 170 * horiz ** 1.4 + 65 * bottom))
    return 4, 7, 14, alpha


def fallback(x, y):
    """Original dark blue-gray ambient backdrop, used if no artwork exists."""
    radial = max(0, 1 - math.hypot((x - 1350) / 1450, (y - 310) / 1100))
    return int(10 + 30 * radial), int(14 + 40 * radial), int(27 + 65 * radial), 255


def panel(x, y, focused=False):
    """Subtle rounded translucent pill; focus state is brighter."""
    w, h, radius = 128, 64, 24
    ax = max(radius - x, 0, x - (w - radius - 1))
    ay = max(radius - y, 0, y - (h - radius - 1))
    inside = ax * ax + ay * ay <= radius * radius
    if not inside:
        return 0, 0, 0, 0
    edge = x in (0, w-1) or y in (0, h-1)
    if focused:
        return 243, 249, 255, 238 if not edge else 255
    return 236, 242, 255, 47 if not edge else 115


def main():
    png(OUT / "hero-scrim.png", 1920, 1080, scrim)
    png(OUT / "fallback.png", 1920, 1080, fallback)
    png(OUT / "power-glass.png", 128, 64, lambda x, y: panel(x, y, False))
    png(OUT / "power-focus.png", 128, 64, lambda x, y: panel(x, y, True))
    print("Generated original artwork in", OUT)


if __name__ == "__main__":
    main()
