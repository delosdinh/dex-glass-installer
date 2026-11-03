"""Generate the genuine Dex Glass skin-settings window.

No Pyrus/Applify settings panels are exposed from our skin, so choosing
'Configure skin' in Kodi or the home screen's Settings icon edits Dex Glass
rather than an unrelated Pyrus homepage.
"""
import xml.etree.ElementTree as ET


def _el(parent, tag, text=None, **attrs):
    node=ET.SubElement(parent,tag,attrs)
    if text is not None:
        node.text=str(text)
    return node


def _image(parent,x,y,w,h,texture,border=None):
    c=_el(parent,"control",type="image")
    for tag,value in (("left",x),("top",y),("width",w),("height",h)):
        _el(c,tag,value)
    _el(c,"texture",texture,**({"border":str(border)} if border else {}))
    return c


def _label(parent,x,y,w,h,value,font="font36_title",color="FFFFFFFF"):
    c=_el(parent,"control",type="label")
    for tag,v in (("left",x),("top",y),("width",w),("height",h)):
        _el(c,tag,v)
    _el(c,"label",value)
    _el(c,"font",font)
    _el(c,"textcolor",color)
    _el(c,"aligny","center")
    return c


def create_settings():
    root=ET.Element("window")
    _el(root,"defaultcontrol","101",always="true")
    _el(root,"backgroundcolor","FF07101C")
    ctrls=_el(root,"controls")
    _image(ctrls,0,0,1920,1080,"dexglass/fallback.png")
    _image(ctrls,0,0,1920,1080,"dexglass/hero-scrim.png")
    _label(ctrls,95,88,1650,90,"Dex Glass  |  Customise Home","font60")
    _label(ctrls,102,175,1560,60,
           "Your row layout belongs to Dex Glass — not the Dex Hub skin.",
           "font25_title","FFD5E7F6")

    buttons=[
        ("Customise All Hub Rows",
         "RunPlugin(plugin://plugin.video.dexglass.bridge/?action=configure)"),
        ("Add a New Row",
         "RunPlugin(plugin://plugin.video.dexglass.bridge/?action=add)"),
        ("Reset One Hub to Defaults",
         "RunPlugin(plugin://plugin.video.dexglass.bridge/?action=reset)"),
        ("Search Films and Series",
         "RunPlugin(plugin://plugin.video.dexglass.bridge/?action=search)"),
        ("Official Dex Hub Add-on Settings",
         "Addon.OpenSettings(plugin.video.dexhub)"),
        ("Kodi System Settings",
         "ActivateWindow(Settings)"),
        ("Back to Dex Glass",
         "PreviousMenu"),
    ]
    for index,(title,action) in enumerate(buttons):
        bid=101+index
        y=274+index*92
        c=_el(ctrls,"control",type="button",id=str(bid))
        for tag,value in (("left",100),("top",y),("width",900),("height",75)):
            _el(c,tag,value)
        _el(c,"label",title)
        _el(c,"font","font36_title")
        _el(c,"textcolor","FFEDF5FF")
        _el(c,"focusedcolor","FFFFFFFF")
        _el(c,"align","left")
        _el(c,"aligny","center")
        _el(c,"textoffsetx",22)
        _el(c,"texturefocus","dexglass/nav-lens.png",border="24,20,24,20")
        _el(c,"texturenofocus","dexglass/nav-surface.png",border="36,25,36,25")
        _el(c,"onclick",action)
        _el(c,"onup",str(101+(index-1)%len(buttons)))
        _el(c,"ondown",str(101+(index+1)%len(buttons)))
        _el(c,"onleft",str(bid))
        _el(c,"onright",str(bid))
    _label(ctrls,1070,315,720,55,"Independent Kodi hubs","font36_title")
    for n,page in enumerate(("Watch Now","Movies","TV Shows","Collections")):
        _label(ctrls,1070,395+n*78,775,58,page,
               "font32_title","FFE7ECFF")
    _label(ctrls,1070,745,700,180,
           "12 configurable slots per hub. Choose built-in feeds or Kaptain catalogues. Reorder, replace or remove rows without changing Dex Hub.",
           "font20_title","FFD5E7F6")
    ET.indent(root,space="  ")
    data=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    assert b"plugin.video.dexglass.bridge" in data
    return data
