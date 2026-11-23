"""Pure state and subprocess helpers for the Textual frontend.

No checkout is initiated by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib.metadata
import json
import re
import shutil
import sys
import time


@dataclass(frozen=True)
class Stage:
    number: int
    label: str
    offer: str


FRIDA_VERSION = "16.5.9"


def needs_setup() -> bool:
    """Only install Android Python tooling when the required Frida build is absent."""
    try:
        return importlib.metadata.version("frida") != FRIDA_VERSION
    except importlib.metadata.PackageNotFoundError:
        return True


STAGES = (
    Stage(0, "Environment", ""),
    Stage(1, "Available offers", ""),
    Stage(2, "Pro 12 months", "12months-eft"),
    Stage(3, "Pro +6 months", "6months-eft"),
    Stage(4, "Pro +6 months (second)", "6months-eft-2"),
    Stage(5, "Optional +6 months", "6months-eft-ss-2026"),
)


@dataclass(frozen=True)
class Outcome:
    code: str
    title: str
    instruction: str
    can_review: bool = False


MESSAGES = {
    "checkout_account_mismatch": (
        "Checkout is using a different account",
        "Verify the billing account in Google Play. If it is different, close checkout and check offers again.",
    ),
    "checkout_account_unverified": (
        "Checkout account could not be verified",
        "Review the billing account and terms directly on the Google Play checkout screen.",
    ),
    "payment_method_not_confirmed": (
        "Payment method could not be verified",
        "Finish payment setup in Google Play and review the checkout screen and subscription status.",
    ),
    "listed": ("Offers loaded", "Offer metadata is not proof of eligibility."),
    "checkout_requested": (
        "Checkout submitted - not yet verified",
        "Check Google Play Subscriptions, renewal date and charges before proceeding.",
    ),
    "checkout_security_blocked": (
        "Google Play requires account verification",
        "Review Google Account Security and Google Payments alerts (OR-REH-04). Stop retrying.",
    ),
    "already_subscribed": (
        "This plan is already subscribed",
        "No extra months are verified. Check the renewal date; do not repeat checkout.",
    ),
    "payment_security_blocked": (
        "Google Play requires account verification",
        "Review Google Account Security and Google Payments alerts (OR-REH-04). Stop retrying.",
    ),
    "today_price_unverified": (
        "Today's checkout amount is unclear",
        "Check the amount payable today on the Android screen before trying again.",
    ),
    "trial_duration_unverified": (
        "Trial duration could not be verified",
        "Check the duration and future pricing shown by Google Play.",
    ),
    "ineligible": (
        "This account is not eligible",
        "Review Google Play's offer terms. Force mode cannot change eligibility.",
    ),
    "backup_payment_methods_prompt": (
        "Google Play asked about backup payments",
        "Review that optional setting in Google Play; it does not confirm a subscription.",
    ),
    "processing": (
        "Google Play is processing a transaction",
        "Check payment history before another attempt.",
    ),
    "checkout_not_confirmed": (
        "Checkout was not confirmed",
        "Check the Google Play subscription status before retrying.",
    ),
    "offer_query_failed": (
        "Could not load offers",
        "Open Google One and Google Play, then retry the read-only offer check.",
    ),
    "offer_not_available": (
        "Offer not available",
        "Use Step 1 to review current offers. Do not assume eligibility.",
    ),
    "exception": (
        "An unexpected error occurred",
        "Open Debug for details. Do not retry a payment until the outcome is known.",
    ),
}


def validate_step(step: int) -> int:
    if type(step) is not int or not 0 <= step <= 5:
        raise ValueError("Step must be a number between 0 and 5")
    return step


def command_for_step(step: int, repo: Path, shell: str | None = None) -> list[str]:
    validate_step(step)
    if sys.platform == "darwin":
        bridge = repo / "macos_runner.py"
        if not bridge.is_file():
            raise FileNotFoundError("macos_runner.py is missing")
        command = [sys.executable, str(bridge), "--step", str(step)]
        # The Textual app shows a separate approval modal for each paid stage.
        # The native adapter requires explicit flags as a second fail-closed gate.
        if step >= 2:
            command.append("--confirmed")
        if step >= 3:
            command.append("--active-confirmed")
        return command
    executable = shell or shutil.which("powershell.exe") or shutil.which("pwsh")
    if not executable:
        raise RuntimeError("PowerShell was not found. Install PowerShell or run on Windows.")
    script = repo / "run-all.ps1"
    if not script.is_file():
        raise FileNotFoundError("run-all.ps1 is missing from the project directory")
    # Single steps are non-interactive at the PowerShell approval layer.
    # Using the existing wrapper keeps ADB, Frida, Play-account, offer and
    # checkout validation in one place instead of copying billing code.
    return [executable, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(script), "-Step", str(step)]


def read_fresh_report(directory: Path, step: int, started_at: float,
                      expected_account: str | None = None) -> dict | None:
    """Read only fresh reports for the account verified by this invocation."""
    validate_step(step)
    if not directory.exists():
        return None
    # A paid result without a verified Google Play account is ambiguous.
    if step >= 2 and not expected_account:
        return None
    expected = (expected_account or "").strip().lower()
    candidates = []
    for path in directory.glob("*.json"):
        try:
            # The previous two-second grace period could accept a report
            # generated by an earlier invocation and unlock a later checkout.
            # Only accept reports written after this stage was launched.
            if path.stat().st_mtime_ns < int(started_at * 1_000_000_000):
                continue
            if step == 1 and path.name != "current.json":
                continue
            if step >= 2 and path.name == "current.json":
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("status"), str):
                if step >= 2 and str(data.get("email", "")).strip().lower() != expected:
                    continue
                candidates.append(data)
        except (OSError, ValueError, UnicodeError):
            continue
    # Multiple matching reports still cannot be assigned unambiguously to a
    # single invocation. Refuse to authorize another checkout.
    return candidates[0] if len(candidates) == 1 else None


def outcome_for_stage(step: int, exit_code: int, report: dict | None) -> Outcome:
    validate_step(step)
    if exit_code != 0:
        return Outcome("tool_error", "The step could not finish",
                       "Check Debug and the Android screen before retrying.")
    if step == 0:
        return Outcome("environment_ok", "Android environment checked",
                       "You can now list available offers.")
    if report is None:
        return Outcome("missing_report", "Could not verify the result",
                       "A fresh result report was not found. Do not proceed to another paid step.")
    status = str(report.get("status", "unknown"))
    sheet = report.get("sheet")
    reason = str(sheet.get("reason", "")) if isinstance(sheet, dict) else ""
    code = reason if status != "checkout_requested" and reason in MESSAGES else status
    title, instruction = MESSAGES.get(
        code, ("Could not verify this step",
               "Check the Android screen and Debug before retrying."))
    return Outcome(code, title, instruction,
                   can_review=(step >= 2 and status == "checkout_requested"))


def mask_email(value: str) -> str:
    m = re.fullmatch(r"([^@\s]+)@([^@\s]+)", value.strip())
    if not m:
        return "Not detected"
    name, domain = m.groups()
    return f"{name[:2]}***@{domain}"


def report_summary(report: dict | None) -> str:
    if not report:
        return "No fresh report"
    offers = report.get("offers")
    if isinstance(offers, list):
        return f"{len(offers)} offers returned (eligibility not verified)"
    return str(report.get("status", "Unknown result"))


# Only display the non-secret metadata that the existing Step 1 report supplies.
# Tokens, account identifiers, raw titles and purchase objects must not be rendered.
_SAFE_OFFER_FIELD = re.compile(r"^[A-Za-z0-9._:-]{1,72}$")


def _offer_field(value: object) -> str:
    text = str(value) if value is not None else ""
    return text if _SAFE_OFFER_FIELD.fullmatch(text) else "(unavailable)"


def offer_explorer_lines(report: dict | None, limit: int = 20) -> list[str]:
    """Format observed introductory phases; never infer eligibility or renewal.

    The source report contains only the *first* pricing phase for each offer.
    Never call a non-zero first phase 'free', never guess the currency, and do
    not render raw Frida payloads (which may include offer tokens).
    """
    if not isinstance(report, dict) or not isinstance(report.get("offers"), list):
        return ["No fresh offer details available."]
    items = [o for o in report["offers"] if isinstance(o, dict)]
    if not items:
        return ["No offers returned. Eligibility remains unknown."]
    rows = ["PRODUCT / OFFER  |  FIRST PHASE  |  INTRO PRICE"]
    for offer in items[:max(0, limit)]:
        product = _offer_field(offer.get("product"))
        offer_id = _offer_field(offer.get("id"))
        period = _offer_field(offer.get("period"))
        micros = offer.get("micros")
        if isinstance(micros, (int, str)) and str(micros) == "0":
            price = "zero (not eligibility)"
        elif isinstance(micros, (int, str)) and str(micros).isdigit():
            price = "nonzero (currency unknown)"
        else:
            price = "unknown"
        rows.append(f"{product} / {offer_id}  |  {period}  |  {price}")
    if len(items) > max(0, limit):
        rows.append(f"... {len(items) - max(0, limit)} more offer(s) not shown.")
    rows.append("Future renewal price, account eligibility and active subscription NOT verified.")
    return rows
