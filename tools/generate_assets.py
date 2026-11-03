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



def lens(x, y):
    """Clear glass highlight with border illumination; nine-slice stretchable."""
    w, h, r = 256, 64, 25
    dx = max(r - x - 0.5, 0, x - (w-r-0.5))
    dy = max(r - y - 0.5, 0, y - (h-r-0.5))
    dist = math.sqrt(dx*dx + dy*dy)
    if dist > r: return 0, 0, 0, 0
    # Darker than frosted white: background details remain identifiable.
    top_spec = max(0, 1 - y/19)
    bottom_spec = max(0, (y-46)/18)
    side_spec = max(0, 1 - min(x, w-1-x)/9)
    edge = max(0, min(1, (dist-(r-2.5))/2.5))
    shine = max(0, 1 - ((x-56)/96)**2) * max(0, 1 - y/39)
    alpha = int(min(200, 35 + 53*top_spec + 39*bottom_spec + 33*side_spec + 60*edge + 44*shine))
    return 204+int(30*top_spec), 231, 255, alpha


def nav_surface(x, y):
    """Semi-transparent navigation capsule; panoramic background stays visible."""
    w, h, r = 1150, 86, 36
    dx=max(r-x,0,x-(w-r-1))
    dy=max(r-y,0,y-(h-r-1))
    distance=math.hypot(dx,dy)
    if distance>r: return 0,0,0,0
    edge=max(0,min(1,(distance-(r-2))/2))
    top=max(0,1-y/18)
    alpha=int(min(140,19+62*edge+52*top))
    return 213,233,252,alpha


def lens_shadow(x, y):
    """Subtle soft shadow, stretched with Kodi texture border handling."""
    w,h=256,90
    edge_x=min(1,x/30,(w-1-x)/30)
    edge_y=min(1,y/24,(h-1-y)/24)
    inside=max(0,min(edge_x,edge_y))
    return 1,7,17,int(60*inside)


def _round_alpha(x,y,w,h,r):
    cx=min(max(x,r),w-1-r)
    cy=min(max(y,r),h-1-r)
    d=math.hypot(x-cx,y-cy)
    return max(0,min(1, r+0.75-d))

def tile_mask(x,y,w=400,h=240):
    a=int(255*_round_alpha(x,y,w,h,20))
    return 255,255,255,a

def tile_vignette(x,y,w=512,h=320):
    shape=_round_alpha(x,y,w,h,22)
    bottom=max(0,min(1,(y/h-.37)/.63))
    alpha=int(shape*(12+210*bottom**1.7))
    return 2,5,12,alpha

def tile_edge(x,y,w=512,h=320):
    a=_round_alpha(x,y,w,h,23)
    bx=min(max(x,23),w-1-23)
    by=min(max(y,23),h-1-23)
    inner=math.hypot(x-bx,y-by)
    edge=max(0,min(1,(inner-19)/4))
    top=max(0,1-y/42)
    alpha=int(175*a*edge+65*a*top)
    return 230,248,255,min(235,alpha)

def main():
    png(OUT / "hero-scrim.png", 1920, 1080, scrim)
    png(OUT / "fallback.png", 1920, 1080, fallback)
    png(OUT / "power-glass.png", 128, 64, lambda x, y: panel(x, y, False))
    png(OUT / "power-focus.png", 128, 64, lambda x, y: panel(x, y, True))
    png(OUT / "nav-surface.png", 1150, 86, nav_surface)
    png(OUT / "nav-lens.png", 256, 64, lens)
    png(OUT / "nav-shadow.png", 256, 90, lens_shadow)
    png(OUT / "tile-mask-wide.png", 400, 240, lambda x,y:tile_mask(x,y,400,240))
    png(OUT / "tile-mask-poster.png", 240, 320, lambda x,y:tile_mask(x,y,240,320))
    png(OUT / "tile-shade.png", 512, 320, tile_vignette)
    png(OUT / "tile-glow.png", 512, 320, tile_edge)
    print("Generated original artwork in", OUT)


if __name__ == "__main__":
    main()
