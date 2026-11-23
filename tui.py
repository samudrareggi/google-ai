"""Interactive Textual frontend for ePlus AI Toolkit (Windows + macOS preview).

UI-only orchestration: the original run-all.ps1 and ultra0.py still own all
Android, Frida, Google Play, payment and account validation. The TUI never
declares an activated subscription from launchBillingFlow or a Subscribe tap.
"""
from __future__ import annotations

import argparse
import os
import signal
from collections import deque
from pathlib import Path
import re
import subprocess
import sys
from threading import Event
import time

from rich.markup import escape
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Link, RichLog, Select, Static

from tui_core import STAGES, Outcome, command_for_step, mask_email, \
    needs_setup, offer_explorer_lines, outcome_for_stage, read_fresh_report, \
    report_summary, validate_step
from device_diagnostics import ConnectionDiagnosis, inspect_connection
import mumu_setup


class Approval(ModalScreen[bool]):
    """Clickable approval without long typed phrases."""

    CSS = """
    Approval { align: center middle; background: #070d19 75%; }
    #approval_card {
        width: 66; max-width: 92%; height: auto;
        max-height: 95%; padding: 1 3; background: #15243a; border: round #3d6383;
    }
    #approval_title { text-style: bold; color: #ebf5ff; margin-bottom: 1; }
    #approval_scroll { height: auto; max-height: 1fr; overflow-y: auto; }
    #approval_message { color: #c9d8e8; margin-bottom: 2; }
    #approval_actions { height: 3; min-height: 3; align-horizontal: right; }
    #approval_actions Button { margin-left: 1; }
    """

    def __init__(self, title: str, message: str, *, continue_label: str = "Continue") -> None:
        super().__init__()
        self.title_text, self.message_text = title, message
        self.continue_label = continue_label

    def compose(self) -> ComposeResult:
        with Vertical(id="approval_card"):
            yield Static(self.title_text, id="approval_title")
            with VerticalScroll(id="approval_scroll", can_focus=True):
                yield Static(self.message_text, id="approval_message")
            with Horizontal(id="approval_actions"):
                yield Button("Cancel", id="cancel")
                yield Button(self.continue_label, id="approve", variant="warning")

    @on(Button.Pressed, "#approval_actions Button")
    def approve(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "approve")


class PrepareMuMu(ModalScreen[str | None]):
    CSS = """
    PrepareMuMu { align: center middle; background: #070d19 75%; }
    #mumu_card { width: 66; max-width: 94%; height: auto; padding: 1 2;
                 background: #15243a; border: round #3d6383; }
    #mumu_message { height: auto; min-height: 2; margin: 1 0; }
    #mumu_controls { height: 3; align-horizontal: right; }
    #mumu_controls Button { margin-left: 1; }
    """

    def __init__(self) -> None:
        super().__init__()
        self.stop = Event()
        self.preparing = False

    def compose(self) -> ComposeResult:
        with Vertical(id="mumu_card"):
            yield Static("Prepare a new MuMu instance", classes="section")
            yield Input(placeholder="Google Play email", id="mumu_email")
            yield Static("Sign in and complete any verification in MuMu.", id="mumu_message")
            with Horizontal(id="mumu_controls"):
                yield Button("Close", id="mumu_close")
                yield Button("Create instance", id="mumu_create", variant="primary")

    @on(Button.Pressed, "#mumu_create")
    def create_instance(self) -> None:
        field = self.query_one("#mumu_email", Input)
        email = field.value.strip()
        if not mumu_setup.EMAIL.fullmatch(email):
            self.query_one("#mumu_message", Static).update("Enter the email you will use in Google Play.")
            return
        field.value = ""
        field.disabled = True
        self.query_one("#mumu_create", Button).disabled = True
        self.query_one("#mumu_close", Button).label = "Stop waiting"
        self.preparing = True
        self.prepare_instance(email)

    @on(Button.Pressed, "#mumu_close")
    def close_setup(self) -> None:
        self.stop.set()
        if self.preparing:
            close = self.query_one("#mumu_close", Button)
            close.label = "Stopping..."
            close.disabled = True
        else:
            self.dismiss(None)

    def on_unmount(self) -> None:
        self.stop.set()

    def show_progress(self, message: str) -> None:
        if not self.stop.is_set():
            self.query_one("#mumu_message", Static).update(message)

    @work(thread=True, exclusive=True)
    def prepare_instance(self, email: str) -> None:
        try:
            serial = mumu_setup.prepare(
                email, self.stop,
                lambda message: self.app.call_from_thread(self.show_progress, message),
            )
            self.app.call_from_thread(self.finish_preparation, serial)
        except (RuntimeError, ValueError) as error:
            self.app.call_from_thread(self.finish_preparation, None, str(error))

    def finish_preparation(self, serial: str | None, error: str = "") -> None:
        self.preparing = False
        if self.stop.is_set():
            self.dismiss(None)
        elif error:
            self.show_progress(error)
            self.query_one("#mumu_close", Button).label = "Close"
        else:
            self.dismiss(serial)


def is_macos_platform() -> bool:
    return sys.platform == "darwin"


class GoogleAITUI(App[None]):
    TITLE = "ePlus AI Toolkit"
    SUB_TITLE = "ePlus.DEV"
    BINDINGS = [
        ("d", "toggle_debug", "Debug"),
        ("r", "run_selected", "Run step"),
        ("q", "quit_safely", "Quit"),
    ]
    CSS = """
    Screen { background: #081424; color: #e8f2fc; }
    Header, Footer { background: #11243e; color: #d7e8fa; }
    #screen { height: 1fr; min-height: 0; padding: 0 1; }
    #brand {
        height: 3; background: #122741; border: round #28628d;
        color: #f0f8ff; padding: 0 2; align: left middle;
    }
    #support_label { width: auto; height: 1; color: #c8dff1; }
    #support_link {
        width: auto; height: 1; color: #75d8ff;
        text-style: underline bold;
    }
    #support_link:hover { color: #e6f8ff; }
    #credit { height: 1; color: #87b8d4; }
    #credit Static { width: auto; height: 1; color: #87b8d4; }
    #credit Link { width: auto; height: 1; color: #75d8ff; text-style: underline; }
    #credit Link:hover { color: #e6f8ff; }
    #details { height: 3; margin-bottom: 1; }
    #device, #account {
        width: 1fr; height: 3; background: #12263d;
        border: round #295a7e; padding: 0 1;
    }
    #account { margin-left: 1; }
    #content { height: 1fr; min-height: 0; }
    #controls {
        width: 26; min-width: 26; min-height: 0;
        border: round #2b5577; background: #101f35;
        padding: 0 1; overflow-y: auto; scrollbar-size: 1 1;
    }
    #results { width: 1fr; min-width: 26; min-height: 0; margin-left: 1; overflow-y: auto; scrollbar-size: 1 1; }
    .section { color: #6cdbf8; text-style: bold; margin: 0 0 1 0; }
    #workflow { height: auto; margin-bottom: 1; }
    .workflow-step { color: #b4cbe0; height: 1; }
    #nav_help, #diagnose, #debug, #exit {
        width: 100%; height: 3; margin: 0;
    }
    #nav_home, #nav_quick, #advanced, #sequence, #run_all { display: none; }
    #start_options { height: 3; }
    #start_options > #prepare_mumu, #start_options > #advanced_toggle { width: 1fr; min-width: 0; }
    #quickstart { display: block; width: 100%; height: 3; margin: 0 0 1 0; }
    #advanced_toggle { width: 100%; height: 3; margin: 0; }
    #workflow_actions { display: none; height: auto; margin-top: 1; border-top: solid #285d83; padding-top: 1; }
    #status_panel { min-height: 8; overflow-y: auto; scrollbar-size: 1 1; }

    #welcome_panel {
        height: auto; border: round #2b97bc;
        background: #112b49; padding: 1 2; margin-bottom: 1;
    }
    #welcome { color: #91e3ff; text-style: bold; height: 1; }
    #quick_hint { color: #afcce3; height: auto; margin: 0 0 1 0; }
    #payment_notice {
        height: auto; margin: 1 0 0 0; padding: 0 1;
        color: #e2ecf4; background: #233248; border-left: solid #d6a34f;
    }
    #payment_notice_compact { display: none; }
    #read_only { color: #81c6df; height: auto; margin-top: 1; }
    #workflow_actions { height: auto; }
    #form_row { height: auto; }
    .field { width: 1fr; min-width: 12; height: auto; }
    #step_field { margin-left: 1; }
    #mode_label, #advanced_label {
        color: #8edff1; text-style: bold; height: 1; margin: 0 0 1 0;
    }
    #mode, #step { width: 100%; margin: 0; }
    #run_row { height: auto; margin-top: 1; }
    #run { width: 25; min-width: 17; height: 3; margin: 0; }
    #mode_hint {
        width: 1fr; height: auto; color: #a5c8df;
        padding: 0 1;
    }
    #step5_plans { display: none; height: 1; margin-top: 1; }
    #next, #stop { display: none; width: 100%; height: 3; margin-top: 1; }
    #status_panel {
        height: 1fr; min-height: 0; border: round #285a80;
        background: #101f35; padding: 0 1;
    }
    #state { color: #f2f9ff; text-style: bold; margin: 1 0 0 0; }
    #message { color: #c5ddee; }
    #step_result { color: #8cdfbb; height: auto; }
    #offers_title { display: none; color: #8edff1; text-style: bold; margin-top: 1; }
    #offer_view {
        display: none; height: 8; min-height: 4; margin-top: 1;
        border: round #285a80; background: #081a2d;
    }
    #elapsed, #activity { color: #95c4dd; }
    #debug_log {
        display: none; height: 1fr; min-height: 3;
        border: round #294b67; background: #071528;
    }
    #manual { display: none; width: 100%; height: 3; }
    #hint { color: #83b1cf; height: auto; margin-top: 1; }
    Screen.compact #brand { height: 1; border: none; padding: 0 1; }
    Screen.compact #credit, Screen.compact #hint { display: none; }
    Screen.compact #details { height: 1; }
    Screen.compact #device, Screen.compact #account { height: 1; border: none; }
    Screen.compact #welcome_panel { padding: 0 1; }
    Screen.compact #quick_hint, Screen.compact #read_only { display: none; }
    Screen.compact #welcome { display: none; }
    Screen.compact #payment_notice { display: none; }
    Screen.compact #payment_notice_compact {
        display: block; height: 1; margin: 0;
        color: #ffe0a0; background: #283047;
    }
    Screen.compact #welcome_panel { padding: 0 1; }
    Screen.compact #quickstart, Screen.compact #advanced_toggle { height: 3; }
    Screen.narrow #form_row { layout: vertical; }
    Screen.narrow #step_field { margin: 1 0 0 0; }
    Screen.narrow #run_row { layout: vertical; }
    Screen.narrow #run { width: 100%; }
    Screen.narrow #mode_hint { padding: 1 0 0 0; }
    Screen.narrow #controls { width: 21; min-width: 21; }
    Screen.tiny #content { layout: vertical; }
    Screen.tiny #controls {
        width: 100%; min-width: 0; height: auto;
        max-height: 11; overflow-y: auto; margin-bottom: 1;
    }
    Screen.tiny #workflow { display: none; }
    Screen.tiny #results { width: 100%; min-width: 0; margin-left: 0; }
    """

    def __init__(self, *, repo: Path, selected_step: int = 1,
                 start_sequence: bool = False, initial_debug: bool = False) -> None:
        super().__init__()
        self.repo = repo.resolve()
        self.initial_step = validate_step(selected_step)
        self.macos_mode = is_macos_platform()
        self.start_sequence = start_sequence
        self.debug_visible = initial_debug
        self.busy = False
        self._diagnosing = False
        self.sequence = False
        self.current_step: int | None = None
        self._child: subprocess.Popen[str] | None = None
        self._last_output: deque[str] = deque(maxlen=350)
        self._run_output: deque[str] = deque(maxlen=35)
        self._stop_after_step = False
        self._cancel_requested = False
        self._exit_after_step = False
        self._last_outcome: Outcome | None = None
        self._verified_account: str | None = None
        self._checked_device: str | None = None
        self._prepared_device: str | None = None
        self.mumu_setup_available = sys.platform == "win32"
        self._quick_check = False
        self._checkout_target: tuple[str, str] | None = None
        self._started_at: float | None = None
        self._last_activity_at: float | None = None
        self.advanced_visible = False
        self._last_mode = "single"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="screen"):
            with Horizontal(id="brand"):
                yield Static("Support: ", id="support_label")
                yield Link("https://t.me/eplus_news", url="https://t.me/eplus_news",
                           tooltip="Telegram support channel", id="support_link")
            with Horizontal(id="credit"):
                yield Static("  Original ")
                yield Link("@gylive", url="https://github.com/gylive",
                           tooltip="Original author on GitHub", id="original_author")
                yield Static("  |  Maintained ")
                yield Link("@hoangsvit", url="https://github.com/hoangsvit",
                           tooltip="Maintainer on GitHub", id="maintainer")
            with Horizontal(id="details"):
                yield Static("ANDROID DEVICE\nMuMu • Auto-detect", id="device")
                yield Static("GOOGLE ACCOUNT\nNot checked", id="account")
            with Horizontal(id="content"):
                with Vertical(id="controls"):
                    yield Static("STEPS", classes="section")
                    with Vertical(id="workflow"):
                        for stage in STAGES:
                            yield Static(f"○  {stage.number}. {stage.label}",
                                         id=f"stage_{stage.number}", classes="workflow-step")
                    yield Button("Help & Guide", id="nav_help")
                    yield Button("Diagnose Android connection", id="diagnose")
                    yield Button("Show technical details", id="debug")
                    yield Button("Exit toolkit", id="exit")
                with Vertical(id="results"):
                    with Vertical(id="welcome_panel"):
                        yield Static("GET STARTED · READ-ONLY CHECK", id="welcome")
                        yield Static("Check MuMu connection and Google AI offers without opening checkout.", id="quick_hint")
                        yield Button("Check Device & Offers", id="quickstart", variant="success")
                        if self.mumu_setup_available:
                            with Horizontal(id="start_options"):
                                yield Button("Prepare MuMu", id="prepare_mumu")
                                yield Button("Advanced: Run by step  +", id="advanced_toggle")
                        else:
                            yield Button("Advanced: Run by step  +", id="advanced_toggle")
                        with Vertical(id="workflow_actions"):
                            with Horizontal(id="form_row"):
                                with Vertical(classes="field", id="mode_field"):
                                    yield Static("Run mode", id="mode_label")
                                    yield Select([
                                        ("One step only", "single"),
                                        ("From selected step", "from"),
                                        ("All: Steps 2–5", "all"),
                                    ], value="single", id="mode", allow_blank=False)
                                with Vertical(classes="field", id="step_field"):
                                    yield Static("Step", id="advanced_label")
                                    yield Select(
                                        [(f"{stage.number}. {stage.label}", stage.number)
                                         for stage in STAGES],
                                        value=self.initial_step, id="step", allow_blank=False)
                            with Horizontal(id="run_row"):
                                yield Button("Run selected step", id="run", variant="primary")
                                yield Static("Runs one step; no next step is automatic.", id="mode_hint")
                            yield Link("Pro 3 months / Ultra on Google One",
                                       url="https://one.google.com/about/google-ai-plans/",
                                       id="step5_plans")
                            yield Button("Run sequence from step", id="sequence")
                            yield Button("Run all", id="run_all")
                            yield Button("Verified in Google Play → Next",
                                         id="next", disabled=True)
                            yield Button("Stop after current step", id="stop", disabled=True)
                            yield Static("Steps 2–5 can open checkout and require confirmation.", id="read_only")
                        yield Static(
                            "24-month example: Step 2 (12 months) + Step 3 (6) + Step 4 (6).\n"
                            "Have at least US$3 available: 3 separate US$1 card checks, "
                            "not one US$3 payment.\n"
                            "These may be temporary holds. Verify each step in Google Play; "
                            "24 months is not guaranteed.",
                            id="payment_notice",
                        )
                        yield Static(
                            "3 separate US$1 checks (not one US$3); 24 months not guaranteed.",
                            id="payment_notice_compact",
                        )
                    with Vertical(id="status_panel"):
                        yield Static("LIVE STATUS", classes="section")
                        yield Static("Ready — no check started", id="state")
                        yield Static("Press Check Device & Offers to begin. Advanced modes are optional.", id="message")
                        yield Static("", id="step_result")
                        yield Static("AVAILABLE OFFERS · FIRST PHASE ONLY", id="offers_title")
                        yield RichLog(id="offer_view", wrap=True, highlight=False, markup=False)
                        yield Static("Elapsed: --", id="elapsed")
                        yield Static("Waiting for your action.", id="activity")
                        yield Button("Completed action on Android", id="manual", disabled=True)
                        yield RichLog(id="debug_log", wrap=True, highlight=False, markup=False)
                        yield Static("Review Google Play pricing and renewal terms "
                                     "before each checkout.", id="hint")
        yield Footer()

    def on_resize(self, event) -> None:
        self.screen.set_class(event.size.height < 27, "compact")
        self.screen.set_class(event.size.width < 90, "narrow")
        self.screen.set_class(event.size.width < 62, "tiny")

    @on(Button.Pressed, "#nav_home")
    def home_pressed(self) -> None:
        if not self.busy:
            self._set_message("Select Check Device & Offers to begin.")

    @on(Button.Pressed, "#nav_quick")
    def quick_pressed(self) -> None:
        self.quickstart_pressed()

    @on(Button.Pressed, "#nav_help")
    def help_pressed(self) -> None:
        self._set_message("Start with a read-only offer check. Steps 2-5 can request "
                          "real payments; verify the account, terms and renewal date.")

    @on(Button.Pressed, "#diagnose")
    def diagnose_pressed(self) -> None:
        if self.busy or self._diagnosing:
            return
        self._diagnosing = True
        self.query_one("#diagnose", Button).disabled = True
        self.query_one("#quickstart", Button).disabled = True
        if self.mumu_setup_available:
            self.query_one("#prepare_mumu", Button).disabled = True
        self.query_one("#run", Button).disabled = True
        self._set_status("Inspecting Android connection...")
        self._set_message(
            "Checking local ADB, Android transport and Google One. No checkout, "
            "installation or emulator reset; adb devices may start the local ADB server."
        )
        self.inspect_android_connection()

    @work(thread=True, exclusive=True, group="android-connection")
    def inspect_android_connection(self) -> None:
        try:
            diagnosis = inspect_connection()
        except Exception:
            diagnosis = ConnectionDiagnosis(
                "error", "Connection check could not complete", (),
                "Check the ADB installation and try again. No checkout was started.",
            )
        self.call_from_thread(self._diagnosis_done, diagnosis)

    def _diagnosis_done(self, diagnosis: ConnectionDiagnosis) -> None:
        self._diagnosing = False
        self.query_one("#diagnose", Button).disabled = False
        self.query_one("#quickstart", Button).disabled = False
        if self.mumu_setup_available:
            self.query_one("#prepare_mumu", Button).disabled = False
        self.query_one("#run", Button).disabled = False
        self._set_status(diagnosis.headline)
        self._set_message(diagnosis.guidance)
        self.query_one("#step_result", Static).update("\n".join(diagnosis.details))
        self.query_one("#offers_title", Static).display = False
        self.query_one("#offer_view", RichLog).display = False

    def on_mount(self) -> None:
        self.set_interval(1, self._refresh_elapsed)
        if self.macos_mode:
            self.query_one("#device", Static).update("ANDROID DEVICE\nADB • Auto-detect")
            self.query_one("#quick_hint", Static).update(
                "Check Android and Google AI offers before any subscription step."
            )
            self.query_one("#read_only", Static).update(
                "Steps 2–5 can charge money. Confirm account, future price and renewal date."
            )
        self.query_one("#debug_log", RichLog).display = self.debug_visible
        self.query_one("#debug", Button).label = "Hide technical details" if self.debug_visible else "Show technical details"
        if self.start_sequence:
            self.query_one("#mode", Select).value = "from"
        self._update_run_mode()

    @on(Button.Pressed, "#advanced_toggle")
    def advanced_pressed(self) -> None:
        self.advanced_visible = not self.advanced_visible
        panel = self.query_one("#workflow_actions", Vertical)
        panel.display = self.advanced_visible
        self.query_one("#advanced_toggle", Button).label = (
            "Hide advanced steps  −" if self.advanced_visible
            else "Advanced: Run by step  +"
        )

    @on(Select.Changed, "#mode")
    def mode_changed(self, event: Select.Changed) -> None:
        self._update_run_mode()

    @on(Select.Changed, "#step")
    def step_changed(self, event: Select.Changed) -> None:
        self._update_run_mode()

    def _update_run_mode(self) -> None:
        if self.busy:
            return
        mode = self.query_one("#mode", Select).value
        step = self.query_one("#step", Select).value
        if mode == "all":
            self.query_one("#step", Select).disabled = True
            self.query_one("#run", Button).label = "Run all: Steps 2-5"
            hint = "Starts Step 2; requires review before every later checkout."
        elif mode == "from":
            self.query_one("#step", Select).disabled = False
            self.query_one("#run", Button).label = "Run from selected step"
            hint = ("Choose Step 2-5. Each later checkout requires verification."
                    if step in (0, 1) else "Continue from this step; verify each checkout before Next.")
        else:
            self.query_one("#step", Select).disabled = False
            self.query_one("#run", Button).label = "Run selected step"
            hint = "Run only this step. Steps 2-5 can request real payment."
        show_step5_plans = step == 5 and mode != "all"
        self.query_one("#step5_plans", Link).display = show_step5_plans
        if show_step5_plans:
            hint += " Check Pro 3 months and Ultra availability in Google One."
        self.query_one("#mode_hint", Static).update(hint)

    def action_toggle_advanced(self) -> None:
        self.advanced_pressed()

    def _refresh_elapsed(self) -> None:
        if not self.busy or self._started_at is None:
            return
        elapsed = int(time.monotonic() - self._started_at)
        self.query_one("#elapsed", Static).update(f"Elapsed: {elapsed // 60:02d}:{elapsed % 60:02d}")
        if self._last_activity_at is not None:
            idle = int(time.monotonic() - self._last_activity_at)
            if idle >= 30:
                self.query_one("#activity", Static).update(
                    f"No new output for {idle}s. Check MuMu or technical details."
                )

    def _set_workflow(self, step: int, state: str) -> None:
        marker = {"running": "●", "done": "✓", "review": "!"}.get(state, "○")
        self.query_one(f"#stage_{step}", Static).update(
            f"{marker}  {step}. {STAGES[step].label}"
        )

    def _set_message(self, value: str) -> None:
        self.query_one("#message", Static).update(value)

    def _set_status(self, value: str) -> None:
        self.query_one("#state", Static).update(value)

    def _selected(self) -> int:
        return validate_step(int(self.query_one("#step", Select).value))

    def _confirm_stage(self, step: int, sequence: bool,
                       previous_verified: bool = False, *, target: tuple[str, str] | None = None) -> None:
        if self.busy or self._diagnosing:
            return
        if step == 2:
            title = "Start initial 12-month checkout?"
            message = ("Confirm this Google Play account has NO active Google One subscription. "
                       "This step can automatically press Subscribe and create real charges.")
        elif step >= 3:
            title = f"Start Step {step} (+6 months)?"
            message = ("Google AI Pro must already be active. Verify the previous "
                       "subscription and renewal date in Google Play. Google may reject "
                       "additional free offers or apply paid renewal terms.")
        else:
            self._start(step, sequence)
            return
        if target:
            account, _ = target
            message += (f" Expected account: {escape(mask_email(account))}. "
                        "If asked, enter your payment method in Google Play.")
        if step in (2, 3, 4):
            number = step - 1
            message += (
                f"\n\nCard check {number} of 3 in the reported example: "
                "about US$1 each, NOT one US$3 payment. "
                "It may be a temporary hold, not a final charge. "
                "Verify the amount and renewal date in Google Play. "
                "24 months is not guaranteed."
            )
        elif step == 5:
            message += (
                "\n\nStep 5 is optional, outside the 3 x US$1 / 24-month example. "
                "Check the actual amount and renewal terms in Google Play."
            )
        if previous_verified:
            message = ("Confirm the previous stage ACTUALLY changed the Google Play "
                       "subscription/renewal date. " + message)
        self.push_screen(Approval(title, message),
                         lambda approved: self._approved_stage(step, sequence, target) if approved else None)

    def _approved_stage(self, step: int, sequence: bool, target: tuple[str, str] | None) -> None:
        if self.busy or self._diagnosing:
            return
        self._checkout_target = target
        self._start(step, sequence)

    @on(Button.Pressed, "#prepare_mumu")
    def prepare_mumu_pressed(self) -> None:
        if not self.mumu_setup_available or self.busy or self._diagnosing or isinstance(self.screen, ModalScreen):
            return
        self.push_screen(PrepareMuMu(), self._mumu_prepared)

    def _mumu_prepared(self, serial: str | None) -> None:
        if not serial:
            return
        self._prepared_device = serial
        self.sequence = False
        self._last_outcome = None
        next_step = self.query_one("#next", Button)
        next_step.disabled = True
        next_step.display = False
        self._set_status("MuMu ready")
        self._set_message("The requested Android account was found. Select Check Device & Offers to verify Google Play.")

    @on(Button.Pressed, "#quickstart")
    def quickstart_pressed(self) -> None:
        if self.busy or self._diagnosing or isinstance(self.screen, ModalScreen):
            return
        self._quick_check = not self.macos_mode
        self._confirm_stage(1, False)

    @on(Button.Pressed, "#run")
    def selected_pressed(self) -> None:
        if self.busy or self._diagnosing:
            return
        mode = self.query_one("#mode", Select).value
        if mode == "all":
            self._confirm_stage(2, True)
        elif mode == "from":
            step = self._selected()
            if step < 2:
                self._set_message("Choose Step 2-5 to start a guided checkout sequence.")
                return
            self._confirm_stage(step, True)
        else:
            self._confirm_stage(self._selected(), False)

    @on(Button.Pressed, "#sequence")
    def sequence_pressed(self) -> None:
        step = self._selected()
        if step < 2:
            self._set_message("Choose Step 2, 3, 4 or 5 to start the subscription sequence.")
            return
        self._confirm_stage(step, True)

    @on(Button.Pressed, "#next")
    def next_pressed(self) -> None:
        if self.busy or not self.sequence or self.current_step is None:
            return
        if self._last_outcome is None or not self._last_outcome.can_review:
            return
        next_step = self.current_step + 1
        if next_step > 5:
            return
        self._confirm_stage(next_step, True, previous_verified=True)

    @on(Button.Pressed, "#stop")
    def stop_pressed(self) -> None:
        if not self.busy:
            return
        if self.current_step in (0, 1):
            self._cancel_readonly()
        else:
            self._stop_after_step = True
            self._set_message("No later step will run. Finish or review the checkout on Android; the current transaction cannot be force-stopped.")
            self.query_one("#stop", Button).disabled = True

    def _cancel_readonly(self) -> None:
        if not self.busy or self.current_step not in (0, 1) or self._cancel_requested:
            return
        self._cancel_requested = True
        self._stop_after_step = True
        self._set_status("Stopping read-only check...")
        self._set_message("Stopping the local check; no checkout was started.")
        self.query_one("#stop", Button).disabled = True
        self.terminate_readonly_child()

    @work(thread=True, exclusive=True, group="read-only-cancel")
    def terminate_readonly_child(self) -> None:
        child = self._child
        if child is None or child.poll() is not None:
            return
        try:
            if os.name == "nt":
                result = subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"],
                                        capture_output=True, text=True, timeout=8, check=False)
                if result.returncode != 0 and child.poll() is None:
                    raise OSError("taskkill failed")
            else:
                os.killpg(child.pid, signal.SIGTERM)
        except (OSError, subprocess.TimeoutExpired) as error:
            self.call_from_thread(self._set_message,
                                  f"Cannot stop the check: {error}. Open technical details.")

    @on(Button.Pressed, "#exit")
    def exit_pressed(self) -> None:
        self.action_quit_safely()

    @on(Button.Pressed, "#manual")
    def manual_pressed(self) -> None:
        child = self._child
        if child and child.stdin:
            try:
                child.stdin.write("\n")
                child.stdin.flush()
                self.query_one("#manual", Button).disabled = True
                self.query_one("#manual", Button).display = False
            except (OSError, ValueError):
                self._set_message("Could not continue the Android prompt. See Debug.")

    @on(Button.Pressed, "#debug")
    def debug_pressed(self) -> None:
        self.action_toggle_debug()

    def action_toggle_debug(self) -> None:
        self.debug_visible = not self.debug_visible
        log = self.query_one("#debug_log", RichLog)
        if self.debug_visible:
            # Rebuild from the bounded current-run buffer: lines received while
            # details were hidden must not disappear or be duplicated.
            log.clear()
            for line in self._last_output:
                log.write(line)
        log.display = self.debug_visible
        self.query_one("#debug", Button).label = (
            "Hide technical details" if self.debug_visible else "Show technical details"
        )

    def action_run_selected(self) -> None:
        if not isinstance(self.screen, ModalScreen):
            self.selected_pressed()

    def action_quit_safely(self) -> None:
        if isinstance(self.screen, PrepareMuMu):
            self.screen.close_setup()
            return
        if not self.busy:
            self.exit()
            return
        self._exit_after_step = True
        if self.current_step in (0, 1):
            self._cancel_readonly()
            self._set_message("Stopping read-only check; toolkit will exit when it stops.")
        else:
            self._stop_after_step = True
            self._set_message("Exit queued after the current checkout. Review Google Play on Android; no later step will start.")
            self.query_one("#stop", Button).disabled = True
            self.query_one("#exit", Button).disabled = True

    def _start(self, step: int, sequence: bool) -> None:
        if self.busy or self._diagnosing:
            return
        self.busy = True
        self.sequence = sequence
        self.current_step = step
        self._stop_after_step = False
        self._cancel_requested = False
        self._exit_after_step = False
        self._last_outcome = None
        self._verified_account = None
        self._checked_device = None
        self._last_output.clear()
        self._run_output.clear()
        self.query_one("#debug_log", RichLog).clear()
        self.query_one("#offer_view", RichLog).clear()
        self.query_one("#offer_view", RichLog).display = False
        self.query_one("#offers_title", Static).display = False
        self.query_one("#device", Static).update(
            "ANDROID DEVICE\nADB • Auto-detect" if self.macos_mode
            else "ANDROID DEVICE\nMuMu • Auto-detect"
        )
        self.query_one("#account", Static).update("GOOGLE ACCOUNT\nNot checked")
        self.query_one("#manual", Button).display = False
        self.query_one("#manual", Button).disabled = True
        self._started_at = time.monotonic()
        self._last_activity_at = self._started_at
        self.query_one("#elapsed", Static).update("Elapsed: 00:00")
        self.query_one("#activity", Static).update(
            "Connecting to Android diagnostics..." if self.macos_mode
            else "Connecting to MuMu and preparing tools..."
        )
        self.query_one("#quickstart", Button).disabled = True
        if self.mumu_setup_available:
            self.query_one("#prepare_mumu", Button).disabled = True
        self.query_one("#diagnose", Button).disabled = True
        self.query_one("#run", Button).disabled = True
        self.query_one("#sequence", Button).disabled = True
        self.query_one("#mode", Select).disabled = True
        self.query_one("#step", Select).disabled = True
        self.query_one("#next", Button).disabled = True
        self.query_one("#stop", Button).disabled = False
        self.query_one("#stop", Button).label = "Stop check" if step <= 1 else "Stop after this step"
        self.query_one("#stop", Button).display = True
        self.query_one("#next", Button).display = False
        self.query_one("#step_result", Static).update(f"Step {step} · {STAGES[step].label}")
        self._set_workflow(step, "running")
        self._set_status(
            "Running — check Android if prompted" if self.macos_mode
            else "Running — check MuMu if prompted"
        )
        self._set_message("Preparing tools and checking Google Play. Missing dependencies are installed automatically.")
        self.run_stage(step)

    def _execute(self, command: list[str]) -> int:
        """Run the existing engine and send output to the TUI without blocking it."""
        # Windows Python defaults to a locale code page when stdout is piped.
        # Force UTF-8 for nested setup/CLI Python processes without changing billing logic.
        child_env = os.environ.copy()
        child_env["PYTHONIOENCODING"] = "utf-8"
        child_env["PYTHONUTF8"] = "1"
        if self._cancel_requested:
            return -1
        options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                   if os.name == "nt" else {"start_new_session": True})
        with subprocess.Popen(
            command, cwd=self.repo, env=child_env, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", bufsize=1, **options
        ) as child:
            self._child = child
            if child.stdout:
                for line in child.stdout:
                    try:
                        self.call_from_thread(self._received, line.rstrip("\r\n"))
                    except RuntimeError:
                        return -1
            return child.wait()

    @work(thread=True, exclusive=True)
    def run_stage(self, step: int) -> None:
        try:
            if not self.macos_mode and needs_setup():
                self.call_from_thread(self._set_status, "Setting up...")
                self.call_from_thread(self._set_message,
                                      "Preparing Frida and ADB. You do not need a separate setup command.")
                setup = self.repo / "setup_env.py"
                if not setup.is_file():
                    raise FileNotFoundError("setup_env.py is missing from the project directory")
                setup_code = self._execute([sys.executable, str(setup)])
                if self._cancel_requested:
                    self.call_from_thread(self._finished, step, Outcome("cancelled", "Check stopped", "Cancelled read-only check."), None)
                    return
                if setup_code != 0:
                    self.call_from_thread(
                        self._finished, step,
                        Outcome("setup_failed", "Setup did not finish",
                                "Open Debug, check the setup issue, then retry. No checkout was started."),
                        None)
                    return

            # Never treat a report from setup or a previous invocation as the
            # outcome of the selected step.
            if self._cancel_requested:
                self.call_from_thread(self._finished, step, Outcome("cancelled", "Check stopped", "Cancelled read-only check."), None)
                return
            started = time.time()
            command = command_for_step(step, self.repo)
            if step == 2 and self._checkout_target:
                account, serial = self._checkout_target
                command.extend(("-Email", account, "-Serial", serial))
            elif self._prepared_device:
                command.extend(("-Serial", self._prepared_device))
            return_code = self._execute(command)
            if self._cancel_requested:
                self.call_from_thread(self._finished, step, Outcome("cancelled", "Check stopped", "Cancelled read-only check."), None)
                return
            report = read_fresh_report(self.repo / "ultra0-report", step, started,
                                       expected_account=self._verified_account)
            result = outcome_for_stage(step, return_code, report)
            self.call_from_thread(self._finished, step, result, report)
        except Exception as error:
            result = Outcome("exception", "Could not start the tool",
                             f"{type(error).__name__}: {error}. See Debug and verify Google Play.")
            self.call_from_thread(self._finished, step, result, None)
        finally:
            self._child = None

    def _received(self, line: str) -> None:
        if not line:
            return
        self._last_output.append(line)
        self._run_output.append(line)
        self._last_activity_at = time.monotonic()
        lower = line.lower()
        if "frida" in lower or "setup" in lower:
            phase = "Preparing Android tools..."
        elif "adb" in lower or "device" in lower:
            phase = "Checking Android device..."
        elif "offer" in lower or "billing" in lower or "google one" in lower:
            phase = "Checking available offers..."
        elif "account" in lower or "play store" in lower:
            phase = "Checking Google Play account..."
        else:
            phase = "Process responding. Details available in technical log."
        self.query_one("#activity", Static).update(phase)
        if self.debug_visible:
            self.query_one("#debug_log", RichLog).write(line)
        if "Action required: Add your payment method directly in Google Play." in line:
            self._set_message("Enter your payment method in Google Play. The checkout will be checked again.")
        elif re.search(r"Action required:|Press Enter to continue", line, re.I):
            btn = self.query_one("#manual", Button)
            btn.display = True
            btn.disabled = False
            self._set_message("Complete the requested action on Android, then click Completed.")
        device = re.fullmatch(r"\s*Device\s+([A-Za-z0-9_.:\[\]-]+)\s*", line)
        if device:
            self._checked_device = device.group(1)
            self.query_one("#device", Static).update("Device  •  " + escape(self._checked_device))
        # Trust only the structured PowerShell "Account <email>" status line,
        # not arbitrary log messages containing an email address.
        account = re.match(
            r"^\s*Account\s+([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})\s*$",
            line,
        )
        if account:
            self._verified_account = account.group(1).lower()
            self.query_one("#account", Static).update(
                "Account  •  " + escape(mask_email(self._verified_account))
            )

    def _visible_failure(self) -> str:
        """Show a concise CLI error without exposing account emails."""
        for raw in reversed(self._run_output):
            line = re.sub(r"\x1b\[[0-9;]*m", "", raw).strip()
            if not line:
                continue
            if re.search(r"error|failed|missing|not found|cannot|unable|offline|unauthorized|issue|stopped|device", line, re.I):
                line = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[account hidden]", line)
                return line[:220]
        return ""

    def _finished(self, step: int, outcome: Outcome, report: dict | None) -> None:
        self.busy = False
        quick_check, self._quick_check = self._quick_check, False
        self._checkout_target = None
        self._last_outcome = outcome
        self.query_one("#manual", Button).display = False
        self.query_one("#manual", Button).disabled = True
        self.query_one("#quickstart", Button).disabled = False
        if self.mumu_setup_available:
            self.query_one("#prepare_mumu", Button).disabled = False
        self.query_one("#diagnose", Button).disabled = False
        self.query_one("#run", Button).disabled = False
        self.query_one("#sequence", Button).disabled = False
        self.query_one("#mode", Select).disabled = False
        self.query_one("#step", Select).disabled = False
        self._update_run_mode()
        self.query_one("#stop", Button).disabled = True
        self.query_one("#stop", Button).display = False
        self.query_one("#exit", Button).disabled = False
        self._started_at = None
        self.query_one("#activity", Static).update("Step finished. Review the result above.")
        self._set_workflow(step, "done" if outcome.code in ("listed", "environment_ok") else "review")
        self._set_status(outcome.title)
        instruction = outcome.instruction
        if outcome.code in ("tool_error", "exception", "missing_report", "setup_failed"):
            diagnostic = self._visible_failure()
            if diagnostic:
                instruction = f"{instruction}  Last CLI message: {diagnostic}"
        self._set_message(instruction)
        if step == 1:
            self.query_one("#step_result", Static).update(report_summary(report))
            if isinstance(report, dict):
                offer_view = self.query_one("#offer_view", RichLog)
                offer_view.clear()
                for item in offer_explorer_lines(report):
                    offer_view.write(item)
                offer_view.display = True
                self.query_one("#offers_title", Static).display = True
            if self.macos_mode and isinstance(report, dict):
                detected = report.get("detected_play_account")
                if isinstance(detected, str) and detected:
                    self.query_one("#account", Static).update(
                        "Account  •  " + escape(mask_email(detected))
                    )
        if outcome.can_review and self.sequence and step < 5 and not self._stop_after_step:
            self.query_one("#next", Button).disabled = False
            self.query_one("#next", Button).display = True
        else:
            self.query_one("#next", Button).disabled = True
            self.query_one("#next", Button).display = False
            self.sequence = False
        if self._exit_after_step:
            self.exit()
            return
        if quick_check and step == 1 and outcome.code == "listed" and report:
            account = self._verified_account
            device = self._checked_device
            detected = str(report.get("detected_play_account") or "").strip().lower()
            if account and device and (not detected or detected == account) and any(
                isinstance(offer, dict) and offer.get("id") == STAGES[2].offer
                and str(offer.get("micros")) == "0" for offer in (report.get("offers") or ())
            ):
                target = (account, device)
                self.push_screen(
                    Approval("Device and offers checked",
                             "Google Play returned a 12-month offer with a zero-priced first phase. "
                             "Review Step 2 for this offer only. Google Play determines eligibility.",
                             continue_label="Review 12-month checkout"),
                    lambda review: self._confirm_stage(2, False, target=target) if review else None,
                )
            elif not account:
                self._set_message("Open the Play Store home screen in MuMu, sign in if needed, "
                                  "select your profile, then run Check Device & Offers again.")
        if outcome.code == "checkout_requested":
            self.notify("Review the actual subscription in Google Play.", severity="warning")
        elif outcome.code not in ("listed", "environment_ok", "cancelled"):
            self.notify("Step stopped; check the result before another attempt.", severity="warning")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ePlus AI Toolkit Textual frontend")
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--sequence", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    try:
        selected = validate_step(args.step)
    except ValueError as exc:
        parser.error(str(exc))
    GoogleAITUI(repo=Path(__file__).resolve().parent, selected_step=selected,
                start_sequence=args.sequence, initial_debug=args.debug).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
