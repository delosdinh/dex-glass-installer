#!/usr/bin/env python3
"""Original Dex Glass home with truly separate Watch, Movies, TV, Collections.

Unlike the earlier scaffold, ALL rail positions are now data-driven by
home_config.py's per-page slots; the XML never embeds a private Dex Hub file.
The rows are standard Kodi plugin-backed widgets using the independent bridge.
"""
import xml.etree.ElementTree as ET

PAGES=("watch","movies","tv","collections")
PAGE_START={"watch":5101,"movies":5201,"tv":5301,"collections":5401}
SLOTS=12
BRIDGE="plugin://plugin.video.dexglass.bridge/"
IDS=[start+idx for start in PAGE_START.values() for idx in range(SLOTS)]


def el(parent,tag,text=None,**attrs):
    node=ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})
    if text is not None:node.text=str(text)
    return node


def ctl(parent,kind,x,y,w,h,ident=None):
    props={"type":kind}
    if ident is not None:props["id"]=str(ident)
    node=el(parent,"control",**props)
    for k,v in (("left",x),("top",y),("width",w),("height",h)):
        el(node,k,v)
    return node


def image(parent,x,y,w,h,texture,visible=None,border=None,aspect=None,background=False):
    node=ctl(parent,"image",x,y,w,h)
    props={}
    if border:props["border"]=str(border)
    if background:props["background"]="true"
    el(node,"texture",texture,**props)
    if visible:el(node,"visible",visible)
    if aspect:el(node,"aspectratio",aspect)
    return node


def text(parent,x,y,w,h,value,font="font25_title",color="FFF0F5FF",visible=None,align="left"):
    node=ctl(parent,"label",x,y,w,h)
    for k,v in (("label",value),("font",font),("textcolor",color),
                ("shadowcolor","B9000000"),("align",align),("aligny","center")):
        el(node,k,v)
    if visible:el(node,"visible",visible)
    return node


def item_layout(lst,w,h,poster=False,focused=False):
    layout=el(lst,"focusedlayout" if focused else "itemlayout",
              width=str(w),height=str(h))
    if focused:
        e=el(layout,"animation",type="Focus")
        el(e,"effect",type="zoom",start="100",end="104",time="190",
           tween="sine",easing="out",center="auto")
        e=el(layout,"animation",type="Unfocus")
        el(e,"effect",type="zoom",start="104",end="100",time="150",
           tween="sine",easing="out",center="auto")
    group=ctl(layout,"group",5,7,w-11,h-16)
    cw=w-18;ch=h-21
    art="poster" if poster else "landscape"
    shape="tile-mask-poster.png" if poster else "tile-mask-wide.png"
    for src,vis in ((f"$INFO[ListItem.Art({art})]",f"!String.IsEmpty(ListItem.Art({art}))"),
                    ("$INFO[ListItem.Art(thumb)]",f"String.IsEmpty(ListItem.Art({art}))")):
        x=image(group,0,0,cw,ch,src,visible=vis,aspect="scale",background=True)
        x.find("texture").set("diffuse","dexglass/"+shape)
    image(group,0,0,cw,ch,"dexglass/tile-shade.png",border="24,24,24,24")
    if focused:
        image(group,0,0,cw,ch,"dexglass/tile-glow.png",border="24,24,24,24")
    text(group,15,ch-(67 if poster else 49),cw-26,38,"$INFO[ListItem.Label]",
         "font20_title","FFFFFFFF")
    text(group,15,ch-27,cw-26,22,"$INFO[ListItem.Label2]",
         "font20_title","FFE1E6F0")
    return layout


def shelf(parent,page,slot):
    ident=PAGE_START[page]+slot
    key=f"DexGlass.Row.{page}.{slot+1}.Title"
    source=f"{BRIDGE}?action=row&page={page}&slot={slot+1}"
    # Shape follows position for consistent and performant 1080p layout;
    # source order is user-editable without rewriting XML.
    poster=slot in (1,4,5,7,9,11)
    cardw=226 if poster else 350
    cardh=300 if poster else 222
    rowh=363
    group=ctl(parent,"group",0,0,1770,rowh)
    el(group,"visible",f"!String.IsEmpty(Skin.String({key}))")
    text(group,6,4,1450,42,f"$INFO[Skin.String({key})]",
         "font32_title","FFFFFFFF")
    lst=ctl(group,"list",0,50,1782,cardh+24,ident)
    el(lst,"orientation","horizontal")
    el(lst,"scrolltime","220",tween="sine",easing="out")
    el(lst,"itemgap","16")
    el(lst,"preloaditems","2")
    el(lst,"onfocus",f"SetProperty(dg.focus,{ident},Home)")
    el(lst,"onup",ident-1 if slot else 1001)
    el(lst,"ondown",ident+1 if slot<SLOTS-1 else ident)
    el(lst,"onback","SetFocus(1001)")
    item_layout(lst,cardw,cardh,poster=poster,focused=False)
    item_layout(lst,cardw,cardh,poster=poster,focused=True)
    el(lst,"content",source,target="videos",limit="32",browse="never")
    return group


def nav_button(parent,cid,x,w,title,actions,left,right,down,icon=None):
    group=ctl(parent,"group",x,43,w,70)
    image(group,9,59,w-18,5,"dexglass/nav-fine-focus.png",
          visible=f"Control.HasFocus({cid})")
    node=ctl(group,"button",0,0,w,62,cid)
    for tag,value in (("label","" if icon else title),("description",title),
                      ("font","font25_title"),("textcolor","FFE0EAF9"),
                      ("focusedcolor","FFFFFFFF"),("align","center"),
                      ("aligny","center"),("texturefocus",""),
                      ("texturenofocus",""),("pulseonselect","false"),
                      ("onleft",left),("onright",right),
                      ("onup",cid),("ondown",down)):
        el(node,tag,value)
    for action in actions:el(node,"onclick",action)
    if icon:
        image(group,(w-45)//2,9,45,45,"dexglass/icon-"+icon+".png")
    return group


def create_variables():
    root=ET.Element("includes")
    fields={
        "Title":"Label","Plot":"Plot","Fanart":"Art(fanart)",
        "Year":"Year","Genre":"Genre","Rating":"Rating",
        "Clearlogo":"Art(clearlogo)"
    }
    for k,tag in fields.items():
        var=el(root,"variable",name="DG_"+k)
        for cid in IDS:
            present=f"String.IsEqual(Window(Home).Property(dg.focus),{cid})"
            if k=="Clearlogo":
                for form in ("Art(clearlogo)","Art(tvshow.clearlogo)",
                             "Property(clearlogo)","Property(tvshow.clearlogo)"):
                    ref=f"Container({cid}).ListItem.{form}"
                    el(var,"value",f"$INFO[{ref}]",
                       condition=present+" + !String.IsEmpty("+ref+")")
            else:
                el(var,"value",f"$INFO[Container({cid}).ListItem.{tag}]",
                   condition=present)
        if k=="Fanart":
            el(var,"value","$INFO[Container(5101).ListItem.Art(fanart)]")
        elif k=="Title":
            el(var,"value","$INFO[Container(5101).ListItem.Label]")
        else:
            el(var,"value","")
    ET.indent(root,space="  ")
    return ET.tostring(root,encoding="utf-8",xml_declaration=True)


def create_home():
    root=ET.Element("window")
    el(root,"defaultcontrol","1001",always="false")
    el(root,"menucontrol","1001")
    el(root,"backgroundcolor","FF030912")
    el(root,"onload","SetProperty(dg.page,watch,Home)")
    el(root,"onload","SetProperty(dg.focus,5101,Home)")
    el(root,"onback","ActivateWindow(ShutdownMenu)")
    controls=el(root,"controls")
    image(controls,0,0,1920,1080,"dexglass/fallback.png",aspect="stretch")
    image(controls,0,0,1920,1080,"$VAR[DG_Fanart]",background=True,aspect="scale")
    image(controls,0,0,1920,1080,"dexglass/hero-scrim.png")
    image(controls,490,38,875,80,"dexglass/nav-surface.png",border="36,25,36,25")
    image(controls,1530,38,330,80,"dexglass/nav-surface.png",border="36,25,36,25")
    # Five real menu actions. Dex Hub is an installed add-on, NOT a main hub.
    menus=[
      (1001,515,166,"Watch Now",["SetProperty(dg.page,watch,Home)","SetFocus(5101)"],None),
      (1002,684,136,"Movies",["SetProperty(dg.page,movies,Home)","SetFocus(5201)"],None),
      (1003,824,148,"TV Shows",["SetProperty(dg.page,tv,Home)","SetFocus(5301)"],None),
      (1004,980,195,"Collections",["SetProperty(dg.page,collections,Home)","SetFocus(5401)"],None),
      (1005,1177,167,"Add-ons",['ActivateWindow(Videos,"addons://sources/video/",return)'],None),
      (1006,1538,96,"Search",["RunPlugin(plugin://plugin.video.dexglass.bridge/?action=search)"],"search"),
      (1007,1644,96,"Settings",["ActivateWindow(SkinSettings)"],"settings"),
      (1008,1750,96,"Power",["ActivateWindow(ShutdownMenu)"],"power"),
    ]
    for i,(cid,x,w,title,actions,icon) in enumerate(menus):
        nav_button(controls,cid,x,w,title,actions,
                   menus[i-1][0] if i else menus[-1][0],
                   menus[i+1][0] if i+1<len(menus) else menus[0][0],
                   {1001:5101,1002:5201,1003:5301,1004:5401}.get(cid,5101),
                   icon=icon)

    has_logo="!String.IsEmpty(Window(Home).Property(dg.hero.clearlogo))"
    image(controls,86,204,860,200,"$INFO[Window(Home).Property(dg.hero.clearlogo)]",
          aspect="keep",visible=has_logo)
    # Guaranteed text fallback. No conditional involving $VAR in a boolean:
    # that was blanking the Dune heading on the CoreELEC photo.
    text(controls,86,237,1020,132,"$VAR[DG_Title]","font60","FFFFFFFF",
         visible="String.IsEmpty(Window(Home).Property(dg.hero.clearlogo))")
    text(controls,88,404,900,39,
         "$VAR[DG_Year]   •   $VAR[DG_Genre]   •   ★ $VAR[DG_Rating]",
         "font25_title","FFF0F5FF")
    plot=ctl(controls,"textbox",89,452,760,105)
    for k,v in (("label","$VAR[DG_Plot]"),("font","font20_title"),
                ("textcolor","FFE4EAF4"),("wrapmultiline","true"),("scroll","false")):
        el(plot,k,v)

    # Replace button saying "Open Dex Hub" with genuine title actions once
    # official plugin URLs expose details on the focused ListItem.
    nav_button(controls,1101,88,260,"Play / Open",
               ["SendClick(5101)"],1101,1102,5101)
    nav_button(controls,1102,367,247,"Customise",
               ["RunPlugin(plugin://plugin.video.dexglass.bridge/?action=configure)"],
               1101,1102,5101)
    # Each hub has its own *actual content* and can be configured separately.
    for page in PAGES:
        scroll=ctl(controls,"grouplist",68,660,1800,420,7000+list(PAGES).index(page))
        el(scroll,"orientation","vertical")
        el(scroll,"itemgap","8")
        el(scroll,"scrolltime","280",tween="sine",easing="out")
        el(scroll,"usecontrolcoords","true")
        el(scroll,"visible",f"String.IsEqual(Window(Home).Property(dg.page),{page})")
        for i in range(SLOTS):shelf(scroll,page,i)
    ET.indent(root,space="  ")
    result=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    check_home(result)
    return result


def patch_includes(data):
    root=ET.fromstring(data)
    if not any(x.attrib.get("file")=="DexGlass_Variables.xml"
               for x in root.findall("include")):
        root.insert(0,ET.Element("include",{"file":"DexGlass_Variables.xml"}))
    ET.indent(root,space="  ")
    return ET.tostring(root,encoding="utf-8",xml_declaration=True)


def check_home(data):
    root=ET.fromstring(data)
    ids={n.attrib.get("id") for n in root.iter("control") if n.attrib.get("id")}
    if not {str(i) for i in IDS}.issubset(ids):
        raise ValueError("A hub is missing configurable row slots")
    paths=[e.text for e in root.iter("content") if e.text and e.text.startswith(BRIDGE)]
    if len(paths)!=len(PAGES)*SLOTS:
        raise ValueError("Expected 12 configurable rows for each of four pages")
    for page in PAGES:
        if not any(f"page={page}" in s for s in paths):
            raise ValueError("Missing page: "+page)
    if not any(n.text=="$VAR[DG_Fanart]" for n in root.iter("texture")):
        raise ValueError("Focus-driven hero background missing")
    labels=[n.text for n in root.iter("label")]
    if "DEX  GLASS" in labels or "Dex Hub" in labels:
        raise ValueError("Unwanted brand navigation")
    if not any("dexglass.bridge/?action=search" in (x.text or "") for x in root.iter("onclick")):
        raise ValueError("Original search shortcut missing")
    return True


if __name__=="__main__":
    print(create_home().decode()[:2500])
