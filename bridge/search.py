# -*- coding: utf-8 -*-
"""Dex Glass search: native Kodi keyboard + results, not Dex Hub's skin UI.

Uses official Dex Hub's public 'skin_search' directory data and Kodi JSON-RPC.
No copied implementation, tokens, account access or custom window from Dex Hub.
"""
import xbmc
import xbmcgui
from urllib.parse import quote

def open_search(rpc):
    dialog=xbmcgui.Dialog()
    try:
        query=dialog.input("Search movies and TV shows",type=xbmcgui.INPUT_ALPHANUM)
    except (TypeError,AttributeError):
        query=dialog.input("Search movies and TV shows")
    query=str(query or "").strip()
    if len(query)<2:
        return
    # The official skin_search endpoint returns regular Kodi ListItems, unlike
    # home_search which opens the Dex Hub-specific full-screen search window.
    url="plugin://plugin.video.dexhub/?action=skin_search&m=all&query="+quote(query)
    rows=[]
    for media,fields in (
        ("video",["title","thumbnail","art","year","plot"]),
        ("video",None),("files",["title","thumbnail"]),("files",None)):
        try:
            rows=rpc(url,media,fields)
            if rows: break
        except Exception as exc:
            xbmc.log("[DexGlassSearch] %s: %s" % (type(exc).__name__,str(exc)[:90]),
                     xbmc.LOGDEBUG)
    if not rows:
        dialog.ok("Dex Glass Search",
                  "No results were returned for this search. Try a different title.")
        return
    rows=[r for r in rows if str(r.get("file") or "").startswith("plugin://plugin.video.dexhub/")]
    if not rows:
        dialog.ok("Dex Glass Search","No playable search items were returned.")
        return
    labels=[r.get("label") or r.get("title") or "Untitled" for r in rows]
    selected=dialog.select("Results for " + query[:50],labels)
    if selected<0:
        return
    path=str(rows[selected].get("file") or "")
    if '"' in path or "," in path or "\n" in path:
        # Kodi built-ins cannot safely accept arbitrary text in URLs.
        dialog.ok("Dex Glass Search","This search result uses an unsupported URL.")
        return
    if str(rows[selected].get("filetype") or "").lower()!="directory":
        xbmc.executebuiltin("PlayMedia("+path+")")
    else:
        xbmc.executebuiltin("ActivateWindow(Videos,"+path+",return)")
