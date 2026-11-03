# -*- coding: utf-8 -*-
"""Dex Glass-only Kaptain catalogue customisation.

This uses installed Dex Hub's group/folder catalogue index at runtime, without
bundling, editing, or copying its proprietary Python/data. Saved selections
live exclusively under this bridge's Kodi profile. Kodi skin strings make
selected shelves immediately visible in skin.dexglass only.
"""
import json
import os
import re
import sys
from urllib.parse import urlencode, parse_qs

import xbmc
import xbmcgui

SLOTS = 4
SKIN = "skin.dexglass"
PREFIX = "DexGlass.Collection"
BASE = "plugin://plugin.video.dexhub/"
SAFE_ACTIONS = {"collection_nuvio_source_open", "collection_nuvio_sources_open",
                "collection_entry_open"}


def _log(msg, level=xbmc.LOGINFO):
    xbmc.log("[DexGlassCollections] " + str(msg), level)


def config_path():
    import xbmcvfs
    root = xbmcvfs.translatePath("special://profile/addon_data/plugin.video.dexglass.bridge/")
    return os.path.join(root, "collections.json")


def load():
    try:
        with open(config_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("slots"), list):
            rows = data["slots"][:SLOTS]
            return (rows + [None] * SLOTS)[:SLOTS]
    except (OSError, ValueError, TypeError):
        pass
    return [None] * SLOTS


def save(rows):
    path = config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".new"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "slots": rows[:SLOTS]}, f, ensure_ascii=False,
                  indent=2)
    os.replace(tmp, path)


def skin_title(index):
    return "%s.%d.Title" % (PREFIX, index + 1)


def safe_label(value):
    text = re.sub(r"[,()\[\]\r\n]", " ", str(value or "").strip())
    return re.sub(r"\s+", " ", text)[:72]


def publish_settings(rows):
    # Skin settings are per-skin in Kodi; never mutate Pyrus or Dex Hub.
    if xbmc.getSkinDir() != SKIN:
        return False
    for i, row in enumerate(rows):
        key = skin_title(i)
        title = safe_label((row or {}).get("title", ""))
        if title:
            xbmc.executebuiltin("Skin.SetString(%s,%s)" % (key, title))
        else:
            xbmc.executebuiltin("Skin.Reset(%s)" % key)
    return True


def current_slot(number):
    try:
        n = int(number)
    except (TypeError, ValueError):
        return None
    if n < 1 or n > SLOTS:
        return None
    record = load()[n - 1]
    if not isinstance(record, dict):
        return None
    url = record.get("url") or ""
    if not url.startswith(BASE + "?"):
        return None
    action = (parse_qs(url.split("?", 1)[1]).get("action") or [""])[0]
    if action not in SAFE_ACTIONS:
        return None
    return record


def get_groups():
    """Import *installed* official Dex Hub API in memory, no source copied.

    The group data includes Kaptain, Dex Collection and imported collections.
    A Dex Hub update might change this private API; fail with an explicit
    message instead of substituting empty or unrelated cards.
    """
    import xbmcaddon
    addon = xbmcaddon.Addon("plugin.video.dexhub")
    root = addon.getAddonInfo("path")
    if not root or not os.path.isfile(os.path.join(root, "resources", "lib",
                                                  "homeui", "community.py")):
        raise RuntimeError("Official Dex Hub installation not found")
    if root not in sys.path:
        sys.path.insert(0, root)
    from resources.lib.homeui import community
    groups = community.groups()
    if not isinstance(groups, list):
        raise RuntimeError("Dex Hub did not return its collection groups")
    return groups


def _choose(collections):
    if not collections:
        raise ValueError("No Kaptain or imported collection groups found")
    dlg = xbmcgui.Dialog()
    idx = dlg.select("Dex Glass — Choose a collection group",
                     [str(g.get("name") or "Untitled") for g in collections])
    if idx < 0:
        return None
    g = collections[idx]
    folders = [f for f in (g.get("folders") or []) if f.get("catalogs")]
    if not folders:
        dlg.ok("Dex Glass", "This group doesn't contain any available catalogues.")
        return None
    j = dlg.select(str(g.get("name") or "Collection") + " — Choose folder",
                   [str(f.get("name") or "Untitled") for f in folders])
    if j < 0:
        return None
    f = folders[j]
    catalogs = f.get("catalogs") or []
    if len(catalogs) > 1:
        k = dlg.select("Choose a catalogue for Dex Glass",
                       [str(c.get("name") or "Catalogue") for c in catalogs])
        if k < 0:
            return None
    else:
        k = 0
    c = catalogs[k]
    title = str(f.get("name") or c.get("name") or "Kaptain Collection")
    cat_name = str(c.get("name") or "")
    if cat_name and cat_name.casefold() != title.casefold():
        title = "%s · %s" % (title, cat_name)

    # Dex Hub's own community API describes the official plugin route.
    if c.get("params"):
        params = dict(c["params"])
    else:
        params = {
            "action": "collection_nuvio_source_open",
            "set_id": str(g.get("set_id") or "builtin-kaptain"),
            "group_id": str(g.get("entry_id") or g.get("id") or ""),
            "folder_id": str(f.get("id") or ""),
            "source_index": str(c.get("idx", k)),
            "page": "1"
        }
    if params.get("action") not in SAFE_ACTIONS:
        raise ValueError("Unsupported Dex Hub collection action")
    # Avoid allowing arbitrary URLs from an imported Kaptain catalogue.
    params = {str(key): str(value) for key, value in params.items()
              if key in ("action", "set_id", "group_id", "folder_id",
                         "source_index", "source_indexes", "entry_id", "page")}
    url = BASE + "?" + urlencode(params)
    return {"title": safe_label(title), "url": url,
            "group": safe_label(g.get("name")), "folder": safe_label(f.get("name"))}


def choose_catalogue():
    try:
        return _choose(get_groups())
    except Exception as exc:
        _log("Cannot browse collection groups: %s: %s" %
             (type(exc).__name__, exc), xbmc.LOGWARNING)
        xbmcgui.Dialog().ok("Dex Glass Collections",
                            "Unable to read Kaptain catalogues from your installed Dex Hub.",
                            "Check that the official Dex Hub add-on is enabled.")
        return None


def _slot_options(rows):
    return ["%d. %s" % (i + 1, (row or {}).get("title") or "(empty)")
            for i, row in enumerate(rows)]


def refresh():
    xbmc.executebuiltin("ActivateWindow(Home)")
    xbmc.executebuiltin("ReloadSkin()")


def add():
    if xbmc.getSkinDir() != SKIN:
        xbmcgui.Dialog().ok("Dex Glass", "Switch to the Dex Glass skin before editing its rows.")
        return
    catalogue = choose_catalogue()
    if not catalogue:
        return
    rows = load()
    first = next((i for i, row in enumerate(rows) if row is None), None)
    # User can choose a specific slot or replace a filled one.
    dlg = xbmcgui.Dialog()
    labels = ["%d. %s" % (i + 1, (row or {}).get("title") or "(empty)")
              for i, row in enumerate(rows)]
    idx = dlg.select("Add catalogue to Dex Glass row", labels, preselect=first or 0)
    if idx < 0:
        return
    rows[idx] = catalogue
    save(rows)
    publish_settings(rows)
    dlg.notification("Dex Glass", "Added: " + catalogue["title"], xbmcgui.NOTIFICATION_INFO, 2500)
    refresh()


def remove():
    rows = load()
    dlg = xbmcgui.Dialog()
    choices = [i for i, r in enumerate(rows) if r]
    if not choices:
        dlg.ok("Dex Glass", "There are no custom collection rows to remove.")
        return
    chosen = dlg.select("Remove a Dex Glass collection row",
                        [_slot_options(rows)[i] for i in choices])
    if chosen < 0:
        return
    slot = choices[chosen]
    if not dlg.yesno("Remove Dex Glass row?",
                     "Remove %s from Dex Glass? This won't change Dex Hub." %
                     (rows[slot].get("title") or "this row")):
        return
    rows[slot] = None
    save(rows)
    publish_settings(rows)
    refresh()


def move():
    rows = load()
    dlg = xbmcgui.Dialog()
    choices = [i for i, r in enumerate(rows) if r]
    if not choices:
        dlg.ok("Dex Glass", "Add a collection row before changing its position.")
        return
    choice = dlg.select("Choose a row to move", [_slot_options(rows)[i] for i in choices])
    if choice < 0:
        return
    source = choices[choice]
    destination = dlg.select("Move row to which position?", _slot_options(rows))
    if destination < 0 or destination == source:
        return
    item = rows.pop(source)
    rows.insert(destination, item)
    save(rows)
    publish_settings(rows)
    refresh()


def configure():
    if xbmc.getSkinDir() != SKIN:
        xbmcgui.Dialog().ok("Dex Glass", "Activate the Dex Glass skin to customise its homepage.")
        return
    dlg = xbmcgui.Dialog()
    # Loading from JSON ensures Kodi skin settings are re-synchronised after
    # updating the skin package; no reliance on Pyrus's customisation keys.
    rows = load()
    publish_settings(rows)
    while True:
        descriptions = [r.get("title") for r in rows if r]
        summary = "%d of %d slots used" % (len(descriptions), SLOTS)
        action = dlg.select("Dex Glass · Customise Watch Now (" + summary + ")",
                            ["Add / replace a Kaptain or Dex Community catalogue",
                             "Remove a collection row",
                             "Change collection row order",
                             "View current rows",
                             "Back to Dex Glass"])
        if action in (-1, 4):
            break
        if action == 0:
            add()
            return
        if action == 1:
            remove()
            return
        if action == 2:
            move()
            return
        if action == 3:
            dlg.ok("Dex Glass custom rows",
                   "\n".join(_slot_options(rows)) or "No rows configured")
