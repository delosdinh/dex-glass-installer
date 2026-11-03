# -*- coding: utf-8 -*-
"""Read-only Dex Glass hero artwork service.

Runs only while skin.dexglass is active. Resolves clearlogos from Kodi item
artwork and, if needed, from *installed* official Dex Hub's existing local
metadata cache. Does not download, modify or redistribute Dex Hub sources.
"""
import os
import sys
import urllib.parse

import xbmc
import xbmcgui

SKIN = "skin.dexglass"
HOME_ID = 10000


def info(cid, key):
    return (xbmc.getInfoLabel("Container(%s).ListItem.%s" % (cid, key)) or "").strip()


def local_logo(title, identifiers, media):
    if not identifiers and not title:
        return ""
    try:
        import xbmcaddon
        root = xbmcaddon.Addon("plugin.video.dexhub").getAddonInfo("path")
        if not root or not os.path.exists(os.path.join(root, "resources", "lib", "art.py")):
            return ""
        if root not in sys.path:
            sys.path.insert(0, root)
        from resources.lib.art import get_art_bundle_from_db
        bundle = get_art_bundle_from_db(
            tmdb_id=identifiers.get("tmdb") or "",
            imdb_id=identifiers.get("imdb") or "",
            media_type=media,
            title=title,
            year=identifiers.get("year") or "") or {}
        return str(bundle.get("clearlogo") or "")
    except Exception:
        return ""


def collect_logo(cid, cache):
    title = info(cid, "Label")
    path = info(cid, "FileNameAndPath")
    if not title:
        return "", ""
    for key in ("Art(clearlogo)", "Art(tvshow.clearlogo)",
                "Property(clearlogo)", "Property(tvshow.clearlogo)"):
        value=info(cid,key)
        if value and not value.lower().endswith(".svg"):
            return value, title
    parsed=urllib.parse.parse_qs(urllib.parse.urlparse(path).query)
    get=lambda k:(parsed.get(k) or [""])[0]
    tmdb = info(cid,"UniqueID(tmdb)") or get("tmdb_id") or get("tmdb")
    imdb = info(cid,"UniqueID(imdb)") or get("imdb_id") or get("imdb")
    year = info(cid,"Year") or get("year")
    media = get("media_type") or get("media") or info(cid,"DBTYPE") or "movie"
    if media.lower() in ("series","show","tv","episode","tvshow","season"):
        media="tv"
    else:
        media="movie"
    ident={"tmdb":tmdb,"imdb":imdb,"year":year}
    key=(title,tmdb,imdb,media)
    if key not in cache:
        cache[key]=local_logo(title,ident,media)
        # Bounded: no growing user title database in this service.
        if len(cache)>180:
            cache.clear()
    return cache.get(key) or "",title


def run():
    monitor=xbmc.Monitor()
    cache={}
    current=None
    synced=False
    home=xbmcgui.Window(HOME_ID)
    while not monitor.abortRequested():
        if xbmc.getSkinDir()!=SKIN:
            current=None
            synced=False
            if monitor.waitForAbort(1.1): break
            continue
        if not synced:
            # Rehydrate persisted collection row labels after Kodi launch.
            try:
                from home_config import publish_settings,load
                publish_settings(load())
            except Exception as exc:
                xbmc.log("[DexGlassHero] settings sync: %s" % type(exc).__name__,
                         xbmc.LOGWARNING)
            synced=True
        try:
            cid=int(home.getProperty("dg.focus") or "5101")
            if cid<5101 or cid>5412:
                cid=5101
            title=info(cid,"Label")
            path=info(cid,"FileNameAndPath")
            key=(cid,title,path)
            if key!=current:
                logo,found=collect_logo(cid,cache)
                home.setProperty("dg.hero.clearlogo",logo)
                current=key
        except Exception:
            pass
        if monitor.waitForAbort(0.45): break
    try:
        home.clearProperty("dg.hero.clearlogo")
    except Exception:
        pass


if __name__=="__main__":
    run()
