"""No-device tests for Play Store account and Google One launch diagnostics."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

script = Path(__file__).resolve().parents[1] / "ultra0.py"
spec = importlib.util.spec_from_file_location("ai_diagnostics", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DeviceDiagnosticsTests(unittest.TestCase):
    def test_unknown_account_fails_closed_without_launching(self):
        with patch.object(mod, "current_play_account", return_value=""), \
             patch.object(mod, "launch_app") as launch:
            result = mod.process("example@example.com", add=False, no_switch=True)
            self.assertEqual(result["status"], "account_unverified")
            launch.assert_not_called()

    def test_account_mismatch_is_separate_from_unknown(self):
        with patch.object(mod, "current_play_account", return_value="another@example.com"), \
             patch.object(mod, "launch_app") as launch:
            result = mod.process("example@example.com", add=False, no_switch=True)
            self.assertEqual(result["status"], "wrong_account")
            launch.assert_not_called()

    def test_play_store_comes_to_foreground_before_account_read(self):
        xml = ['<node package="com.google.android.apps.subscriptions.red" />',
               '<node package="com.android.vending" />',
               '<node package="com.android.vending" />']
        profile = [{"desc": "Account and settings", "text": "", "x": 12, "y": 34}]
        email = [{"desc": "example@example.com", "text": "", "x": 12, "y": 34}]
        called = []
        with patch.object(mod, "ui_xml", side_effect=xml), \
             patch.object(mod, "nodes", side_effect=[profile, email]), \
             patch.object(mod, "tap"), patch.object(mod.time, "sleep"), \
             patch.object(mod, "sh", side_effect=lambda *a, **kw: called.append(a) or ""):
            result = mod.current_play_account()
            self.assertEqual(result, "example@example.com")
            self.assertTrue(any("am start -n com.android.vending/" in " ".join(a) for a in called))

    def test_google_one_store_listing_returns_to_active_profile(self):
        listing = '<node package="com.android.vending" />'
        detail = [{"text": "Google One", "desc": ""},
                  {"text": "", "desc": "Navigate up", "x": 10, "y": 20}]
        home = [{"text": "", "desc": "Google Account: selected@example.com"}]
        with patch.object(mod, "ui_xml", return_value=listing), \
             patch.object(mod, "nodes", side_effect=[detail, home]), \
             patch.object(mod.time, "sleep"), patch.object(mod, "tap") as tap:
            self.assertEqual(mod.current_play_account(), "selected@example.com")
        tap.assert_called_once_with(10, 20)

    def test_ui_snapshot_uses_no_persistent_android_file(self):
        with patch.object(mod, "sh", return_value=(
                '<?xml version="1.0"?><hierarchy></hierarchy>'
                'UI hierchary dumped to: /dev/tty')) as adb:
            self.assertEqual(mod.ui_xml(), '<?xml version="1.0"?><hierarchy></hierarchy>')
        adb.assert_called_once_with("exec-out", "uiautomator dump /dev/tty")

    def test_missing_google_one_is_not_launched(self):
        with patch.object(mod, "sh", return_value="") as adb:
            self.assertEqual(mod.launch_app(), 0)
            self.assertEqual(adb.call_count, 1)

    def test_slow_google_one_launch_is_retried(self):
        seen = {"pid": 0}
        def shell(*args, **kwargs):
            cmd = " ".join(args)
            if "pm path" in cmd: return "package:/data/app/base.apk"
            if "pidof" in cmd:
                seen["pid"] += 1
                return "" if seen["pid"] == 1 else "1234"
            return ""
        with patch.object(mod, "sh", side_effect=shell), patch.object(mod.time, "sleep") as pause:
            self.assertEqual(mod.launch_app(), 1234)
            self.assertEqual(pause.call_count, 2)


if __name__ == "__main__":
    unittest.main()
