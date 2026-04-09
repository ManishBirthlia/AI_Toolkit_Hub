"""
System Modules — Jarvis-like AI Agent Toolkit
=============================================

A collection of system-level tools for building an AI agent that can
interact with the operating system, browser, files, clipboard, audio,
vision, email, and persistent memory.

Each module exposes:
  • Action functions that return ``{"success": bool, "result": ..., "error": ...}``
  • A ``get_tool_schema()`` helper that emits Anthropic-compatible tool definitions.

Usage:
    from system_modules import system, browser, files, keyboard
    from system_modules import vision, email_tool, clipboard, audio, memory
"""

from . import system
from . import browser
from . import files
from . import keyboard
from . import vision
from . import email_tool
from . import clipboard
from . import audio
from . import memory

__all__ = [
    "system",
    "browser",
    "files",
    "keyboard",
    "vision",
    "email_tool",
    "clipboard",
    "audio",
    "memory",
]


def get_all_tool_schemas() -> list[dict]:
    """Aggregate every tool schema from every module into one flat list.

    Returns:
        A list of Anthropic-compatible tool-definition dicts ready to be
        passed as the ``tools`` parameter in an API call.
    """
    schemas: list[dict] = []
    for mod in (system, browser, files, keyboard, vision,
                email_tool, clipboard, audio, memory):
        schemas.extend(mod.get_tool_schema())
    return schemas
