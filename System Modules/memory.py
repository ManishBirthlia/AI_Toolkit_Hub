"""
memory.py — Persistent key-value memory for the Jarvis AI agent.

Stores memories as a JSON file on disk so they survive across sessions.
Designed for simple agent recall — "remember this for later" workflows.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Default memory file lives next to this module
_MEMORY_DIR = Path(__file__).resolve().parent / ".memory"
_MEMORY_FILE = _MEMORY_DIR / "agent_memory.json"


# ── Internal Helpers ─────────────────────────────────────────────────────────

def _ensure_memory_file() -> Path:
    """Create the memory directory and file if they don't exist yet."""
    _MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not _MEMORY_FILE.exists():
        _MEMORY_FILE.write_text("{}", encoding="utf-8")
    return _MEMORY_FILE


def _load_memory() -> dict:
    """Load the full memory store from disk."""
    path = _ensure_memory_file()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_memory_store(data: dict) -> None:
    """Persist the memory store to disk."""
    path = _ensure_memory_file()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Public Tool Functions ────────────────────────────────────────────────────

def save_memory(key: str, value: str) -> dict:
    """Store a key-value pair in the agent's persistent memory.

    If the key already exists it will be overwritten.  A timestamp is
    recorded alongside the value.

    Args:
        key:   A unique name for this memory (e.g. 'user_name', 'project_dir').
        value: The value to remember (any string).

    Returns:
        dict confirming the save.
    """
    try:
        store = _load_memory()
        store[key] = {
            "value": value,
            "created_at": datetime.now().isoformat(),
        }
        _save_memory_store(store)
        return {"success": True, "result": f"Saved memory: '{key}'", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def get_memory(key: str) -> dict:
    """Retrieve a value from the agent's persistent memory.

    Args:
        key: The memory key to look up.

    Returns:
        dict with the stored value in ``result``, or an error if the key
        doesn't exist.
    """
    try:
        store = _load_memory()
        if key not in store:
            return {"success": False, "result": None, "error": f"No memory found for key '{key}'"}

        entry = store[key]
        return {
            "success": True,
            "result": {
                "key": key,
                "value": entry["value"],
                "created_at": entry.get("created_at", "unknown"),
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def list_all_memories() -> dict:
    """List every key and value currently in the agent's memory.

    Returns:
        dict with ``result`` containing a list of all stored entries.
    """
    try:
        store = _load_memory()
        entries = []
        for key, entry in store.items():
            entries.append({
                "key": key,
                "value": entry.get("value", ""),
                "created_at": entry.get("created_at", "unknown"),
            })
        return {"success": True, "result": entries, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def clear_memory() -> dict:
    """Delete ALL memories from the agent's persistent store.

    ⚠  This action is irreversible.

    Returns:
        dict confirming the memory was cleared.
    """
    try:
        store = _load_memory()
        count = len(store)
        _save_memory_store({})
        return {"success": True, "result": f"Cleared {count} memories", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for this module."""
    return [
        {
            "name": "save_memory",
            "description": "Store a key-value pair in the agent's persistent memory for later recall.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "A unique name for this memory (e.g. 'user_name', 'favourite_color')."
                    },
                    "value": {
                        "type": "string",
                        "description": "The string value to store."
                    }
                },
                "required": ["key", "value"]
            }
        },
        {
            "name": "get_memory",
            "description": "Retrieve a previously stored value from the agent's persistent memory.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The memory key to look up."
                    }
                },
                "required": ["key"]
            }
        },
        {
            "name": "list_all_memories",
            "description": "List every key-value pair currently stored in the agent's memory.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "clear_memory",
            "description": "Delete ALL memories from the agent's persistent store. This is irreversible.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
    ]
