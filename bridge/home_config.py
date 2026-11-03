# -*- coding: utf-8 -*-
"""Dex Glass independent multi-page home editor.

All rows are positioned using bridge-managed slots, so users can reorder
presets and Kaptain catalogues without rewriting Kodi XML. The state lives
exclusively in this bridge's addon_data and is never written to Dex Hub.
"""
import json
import os
import time
from urllib.parse import parse_qs, urlparse

import xbmc
import xbmcgui

PAGES=("watch","movies","tv","collections")
PAGE_NAMES={"watch":"Watch Now","movies":"Movies","tv":"TV Shows","collections":"Collections"}
SLOTS=12
SKIN="skin.dexglass"
PRESETS={
 "continue_movies":("Continue Watching Movies","bridge:movie","wide"),
 "recent_movies":("Recently Watched Movies","action=recently_watched&media=movie","poster"),
 "continue_episodes":("Continue Watching Episodes","bridge:series","wide"),
 "next_episodes":("Next Episodes","action=nextup","wide"),
 "recent_series":("Recently Watched Series","action=recently_watched&media=series","poster"),
 "recommended_movies":("Recommended for You","action=lib_because&media=movie","poster"),
 "collections":("Dex Collections","actions:collections","wide")
}
DEFAULTS={
 "watch":["continue_movies","recent_movies","continue_episodes","next_episodes",
          "recent_series","recommended_movies","collections"],
 "movies":["continue_movies","recent_movies","recommended_movies","collections"],
 "tv":["continue_episodes","next_episodes","recent_series","collections"],
 "collections":["collections"]
}


def _profile():
    import xbmcvfs
    root=xbmcvfs.translatePath("special://profile/addon_data/plugin.video.dexglass.bridge/")
    os.makedirs(root,exist_ok=True)
    return root


def config_path():
    return os.path.join(_profile(),"home_rows.json")


def _default():
    return {page:[{"kind":"preset","id":id} for id in defaults]
            for page,defaults in DEFAULTS.items()}


def safe_row(row):
    if not isinstance(row,dict):
        return None
    kind=str(row.get("kind") or "")
    if kind=="preset" and row.get("id") in PRESETS:
        return {"kind":"preset","id":row["id"]}
    if kind=="catalog":
        url=str(row.get("url") or "")
        if not url.startswith("plugin://plugin.video.dexhub/?"):
            return None
        action=(parse_qs(urlparse(url).query).get("action") or [""])[0]
        if action not in ("collection_nuvio_source_open","collection_nuvio_sources_open",
                          "collection_entry_open"):
            return None
        return {"kind":"catalog","url":url,"title":str(row.get("title") or "Collection")[:110],
                "group":str(row.get("group") or "")[:100],
                "folder":str(row.get("folder") or "")[:100]}
    return None


def load():
    cfg=_default()
    try:
        with open(config_path(),"r",encoding="utf-8") as f:
            saved=json.load(f)
        if isinstance(saved,dict) and saved.get("version")==2:
            for p in PAGES:
                page=(saved.get("pages") or {}).get(p)
                if isinstance(page,list):
                    cfg[p]=[r for r in (safe_row(x) for x in page) if r][:SLOTS]
            return cfg
    except (OSError,ValueError,TypeError):
        pass
    # Migrate user choices created by the first Dex Glass collection editor.
    # Keep their old file intact for rollback, append choices after defaults.
    old=os.path.join(_profile(),"collections.json")
    try:
        with open(old,"r",encoding="utf-8") as f:
            legacy=json.load(f)
        for item in (legacy.get("slots") or []):
            if isinstance(item,dict):
                obj=safe_row(dict(item,kind="catalog"))
                if obj:
                    cfg["watch"].append(obj)
    except (OSError,ValueError,TypeError,AttributeError):
        pass
    return cfg


def save(cfg):
    cleaned={p:[r for r in (safe_row(x) for x in cfg.get(p,[]))
                if r][:SLOTS] for p in PAGES}
    path=config_path()
    tmp=path+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        json.dump({"version":2,"pages":cleaned},f,indent=2,ensure_ascii=False)
    os.replace(tmp,path)


def name_of(row):
    if row.get("kind")=="preset":
        return PRESETS[row["id"]][0]
    return str(row.get("title") or "Kaptain Catalogue")


def source_of(row):
    if row.get("kind")=="preset":
        return PRESETS[row["id"]][1]
    return row.get("url") or ""


def row_at(page,slot):
    if page not in PAGES: return None
    try: idx=int(slot)-1
    except (TypeError,ValueError): return None
    if idx<0 or idx>=SLOTS:return None
    rows=load().get(page,[])
    return rows[idx] if idx<len(rows) else None


def key(page,index):
    return "DexGlass.Row.%s.%d.Title"%(page,index+1)


def publish_settings(cfg=None):
    if xbmc.getSkinDir()!=SKIN:
        return False
    cfg=cfg or load()
    for p in PAGES:
        rows=cfg.get(p,[])
        for i in range(SLOTS):
            text=name_of(rows[i]) if i<len(rows) else ""
            # Kodi skin strings are namespaced to skin.dexglass, not Dex Hub.
            # Only saved catalogue titles and preset names go into this call.
            value=str(text).replace(","," ").replace("("," ").replace(")"," ")[:110]
            if value:
                xbmc.executebuiltin("Skin.SetString(%s,%s)"%(key(p,i),value))
            else:
                xbmc.executebuiltin("Skin.Reset(%s)"%key(p,i))
    return True


def _commit(cfg):
    save(cfg)
    publish_settings(cfg)
    try:
        home=xbmcgui.Window(10000)
        home.setProperty("dg.config.updated",str(time.time()))
    except Exception:
        pass
    xbmc.executebuiltin("ActivateWindow(Home)")
    xbmc.executebuiltin("ReloadSkin()")


def _choose_page(title):
    idx=xbmcgui.Dialog().select(title,[PAGE_NAMES[p] for p in PAGES])
    return PAGES[idx] if 0<=idx<len(PAGES) else None


def _choose_source():
    dlg=xbmcgui.Dialog()
    choice=dlg.select("Choose row source",
                       ["Kaptain / Dex Community catalogue",
                        "Built-in Kodi / Dex Hub media feed"])
    if choice<0:return None
    if choice==0:
        from custom_collections import choose_catalogue
        result=choose_catalogue()
        if result:
            return safe_row(dict(result,kind="catalog"))
        return None
    values=list(PRESETS)
    idx=dlg.select("Choose media row",[PRESETS[k][0] for k in values])
    return {"kind":"preset","id":values[idx]} if 0<=idx<len(values) else None


def _row_picker(page,rows):
    labels=["%d. %s"%(i+1,name_of(row)) for i,row in enumerate(rows)]
    labels+=["%d. + Add another row"%(len(rows)+1)]
    return xbmcgui.Dialog().select(PAGE_NAMES[page]+" — Choose row",labels)


def configure():
    if xbmc.getSkinDir()!=SKIN:
        xbmcgui.Dialog().ok("Dex Glass","Switch to the Dex Glass skin before editing its layout.")
        return
    dlg=xbmcgui.Dialog()
    while True:
        page=_choose_page("Customise Dex Glass page")
        if page is None:return
        while True:
            cfg=load()
            rows=cfg[page]
            ix=_row_picker(page,rows)
            if ix<0:break
            if ix==len(rows):
                if len(rows)>=SLOTS:
                    dlg.ok("Dex Glass","This page already has %d rows."%SLOTS)
                    continue
                chosen=_choose_source()
                if chosen:
                    rows.append(chosen)
                    _commit(cfg)
                    return
                continue
            row=rows[ix]
            action=dlg.select(name_of(row),[
                "Replace this row source",
                "Move row earlier",
                "Move row later",
                "Remove row",
                "Back"
            ])
            if action==0:
                new=_choose_source()
                if new:rows[ix]=new
                else:continue
            elif action==1:
                if ix==0:continue
                rows[ix-1],rows[ix]=rows[ix],rows[ix-1]
            elif action==2:
                if ix>=len(rows)-1:continue
                rows[ix+1],rows[ix]=rows[ix],rows[ix+1]
            elif action==3:
                if not dlg.yesno("Remove row from Dex Glass?",
                                 name_of(row)+" will be removed only from this skin."):
                    continue
                rows.pop(ix)
            else:
                continue
            _commit(cfg)
            return


def add():
    """One-step create action, picking the destination page and source."""
    page=_choose_page("Add a row to which page?")
    if not page:return
    cfg=load()
    if len(cfg[page])>=SLOTS:
        xbmcgui.Dialog().ok("Dex Glass","The selected page is full. Replace or remove a row.")
        return
    row=_choose_source()
    if not row:return
    cfg[page].append(row)
    _commit(cfg)


def reset():
    dlg=xbmcgui.Dialog()
    page=_choose_page("Reset which Dex Glass page?")
    if not page:return
    if not dlg.yesno("Restore default rows?",PAGE_NAMES[page]+" will return to its original row order."):
        return
    cfg=load()
    cfg[page]=_default()[page]
    _commit(cfg)
