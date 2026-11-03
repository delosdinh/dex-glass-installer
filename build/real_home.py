#!/usr/bin/env python3
"""Build the *original* Dex Glass home screen, independent of Pyrus Home.xml.

Pyrus is only the compatibility scaffold for Kodi's other windows, media and
fonts. The entire Home.xml here is new: floating clear-glass navigation,
focus-responsive full-screen fanart, seven real Dex Hub plugin-fed shelves,
native search and power buttons. Nothing from proprietary Dex Hub is copied.

Dex Hub is an optional external plugin: its routes are invoked by Kodi.
"""
import xml.etree.ElementTree as ET

DEX = "plugin://plugin.video.dexhub/"
BRIDGE = "plugin://plugin.video.dexglass.bridge/"
ROWS = (
    # label, external public plugin route, presentation
    ("Continue Watching Movies", "bridge:movie", "wide"),
    ("Recently Watched Movies", "action=recently_watched&media=movie", "poster"),
    ("Continue Watching Episodes", "bridge:series", "wide"),
    ("Next Episodes", "action=nextup", "wide"),
    ("Recently Watched Series", "action=recently_watched&media=series", "poster"),
    ("Recommended for You", "action=lib_because&media=movie", "poster"),
    ("Dex Collections", "collections:static", "wide"),
)
CUSTOM_SLOTS = 4
IDS = tuple(5101+i for i in range(len(ROWS)+CUSTOM_SLOTS))


def el(parent, tag, value=None, **attrs):
    node=ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})
    if value is not None:
        node.text=str(value)
    return node


def control(parent, kind, left, top, width, height, ident=None):
    attrib={"type":kind}
    if ident is not None:
        attrib["id"]=str(ident)
    node=el(parent,"control",**attrib)
    for name,value in (("left",left),("top",top),("width",width),("height",height)):
        el(node,name,value)
    return node


def image(parent,x,y,w,h,texture,*,fade=0,diffuse=None,visible=None,
          border=None,background=False,aspect=None):
    node=control(parent,"image",x,y,w,h)
    attrs={}
    if border is not None: attrs["border"]=str(border)
    if diffuse:attrs["diffuse"]=diffuse
    if background:attrs["background"]="true"
    el(node,"texture",texture,**attrs)
    if fade:el(node,"fadetime",fade)
    if aspect:el(node,"aspectratio",aspect)
    if visible:el(node,"visible",visible)
    return node


def label(parent,x,y,w,h,text,size="font13",color="FFF4F6FC",*,
          visible=None,align="left",scroll=False):
    node=control(parent,"label",x,y,w,h)
    el(node,"label",text)
    el(node,"font",size)
    el(node,"textcolor",color)
    el(node,"shadowcolor","AA000000")
    el(node,"align",align)
    el(node,"aligny","center")
    if not scroll:el(node,"scroll","false")
    if visible:el(node,"visible",visible)
    return node


def textbox(parent,x,y,w,h,text,size="font14",color="FFE4EAF4"):
    node=control(parent,"textbox",x,y,w,h)
    el(node,"label",text)
    el(node,"font",size)
    el(node,"textcolor",color)
    el(node,"wrapmultiline","true")
    el(node,"scroll","false")
    return node


def pill_button(parent, ident, x, y, w, text, onclick, left=None, right=None, down=5101, icon=None):
    group=control(parent,"group",x,y,w,64)
    image(group,0,0,w,62,"dexglass/nav-shadow.png",border="28,20,28,20",
          visible=f"Control.HasFocus({ident})")
    image(group,0,0,w,62,"dexglass/nav-lens.png",border="24,20,24,20",
          visible=f"Control.HasFocus({ident})")
    node=control(group,"button",0,0,w,62,ident)
    el(node,"label","" if icon else text)
    el(node,"description",text)
    el(node,"font","font25_title")
    el(node,"textcolor","FFDCE8F9")
    el(node,"focusedcolor","FFFFFFFF")
    el(node,"align","center")
    el(node,"aligny","center")
    el(node,"shadowcolor","90000000")
    el(node,"texturefocus")
    el(node,"texturenofocus")
    el(node,"pulseonselect","false")
    el(node,"onclick",onclick)
    el(node,"onleft",left if left else ident)
    el(node,"onright",right if right else ident)
    el(node,"onup",ident)
    el(node,"ondown",down)
    el(node,"onback","ActivateWindow(ShutdownMenu)")
    if icon:
        image(group,(w-46)//2,8,46,46,"dexglass/icon-"+icon+".png")
    return group


def tile(parent, width, height, poster=False, focused=False):
    holder=el(parent,"focusedlayout" if focused else "itemlayout",
              width=str(width),height=str(height))
    if focused:
        anim=el(holder,"animation",type="Focus")
        el(anim,"effect",type="zoom",start="100",end="105",time="190",
           tween="sine",easing="out",center="auto")
        anim2=el(holder,"animation",type="Unfocus")
        el(anim2,"effect",type="zoom",start="105",end="100",time="160",
           tween="sine",easing="out",center="auto")
    group=control(holder,"group",6,7,width-15,height-20)
    cw=width-20
    ch=height-23
    art="poster" if poster else "landscape"
    alt="thumb"
    mask="dexglass/tile-mask-poster.png" if poster else "dexglass/tile-mask-wide.png"
    image(group,0,0,cw,ch,f"$INFO[ListItem.Art({art})]",
          background=True,aspect="scale",diffuse=mask,
          visible=f"!String.IsEmpty(ListItem.Art({art}))")
    image(group,0,0,cw,ch,f"$INFO[ListItem.Art({alt})]",
          background=True,aspect="scale",diffuse=mask,
          visible=f"String.IsEmpty(ListItem.Art({art}))")
    image(group,0,0,cw,ch,"dexglass/tile-shade.png",
          border="24,24,24,24")
    if focused:
        image(group,0,0,cw,ch,"dexglass/tile-glow.png",border="24,24,24,24")
    title_y=ch-(57 if not poster else 72)
    label(group,15,title_y,cw-27,38,"$INFO[ListItem.Label]",
          "font25_title" if not poster else "font20_title","FFFFFFFF")
    label(group,15,ch-28,cw-28,22,"$INFO[ListItem.Label2]",
          "font20_title","FFD4DAE5")
    return holder


def shelf(parent, index, title, query, shape):
    ident=IDS[index]
    poster=shape=="poster"
    card_width=224 if poster else 364
    card_height=300 if poster else 225
    group_height=370 if poster else 285
    wrapper=control(parent,"group",0,0,1790,group_height)
    label(wrapper,4,0,1480,42,title,"font36_title","FFEDF5FF")
    # Rows are Kodi lists containing Dex Hub's own items, click paths and context menus.
    view=control(wrapper,"list",0,45,1800,card_height+24,ident)
    el(view,"orientation","horizontal")
    el(view,"scrolltime","260",tween="sine",easing="out")
    el(view,"itemgap","15")
    el(view,"preloaditems","2")
    el(view,"onfocus",f"SetProperty(dg.focus,{index+1},Home)")
    el(view,"onup",IDS[index-1] if index else "1001")
    el(view,"ondown",IDS[index+1] if index<len(ROWS)-1 else ident)
    el(view,"onleft",ident)
    el(view,"onright",ident)
    el(view,"onback","SetFocus(1001)")
    tile(view,card_width,card_height,poster=poster,focused=False)
    tile(view,card_width,card_height,poster=poster,focused=True)
    if query == "collections:static":
        # Dex Hub's collection_sets opens its custom interface and does not
        # provide Kodi poster items. Launch the official Kaptain/Community
        # screen from static, focusable collection cards instead.
        content=el(view,"content")
        shortcuts=(
            ("Kaptain / Dex Collection", "Add its catalogues to Dex Glass", "kaptain",
             "RunPlugin(plugin://plugin.video.dexglass.bridge/?action=add)"),
            ("Customise My Collections", "Edit rows in Dex Glass, not Dex Hub", "community",
             "RunPlugin(plugin://plugin.video.dexglass.bridge/?action=configure)"),
            ("Arrange Dex Glass Rows", "Move or remove pinned catalogues", "organise",
             "RunPlugin(plugin://plugin.video.dexglass.bridge/?action=configure)"),
            ("Open Dex Community", "Optional original Dex Hub collection browser", "imports",
             "RunPlugin(plugin://plugin.video.dexhub/?action=home_community)"),
        )
        for k,(name,subtitle,art,action) in enumerate(shortcuts,1):
            item=el(content,"item",id=k)
            el(item,"label",name)
            el(item,"label2",subtitle)
            el(item,"thumb","special://skin/media/dexglass/collection-"+art+".png")
            el(item,"onclick",action)
    elif query.startswith("bridge:"):
        el(view,"content",BRIDGE+"?media="+query.split(":",1)[1],
           target="videos",limit="30",browse="never")
    elif query.startswith("slot:"):
        el(view,"content",BRIDGE+"?action=slot&slot="+query.split(":",1)[1],
           target="videos",limit="30",browse="never")
    else:
        el(view,"content",DEX+"?"+query,target="videos",limit="30",browse="never")
    return wrapper


def create_variables():
    root=ET.Element("includes")
    props=("Title","Plot","Fanart","Clearlogo","Year","Genre","Rating")
    labels={
        "Title":"Label",
        "Plot":"Plot",
        "Fanart":"Art(fanart)",
        "Clearlogo":"Art(clearlogo)",
        "Year":"Year",
        "Genre":"Genre",
        "Rating":"Rating",
    }
    for key in props:
        var=el(root,"variable",name="DG_"+key)
        for i,ident in enumerate(IDS,1):
            current=f"String.IsEqual(Window(Home).Property(dg.focus),{i})"
            if key=="Clearlogo":
                # Kodi/official Dex Hub may supply a clearlogo on the work,
                # on the parent TV show or as a ListItem property. Do not
                # replace title artwork with a generic image when it is absent.
                artwork=("Art(clearlogo)","Art(tvshow.clearlogo)",
                         "Property(clearlogo)","Property(tvshow.clearlogo)")
                for label in artwork:
                    info=f"Container({ident}).ListItem.{label}"
                    el(var,"value","$INFO["+info+"]",
                       condition=current+" + !String.IsEmpty("+info+")")
            else:
                value=f"$INFO[Container({ident}).ListItem.{labels[key]}]"
                el(var,"value",value,condition=current)
        default="Select a title" if key=="Title" else ""
        if key=="Fanart":
            default="$INFO[Container(5101).ListItem.Art(fanart)]"
        elif key=="Title":
            default="$INFO[Container(5101).ListItem.Label]"
        el(var,"value",default)
    ET.indent(root,space="  ")
    return ET.tostring(root,encoding="utf-8",xml_declaration=True)


def create_home():
    root=ET.Element("window")
    el(root,"defaultcontrol","1001",always="false")
    el(root,"menucontrol","1001")
    el(root,"backgroundcolor","FF030912")
    el(root,"onload","SetProperty(dg.focus,1,Home)")
    el(root,"onback","ActivateWindow(ShutdownMenu)")
    controls=el(root,"controls")
    # Fanart always occupies the whole display (even behind rows/navigation).
    image(controls,0,0,1920,1080,"dexglass/fallback.png",aspect="stretch")
    image(controls,0,0,1920,1080,"$VAR[DG_Fanart]",
          fade=500,background=True,aspect="scale")
    image(controls,0,0,1920,1080,"dexglass/hero-scrim.png")
    # Clear navigation surfaces; avoid opaque frosted panes.
    image(controls,490,38,875,80,"dexglass/nav-surface.png",border="36,25,36,25")
    image(controls,1530,38,330,80,"dexglass/nav-surface.png",border="36,25,36,25")
    # No top-left Dex Glass wordmark: let the cinematic artwork breathe.
    navigation=(
        (1001,515,166,"Watch Now","SetFocus(5101)"),
        (1002,684,136,"Movies",'ActivateWindow(Videos,"plugin://plugin.video.dexhub/?action=nuvio_home_media&media=movie",return)'),
        (1003,824,148,"TV Shows",'ActivateWindow(Videos,"plugin://plugin.video.dexhub/?action=nuvio_home_media&media=series",return)'),
        (1004,980,195,"Collections","RunPlugin(plugin://plugin.video.dexglass.bridge/?action=configure)"),
        (1005,1177,167,"Dex Hub",'ActivateWindow(Videos,"plugin://plugin.video.dexhub/",return)'),
        (1006,1538,96,"Search","RunPlugin(plugin://plugin.video.dexhub/?action=home_search)"),
        (1007,1644,96,"Settings","ActivateWindow(SkinSettings)"),
        (1008,1750,96,"Power","ActivateWindow(ShutdownMenu)"),
    )
    for k,(ident,x,w,text,action) in enumerate(navigation):
        pill_button(controls,ident,x,45,w,text,action,
                    left=navigation[k-1][0] if k else 1008,
                    right=navigation[k+1][0] if k<len(navigation)-1 else 1001,
                    icon={1006:"search",1007:"settings",1008:"power"}.get(ident))
    # Hero title supports optional clearlogo supplied by Dex Hub, then text.
    image(controls,86,202,885,214,"$VAR[DG_Clearlogo]",aspect="keep",
          visible="!String.IsEmpty($VAR[DG_Clearlogo])",fade=200)
    label(controls,86,233,1030,160,"$VAR[DG_Title]","font60","FFFFFFFF",
          visible="String.IsEmpty($VAR[DG_Clearlogo])")
    label(controls,88,405,800,42,
          "$VAR[DG_Year]   •   $VAR[DG_Genre]   •   ★ $VAR[DG_Rating]",
          "font25_title","FFECF1FA")
    textbox(controls,89,462,775,122,"$VAR[DG_Plot]","font14")
    pill_button(controls,1101,86,590,280,"Open Dex Hub",
                'ActivateWindow(Videos,"plugin://plugin.video.dexhub/",return)',
                left=1101,right=1102)
    pill_button(controls,1102,377,590,258,"Browse Movies",
                'ActivateWindow(Videos,"plugin://plugin.video.dexhub/?action=nuvio_home_media&media=movie",return)',
                left=1101,right=1102)
    # First screen shows a section and part of the next; down scrolls all seven.
    shelves=control(controls,"grouplist",68,680,1805,400,7000)
    el(shelves,"orientation","vertical")
    el(shelves,"itemgap","16")
    el(shelves,"scrolltime","330",tween="sine",easing="out")
    el(shelves,"usecontrolcoords","true")
    for i,(title,query,shape) in enumerate(ROWS):
        shelf(shelves,i,title,query,shape)
    # Four real, user-configurable collection shelves, populated by the
    # bridge from selected Kaptain/Dex Community catalogue paths. The
    # separate Kodi Skin.String values make empty slots disappear completely.
    for i in range(CUSTOM_SLOTS):
        slot=i+1
        title="$INFO[Skin.String(DexGlass.Collection.%d.Title)]" % slot
        custom=shelf(shelves,len(ROWS)+i,title,"slot:%d"%slot,"poster")
        el(custom,"visible","Skin.String(DexGlass.Collection.%d.Title)"%slot)
    label(controls,1140,568,680,45,
          "ARROWS  BROWSE    •    OK  OPEN    •    BACK  MENU",
          "font20_title","CCDBE6F5",align="right")
    ET.indent(root,space="  ")
    data=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    check_home(data)
    return data


def patch_includes(data):
    root=ET.fromstring(data)
    if not any(item.attrib.get("file")=="DexGlass_Variables.xml"
               for item in root.findall("include")):
        root.insert(0,ET.Element("include",{"file":"DexGlass_Variables.xml"}))
    ET.indent(root,space="  ")
    return ET.tostring(root,encoding="utf-8",xml_declaration=True)


def check_home(data):
    root=ET.fromstring(data)
    ids={n.attrib.get("id") for n in root.iter("control") if n.attrib.get("id")}
    expected={str(i) for i in IDS}
    if not expected.issubset(ids):raise ValueError("Missing one or more Dex Hub shelves")
    paths=[n.text for n in root.iter("content") if n.text and
           (DEX in n.text or BRIDGE in n.text)]
    expected_feeds=6+CUSTOM_SLOTS
    if len(paths)!=expected_feeds:
        raise ValueError(f"Expected {expected_feeds} feeds including custom slots, found {len(paths)}")
    bridges=[p for p in paths if p.startswith(BRIDGE)]
    if len(bridges)!=2+CUSTOM_SLOTS:raise ValueError("Missing film, episode or custom Kaptain feeds")
    items=[n for n in root.iter("item") if n.find("onclick") is not None]
    if len(items)!=4:raise ValueError("Dex Glass Collections chooser cards missing")
    if not any("dexglass.bridge/?action=add" in (x.findtext("onclick") or "") for x in items):
        raise ValueError("Kaptain picker isn't linked into Dex Glass")
    for n in range(1,CUSTOM_SLOTS+1):
        if not any("Skin.String(DexGlass.Collection.%d.Title)"%n in
                   (element.text or "") for element in root.iter("visible")):
            raise ValueError("Custom slot %d visibility isn't wired to skin settings" % n)
    utility_icons=[n.text for n in root.iter("texture") if (n.text or "").startswith("dexglass/icon-")]
    if len(utility_icons)!=3:raise ValueError("Top-right icon artwork missing")
    fanart=[n for n in root.iter("texture") if n.text=="$VAR[DG_Fanart]"]
    if not fanart:raise ValueError("No cinematic full-screen fanart")
    return True


if __name__=="__main__":
    print(create_home().decode()[:3200])
    print(create_variables().decode()[:500])
