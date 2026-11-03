# Dex Glass Installer

A **public Kodi ZIP installer** for Dex Glass, an experimental Kodi 21/22 skin with an original tvOS-inspired home screen. The main \`delosdinh/dex-glass\` development repository stays private. This public installer contains only a reproducible skin builder, an original read-only bridge, generated Kodi artwork and publishing workflows.

## Dex Glass v0.4.0 — on-device issues addressed

Based on the owner's successful v0.3 installation and screenshot:

- **Top-right toolbar:** Search, Settings and Power have actual custom PNG icons rather than squeezed text. Their Kodi actions remain intact.
- **Continue Watching Movies / Episodes:** the official Dex Hub public \`?action=continue\` listing does **not** filter on \`media=movie\`/ \`media=series\`; a small, separate \`plugin.video.dexglass.bridge\` asks Kodi JSON-RPC for that listing and splits films and episodes using media-type metadata. Unknown types stay out of both rows rather than being misfiled. This bridge is **experimental and not confirmed on the device yet**.
- **Dex Collections:** \`?action=collection_sets\` returns a custom interface, not poster items. The row now has focusable Kodi cards for **Kaptain / Dex Collection**, Dex Community, arranging home rows and importing collections, opening Dex Hub's **supported native \`?action=home_community\`** route. These are *navigation shortcuts*, not a copy of the Kaptain catalogs or full widget rails.

The cinematic hero, seven section names and original \`Home.xml\` from v0.3 are preserved. **Full Dex Hub custom playback overlays, editable row builder, complete cast/crew detail pages and native Apple tvOS physical light refraction are not implemented.** Pyrus/Estuary remains the compatibility base for secondary Kodi screens.

## Installation on CoreELEC (no repository catalogue required)

Use the **public installer URL** already added to Kodi File Manager:

https://delosdinh.github.io/dex-glass-installer/

The Kodi **Install from repository** catalogue has failed on this user's device. Bypass it:

1. Open **Kodi → Add-ons → Install from ZIP file → Dex Glass**.
2. Select **\`plugin.video.dexglass.bridge-0.1.0.zip\`** and install the small companion add-on **first**.
3. Return to the **Dex Glass** ZIP file source and install **\`skin.dexglass-0.4.0.zip\`**.
4. Keep the existing official Dex Hub installed. Go to **Settings → Interface → Skin → Dex Glass (Preview)**, if Kodi has not switched automatically.

Both ZIPs are also linked at the public installer web page. Do **not** extract them.

The bridge is an independent Kodi plug-in. It does not change or ship Dex Hub's Python files, artwork, accounts, authentication data or settings. It calls Kodi's own \`Files.GetDirectory\` API to request public plugin listings from the user's installed official Dex Hub.

If Kodi cannot classify an item, the row may show a shortcut to the original Dex Hub Continue Watching list. This is preferable to putting the same series into the films shelf.

### Troubleshooting

If v0.4's two Continue Watching rows are empty, inspect \`kodi.log\` for \`[DexGlassBridge]\`: it logs **media counts and error classes only**, never titles or streaming credentials. Kodi 22's JSON-RPC behaviour varies between platform builds and has not been directly tested on the owner's CoreELEC device.

If any window fails, revert via **Settings → Interface → Skin → previous skin**. The installed official Dex Hub itself remains unchanged.

## Build / publication

The GitHub Actions workflow [.github/workflows/publish.yml](.github/workflows/publish.yml) pins the official Pyrus v1.1.6 release by SHA-256, rebuilds Kodi \`skin.dexglass\` from an **original Home.xml** ([build/real_home.py](build/real_home.py)) and original PNG assets, packages the original bridge from [bridge/default.py](bridge/default.py), and assembles Kodi \`addons.xml\` and both ZIPs on GitHub Pages.

The Kodi repository package \`repository.dexglass-1.0.4.zip\` is also published, but direct ZIP installation is preferred until repository browsing works on-device.

Keep passwords and personal API tokens out of this public repository.

## Licence and credits

- [Pyrus / Applify](https://github.com/kamilfotoveci-design/applify) by kamilwhoo, incorporating Kodi Estuary. The skin ZIP includes upstream GPLv2, CC BY-SA and font notices, which must be retained.
- Apple SF Pro proprietary binaries are intentionally **excluded** from the redistributed skin ZIP and replaced by the open-licensed OrchardUI files already supplied upstream.
- [Dex Hub](https://github.com/6ahd/plugin.video.dexhub) is a separate proprietary plugin © 6ahd / DexWorld. It is **not** bundled or modified. Users install it through official channels. This installer is not affiliated with DexWorld.
- The original \`plugin.video.dexglass.bridge\` code is published under MIT, independent of Dex Hub.

This is an independent experimental project, unaffiliated with Apple, Team Kodi, Pyrus or DexWorld.
