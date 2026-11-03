"""Contract tests for Dex Glass's v0.6 native 4-page home and row editor.

These use fake Kodi objects; only a user's CoreELEC hardware can validate
rendering, playback and actual third-party plugin catalogue compatibility.
"""
import importlib.util
import json
import pathlib
import sys
import tempfile
import types
import unittest
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[1]
temp=tempfile.TemporaryDirectory()
xbmc=types.ModuleType("xbmc")
xbmc.LOGINFO=1;xbmc.LOGWARNING=2;xbmc.LOGERROR=3;xbmc.LOGDEBUG=4
xbmc.log=lambda *args,**kwargs:None
xbmc.executeJSONRPC=lambda _: '{"result":{"files":[]}}'
xbmc.getSkinDir=lambda:"skin.dexglass"
xbmc.executebuiltin=lambda command:None
sys.modules["xbmc"]=xbmc
xbmcgui=types.ModuleType("xbmcgui")
sys.modules["xbmcgui"]=xbmcgui
sys.modules["xbmcplugin"]=types.ModuleType("xbmcplugin")
xbmcvfs=types.ModuleType("xbmcvfs")
xbmcvfs.translatePath=lambda _:temp.name
sys.modules["xbmcvfs"]=xbmcvfs
sys.path.insert(0,str(ROOT/"bridge"))
sys.path.insert(0,str(ROOT/"build"))
from real_home_pages import create_home,create_variables,check_home,PAGES,SLOTS,IDS
import home_config
import custom_collections
import default as bridge

class HomeLayoutTests(unittest.TestCase):
    def test_four_hubs_have_actual_configured_plugin_rows(self):
        data=create_home()
        self.assertTrue(check_home(data))
        root=ET.fromstring(data)
        paths=[n.text for n in root.iter("content") if n.text and n.text.startswith("plugin://")]
        self.assertEqual(len(paths),48)
        self.assertEqual(len(IDS),48)
        for page in ("watch","movies","tv","collections"):
            self.assertEqual(sum(("page="+page+"&slot=") in x for x in paths),12)
        self.assertNotIn(b"DEX  GLASS",data)
        self.assertIn(b"addons://sources/video/",data)
        self.assertNotIn(b"plugin://plugin.video.dexhub/?action=home_search",data)
        self.assertIn(b"dexglass/nav-fine-focus.png",data)
        self.assertNotIn(b"dexglass/nav-lens.png",data)
        self.assertIn(b"font20_title",data)
        self.assertIn(b"Window(Home).Property(dg.hero.clearlogo)",data)

    def test_parent_tv_logo_fallback_and_hero(self):
        variables=create_variables()
        self.assertIn(b"Art(tvshow.clearlogo)",variables)
        self.assertIn(b"Art(clearlogo)",variables)
        self.assertIn(b"Window(Home).Property(dg.focus)",variables)
        self.assertIn(b"DG_Fanart",variables)

    def test_settings_are_not_pyrus(self):
        from dexglass_settings import create_settings
        data=create_settings()
        self.assertIn(b"Customise All Hub Rows",data)
        self.assertIn(b"Reset One Hub to Defaults",data)
        self.assertIn(b"Dex Glass",data)
        self.assertNotIn(b"Customize Watch Now",data)

class ConfigTests(unittest.TestCase):
    def setUp(self):
        path=pathlib.Path(home_config.config_path())
        if path.exists():
            path.unlink()
        legacy=path.parent/"collections.json"
        if legacy.exists():
            legacy.unlink()

    def test_defaults_preserve_requested_watch_now_rows(self):
        rows=home_config.load()
        self.assertEqual(len(rows["watch"]),7)
        self.assertEqual([home_config.name_of(i) for i in rows["watch"]],[
            "Continue Watching Movies","Recently Watched Movies",
            "Continue Watching Episodes","Next Episodes",
            "Recently Watched Series","Recommended for You","Dex Collections"])
        self.assertEqual(set(rows),set(PAGES))
        self.assertTrue(rows["movies"] and rows["tv"] and rows["collections"])

    def test_reorder_and_page_assignment_sticks(self):
        rows=home_config.load()
        rows["movies"].insert(0,{"kind":"catalog","url":
            "plugin://plugin.video.dexhub/?action=collection_nuvio_source_open&set_id=builtin-kaptain",
            "title":"The Headliner"})
        moved=rows["movies"].pop(0)
        rows["tv"].append(moved)
        home_config.save(rows)
        restored=home_config.load()
        self.assertEqual(restored["tv"][-1]["title"],"The Headliner")
        self.assertNotIn("The Headliner",[home_config.name_of(i) for i in restored["movies"]])

    def test_migrates_existing_v05_collections(self):
        p=pathlib.Path(home_config.config_path()).parent/"collections.json"
        p.write_text(json.dumps({"slots":[{"title":"Old choice",
            "url":"plugin://plugin.video.dexhub/?action=collection_nuvio_source_open&folder_id=abc"}]}),
            encoding="utf-8")
        rows=home_config.load()
        self.assertEqual(rows["watch"][-1]["title"],"Old choice")

    def test_rejects_external_catalogue_url(self):
        self.assertIsNone(home_config.safe_row({"kind":"catalog","title":"bad",
                                                 "url":"https://example.com/steal"}))
        self.assertIsNone(home_config.row_at("other",1))
        self.assertIsNone(home_config.row_at("watch",999))

class BridgeTests(unittest.TestCase):
    def test_continue_classification(self):
        self.assertEqual(bridge.classify({"file":"plugin://plugin.video.dexhub/?action=item_open&media_type=movie"}),"movie")
        self.assertEqual(bridge.classify({"showtitle":"Dune: Prophecy","episode":2}),"series")
        self.assertEqual(bridge.classify({"title":"Unknown Title"}),"unknown")

    def test_search_uses_native_bridge(self):
        from search import open_search
        self.assertTrue(callable(open_search))
        self.assertIn("skin_search",(ROOT/"bridge"/"search.py").read_text())

if __name__=="__main__":
    unittest.main()
