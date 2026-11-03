# -*- coding: utf-8 -*-
"""Dex Glass original, read-only Kodi bridge for public Dex Hub listings.

Keeps films out of the series widget and vice versa. It asks Kodi to list
plugin://plugin.video.dexhub/?action=continue with Files.GetDirectory; it
does not import, modify or redistribute any Dex Hub files or tokens.

Compatibility: Kodi 21+/22, Python 3. JSON-RPC provider behaviour may differ
between installations. Unknown classifications are deliberately excluded
rather than misleadingly shown in both rows. Report counts, never titles.
"""
import json
import re
import sys
from urllib.parse import parse_qs, urlparse

import xbmc
import xbmcgui
import xbmcplugin

SOURCE = "plugin://plugin.video.dexhub/?action=continue"
MEDIA_ALIASES = {
    "movie": "movie", "film": "movie", "movies": "movie",
    "episode": "series", "episodes": "series", "tvshow": "series",
    "tvshows": "series", "tv": "series", "series": "series",
    "show": "series", "shows": "series", "season": "series",
    "anime": "series"
}
EPISODE_PATTERN = re.compile(r"\bS\d{1,2}\s*[:.\- ]?E\d{1,3}\b", re.I)


def log(message, level=xbmc.LOGINFO):
    xbmc.log("[DexGlassBridge] " + str(message), level)


def rpc(directory, media="video", properties=None):
    """Call Kodi itself. No remote service, no credentials."""
    query = {"jsonrpc": "2.0", "method": "Files.GetDirectory",
             "params": {"directory": directory, "media": media}, "id": 1}
    if properties:
        query["params"]["properties"] = properties
    result = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
    if result.get("error"):
        raise RuntimeError(str(result["error"].get("message") or "JSONRPC error"))
    return (result.get("result") or {}).get("files") or []


def read_continue():
    preferred = ["title", "plot", "year", "genre", "rating", "art",
                 "thumbnail", "showtitle", "season", "episode"]
    variants = [
        ("video", preferred),
        ("video", ["title", "art", "showtitle", "season", "episode"]),
        ("files", ["title", "art", "thumbnail"]),
        ("files", None),
    ]
    last = None
    for media, fields in variants:
        try:
            found = rpc(SOURCE, media, fields)
            # Kodi builds differ: some successfully return an empty video
            # list for plugin:// while the "files" mode contains the items.
            if found:
                return found
        except Exception as exc:
            last = exc
    if last:
        log("Kodi could not read all Dex Hub listing modes: %s" % last,
            xbmc.LOGWARNING)
    return []


def classify(item):
    """Use positive video-type evidence; never infer a film from no evidence."""
    file_path = str(item.get("file") or "")
    params = parse_qs(urlparse(file_path).query)
    # Prefer Dex Hub's canonical item type from its actual playable URL.
    for key in ("media_type", "type", "media", "content_type"):
        v = str((params.get(key) or [""])[0]).strip().lower()
        if v in MEDIA_ALIASES:
            return MEDIA_ALIASES[v]
    for key in ("type", "mediatype", "media_type"):
        value = str(item.get(key) or "").strip().lower()
        if value in MEDIA_ALIASES:
            return MEDIA_ALIASES[value]
    # JSON-RPC v12/v14 exposes VideoInfoTag fields on some Kodi builds.
    show = str(item.get("showtitle") or item.get("tvshowtitle") or "").strip()
    if show:
        return "series"
    season, episode = item.get("season"), item.get("episode")
    try:
        if season not in (None, "", -1) and episode not in (None, "", -1):
            if int(season) >= 0 and int(episode) >= 0:
                return "series"
    except (TypeError, ValueError):
        pass
    title = str(item.get("title") or item.get("label") or "")
    if EPISODE_PATTERN.search(title):
        return "series"
    return "unknown"


def make_item(row):
    title = row.get("label") or row.get("title") or "Untitled"
    item = xbmcgui.ListItem(label=str(title))
    raw_art=row.get("art") or {}
    art = dict(raw_art) if isinstance(raw_art,dict) else {}
    # Kodi JSON-RPC may return Dex Hub's art under a top-level key,
    # especially for Continue Watching episodes and TV parent titles.
    for source_key,dest in (("clearlogo","clearlogo"),
                            ("logo","clearlogo"),
                            ("tvshow.clearlogo","tvshow.clearlogo"),
                            ("clearart","clearart")):
        value=row.get(source_key)
        if value and not art.get(dest):
            art[dest]=str(value)
    if art.get("tvshow.clearlogo") and not art.get("clearlogo"):
        art["clearlogo"]=art["tvshow.clearlogo"]
    if row.get("thumbnail"):
        art.setdefault("thumb", row["thumbnail"])
        art.setdefault("poster", row["thumbnail"])
    if row.get("fanart"):
        art.setdefault("fanart", row["fanart"])
    if art:
        item.setArt(art)
    try:
        inf = item.getVideoInfoTag()
        inf.setTitle(str(row.get("title") or title))
        if row.get("plot"): inf.setPlot(str(row["plot"]))
        if row.get("year"): inf.setYear(int(row["year"]))
        if row.get("showtitle"): inf.setTvShowTitle(str(row["showtitle"]))
        if row.get("season") is not None: inf.setSeason(int(row["season"]))
        if row.get("episode") is not None: inf.setEpisode(int(row["episode"]))
    except (AttributeError, TypeError, ValueError):
        pass
    # No silent modifications of Dex Hub's own playback URLs.
    item.setProperty("dexglass.bridge", "1")
    return item


def note(handle, text):
    item = xbmcgui.ListItem(label=text)
    item.setProperty("dexglass.bridge.note", "1")
    xbmcplugin.addDirectoryItem(
        handle, "plugin://plugin.video.dexhub/?action=continue",
        item, isFolder=True)


def read_catalogue(url):
    """Get work cards from an installed Dex Hub collection's public route."""
    expected=["title","plot","year","genre","rating","art","thumbnail",
              "showtitle","season","episode"]
    last_error=None
    for mode, fields in (("video",expected),
                         ("video",["title","art","thumbnail"]),
                         ("files",["title","art","thumbnail"]),
                         ("files",None)):
        try:
            items=rpc(url,mode,fields)
            if items:
                return items
        except Exception as exc:
            last_error=exc
    if last_error:
        log("Kaptain widget catalogue: %s" % type(last_error).__name__,
            xbmc.LOGWARNING)
    return []


def collection_slot(handle, slot):
    """Render a saved Dex Glass collection as its own horizontal Kodi row."""
    from custom_collections import current_slot
    data=current_slot(slot)
    xbmcplugin.setContent(handle,"videos")
    if not data:
        xbmcplugin.endOfDirectory(handle,cacheToDisc=False)
        return
    url=data["url"]
    try:
        rows=read_catalogue(url)
        accepted=0
        for item in rows[:75]:
            path=str(item.get("file") or "")
            if not (path.startswith("plugin://plugin.video.dexhub/") or
                    path.startswith("videodb://")):
                continue
            folder=str(item.get("filetype") or "").lower()=="directory"
            xbmcplugin.addDirectoryItem(handle,path,make_item(item),isFolder=folder)
            accepted+=1
        # Keep a working pathway into the actual installed source even when
        # metadata cannot be enumerated via Kodi JSON-RPC on a CoreELEC build.
        if not accepted:
            li=xbmcgui.ListItem(label="Open " + str(data["title"]) + " in Dex Hub")
            li.setProperty("dexglass.bridge.note","1")
            xbmcplugin.addDirectoryItem(handle,url,li,isFolder=True)
        log("Kaptain widget slot %s: %d cards" % (slot,accepted))
    except Exception as exc:
        log("Kaptain widget slot %s failed: %s" % (slot,type(exc).__name__),
            xbmc.LOGWARNING)
        li=xbmcgui.ListItem(label="Open " + str(data["title"]) + " in Dex Hub")
        xbmcplugin.addDirectoryItem(handle,url,li,isFolder=True)
    xbmcplugin.endOfDirectory(handle,cacheToDisc=False)


def _list_items(handle, entries):
    accepted=0
    for obj in entries[:90]:
        path=str(obj.get("file") or "")
        if not (path.startswith("plugin://plugin.video.dexhub/") or
                path.startswith("videodb://")):
            continue
        is_folder=str(obj.get("filetype") or "").lower()=="directory"
        xbmcplugin.addDirectoryItem(handle,path,make_item(obj),isFolder=is_folder)
        accepted+=1
    return accepted


def _row_note(handle,label,url):
    li=xbmcgui.ListItem(label=label)
    li.setProperty("dexglass.bridge.note","1")
    xbmcplugin.addDirectoryItem(handle,url,li,isFolder=True)


def _actions_row(handle):
    """Browse/add/arrange *Dex Glass* collections rather than Dex Hub settings."""
    cards=(
        ("Add Kaptain Catalogue","Choose a group and its actual content",
         "collection-kaptain.png","plugin://plugin.video.dexglass.bridge/?action=add"),
        ("Customise All Rows","Change Watch Now, Movies and TV Shows",
         "collection-community.png","plugin://plugin.video.dexglass.bridge/?action=configure"),
        ("Open Dex Community","Browse the original catalogue catalogue",
         "collection-imports.png","plugin://plugin.video.dexhub/?action=home_community"),
    )
    for title,subtitle,asset,url in cards:
        item=xbmcgui.ListItem(label=title,label2=subtitle)
        item.setArt({"thumb":"special://skin/media/dexglass/"+asset,
                     "landscape":"special://skin/media/dexglass/"+asset})
        xbmcplugin.addDirectoryItem(handle,url,item,isFolder=True)
    xbmcplugin.endOfDirectory(handle,cacheToDisc=False)


def home_row(handle,page,slot):
    """One of 12 freely reorderable native widgets in each Dex Glass hub."""
    from home_config import row_at,source_of,name_of
    selected=row_at(page,slot)
    xbmcplugin.setContent(handle,"videos")
    if not selected:
        xbmcplugin.endOfDirectory(handle,cacheToDisc=False)
        return
    source=source_of(selected)
    if source=="actions:collections":
        _actions_row(handle)
        return
    if source in ("bridge:movie","bridge:series"):
        kind=source.split(":",1)[1]
        items=[x for x in read_continue() if classify(x)==kind]
        count=_list_items(handle,items)
        if not count:
            _row_note(handle,"Open Continue Watching in Dex Hub",SOURCE)
        xbmcplugin.endOfDirectory(handle,cacheToDisc=False)
        return
    url=source if source.startswith("plugin://plugin.video.dexhub/") else (
        "plugin://plugin.video.dexhub/?"+source)
    if not url.startswith("plugin://plugin.video.dexhub/?"):
        xbmcplugin.endOfDirectory(handle,cacheToDisc=False)
        return
    listed=read_catalogue(url)
    accepted=_list_items(handle,listed)
    if not accepted:
        _row_note(handle,"Open "+name_of(selected)+" in Dex Hub",url)
    xbmcplugin.endOfDirectory(handle,cacheToDisc=False)


def run():
    query=parse_qs((sys.argv[2] if len(sys.argv)>2 else "").lstrip("?"))
    action=(query.get("action") or [""])[0]
    # RunPlugin() invokes a video add-on with handle=-1; these are Kodi
    # dialogues, not listings. They must run before parsing the handle.
    if action in ("configure","add","reset"):
        from home_config import configure,add,reset
        {"configure":configure,"add":add,"reset":reset}[action]()
        return
    if action == "search":
        from search import open_search
        open_search(rpc)
        return
    try:
        handle = int(sys.argv[1])
    except (IndexError, ValueError):
        return
    if action == "row":
        home_row(handle,
                 (query.get("page") or ["watch"])[0],
                 (query.get("slot") or ["1"])[0])
        return
    if action == "slot":
        collection_slot(handle,(query.get("slot") or ["1"])[0])
        return
    try:
        wanted = (query.get("media") or ["movie"])[0]
        if wanted not in ("movie", "series"):
            wanted = "movie"
        result = read_continue()
        matches = [r for r in result if classify(r) == wanted
                   and str(r.get("file") or "").startswith("plugin://plugin.video.dexhub/")]
        counts = {"movie": 0, "series": 0, "unknown": 0}
        for row in result:
            counts[classify(row)] += 1
        log("Continue Watching: movie=%s series=%s unclassified=%s (requested %s)" %
            (counts["movie"], counts["series"], counts["unknown"], wanted))
        xbmcplugin.setContent(handle, "movies" if wanted == "movie" else "episodes")
        for row in matches:
            filepath = row["file"]
            item = make_item(row)
            folder = str(row.get("filetype") or "").lower() == "directory"
            xbmcplugin.addDirectoryItem(handle, filepath, item, isFolder=folder)
        if not matches and counts["unknown"]:
            # Don't put the same mixed titles into both rails as before.
            note(handle, "Open Dex Hub — some items have no movie/TV type")
        elif not result:
            note(handle, "Open Dex Hub Continue Watching")
        xbmcplugin.endOfDirectory(handle, cacheToDisc=False)
    except Exception as exc:
        log("Failed to build separated row: %s" % exc, xbmc.LOGERROR)
        try:
            note(handle, "Open Dex Hub Continue Watching")
            xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)
        except Exception:
            pass


if __name__ == "__main__":
    run()
