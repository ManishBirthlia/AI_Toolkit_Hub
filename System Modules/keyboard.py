"""
keyboard.py — Keyboard, mouse, and screenshot tools for the Jarvis AI agent.

Provides helpers to type text, press hotkeys, click at screen coordinates,
scroll, and take screenshots.  Uses ``pyautogui`` as the primary driver.
"""

import os
import time
from pathlib import Path
from datetime import datetime

try:
    import pyautogui
    pyautogui.FAILSAFE = True   # move mouse to top-left corner to abort
    pyautogui.PAUSE = 0.05      # slight delay between actions for stability
    _PYAUTOGUI_AVAILABLE = True
except ImportError:
    _PYAUTOGUI_AVAILABLE = False
    print("[keyboard] ⚠  pyautogui not installed — keyboard/mouse tools disabled.  "
          "pip install pyautogui")


# ── Public Tool Functions ────────────────────────────────────────────────────

def type_text(text: str, interval: float = 0.02) -> dict:
    """Type a string of text character by character via the keyboard.

    Args:
        text:     The text to type.
        interval: Seconds between each keystroke (default 0.02).

    Returns:
        dict confirming how many characters were typed.
    """
    if not _PYAUTOGUI_AVAILABLE:
        return {"success": False, "result": None, "error": "pyautogui is not installed."}
    try:
        pyautogui.typewrite(text, interval=interval) if text.isascii() else pyautogui.write(text)
        return {"success": True, "result": f"Typed {len(text)} characters", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def press_hotkey(*keys: str) -> dict:
    """Press a keyboard shortcut (e.g. 'ctrl', 'c' for Ctrl+C).

    Args:
        *keys: One or more key names as positional arguments.
               Examples: press_hotkey('ctrl', 'c'), press_hotkey('alt', 'f4').

    Returns:
        dict confirming the hotkey was pressed.
    """
    if not _PYAUTOGUI_AVAILABLE:
        return {"success": False, "result": None, "error": "pyautogui is not installed."}
    try:
        pyautogui.hotkey(*keys)
        return {"success": True, "result": f"Pressed hotkey: {' + '.join(keys)}", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
    """Click the mouse at screen coordinates (x, y).

    Args:
        x:       Horizontal pixel position.
        y:       Vertical pixel position.
        button:  'left', 'right', or 'middle' (default 'left').
        clicks:  Number of consecutive clicks (default 1, use 2 for double-click).

    Returns:
        dict confirming the click location and button.
    """
    if not _PYAUTOGUI_AVAILABLE:
        return {"success": False, "result": None, "error": "pyautogui is not installed."}
    try:
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)
        return {
            "success": True,
            "result": f"Clicked {button} button {clicks}x at ({x}, {y})",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def scroll(direction: str = "down", amount: int = 3) -> dict:
    """Scroll the mouse wheel up or down.

    Args:
        direction: 'up' or 'down' (default 'down').
        amount:    Number of scroll "clicks" (default 3).

    Returns:
        dict confirming the scroll action.
    """
    if not _PYAUTOGUI_AVAILABLE:
        return {"success": False, "result": None, "error": "pyautogui is not installed."}
    try:
        scroll_amount = amount if direction.lower() == "up" else -amount
        pyautogui.scroll(scroll_amount)
        return {
            "success": True,
            "result": f"Scrolled {direction} by {amount}",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def take_screenshot(save_path: str | None = None) -> dict:
    """Capture the entire screen and save it as a PNG file.

    Args:
        save_path: Optional path to save the screenshot.  If omitted a
                   timestamped file is created in the current directory.

    Returns:
        dict with the saved file path in ``result``.
    """
    if not _PYAUTOGUI_AVAILABLE:
        return {"success": False, "result": None, "error": "pyautogui is not installed."}
    try:
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"screenshot_{timestamp}.png"

        path = Path(save_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        screenshot = pyautogui.screenshot()
        screenshot.save(str(path))
        return {"success": True, "result": f"Screenshot saved to {path}", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for this module."""
    return [
        {
            "name": "type_text",
            "description": "Type a string of text via the keyboard, character by character.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text string to type."
                    },
                    "interval": {
                        "type": "number",
                        "description": "Seconds between each keystroke. Defaults to 0.02."
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "press_hotkey",
            "description": "Press a keyboard shortcut. Pass each key as a separate argument (e.g. 'ctrl' and 'c' for Ctrl+C).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of key names to press simultaneously (e.g. ['ctrl', 'c'])."
                    }
                },
                "required": ["keys"]
            }
        },
        {
            "name": "click",
            "description": "Click the mouse at specific screen coordinates.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Horizontal pixel position."},
                    "y": {"type": "integer", "description": "Vertical pixel position."},
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "middle"],
                        "description": "Mouse button to click. Defaults to 'left'."
                    },
                    "clicks": {
                        "type": "integer",
                        "description": "Number of clicks. Use 2 for double-click. Defaults to 1."
                    }
                },
                "required": ["x", "y"]
            }
        },
        {
            "name": "scroll",
            "description": "Scroll the mouse wheel up or down.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down"],
                        "description": "Direction to scroll. Defaults to 'down'."
                    },
                    "amount": {
                        "type": "integer",
                        "description": "Number of scroll clicks. Defaults to 3."
                    }
                },
                "required": []
            }
        },
        {
            "name": "take_screenshot",
            "description": "Capture the entire screen and save it as a PNG file.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "save_path": {
                        "type": "string",
                        "description": "Optional file path to save the screenshot. Auto-generated if omitted."
                    }
                },
                "required": []
            }
        },
    ]
