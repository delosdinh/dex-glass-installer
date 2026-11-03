# Dex Glass Installer

This is the **public Kodi installer** for [Dex Glass](https://github.com/delosdinh/dex-glass), an experimental Apple TV-inspired skin. The development repository is private. This public repository contains **only the reproducible skin builder, original asset generator, Kodi repository metadata generator, and publishing workflow**.

> **Version 0.2.0 is a Pyrus-derived test skin with original clear Liquid Glass-style Kodi navigation, not the completed tvOS 26 design.** It has a separate `skin.dexglass` identity and a top-level link to the **separately installed official Dex Hub plugin**. Actual on-device CoreELEC/Kodi 22 compatibility and full Dex Hub playback/credits integrations have not yet been confirmed on-device.

## Direct Kodi installation

Once the automated deployment is successful, the public landing page is intended to be:

**https://delosdinh.github.io/dex-glass-installer/**

1. In Kodi: **Settings → File Manager → Add source**.
2. Enter the published URL, name it **Dex Glass**, and save.
3. Navigate to **Add-ons → Install from ZIP file → Dex Glass**.
4. Install `repository.dexglass-1.0.2.zip` (replaces previous repository packages).
5. Choose **Install from repository → Dex Glass Repository → Look and feel → Skin → Dex Glass (Preview)**.

If the File Manager's HTTP directory browser does not list the ZIP, open the public site in a browser and use its direct links, or try the alternative URL-specific install instructions. **Do not claim installation works until the site is live and tested on a Kodi device.**

The site also provides direct links to the **repository ZIP** and **skin ZIP**, plus `addons.xml` for repository metadata updates.

## Publishing

GitHub Actions workflow: [Publish Dex Glass Kodi installer](.github/workflows/publish.yml).

For first-time setup: **Settings → Pages → Build and deployment → Source: GitHub Actions**, then **Actions → Publish Dex Glass Kodi installer → Run workflow** (if a push has not already triggered it). If publishing fails, inspect the workflow log rather than assuming the page exists.

The workflow fetches a pinned official Pyrus v1.1.6 release ZIP, validates its SHA-256, packages it as `skin.dexglass`, generates original transparent UI textures, builds a Kodi repository ZIP and metadata, validates output files and publishes them on GitHub Pages.

Do not put any personal API keys, account credentials, or the private repository's contents into this public repository.

## Licence and credits

- [Pyrus/Applify](https://github.com/kamilfotoveci-design/applify) by kamilwhoo — upstream Kodi skin source. It incorporates Team Kodi's Estuary. The distributable ZIP preserves Pyrus's upstream `LICENSE` and `NOTICE.txt`, including GPLv2 code, CC BY-SA artwork and third-party font notices.
- The build intentionally excludes **Apple SF Pro font binaries** and substitutes **OrchardUI** open-licensed fonts already supplied by Pyrus. No Apple proprietary UI assets are committed or redistributed here.
- [Dex Hub](https://github.com/6ahd/plugin.video.dexhub) © DexWorld/6ahd — **separate, proprietary video add-on, not included in this repository or installer**. Install Dex Hub through official sources. This project makes no claim of authorisation from DexWorld.

This is an independent, personal experimental project. Not affiliated with Apple, Kodi, Pyrus, or DexWorld.
