"""Windows MuMu provisioning and read-only Android account monitoring."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from threading import Event
from typing import Callable

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
GOOGLE_ACCOUNT = re.compile(r"Account \{name=([^,{}]+), type=com\.google\}")


def _mumu_cli() -> str:
    installed = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    bundled = installed / "Netease" / "MuMuPlayer" / "nx_main" / "mumu-cli.exe"
    executable = shutil.which("mumu-cli.exe")
    if executable:
        return executable
    if bundled.is_file():
        return str(bundled)
    raise RuntimeError("MuMu Player or mumu-cli.exe could not be found.")


def _run(*args: str) -> str:
    try:
        result = subprocess.run(args, capture_output=True, encoding="utf-8", errors="replace",
                                timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.TimeoutExpired):
        raise RuntimeError("MuMu or ADB did not respond. Check that MuMu is installed and running.") from None
    if result.returncode:
        raise RuntimeError("MuMu or ADB reported an error. Check the new instance in MuMu Manager.")
    return result.stdout


def _instances(cli: str) -> dict:
    try:
        result = json.loads(_run(cli, "info", "--vmindex", "all"))
        return {key: value for key, value in result.items() if key.isdecimal()
                and isinstance(value, dict)}
    except (ValueError, AttributeError):
        raise RuntimeError("MuMu returned an unexpected instance list.") from None


def prepare(email: str, stop: Event, progress: Callable[[str], None]) -> str | None:
    """Create one MuMu instance and watch for the expected Android account."""
    if stop.is_set():
        return None
    if not EMAIL.fullmatch(email):
        raise ValueError("Enter the email address you will use in Google Play.")
    cli = _mumu_cli()
    adb = shutil.which("adb") or shutil.which("adb.exe")
    if not adb:
        raise RuntimeError("ADB was not found on PATH. Install Android SDK platform-tools first.")

    before = _instances(cli)
    if stop.is_set():
        return None
    progress("Creating an Android 15 MuMu instance...")
    _run(cli, "create", "--number", "1", "--version", "15")
    after = _instances(cli)
    new_ids = after.keys() - before.keys()
    if len(new_ids) != 1:
        raise RuntimeError("Could not uniquely identify the new MuMu instance. Check MuMu Manager.")
    index = new_ids.pop()
    if stop.is_set():
        return None

    _run(cli, "setting", "--vmindex", index,
         "--key", "resolution_width.custom", "--value", "900",
         "--key", "resolution_height.custom", "--value", "1600",
         "--key", "resolution_dpi.custom", "--value", "320")
    launch = json.loads(_run(cli, "control", "--vmindex", index, "launch"))
    if launch.get("errcode") != 0:
        raise RuntimeError("MuMu could not start the new instance.")

    progress("Waiting for Android to finish starting...")
    for _ in range(45):
        if stop.is_set():
            return None
        if _instances(cli).get(index, {}).get("is_android_started"):
            break
        if stop.wait(2):
            return None
    else:
        raise RuntimeError("Android did not finish starting. Check the new instance in MuMu.")

    connection = _run(cli, "adb", "--vmindex", index, "--cmd", "connect")
    endpoint = re.search(r"\b(?:127\.0\.0\.1|localhost):[0-9]{1,5}\b", connection)
    if not endpoint:
        raise RuntimeError("MuMu did not expose a local ADB connection for the new instance.")
    serial = endpoint[0]
    _run(adb, "connect", serial)
    if _run(adb, "-s", serial, "get-state").strip() != "device":
        raise RuntimeError("The new MuMu instance is not online through ADB.")
    if stop.is_set():
        return None
    resolved = _run(adb, "-s", serial, "shell", "cmd", "package", "resolve-activity",
                    "--brief", "-a", "android.intent.action.MAIN",
                    "-c", "android.intent.category.LAUNCHER", "com.android.vending")
    activity = re.search(r"^com\.android\.vending/[A-Za-z0-9_.$]+$", resolved, re.MULTILINE)
    if not activity:
        raise RuntimeError("Google Play could not be opened on the new MuMu instance.")
    launch_output = _run(adb, "-s", serial, "shell", "am", "start", "-W", "-n", activity[0])
    if "Error:" in launch_output:
        raise RuntimeError("Google Play could not be opened on the new MuMu instance.")

    progress("Sign in to Google Play in MuMu. Complete any QR or verification prompts there.")
    for _ in range(150):
        if stop.is_set():
            return None
        accounts = GOOGLE_ACCOUNT.findall(_run(adb, "-s", serial, "shell", "dumpsys", "account"))
        if email.casefold() in {account.casefold() for account in accounts}:
            return serial
        if stop.wait(4):
            return None
    raise RuntimeError("The expected account did not appear. Finish sign-in in MuMu before checking offers.")
