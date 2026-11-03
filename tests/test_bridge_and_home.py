"""Pure-Python contract tests. Kodi itself is only tested on device."""
import importlib.util
import pathlib
import sys
import types
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
xbmc = types.ModuleType("xbmc")
xbmc.LOGINFO = 1
xbmc.LOGWARNING = 2
xbmc.LOGERROR = 3
xbmc.log = lambda *a, **k: None
xbmc.executeJSONRPC = lambda _: '{"result":{"files":[]}}'
sys.modules["xbmc"] = xbmc
sys.modules["xbmcgui"] = types.ModuleType("xbmcgui")
sys.modules["xbmcplugin"] = types.ModuleType("xbmcplugin")

spec = importlib.util.spec_from_file_location("dexglass_bridge", ROOT / "bridge" / "default.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
sys.path.insert(0, str(ROOT / "build"))
from real_home import create_home, check_home

class BridgeClassificationTests(unittest.TestCase):
    def test_url_media_overrides_missing_jsonrpc_type(self):
        self.assertEqual(bridge.classify({"file":"plugin://plugin.video.dexhub/?action=item_open&media_type=movie"}),"movie")
        self.assertEqual(bridge.classify({"file":"plugin://plugin.video.dexhub/?action=item_open&media_type=series"}),"series")

    def test_series_metadata(self):
        self.assertEqual(bridge.classify({"showtitle":"Home Economics", "title":"Pilot"}),"series")
        self.assertEqual(bridge.classify({"title":"A Show S02E07"}),"series")
        self.assertEqual(bridge.classify({"season":1,"episode":4}),"series")

    def test_movie_not_assumed_from_unknown(self):
        self.assertEqual(bridge.classify({"title":"Unknown Title", "file":"plugin://plugin.video.dexhub/?action=item_open"}),"unknown")
        self.assertEqual(bridge.classify({"type":"movie"}),"movie")

    def test_jsonrpc_empty_video_mode_falls_back(self):
        calls=[]
        old=bridge.rpc
        def fake(directory, media, props):
            calls.append(media)
            return [] if media=="video" else [{"type":"movie","file":"plugin://plugin.video.dexhub/?x=1"}]
        try:
            bridge.rpc=fake
            rows=bridge.read_continue()
        finally:
            bridge.rpc=old
        self.assertEqual(calls,["video","video","files"])
        self.assertEqual(len(rows),1)

class HomeContractTests(unittest.TestCase):
    def test_kodi_home_and_bridge(self):
        data=create_home()
        self.assertTrue(check_home(data))
        root=ET.fromstring(data)
        self.assertEqual(len(list(root.iter("item"))),4)
        feeds=[x.text for x in root.iter("content") if (x.text or "").startswith("plugin://")]
        self.assertEqual(sum("dexglass.bridge" in x for x in feeds),2)
        self.assertEqual(len(feeds),6)
        onclick=[x.text or "" for x in root.iter("onclick")]
        self.assertTrue(any("home_community" in x for x in onclick))
        self.assertTrue(any("ActivateWindow(ShutdownMenu)" in x for x in onclick))
        self.assertEqual(len([x for x in root.iter("texture") if (x.text or "").startswith("dexglass/icon-")]),3)

if __name__ == "__main__":
    unittest.main()
