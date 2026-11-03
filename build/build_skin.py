#!/usr/bin/env python3
"""Build an experimental Kodi skin from official Pyrus 1.1.6, without Dex Hub code."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from liquid_glass import style_home

URL = "https://github.com/kamilfotoveci-design/applify/releases/download/v1.1.6/skin.applify-1.1.6.zip"
EXPECTED = "2e36befee29fa4f904f7a4e27d85779a504e23a963c646224019dc98e6a7cd9c"
TEXT_TYPES = {".xml", ".py", ".txt", ".po", ".md", ".json", ".ini", ".cfg"}

def source_zip(path):
    if path:
        data = Path(path).read_bytes()
    else:
        print("Downloading official Pyrus v1.1.6...", flush=True)
        req = urllib.request.Request(URL, headers={"User-Agent": "DexGlassPersonalBuild/0.1"})
        with urllib.request.urlopen(req, timeout=120) as response:
            data = response.read()
    got = hashlib.sha256(data).hexdigest()
    if got != EXPECTED:
        raise ValueError("Official source SHA-256 mismatch: " + got)
    return data

def addon_xml(data):
    element = ET.fromstring(data)
    if element.attrib.get("id") != "skin.applify":
        raise ValueError("Not the expected Pyrus skin")
    element.attrib.update({"id":"skin.dexglass",
                           "name":"Dex Glass (Preview)",
                           "version":"0.2.0",
                           "provider-name":"Dex Glass; based on Pyrus by kamilwhoo"})
    meta = element.find("extension[@point='xbmc.addon.metadata']")
    if meta is not None:
        for child in meta:
            if child.tag in ("summary", "description") and child.attrib.get("lang") == "en_GB":
                child.text = ("Experimental tvOS-inspired Dex Glass skin, based on Pyrus. "
                              "Requires separately installed official Dex Hub for streaming and sync.")
            elif child.tag in ("website", "source"):
                child.text = "https://github.com/delosdinh/dex-glass"
    return ET.tostring(element, encoding="utf-8", xml_declaration=True)

def home_hubs(data):
    raw = data.decode("utf-8")
    raw = raw.replace("'addons':'Add-ons'", "'addons':'Dex Hub'")
    pattern = r"""if page=='addons':\s*xbmc\.executebuiltin\('ActivateWindow\(Videos,"addons://sources/video/",return\)'\);return"""
    following = ("if page=='addons':\n"
                 '        xbmc.executebuiltin(\'ActivateWindow(Videos,"plugin://plugin.video.dexhub/",return)\');return')
    raw, count = re.subn(pattern, lambda _: following, raw)
    if count != 1:
        raise ValueError("The Pyrus Add-ons action is missing or has changed")
    return raw.encode("utf-8")

def build(source, dest, assets):
    files = {}
    with zipfile.ZipFile(io.BytesIO(source)) as z:
        candidates = [name for name in z.namelist() if name.endswith("/addon.xml") or name == "addon.xml"]
        if len(candidates) != 1:
            raise ValueError("Unable to identify Pyrus ZIP root")
        prefix = candidates[0][:-len("addon.xml")]
        print("Upstream ZIP root:", prefix or "(top-level)")
        for path in z.namelist():
            if path.endswith("/") or not path.startswith(prefix):
                continue
            name = path[len(prefix):]
            if not name or name.startswith("/") or ".." in Path(name).parts:
                raise ValueError("Unexpected ZIP path: " + path)
            if name.lower().startswith("fonts/sf-pro-display") and name.lower().endswith(".ttf"):
                print("Excluding Apple SF Pro font:", name)
                continue
            data = z.read(path)
            if name == "addon.xml":
                data = addon_xml(data)
            elif name == "resources/home_hubs.py":
                data = home_hubs(data)
            elif name == "xml/Home.xml":
                data = style_home(data)
            elif name == "xml/Font.xml":
                data = data.replace(b"sf-pro-display-regular.ttf", b"OrchardUI-Regular.ttf")
                data = data.replace(b"sf-pro-display-semibold.ttf", b"OrchardUI-Semibold.ttf")
            if Path(name).suffix.lower() in TEXT_TYPES and name not in ("addon.xml", "resources/package-sha256.json"):
                data = data.replace(b"skin.applify", b"skin.dexglass")
            files[name] = data
    required = ["addon.xml","xml/Home.xml","xml/Font.xml","resources/home_hubs.py",
                "LICENSE","NOTICE.txt","fonts/OrchardUI-Regular.ttf","fonts/OrchardUI-Semibold.ttf"]
    missing = [name for name in required if name not in files]
    if missing:
        raise ValueError("Missing source files: " + ", ".join(missing))
    if assets.is_dir():
        count = 0
        for asset in assets.rglob("*.png"):
            files["media/dexglass/" + asset.relative_to(assets).as_posix()] = asset.read_bytes()
            count += 1
        print("Included original Dex Glass assets:", count)
    files["DEXGLASS-INTEGRATION.md"] = b"""# Dex Glass preview 0.2.0

Based on Pyrus v1.1.6 by kamilwhoo and Estuary/Team Kodi.
Pyrus/Estuary licences and notices are preserved. Apple SF Pro font
binaries have been excluded and OFL-licensed OrchardUI substituted.

The Add-ons hub in this experimental skin now opens the separately
installed official Dex Hub plugin at plugin://plugin.video.dexhub/.
This does not embed or modify any Dex Hub code or service.

This preview adds real Kodi Liquid Lens navigation assets.\nReal Dex Hub homepage rows,
detail pages, full optical Liquid Glass shaders, playback overlays and
CoreELEC-specific integration are not yet implemented/tested.
The first goal is to verify independent skin installation and launcher.
You can always switch back using Kodi Settings > Interface > Skin.
"""
    # Pyrus diagnostics reference this manifest; recalculate for modified files.
    manifest_name = "resources/package-sha256.json"
    if manifest_name in files:
        try:
            manifest = json.loads(files[manifest_name].decode("utf-8"))
            manifest["files"] = {name: hashlib.sha256(data).hexdigest()
                                 for name, data in sorted(files.items()) if name != manifest_name}
            files[manifest_name] = (json.dumps(manifest, indent=2) + "\n").encode()
        except (KeyError, ValueError) as exc:
            print("Warning: upstream manifest was not updated:", exc)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        for name, data in sorted(files.items()):
            out.writestr("skin.dexglass/" + name, data)
    with zipfile.ZipFile(dest) as check:
        if check.testzip():
            raise ValueError("Generated ZIP failed CRC validation")
        root = ET.fromstring(check.read("skin.dexglass/addon.xml"))
        assert root.attrib["id"] == "skin.dexglass"
        assert "skin.dexglass/fonts/sf-pro-display-regular.ttf" not in check.namelist()
    print(f"Built {dest} ({dest.stat().st_size:,} bytes, {len(files)} files)")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Local official Pyrus v1.1.6 ZIP; optional in GitHub Actions")
    parser.add_argument("--output", default="dist/skin.dexglass-0.2.0.zip")
    parser.add_argument("--assets", default="build/media/dexglass")
    args = parser.parse_args()
    build(source_zip(args.source), Path(args.output), Path(args.assets))

if __name__ == "__main__":
    main()
