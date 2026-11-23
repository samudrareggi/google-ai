"""Offline tests for the Textual frontend and its safe execution boundary."""
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from tui_core import (
    command_for_step, mask_email, needs_setup, outcome_for_stage,
    read_fresh_report, validate_step,
)


class CoreTests(unittest.TestCase):
    def test_setup_only_when_pinned_frida_is_missing(self):
        with patch("tui_core.importlib.metadata.version", return_value="16.5.9"):
            self.assertFalse(needs_setup())
        with patch("tui_core.importlib.metadata.version", return_value="16.4.0"):
            self.assertTrue(needs_setup())
        from importlib.metadata import PackageNotFoundError
        with patch("tui_core.importlib.metadata.version", side_effect=PackageNotFoundError):
            self.assertTrue(needs_setup())

    def test_step_range(self):
        for step in range(6):
            self.assertEqual(validate_step(step), step)
        for value in (-1, 6, "2", True):
            with self.assertRaises(ValueError):
                validate_step(value)

    def test_reuses_single_step_powershell_wrapper(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "run-all.ps1").write_text("# test")
            command = command_for_step(3, p, shell="powershell.exe")
            self.assertEqual(command[-4:], ["-File", str(p / "run-all.ps1"), "-Step", "3"])
            self.assertNotIn("-AllStages", command)
            self.assertNotIn("-Force", command)

    def test_no_shell_or_script_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                command_for_step(1, Path(folder), shell="pwsh")

    def test_stale_reports_cannot_confirm_old_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "report"
            p.mkdir()
            f = p / "test.json"
            f.write_text(json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            now = time.time()
            import os
            os.utime(f, (now - 600, now - 600))
            self.assertIsNone(read_fresh_report(p, 3, now, expected_account="alice@example.com"))
            result = outcome_for_stage(3, 0, None)
            self.assertFalse(result.can_review)

    def test_recent_previous_report_cannot_authorize_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            report = p / "account.json"
            report.write_text(json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            started_at = time.time()
            # A completed run 0.5 seconds earlier must not be treated as
            # belonging to a new request just because file mtime is recent.
            import os
            os.utime(report, (started_at - 0.5, started_at - 0.5))
            self.assertIsNone(read_fresh_report(p, 3, started_at, expected_account="alice@example.com"))

    def test_conflicting_account_reports_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            started_at = time.time() - 10
            (p / "account-a.json").write_text(
                json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            (p / "account-b.json").write_text(
                json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            self.assertIsNone(read_fresh_report(
                p, 3, started_at, expected_account="alice@example.com"))
            self.assertFalse(outcome_for_stage(3, 0, None).can_review)

    def test_one_fresh_checkout_report_can_be_reviewed(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            started_at = time.time() - 10
            (p / "account.json").write_text(
                json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            report = read_fresh_report(p, 3, started_at, expected_account="alice@example.com")
            self.assertIsNotNone(report)
            self.assertTrue(outcome_for_stage(3, 0, report).can_review)

    def test_foreign_checkout_report_is_never_eligible_for_review(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "account-foreign.json").write_text(json.dumps({
                "email": "other@example.com", "status": "checkout_requested",
            }))
            started_at = time.time() - 10
            self.assertIsNone(read_fresh_report(
                p, 3, started_at, expected_account="alice@example.com"))
            self.assertIsNone(read_fresh_report(p, 3, started_at))
            # The account matches, but the report belongs to another person.
            self.assertIsNotNone(read_fresh_report(
                p, 3, started_at, expected_account="other@example.com"))

    def test_step_one_remains_account_independent(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "current.json").write_text(json.dumps({
                "email": "current@device", "status": "listed", "offers": [],
            }))
            self.assertIsNotNone(read_fresh_report(p, 1, time.time() - 10))

    def test_security_block_and_duplicate_cannot_continue(self):
        for reason in ("payment_security_blocked", "already_subscribed",
                       "trial_duration_unverified"):
            result = outcome_for_stage(3, 0, {
                "status": "checkout_not_confirmed", "sheet": {"reason": reason}
            })
            self.assertFalse(result.can_review)

    def test_requested_is_not_claimed_active(self):
        result = outcome_for_stage(3, 0, {"status": "checkout_requested"})
        self.assertTrue(result.can_review)
        self.assertNotIn("activated", result.title.lower())
        self.assertIn("Check Google Play", result.instruction)

    def test_slider_checkout_cannot_authorize_next_stage(self):
        report = {"status": "checkout_not_confirmed",
                  "sheet": {"reason": "manual_subscribe_required", "price": "0"}}
        outcome = outcome_for_stage(2, 0, report)
        self.assertEqual(outcome.code, "manual_subscribe_required")
        self.assertIn("Slide to subscribe", outcome.title)
        self.assertIn("12-month free trial starting today", outcome.instruction)
        self.assertFalse(outcome.can_review)

    def test_exit_error_never_allows_next(self):
        result = outcome_for_stage(3, 1, {"status": "checkout_requested"})
        self.assertFalse(result.can_review)

    def test_account_mask(self):
        self.assertEqual(mask_email("example@gmail.com"), "ex***@gmail.com")
        self.assertEqual(mask_email("invalid"), "Not detected")


class TextualSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def test_step5_links_to_google_one_plans(self):
        from textual.widgets import Link, Select
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as tmp:
            app = GoogleAITUI(repo=Path(tmp))
            async with app.run_test(size=(110, 35)) as pilot:
                await pilot.click("#advanced_toggle")
                link = app.query_one("#step5_plans", Link)
                self.assertFalse(link.display)
                app.query_one("#step", Select).value = 5
                await pilot.pause()
                self.assertTrue(link.display)
                self.assertEqual(link.url, "https://one.google.com/about/google-ai-plans/")
                app.query_one("#mode", Select).value = "all"
                await pilot.pause()
                self.assertFalse(link.display)

    async def test_quick_check_offers_only_12_months_and_requires_approval(self):
        from tui import Approval, GoogleAITUI
        from tui_core import Outcome

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            report = {"status": "listed", "detected_play_account": "test@example.com",
                      "offers": [{"id": "12months-eft", "period": "P1Y", "micros": 0}]}
            with patch.object(app, "run_stage") as launch:
                async with app.run_test(size=(90, 20)) as pilot:
                    await pilot.click("#quickstart")
                    launch.assert_called_once_with(1)
                    app._received("Device emulator-5554")
                    app._received("Account test@example.com")
                    app._finished(1, Outcome("listed", "Offers loaded", ""), report)
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    self.assertEqual(app.screen.query_one("#approve").label.plain,
                                     "Review 12-month checkout")
                    await pilot.click("#approve")
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    launch.assert_called_once_with(1)
                    await pilot.click("#approve")
                    await pilot.pause()
                    launch.assert_called_with(2)
                    self.assertFalse(app.sequence)

    async def test_quick_check_requires_verified_identity_and_exact_offer(self):
        from tui import Approval, GoogleAITUI
        from tui_core import Outcome

        for detected, offer_id, micros in (
            ("another@example.com", "12months-eft", 0),
            ("test@example.com", "other-offer", 0),
            ("test@example.com", "12months-eft", 1),
        ):
            with self.subTest(detected=detected, offer_id=offer_id, micros=micros):
                app = GoogleAITUI(repo=Path.cwd())
                report = {"status": "listed", "detected_play_account": detected,
                          "offers": [{"id": offer_id, "period": "P1Y", "micros": micros}]}
                with patch.object(app, "run_stage") as launch:
                    async with app.run_test(size=(110, 35)) as pilot:
                        await pilot.click("#quickstart")
                        app._received("Device emulator-5554")
                        app._received("Account test@example.com")
                        app._finished(1, Outcome("listed", "Offers loaded", ""), report)
                        await pilot.pause()
                        self.assertNotIsInstance(app.screen, Approval)
                        launch.assert_called_once_with(1)

    async def test_application_branding(self):
        from tui import GoogleAITUI
        self.assertEqual(GoogleAITUI.TITLE, "ePlus AI Toolkit")
        self.assertEqual(GoogleAITUI.SUB_TITLE, "ePlus.DEV")

    async def test_telegram_support_channel_is_clickable(self):
        from textual.widgets import Link, Static
        from tui import GoogleAITUI

        for size in ((110, 35), (90, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.subprocess.Popen") as launch:
                    async with app.run_test(size=size) as pilot:
                        await pilot.pause()
                        channel = app.query_one("#support_link", Link)
                        self.assertEqual(channel.url, "https://t.me/eplus_news")
                        self.assertTrue(channel.display)
                        self.assertGreater(channel.region.width, 8)
                        self.assertIn(
                            "Support:", str(app.query_one("#support_label", Static).render())
                        )
                    launch.assert_not_called()

    async def test_github_credits_are_clickable_links(self):
        from textual.widgets import Link
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(110, 35)):
                    self.assertEqual(
                        app.query_one("#original_author", Link).url,
                        "https://github.com/gylive",
                    )
                    self.assertEqual(
                        app.query_one("#maintainer", Link).url,
                        "https://github.com/hoangsvit",
                    )
                popen.assert_not_called()

    async def test_tui_loads_without_starting_any_checkout(self):
        from textual.widgets import Button, Select, Static
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), selected_step=3)
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(110, 35)) as pilot:
                    self.assertEqual(app.query_one("#step", Select).value, 3)
                    self.assertIn("Ready", str(app.query_one("#state", Static).render()))
                    self.assertTrue(app.query_one("#next", Button).disabled)
                    await pilot.press("d")
                    self.assertTrue(app.debug_visible)
                popen.assert_not_called()

    async def test_first_run_shows_clear_workflow_mode(self):
        from textual.widgets import Button, Select, Static
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(90, 20)) as pilot:
                    self.assertFalse(app.query_one("#workflow_actions").display)
                    self.assertTrue(app.query_one("#quickstart", Button).display)
                    self.assertEqual(app.query_one("#mode", Select).value, "single")
                    self.assertEqual(app.query_one("#step", Select).value, 1)
                    self.assertFalse(app.query_one("#stop", Button).display)
                    self.assertFalse(app.query_one("#next", Button).display)
                    self.assertIn("Run selected step", str(app.query_one("#run", Button).label))
                    app.query_one("#mode", Select).value = "all"
                    # Select.Changed can be queued behind layout work on Windows.
                    # Wait for the event rather than asserting after one idle tick.
                    for _ in range(20):
                        if app.query_one("#step", Select).disabled:
                            break
                        await pilot.pause(0.05)
                    self.assertTrue(app.query_one("#step", Select).disabled)
                    self.assertIn("Run all", str(app.query_one("#run", Button).label))
                popen.assert_not_called()

    async def test_run_controls_use_wide_content_not_sidebar(self):
        from textual.widgets import Button, Select
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(110, 35)) as pilot:
                    await pilot.pause()
                    app.advanced_pressed()
                    await pilot.pause()
                    sidebar = app.query_one("#controls").region
                    for selector in ("#mode", "#step", "#run"):
                        widget = app.query_one(selector)
                        self.assertGreaterEqual(widget.region.x, sidebar.right)
                        self.assertGreater(widget.region.width, 15)
                    self.assertTrue(app.query_one("#run", Button).display)
                    self.assertTrue(app.query_one("#quickstart", Button).display)
                    self.assertEqual(app.query_one("#mode", Select).value, "single")
                popen.assert_not_called()

    async def test_compact_run_controls_remain_visible(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)) as pilot:
                await pilot.pause()
                self.assertTrue(app.query_one("#quickstart").display)
                self.assertFalse(app.query_one("#workflow_actions").display)
                self.assertGreater(app.query_one("#quickstart").region.width, 15)
                self.assertGreater(app.query_one("#status_panel").region.height, 3)

    async def test_all_and_from_modes_route_to_expected_step(self):
        from textual.widgets import Select
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "_confirm_stage") as confirm:
                async with app.run_test(size=(110, 35)) as pilot:
                    app.query_one("#mode", Select).value = "all"
                    await pilot.pause()
                    app.selected_pressed()
                    confirm.assert_called_with(2, True)
                    app.query_one("#mode", Select).value = "from"
                    app.query_one("#step", Select).value = 4
                    await pilot.pause()
                    app.selected_pressed()
                    confirm.assert_called_with(4, True)
                    app.query_one("#mode", Select).value = "single"
                    await pilot.pause()
                    app.selected_pressed()
                    confirm.assert_called_with(4, False)

    async def test_new_run_clears_stale_debug_and_device_account_cards(self):
        from textual.widgets import Button, RichLog, Static
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(110, 35)) as pilot:
                    app._received("Account alice@example.com")
                    app._received("Device emulator-5554")
                    app.action_toggle_debug()
                    await pilot.pause()
                    self.assertEqual(len(app.query_one("#debug_log", RichLog).lines), 2)
                    app._start(1, False)
                    await pilot.pause()
                    self.assertFalse(app._last_output)
                    self.assertFalse(app._run_output)
                    self.assertEqual(len(app.query_one("#debug_log", RichLog).lines), 0)
                    self.assertIn("Not checked", str(app.query_one("#account", Static).render()))
                    self.assertIn("Auto-detect", str(app.query_one("#device", Static).render()))
                    self.assertFalse(app.query_one("#manual", Button).display)

    async def test_debug_reopen_includes_hidden_lines_without_duplicates(self):
        from textual.widgets import RichLog
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._received("ADB first line")
                app.action_toggle_debug()
                await pilot.pause()
                self.assertEqual(len(app.query_one("#debug_log", RichLog).lines), 1)
                app.action_toggle_debug()  # Hide technical details
                app._received("ADB second line")
                app.action_toggle_debug()  # Reopen with the full current-run buffer
                await pilot.pause()
                self.assertEqual(len(app.query_one("#debug_log", RichLog).lines), 2)

    async def test_verified_account_captured_only_from_structured_status(self):
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(110, 35)):
                    app._received("Message about Account other@example.com")
                    self.assertIsNone(app._verified_account)
                    app._received("  Account      Alice@Example.com")
                    self.assertEqual(app._verified_account, "alice@example.com")
                    app._start(3, True)
                    self.assertIsNone(app._verified_account)

    async def test_busy_state_locks_run_controls_but_keeps_help_available(self):
        from textual.widgets import Button, Select
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(110, 35)) as pilot:
                    app._start(1, False)
                    self.assertTrue(app.query_one("#run", Button).disabled)
                    self.assertTrue(app.query_one("#mode", Select).disabled)
                    self.assertTrue(app.query_one("#step", Select).disabled)
                    self.assertTrue(app.query_one("#quickstart", Button).disabled)
                    self.assertFalse(app.query_one("#nav_help", Button).disabled)
                    self.assertFalse(app.query_one("#debug", Button).disabled)
                    self.assertTrue(app.query_one("#stop", Button).display)

    async def test_stop_is_real_only_for_read_only_checks(self):
        from tui import GoogleAITUI
        from textual.widgets import Button
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "terminate_readonly_child") as stop:
                async with app.run_test(size=(110, 35)):
                    app.busy = True
                    app.current_step = 1
                    app.stop_pressed()
                    self.assertTrue(app._cancel_requested)
                    stop.assert_called_once()
                    app._cancel_requested = False
                    app.current_step = 3
                    app.stop_pressed()
                    self.assertTrue(app._stop_after_step)
                    self.assertFalse(app._cancel_requested)
                    self.assertTrue(app.query_one("#stop", Button).disabled)

    async def test_quit_during_checkout_queues_exit_without_killing_process(self):
        from tui import GoogleAITUI
        from textual.widgets import Button
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "terminate_readonly_child") as stop:
                async with app.run_test(size=(110, 35)):
                    app.busy = True
                    app.current_step = 3
                    app.action_quit_safely()
                    self.assertTrue(app._exit_after_step)
                    self.assertTrue(app._stop_after_step)
                    self.assertFalse(app._cancel_requested)
                    self.assertTrue(app.query_one("#exit", Button).disabled)
                    stop.assert_not_called()

    async def test_quit_during_readonly_requests_stop(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "terminate_readonly_child") as stop:
                async with app.run_test(size=(110, 35)):
                    app.busy = True
                    app.current_step = 0
                    app.action_quit_safely()
                    self.assertTrue(app._exit_after_step)
                    self.assertTrue(app._cancel_requested)
                    stop.assert_called_once()

    async def test_quick_check_starts_readonly_step_without_approval(self):
        from textual.widgets import Button
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "_confirm_stage") as confirm:
                async with app.run_test(size=(110, 35)) as pilot:
                    await pilot.click("#quickstart")
                    await pilot.pause()
                    confirm.assert_called_once_with(1, False)
                    self.assertFalse(app.query_one("#workflow_actions").display)
                    self.assertTrue(app.query_one("#status_panel").display)

    async def test_advanced_controls_are_explicitly_opt_in(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                self.assertFalse(app.query_one("#workflow_actions").display)
                await pilot.click("#advanced_toggle")
                await pilot.pause()
                self.assertTrue(app.query_one("#workflow_actions").display)
                app.advanced_pressed()
                self.assertFalse(app.query_one("#workflow_actions").display)

    async def test_reported_payment_notice_is_visible_without_checkout(self):
        from textual.widgets import Static
        from tui import GoogleAITUI

        for size in ((110, 35), (90, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.subprocess.Popen") as launch:
                    async with app.run_test(size=size) as pilot:
                        await pilot.pause()
                        notice = app.query_one("#payment_notice", Static)
                        compact = app.query_one("#payment_notice_compact", Static)
                        if size[1] < 27:
                            self.assertFalse(notice.display)
                            self.assertTrue(compact.display)
                            wording = str(compact.render())
                            self.assertIn("3 separate US$1 checks", wording)
                            self.assertIn("not one US$3", wording)
                            self.assertIn("24 months not guaranteed", wording)
                            self.assertGreater(app.query_one("#status_panel").region.height, 3)
                        else:
                            self.assertTrue(notice.display)
                            self.assertFalse(compact.display)
                            wording = str(notice.render())
                            self.assertIn("Step 2 (12 months)", wording)
                            self.assertIn("Step 3 (6)", wording)
                            self.assertIn("Step 4 (6)", wording)
                            self.assertIn("at least US$3 available", wording)
                            self.assertIn("3 separate US$1 card checks", wording)
                            self.assertIn("not one US$3 payment", wording)
                            self.assertIn("temporary holds", wording)
                            self.assertIn("24 months is not guaranteed", wording)
                        self.assertTrue(app.query_one("#quickstart").display)
                    launch.assert_not_called()

    async def test_checkout_confirmations_explain_each_one_dollar_event(self):
        from textual.widgets import Static
        from tui import Approval, GoogleAITUI

        for step, expected in ((2, "1"), (3, "2"), (4, "3"), (5, None)):
            with self.subTest(step=step), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.subprocess.Popen") as launch:
                    async with app.run_test(size=(110, 35)) as pilot:
                        app._confirm_stage(step, False)
                        await pilot.pause()
                        self.assertIsInstance(app.screen, Approval)
                        wording = str(app.screen.query_one("#approval_message", Static).render())
                        if expected:
                            self.assertIn("Card check " + expected + " of 3", wording)
                            self.assertIn("NOT one US$3 payment", wording)
                            self.assertIn("temporary hold", wording)
                            self.assertIn("not guaranteed", wording)
                        else:
                            self.assertIn("Step 5 is optional", wording)
                            self.assertIn("outside the 3 x US$1", wording)
                        await pilot.click("#cancel")
                        await pilot.pause()
                    launch.assert_not_called()

    async def test_step_click_requires_approval_before_subprocess(self):
        from tui import GoogleAITUI, Approval

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), selected_step=3)
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(110, 35)) as pilot:
                    await pilot.click("#advanced_toggle")
                    await pilot.pause()
                    await pilot.click("#run")
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    await pilot.click("#cancel")
                    await pilot.pause()
                    popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
