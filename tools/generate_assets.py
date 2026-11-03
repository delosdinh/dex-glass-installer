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


def _segment_distance(px,py,ax,ay,bx,by):
    vx,vy=bx-ax,by-ay
    u=max(0,min(1,((px-ax)*vx+(py-ay)*vy)/max(.001,vx*vx+vy*vy)))
    return math.hypot(px-(ax+u*vx),py-(ay+u*vy))

def nav_icon(kind,x,y):
    """Alpha-antialiased original white line artwork for Kodi's right utilities."""
    px,py=x+0.5,y+0.5
    cx,cy=36,36
    d=999.
    if kind=="search":
        d=min(abs(math.hypot(px-31,py-30)-15), _segment_distance(px,py,42,42,56,56))
    elif kind=="settings":
        radial=math.hypot(px-cx,py-cy)
        d=min(abs(radial-13), abs(radial-4.5))
        for i in range(8):
            angle=math.pi*i/4
            ax,ay=cx+18*math.cos(angle),cy+18*math.sin(angle)
            bx,by=cx+23*math.cos(angle),cy+23*math.sin(angle)
            d=min(d,_segment_distance(px,py,ax,ay,bx,by))
    elif kind=="power":
        rad=math.hypot(px-36,py-39)
        angle=math.degrees(math.atan2(py-39,px-36))
        if not -125 < angle < -55:
            d=abs(rad-19)
        d=min(d,_segment_distance(px,py,36,10,36,36))
    alpha=max(0,min(1,(3.1-d)/2.3))
    return 240,249,255,int(245*alpha)

def collections_card(which,x,y):
    """Original restrained iridescent Kaptain/Community shortcuts."""
    w,h=380,210
    palettes=(
        ((10,38,62),(14,91,125),(47,171,209)),
        ((22,21,68),(72,55,133),(152,117,215)),
        ((25,42,53),(37,104,89),(88,187,164)),
        ((45,25,58),(105,57,102),(226,132,151)),
    )
    dark,mid,lit=palettes[which%len(palettes)]
    t=x/(w-1)
    base=[int(dark[i]*(1-t)+mid[i]*t) for i in range(3)]
    halo=max(0,1-math.hypot((x-(190+which*25))/240,(y-65)/185))
    shimmer=max(0,1-abs((x+y*.34)-(125+which*40))/45)
    out=[min(255,int(base[i]+lit[i]*halo*.25+lit[i]*shimmer*.1)) for i in range(3)]
    rounded=_round_alpha(x,y,w,h,22)
    edge=max(0,1-min(x,w-1-x,y,h-1-y)/10)
    a=int(rounded*255)
    if edge and rounded:
        out=[min(255,int(out[i]+55*edge)) for i in range(3)]
    return *out,a


def nav_fine_focus(x,y):
    """A thin luminous tvOS-style focus underline, not an opaque lens pill."""
    w,h=240,10
    rel=abs(x-(w-1)/2)/((w-1)/2)
    taper=max(0,1-rel**2)**1.8
    vertical=max(0,1-abs(y-4.5)/5)
    a=int(195*taper*vertical)
    return 229,248,255,a

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
    for kind in ("search", "settings", "power"):
        png(OUT / ("icon-" + kind + ".png"), 72, 72,
            lambda x,y,k=kind: nav_icon(k,x,y))
    for i,key in enumerate(("kaptain","community","organise","imports")):
        png(OUT / ("collection-" + key + ".png"),380,210,
            lambda x,y,z=i: collections_card(z,x,y))
    png(OUT / "nav-fine-focus.png",240,10,nav_fine_focus)
    print("Generated original artwork in", OUT)


if __name__ == "__main__":
    main()
