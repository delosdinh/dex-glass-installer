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
            return rpc(SOURCE, media, fields)
        except Exception as exc:
            last = exc
    log("Kodi could not read the Dex Hub Continue Watching listing: %s" % last,
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
    art = dict(row.get("art") or {})
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


def run():
    try:
        handle = int(sys.argv[1])
    except (IndexError, ValueError):
        return
    try:
        query = parse_qs(sys.argv[2].lstrip("?"))
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
