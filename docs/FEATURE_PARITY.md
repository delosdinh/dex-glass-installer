# Dex Glass functional parity tracker

**Purpose:** Keep every agreed Dex Hub requirement visible. A ZIP that merely
launches Dex Hub is not feature parity. These statuses describe Dex Glass,
not the capabilities of the separately installed official Dex Hub plugin.

**Status:** v0.6.1 is a development build. A successful automated XML/ZIP
test does not mean a feature is verified on the user's CoreELEC/Kodi 22 device.

| Requirement | State | What v0.6.1 actually does / what remains |
|---|---|---|
| Full-screen dynamic cinematic backdrop follows focused title | Implemented, device-tested in v0.3 | Fullscreen Kodi fanart works; transitions/hero art can still be improved |
| Top navigation styled after Applify, inspired by tvOS Liquid Glass | Partial, device-tested in v0.4 | Custom native Kodi transparent lenses and icons; no true OS refraction in Kodi |
| No brand label in top left | Implemented in v0.6.1 | Removes permanent "DEX GLASS" text |
| SF-like typography | Implemented in v0.6.1, device untested | Pinned SIL OFL Inter; do not embed restricted Apple SF Pro font |
| Graphical film/TV title clearlogos | Improved in v0.6.1, device untested | Native item art plus a read-only local Dex Hub cached-clearlogo service; guaranteed text fallback when artwork unavailable |
| Continue Watching Movies | Device-tested v0.4 | Independent bridge filters Dex Hub's combined list |
| Recently Watched Movies | Partial | Official Dex Hub widget route; artwork/typing to verify |
| Continue Watching Episodes | Device-tested v0.4 | Independent bridge splits movie and episode rows |
| Next Episodes | Partial | Official Dex Hub Next Up widget route |
| Recently Watched Series | Partial | Official watched series widget route |
| Recommended for You | Partial | Official Dex Hub recommendations route |
| Dex/Kaptain Community Collections | Improved in v0.6.1; device untested | Real custom rows from locally installed Dex Hub Kaptain group/folder/catalogue index |
| Fully customisable skin rows | Partial | Up to 12 source-and-order slots on each of four real hubs; built-in feeds and selected Kaptain catalogues can be added, replaced, moved and removed. Card-shape and artwork overrides still remain |
| Dex Community Collections selector | New in v0.6.1 | Dex Glass-specific picker and per-page source assignment do not modify Dex Hub's own page |
| Trailer autoplay on focused title | Not yet integrated | Requires hook to official Dex Hub's trailers (respect existing settings) |
| Full title information with cast and crew | Not yet integrated | A redesigned title-detail window and proper metadata linkage required |
| Native item context menu | Not yet verified | Raw original plugin rows may expose menus; bridge-generated Kodi items can lose context actions; needs a bridge approach |
| Nuvio/AIOStreams access | Preserved by installed Dex Hub, interface incomplete | Dex Glass uses official Dex Hub routes; no sync credentials transferred |
| Trakt/MDBList/Simkl/Plex account sync | Preserved by installed Dex Hub, interface incomplete | Dex Hub retains account/sync logic; Dex Glass does not implement its own syncing |
| Notifications | Not yet integrated | Need to surface existing Dex Hub notifications inside Dex Glass |
| UI sounds | Not yet integrated | No final original sound design / settings yet |
| Ratings | Partial | Kodi row metadata; complete multi-source badges/ratings still pending |
| End-of-episode next-episode autoplay & prompt | Not yet independently verified | Dex Hub may handle playback; matching Dex Glass overlay/prompt needs implementation and CoreELEC testing |
| Skip credits button | Not yet integrated | Must preserve/implement Kodi-compatible player buttons and official Dex Hub playback triggers |
| Power/shutdown menu | Device-tested | Original Kodi shutdown menu from top-right icon |
| Free to use / no phone companion | Implemented | Uses Kodi, original local bridge and official separately installed Dex Hub |

## Delivery phases — stop shipping single-line cosmetic releases

1. **v0.6.1 consolidated bundle:** four independent configurable hubs, separate source ordering, per-page Kaptain selections, cached clearlogo service and text fallback, native search, restrained focus and smaller synopsis. Verify together on-device.
2. **Playback/metadata integration:** title information (cast and crew), context menu, next-episode prompt and skip credits integrated with official Dex Hub.
3. **Experience parity:** trailer autoplay, notifications, sound scheme, multi-source ratings and comprehensive layout editor. Do not fake these using links to Dex Hub's separate settings.
4. **Fit/finish:** Apple tvOS-inspired clear optical edges, smooth focus transitions, custom text and accessibility, performance testing on Ugoos AM9 Pro/CoreELEC.

All future builds should include automated syntax, XML and ZIP contract tests plus
explicit on-device compatibility notes. The separately installed official
Dex Hub plugin remains untouched, proprietary and separately licensed.

### Search / external navigation (v0.6.1)

The top navigation contains distinct Watch Now, Movies, TV Shows and Collections pages. The earlier Dex Hub tab is now the standard Kodi Add-ons tab. Search uses the original bridge Kodi keyboard and official Dex Hub public `skin_search` listing, rather than opening the Dex Hub-specific search window. A fully designed graphical Dex Glass search result page is not yet implemented.
