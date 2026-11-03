# Dex Glass Kodi installer

An independent Apple tvOS-inspired Kodi skin, built around the separately
installed **official Dex Hub**. The main design repository
\`delosdinh/dex-glass\` stays private. This public repository provides a
reproducible skin build, original Kodi UI files and an independently licensed
bridge; **no Dex Hub sources, settings, tokens or bundled add-on ZIPs**.

## v0.6.1 — four genuine hubs, row customisation and title artwork

This is a consolidated functional update driven by on-device screenshots.
Kodi XML and the public ZIPs are machine-validated; the current release is
**experimental and must still be tested on CoreELEC**.

- Watch Now, Movies, TV Shows and Collections are now **four actual Dex Glass
  homepage pages**, not buttons opening Dex Hub's custom windows.
- Each page has 12 positions. In **Dex Glass Settings → Customise All Hub Rows**
  or the home **Customise** button, you can select the page, add a row, choose
  a builtin feed or Kaptain/Dex Community catalogue, replace a row, move it
  earlier/later or remove it. Empty positions disappear. Default Watch Now
  still has the seven requested rows. The page-specific editor saves all
  choices only in the original Dex Glass bridge profile.
- Existing Kaptain catalogue selections made in v0.5 are **migrated to Watch
  Now**, without deleting the previous \`collections.json\` backup.
- Kaptain selections now load through a per-page **real Kodi widget content
  route**, not just a settings button. Because some Dex Hub catalogue routes
  may return no Kodi JSON-RPC items on CoreELEC, a failed feed shows an
  explicit clickable fallback opening the original source instead of a
  misleading empty row.
- The top menu no longer has a Dex Hub tab: **Add-ons** opens Kodi's video
  add-ons. Official Dex Hub is still separately installed and can be accessed
  there.
- The **Search icon** launches a native Dex Glass search keyboard and
  selects from official Dex Hub's \`skin_search\` result items. It does not open
  Dex Hub's full-screen custom search. Results still use Kodi's own dialogs;
  an original cinematic search-grid page is future work.
- The focused menu uses a **thin luminous underline**, not an opaque white
  focus pill.
- Hero title **text always appears when a graphical logo is unavailable**,
  fixing the blank Dune title seen in the screen photos. The bridge service
  first reads Kodi's own focused-title logos, and can read missing logos from
  the installed official Dex Hub's **local art cache**. No network artwork
  fetch is done by the service. A graphical logo is shown only if available;
  otherwise it remains text.
- Reduced plot summary font size and kept the clean top-left corner.
- Inter fonts under the SIL OFL remain bundled, not restricted Apple SF Pro.

**Still missing:** exact Apple compositor refraction is not supported by Kodi
XML; trailer autoplay, full title-details/cast/crew, player-overlay parity,
notifications, next-episode/skip-credits controls and sound design are
separate feature tracks. Account sync and streaming remain in the official
installed Dex Hub. See [feature parity](docs/FEATURE_PARITY.md).

## How to install on your Ugoos / CoreELEC

The built-in Kodi **Install from repository** index has repeatedly failed on
this device. Use **Install from ZIP file** through your existing "Dex Glass"
File Manager source:

https://delosdinh.github.io/dex-glass-installer/

**Install in this exact order**, without extracting either ZIP:

1. \`plugin.video.dexglass.bridge-0.3.0.zip\` — mandatory original companion.
2. \`skin.dexglass-0.6.1.zip\` — updates the Dex Glass Kodi skin.
3. Restart Kodi, then choose **Settings → Interface → Skin → Dex Glass
   (Preview)** if it did not automatically remain selected.

The standalone \`repository.dexglass-1.0.7.zip\` is optional and need not be
installed; it is not required for the direct ZIP method.

Open Settings (gear) → **Customise All Hub Rows** to edit any of the four
pages. A change prompts Kodi to reload its skin and restore the home screen.
The Kodi companion service rehydrates its saved row titles after login.
The old Dex Glass v0.5 choices remain on disk for migration or rollback.

No phone companion, paid subscription or new personal credentials required.

## How the pieces work

- [build/real_home_pages.py](build/real_home_pages.py) generates our own
  four-page cinematic \`Home.xml\`, not the Pyrus Home editor.
- [bridge/home_config.py](bridge/home_config.py) provides per-page row
  persistence, source replacement and reordering in Kodi using only the
  Dex Glass add-on profile.
- [bridge/default.py](bridge/default.py) populates configurable Kodi
  widgets with official Dex Hub's public plugin directory items.
- [bridge/search.py](bridge/search.py) provides a separate Kodi search
  keyboard/result selector without launching Dex Hub's custom search.
- [bridge/service.py](bridge/service.py) keeps the hero title logo in sync
  with the selected widget and restores saved row titles after starting Kodi.
- [build/inter_font.py](build/inter_font.py) uses a pinned and SHA-256
  validated Inter source from Google Fonts under its bundled OFL.
- The [Actions workflow](.github/workflows/publish.yml) produces and
  validates the ZIPs and publishes the static install directory.

This skin is currently a **compatibility framework plus our own Home.xml and
SkinSettings.xml**. Pyrus/Estuary-based source remains for other Kodi windows
with the required upstream licences and notices. Do not promise full Dex Hub
parity until the unfinished player and details windows are implemented.

## Attribution and licensing

- [Pyrus/Applify](https://github.com/kamilfotoveci-design/applify) by kamilwhoo
  incorporates Team Kodi Estuary. The redistributed skin ZIP retains upstream
  GPL/CC BY-SA notices and readable code.
- [Inter](https://github.com/google/fonts/tree/main/ofl/inter) is licensed
  under the SIL Open Font License. Its OFL notice accompanies the font files.
- **Apple SF Pro** proprietary fonts are not included or copied.
- [Dex Hub](https://github.com/6ahd/plugin.video.dexhub) is separately
  installed proprietary software (6ahd/DexWorld), never redistributed by
  this repository or written to by its companion.
- The original bridge is independently licensed under MIT.

Independent experimental project; no affiliation with Apple, Pyrus, Team Kodi
or DexWorld.
