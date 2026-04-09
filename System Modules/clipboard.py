"""
clipboard.py — Clipboard tools for the Jarvis AI agent.

Provides cross-platform copy and paste using ``pyperclip``.
Falls back to Windows-native ``win32clipboard`` or ``subprocess`` calls
for macOS/Linux when ``pyperclip`` is unavailable.
"""

import platform
import subprocess

try:
    import pyperclip
    _PYPERCLIP_AVAILABLE = True
except ImportError:
    _PYPERCLIP_AVAILABLE = False
    print("[clipboard] ⚠  pyperclip not installed — using OS-native fallbacks.  "
          "pip install pyperclip")


# ── Internal Fallbacks ───────────────────────────────────────────────────────

def _copy_fallback(text: str) -> None:
    """Platform-specific clipboard copy without pyperclip."""
    system = platform.system()
    if system == "Windows":
        # Use PowerShell's Set-Clipboard
        proc = subprocess.run(
            ["powershell", "-Command", f"Set-Clipboard -Value '{text}'"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip())
    elif system == "Darwin":
        proc = subprocess.run(["pbcopy"], input=text, text=True, capture_output=True)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip())
    elif system == "Linux":
        # Try xclip first, then xsel
        for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]]:
            try:
                subprocess.run(cmd, input=text, text=True, check=True, capture_output=True)
                return
            except FileNotFoundError:
                continue
        raise RuntimeError("No clipboard tool found. Install xclip or xsel.")
    else:
        raise RuntimeError(f"Unsupported OS: {system}")


def _paste_fallback() -> str:
    """Platform-specific clipboard paste without pyperclip."""
    system = platform.system()
    if system == "Windows":
        proc = subprocess.run(
            ["powershell", "-Command", "Get-Clipboard"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip())
        return proc.stdout.strip()
    elif system == "Darwin":
        proc = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return proc.stdout
    elif system == "Linux":
        for cmd in [["xclip", "-selection", "clipboard", "-o"], ["xsel", "--clipboard", "--output"]]:
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return proc.stdout
            except FileNotFoundError:
                continue
        raise RuntimeError("No clipboard tool found. Install xclip or xsel.")
    else:
        raise RuntimeError(f"Unsupported OS: {system}")


# ── Public Tool Functions ────────────────────────────────────────────────────

def copy_to_clipboard(text: str) -> dict:
    """Copy a text string to the system clipboard.

    Args:
        text: The text to place on the clipboard.

    Returns:
        dict confirming the copy.
    """
    try:
        if _PYPERCLIP_AVAILABLE:
            pyperclip.copy(text)
        else:
            _copy_fallback(text)

        snippet = text[:80] + ("…" if len(text) > 80 else "")
        return {
            "success": True,
            "result": f"Copied {len(text)} chars to clipboard: '{snippet}'",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def paste_from_clipboard() -> dict:
    """Read the current text content of the system clipboard.

    Returns:
        dict with the clipboard text in ``result``.
    """
    try:
        if _PYPERCLIP_AVAILABLE:
            content = pyperclip.paste()
        else:
            content = _paste_fallback()

        return {"success": True, "result": content, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for this module."""
    return [
        {
            "name": "copy_to_clipboard",
            "description": "Copy a text string to the system clipboard.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to copy to the clipboard."
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "paste_from_clipboard",
            "description": "Read and return the current text content of the system clipboard.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
    ]
