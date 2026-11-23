import json
import unittest
from threading import Event
from unittest.mock import patch

import mumu_setup


class MuMuSetupTests(unittest.TestCase):
    def test_waits_for_requested_account_on_the_new_instance(self):
        statuses = [
            {"1": {"is_android_started": True}},
            {"0": {"is_android_started": False}, "1": {"is_android_started": True}},
            {"0": {"is_android_started": True}, "1": {"is_android_started": True}},
        ]
        calls = []

        def run(*args):
            calls.append(args)
            if args[1:3] == ("info", "--vmindex"):
                return json.dumps(statuses.pop(0))
            if args[1] == "adb":
                return "connected to 127.0.0.1:16416"
            if args[-1] == "get-state":
                return "device"
            if args[-2:] == ("dumpsys", "account"):
                if sum(call[-2:] == ("dumpsys", "account") for call in calls) == 1:
                    return "Account {name=other@example.com, type=com.google}"
                return "Account {name=requested@example.com, type=com.google}"
            return '{"errcode": 0}'

        with patch.object(mumu_setup, "_run", side_effect=run), \
             patch.object(mumu_setup, "_mumu_cli", return_value="mumu-cli.exe"), \
             patch.object(mumu_setup.shutil, "which", return_value="adb.exe"), \
             patch("mumu_setup.Event.wait", return_value=False):
            result = mumu_setup.prepare("requested@example.com", Event(), lambda message: None)
        self.assertEqual(result, "127.0.0.1:16416")
        self.assertTrue(any("--vmindex" in call and "0" in call and "launch" in call for call in calls))
        self.assertTrue(any("android.intent.action.MAIN" in call and "-s" in call for call in calls))
        self.assertTrue(all("requested@example.com" not in call for call in calls))

    def test_cancelled_before_start_creates_no_instance(self):
        stop = Event()
        stop.set()
        with patch.object(mumu_setup, "_run") as run:
            self.assertIsNone(mumu_setup.prepare("requested@example.com", stop, lambda message: None))
        run.assert_not_called()
