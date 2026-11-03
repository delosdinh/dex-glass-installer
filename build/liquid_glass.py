#!/usr/bin/env python3
"""Apply original clear-lens Dex Glass theme to a legally sourced Pyrus Home.xml.

Preserves all Pyrus controls/routes. This is an experimental Kodi skin, not
a reproduction of Apple's proprietary compositor or the finished web concept.
"""
import xml.etree.ElementTree as ET

def style_home(data: bytes) -> bytes:
    root=ET.fromstring(data)
    controls=root.find("controls")
    if controls is None:raise ValueError("Pyrus Home controls not found")
    nav=next((node for node in controls.iter("control")
              if node.attrib.get("id")=="9000" and node.attrib.get("type")=="grouplist"),None)
    if nav is None or nav not in list(controls):
        raise ValueError("Pyrus top-level navigation grouplist changed")
    index=list(controls).index(nav)

    # The full-screen hero already comes from $VAR[OrchardHeroArt], and must
    # remain before navigation. Insert a minimal 1920px-independent glass
    # surface directly underneath the centered nav container.
    layer=ET.Element("control", {"type":"image"})
    for tag,value in (("left","396"),("top","44"),("width","1128"),("height","84"),
                      ("texture","dexglass/nav-surface.png"),
                      ("aspectratio","stretch")):
        ET.SubElement(layer,tag).text=value
    controls.insert(index,layer)

    # Preserve existing per-hub focus positioning and Pyrus navigation logic.
    # Just replace the visual texture paths, not control IDs or actions.
    focus_count=shadow_count=0
    for texture in nav.iter("texture"):
        value=texture.text or ""
        if value=="orchard/nav-focus-depth-128.png":
            texture.text="dexglass/nav-lens.png"
            texture.set("border","24,20,24,20")
            focus_count+=1
        elif value=="orchard/nav-focus-shadow-128.png":
            texture.text="dexglass/nav-shadow.png"
            texture.set("border","30,20,30,20")
            shadow_count+=1
    for btn in nav.iter("control"):
        if btn.attrib.get("type")=="button" and btn.attrib.get("id") in {
            "9101","9102","9103","9104","9111","9112","9113","9114"
        }:
            selected=btn.find("focusedcolor")
            if selected is not None: selected.text="FFFFFFFF"
    if focus_count < 3 or shadow_count < 3:
        raise ValueError(f"Upstream focus textures changed: lens={focus_count} shadow={shadow_count}")

    # Keep original power button routes and Kodi's actual ShutdownMenu.
    # Preserve Kodi Home layout, hero source and widget/provider controls.
    # Add readable comment at root, without touching any proprietary Dex Hub.
    root.insert(0,ET.Comment(
        "Dex Glass Liquid Lens test: original transparent nav assets; "
        "Pyrus Kodi controls preserved; no proprietary Dex Hub code."
    ))
    output=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    ET.fromstring(output)
    print(f"Liquid Glass nav: {focus_count} focus lenses / {shadow_count} shadows")
    return output
