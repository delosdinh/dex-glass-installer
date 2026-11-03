# Dex Glass Kodi installer

An **original cinematic Kodi home screen**, inspired by the tvOS Liquid Glass
aesthetic, with a **separately installed** official Dex Hub add-on supplying
media and sync services. The main \`delosdinh/dex-glass\` design/development
repository stays private; this public installer contains only the reproducible
Kodi build, original bridge, openly licensed fonts, textures and workflows.

## v0.5.0 — consolidated experience update

This release addresses the owner's latest on-device screenshots and requests:

- **No "DEX GLASS" label** at the top left: artwork fills that area.
- **Inter fonts** for an Apple-like typographic feel. Inter is SIL OFL; SF Pro
  is proprietary and is **not included**, downloaded or used.
- **Movie/TV graphical title logos** preferred on the hero. Kodi tries the
  selected title's clearlogo, the parent TV show's clearlogo and relevant
  list-item properties. When no usable clearlogo exists, the text title is
  deliberately retained rather than displaying a fake graphical logo.
- **Dex Glass custom settings window** replaces the inherited Pyrus
  "Customize Watch Now" editor.
- **Four add/replace/remove/reorder collection row slots**, saved only for
  Dex Glass. Choose a Kaptain/Dex Community group, folder and catalogue via
  the installed official Dex Hub; the bridge writes its own profile config
  and fetches that catalogue into a real Kodi widget row (falling back to
  an open-Dex-Hub tile where Kodi cannot resolve the listing).
- **Separate Continue Watching films/episodes** and the working cinematic
  background/navigation from v0.4 remain.
- **Feature-parity status and plan:** [docs/FEATURE_PARITY.md](docs/FEATURE_PARITY.md).

> **Experimental:** The skin package, Python syntax, test fixtures and public
> ZIPs are checked by GitHub Actions. Kaptain widgets, new settings interactions,
> Inter rendering and clearlogo availability still need **on-device** testing.
> Full Dex Hub playback overlays, trailer autoplay, credits controls, cast/crew,
> notifications and arbitrary row arrangement are not yet implemented.

## Direct ZIP installation on Kodi / CoreELEC

Public installer directory:

https://delosdinh.github.io/dex-glass-installer/

The separate Kodi repository catalogue previously failed on CoreELEC, so
**use Install from ZIP file rather than Install from repository**.

1. In Kodi go to **Add-ons → Install from ZIP file → Dex Glass**, using the
   existing File Manager source above.
2. Install **\`plugin.video.dexglass.bridge-0.2.0.zip\`** *first*. This updates
   the original Dex Glass companion media bridge and collection editor.
3. Then install **\`skin.dexglass-0.5.0.zip\`**. This is the new Kodi skin.
4. Return to **Settings → Interface → Skin → Dex Glass (Preview)** if needed.
   Restart Kodi if the settings screen isn't updated immediately.
5. In Dex Glass choose the top-right **Settings icon**; the screen should now
   read **Dex Glass | Customise Home**, not Pyrus's *Customize Watch Now*.
   Choose **Add / replace Kaptain catalogue** to add a row.

No Dex Hub settings, Nuvio account, Trakt/Simkl token, or personal settings
are changed or copied. The catalogue picker reads installed Dex Hub collection
data at runtime; it may need adjustment after future official Dex Hub updates.

Both ZIP files must remain intact; do not unzip them.

## Publishing

The [GitHub Actions release workflow](.github/workflows/publish.yml) downloads
the pinned upstream Pyrus v1.1.6 as a licensed framework, replaces **Home.xml**
and **SkinSettings.xml** with original Dex Glass windows, builds pinned Inter
from Google Fonts under the SIL OFL and original glass artwork, then generates
the skin, bridge, repository and public index ZIPs.

The original [Kaptain bridge](bridge/custom_collections.py) saves rows under
\`addon_data/plugin.video.dexglass.bridge/collections.json\`; this file is local
to the user's Kodi profile, not stored on GitHub or synced to external apps.

See [feature coverage](docs/FEATURE_PARITY.md) for unimplemented functionality.
No secrets or proprietary Dex Hub add-on code are distributed.

## Licences and attribution

- [Pyrus/Applify](https://github.com/kamilfotoveci-design/applify) by kamilwhoo,
  with underlying Team Kodi Estuary portions. The skin ZIP preserves the
  required upstream licences and notices.
- [Inter](https://github.com/google/fonts/tree/main/ofl/inter), the
  SIL Open Font License. The build includes its OFL notice.
- **No Apple SF Pro font files are included.** Apple's licence restricts
  their use and redistribution.
- [Dex Hub](https://github.com/6ahd/plugin.video.dexhub) © 6ahd/DexWorld:
  separate proprietary add-on, never bundled or modified. Users install and
  configure it from its official sources.
- The original Dex Glass companion bridge is under MIT (separate from any
  components with their own licence).

Independent experimental project, not affiliated with Apple, Pyrus, Team Kodi
or DexWorld.
