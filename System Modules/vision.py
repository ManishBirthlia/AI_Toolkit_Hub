"""
vision.py — Screen-vision tools for the Jarvis AI agent.

Provides helpers to capture the screen, find text on-screen via OCR,
get the title of the active window, and describe the screen using an
AI vision model (Claude / OpenAI).
"""

import io
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import pyautogui
    _PYAUTOGUI_AVAILABLE = True
except ImportError:
    _PYAUTOGUI_AVAILABLE = False
    print("[vision] ⚠  pyautogui not installed — screen capture disabled.  "
          "pip install pyautogui")

try:
    from PIL import Image
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False
    print("[vision] ⚠  Pillow not installed — image processing disabled.  "
          "pip install Pillow")

try:
    import pytesseract
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False
    print("[vision] ⚠  pytesseract not installed — OCR (find_text_on_screen) disabled.  "
          "pip install pytesseract  +  install Tesseract-OCR binary")

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    # Silently skip — describe_screen_with_ai is optional


# ── Internal Helpers ─────────────────────────────────────────────────────────

def _capture_pil_image():
    """Capture the full screen and return a PIL Image object."""
    if not _PYAUTOGUI_AVAILABLE:
        raise RuntimeError("pyautogui is required for screen capture.")
    return pyautogui.screenshot()


# ── Public Tool Functions ────────────────────────────────────────────────────

def capture_screen(save_path: str | None = None) -> dict:
    """Capture the full screen and optionally save to a file.

    Args:
        save_path: Optional PNG file path.  Auto-generated if omitted.

    Returns:
        dict with the saved path and image dimensions in ``result``.
    """
    if not _PYAUTOGUI_AVAILABLE:
        return {"success": False, "result": None, "error": "pyautogui is not installed."}
    try:
        img = _capture_pil_image()

        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"capture_{timestamp}.png"

        path = Path(save_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(path))

        return {
            "success": True,
            "result": {
                "path": str(path),
                "width": img.width,
                "height": img.height,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def find_text_on_screen(text: str) -> dict:
    """Use OCR to search for a text string on the current screen.

    Captures a screenshot, runs Tesseract OCR on it, and checks whether
    the target text appears in the recognised output.

    Args:
        text: The text string to search for (case-insensitive).

    Returns:
        dict with ``result`` containing a boolean ``found`` flag plus
        the full OCR text for context.
    """
    if not _PYAUTOGUI_AVAILABLE:
        return {"success": False, "result": None, "error": "pyautogui is not installed."}
    if not _TESSERACT_AVAILABLE:
        return {"success": False, "result": None,
                "error": "pytesseract is not installed. Run: pip install pytesseract"}
    try:
        img = _capture_pil_image()
        ocr_text = pytesseract.image_to_string(img)
        found = text.lower() in ocr_text.lower()
        return {
            "success": True,
            "result": {
                "found": found,
                "search_term": text,
                "ocr_text_snippet": ocr_text[:2000],
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def get_active_window_title() -> dict:
    """Return the title of the currently focused window.

    Uses pyautogui on Windows; falls back to ``xdotool`` on Linux and
    ``osascript`` on macOS.

    Returns:
        dict with the window title string in ``result``.
    """
    try:
        if _PYAUTOGUI_AVAILABLE:
            win = pyautogui.getActiveWindow()
            if win:
                return {"success": True, "result": win.title, "error": None}

        # Platform-specific fallbacks
        sys_name = platform.system()
        if sys_name == "Windows":
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return {"success": True, "result": buf.value, "error": None}
        elif sys_name == "Linux":
            title = subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"], text=True
            ).strip()
            return {"success": True, "result": title, "error": None}
        elif sys_name == "Darwin":
            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            title = subprocess.check_output(["osascript", "-e", script], text=True).strip()
            return {"success": True, "result": title, "error": None}
        else:
            return {"success": False, "result": None, "error": f"Unsupported OS: {sys_name}"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def describe_screen_with_ai(api_key: str, prompt: str = "Describe what you see on this screen.") -> dict:
    """Capture the screen and send it to Claude's vision API for description.

    Requires the ``anthropic`` package and a valid API key.

    Args:
        api_key: Anthropic API key.
        prompt:  The question to ask about the screenshot (default: describe it).

    Returns:
        dict with Claude's description in ``result``.
    """
    if not _ANTHROPIC_AVAILABLE:
        return {"success": False, "result": None,
                "error": "anthropic package is not installed. Run: pip install anthropic"}
    if not _PYAUTOGUI_AVAILABLE or not _PIL_AVAILABLE:
        return {"success": False, "result": None,
                "error": "pyautogui and Pillow are required for screen capture."}
    try:
        import base64

        # Capture and encode screenshot as base64 PNG
        img = _capture_pil_image()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        description = message.content[0].text
        return {"success": True, "result": description, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for this module."""
    return [
        {
            "name": "capture_screen",
            "description": "Capture the full screen and save as a PNG image file.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "save_path": {
                        "type": "string",
                        "description": "Optional file path for the screenshot. Auto-generated if omitted."
                    }
                },
                "required": []
            }
        },
        {
            "name": "find_text_on_screen",
            "description": "Use OCR to search for a specific text string currently visible on the screen.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to search for (case-insensitive)."
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "get_active_window_title",
            "description": "Return the title of the currently focused/active window.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "describe_screen_with_ai",
            "description": "Capture the screen and send it to Claude's vision API for AI-powered description.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "Anthropic API key for Claude vision."
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Question to ask about the screenshot. Defaults to 'Describe what you see on this screen.'"
                    }
                },
                "required": ["api_key"]
            }
        },
    ]
