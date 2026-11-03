#!/usr/bin/env python3
"""Generate redistributable static Inter TTF weights from Google Fonts.

Inter is licensed under the SIL Open Font License, unlike Apple SF Pro.
Use a pinned Google Fonts git commit for reproducible sources. Font binaries
are build inputs, NOT checked in or linked as standalone file downloads.
"""
import hashlib
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

COMMIT = "e1d6480102fed30739fead0faee463101f892c8f"
BASE = "https://raw.githubusercontent.com/google/fonts/" + COMMIT + "/ofl/inter/"
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "build" / "fonts"

def get(filename):
    url=BASE+quote(filename,safe="")
    request=Request(url,headers={"User-Agent":"DexGlassInterBuild/1.0"})
    with urlopen(request,timeout=120) as resp:
        return resp.read()

def main():
    raw=get("Inter[opsz,wght].ttf")
    license_text=get("OFL.txt")
    expected="29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031"
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError("Inter font source hash did not match pinned Google Fonts version")
    if not raw.startswith(b"\x00\x01\x00\x00") or len(raw)<100000:
        raise ValueError("Unexpected Inter TrueType download")
    if b"SIL OPEN FONT LICENSE" not in license_text.upper():
        raise ValueError("Inter OFL license was not retrieved")
    DEST.mkdir(parents=True,exist_ok=True)
    variable=DEST/"Inter-Variable.ttf"
    variable.write_bytes(raw)
    weights=(("Regular",400),("Semibold",600))
    for label,weight in weights:
        font=TTFont(variable)
        instance=instantiateVariableFont(font,{"wght":weight,"opsz":18.0},inplace=True)
        output=DEST/("Inter-"+label+".ttf")
        instance.save(output)
        instance.close()
        font.close()
        if output.stat().st_size<10000:
            raise ValueError("Font build empty: "+label)
        print("%s %d bytes" %(output.name,output.stat().st_size),flush=True)
    (DEST/"Inter-OFL.txt").write_bytes(license_text)
    variable.unlink()
    print("Inter OFL source SHA-256:",hashlib.sha256(raw).hexdigest(),flush=True)

if __name__=="__main__":
    main()
