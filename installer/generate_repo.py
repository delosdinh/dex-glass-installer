#!/usr/bin/env python3
"""Build a Kodi repository add-on + GitHub Pages static installer for Dex Glass.

This consumes an independently built, verified Pyrus-based Dex Glass skin ZIP.
It does not contain or download proprietary Dex Hub files.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

HOST = "https://delosdinh.github.io/dex-glass-installer/"
REPO_ID = "repository.dexglass"
REPO_VERSION = "1.0.0"
SKIN_ID = "skin.dexglass"
SKIN_VERSION = "0.1.0"

def element_bytes(node):
    return ET.tostring(node, encoding="utf-8", xml_declaration=True)

def make_repository_xml():
    root = ET.Element("addon", {
        "id": REPO_ID,
        "name": "Dex Glass Repository",
        "version": REPO_VERSION,
        "provider-name": "Dex Glass community preview",
    })
    ET.SubElement(root, "requires")
    ext = ET.SubElement(root, "extension", {"point": "xbmc.addon.repository"})
    d = ET.SubElement(ext, "dir")
    ET.SubElement(d, "info", {"compressed": "false"}).text = HOST + "addons.xml"
    ET.SubElement(d, "checksum").text = HOST + "addons.xml.md5"
    ET.SubElement(d, "datadir", {"zip": "true"}).text = HOST
    ET.SubElement(d, "hashes").text = "false"
    meta = ET.SubElement(root, "extension", {"point": "xbmc.addon.metadata"})
    ET.SubElement(meta, "platform").text = "all"
    ET.SubElement(meta, "license").text = "Original repository configuration; see upstream skin licences"
    ET.SubElement(meta, "summary", {"lang": "en_GB"}).text = "Experimental Dex Glass Kodi skin updates"
    ET.SubElement(meta, "description", {"lang": "en_GB"}).text = (
        "Publishes an independent experimental Dex Glass skin based on Pyrus. "
        "The proprietary Dex Hub video add-on must be installed separately."
    )
    ET.SubElement(meta, "website").text = "https://github.com/delosdinh/dex-glass-installer"
    return element_bytes(root)

def build(skin_zip, out):
    if not skin_zip.is_file():
        raise FileNotFoundError("Run the skin builder first: " + str(skin_zip))
    out.mkdir(parents=True, exist_ok=True)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    with zipfile.ZipFile(skin_zip) as z:
        if z.testzip() is not None:
            raise ValueError("Skin ZIP CRC check failed")
        skin_xml = ET.fromstring(z.read(SKIN_ID + "/addon.xml"))
    if skin_xml.attrib.get("id") != SKIN_ID or skin_xml.attrib.get("version") != SKIN_VERSION:
        raise ValueError("Unexpected skin ID or version")

    repo_xml = make_repository_xml()
    repo_dir = out / REPO_ID
    repo_dir.mkdir(exist_ok=True)
    repository_zip = repo_dir / (REPO_ID + "-" + REPO_VERSION + ".zip")
    with zipfile.ZipFile(repository_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(REPO_ID + "/addon.xml", repo_xml)
    shutil.copy2(repository_zip, out / repository_zip.name)
    skin_dir = out / SKIN_ID
    skin_dir.mkdir(exist_ok=True)
    shutil.copy2(skin_zip, skin_dir / (SKIN_ID + "-" + SKIN_VERSION + ".zip"))
    shutil.copy2(skin_zip, out / (SKIN_ID + "-" + SKIN_VERSION + ".zip"))

    addons = ET.Element("addons")
    addons.append(ET.fromstring(repo_xml))
    addons.append(skin_xml)
    addons_xml = element_bytes(addons)
    (out / "addons.xml").write_bytes(addons_xml)
    (out / "addons.xml.md5").write_text(hashlib.md5(addons_xml).hexdigest(), encoding="ascii")
    (out / "addons.xml.sha256").write_text(hashlib.sha256(addons_xml).hexdigest(), encoding="ascii")
    # Kodi's CHTTPDirectory parser accepts links only when the visible anchor text
    # is exactly the relative href filename (plus metadata after the closing tag).
    # A styled download button with another label looks fine in browsers but is
    # invisible in Kodi's "Install from ZIP file" HTTP file browser.
    repo_name = REPO_ID + "-" + REPO_VERSION + ".zip"
    skin_name = SKIN_ID + "-" + SKIN_VERSION + ".zip"
    index = (
        '<!doctype html><html lang="en-AU"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Index of /dex-glass-installer/ - Dex Glass Kodi Repository</title>'
        '<style>body{font:16px/1.65 system-ui,sans-serif;background:#090f1c;'
        'color:#f0f6ff;max-width:790px;margin:9vh auto;padding:24px}'
        'a{color:#a8d8ff}table{border-collapse:collapse;width:100%;'
        'background:#15223c}td{border:1px solid #41506c;'
        'padding:14px 12px}small{color:#acb8d0}code{color:#e1ecff}'
        '</style></head><body>'
        '<h1>Index of /dex-glass-installer/</h1>'
        '<p>Dex Glass - experimental Kodi skin repository. '
        'The proprietary Dex Hub add-on is not bundled.</p>'
        '<table>'
        '<tr><td><a href="' + repo_name + '">' + repo_name + '</a></td>'
        '<td>Repository installer ZIP</td></tr>'
        '<tr><td><a href="' + skin_name + '">' + skin_name + '</a></td>'
        '<td>Direct skin ZIP</td></tr>'
        '</table>'
        '<p>In Kodi, add <code>' + HOST + '</code> as a File Manager source, '
        'then choose <strong>Install from ZIP file</strong> and select '
        '<code>' + repo_name + '</code>.</p>'
        '<p>Then open <strong>Install from repository - Dex Glass Repository - '
        'Look and feel - Skin</strong>.</p>'
        '<p><small>Based on Pyrus by kamilwhoo and Team Kodi Estuary; '
        'upstream notices preserved. Apple SF Pro binaries excluded. '
        'Not affiliated with Apple, Pyrus, DexWorld or Kodi.</small></p>'
        '</body></html>'
    )
    # Reproduce Kodi CHTTPDirectory's restrictive anchor matching so
    # future styling edits cannot silently make ZIPs invisible in Kodi.
    import re
    parsed = re.findall(
        r'<a href="([^"]*)"[^>]*>\\s*(.*?)\\s*</a>(.+?)(?=<a|</tr|$)',
        index, flags=re.IGNORECASE
    )
    visible = {href for href, label, _ in parsed if href == label.strip()}
    if {repo_name, skin_name} != visible:
        raise ValueError("Website HTML directory links are not Kodi-compatible: " + str(visible))
    (out / "index.html").write_text(index, encoding="utf-8")
    (out / "README.txt").write_text(
        "Generated GitHub Pages Kodi repository. No Dex Hub code or accounts.\n", encoding="utf-8"
    )
    with zipfile.ZipFile(repository_zip) as z:
        assert z.testzip() is None
        assert ET.fromstring(z.read(REPO_ID + "/addon.xml")).get("id") == REPO_ID
    assert len(ET.parse(out / "addons.xml").getroot()) == 2
    assert (skin_dir / (SKIN_ID + "-" + SKIN_VERSION + ".zip")).is_file()
    print("Built Kodi repository and installer site in", out)
    print("Publish at:", HOST)

if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist/skin.dexglass-0.1.0.zip"),
          Path(sys.argv[2]) if len(sys.argv) > 2 else Path("dist/site"))
