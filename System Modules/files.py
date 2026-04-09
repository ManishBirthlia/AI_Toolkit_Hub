"""
files.py — File-system tools for the Jarvis AI agent.

Provides helpers to read, write, move, delete files and list directory
contents.  Uses ``pathlib`` throughout for clean cross-platform paths.
"""

import os
import shutil
from pathlib import Path


# ── Public Tool Functions ────────────────────────────────────────────────────

def read_file(path: str) -> dict:
    """Read and return the text content of a file.

    Args:
        path: Absolute or relative path to the file.

    Returns:
        dict with the file's text content in ``result``.
    """
    try:
        file_path = Path(path).resolve()
        if not file_path.exists():
            return {"success": False, "result": None, "error": f"File not found: {file_path}"}
        if not file_path.is_file():
            return {"success": False, "result": None, "error": f"Not a file: {file_path}"}

        content = file_path.read_text(encoding="utf-8")
        return {"success": True, "result": content, "error": None}
    except UnicodeDecodeError:
        # Binary file — return size instead
        size = file_path.stat().st_size
        return {
            "success": True,
            "result": f"[Binary file — {size:,} bytes. Cannot display as text.]",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def write_file(path: str, content: str) -> dict:
    """Write text content to a file, creating parent directories if needed.

    Args:
        path:    Destination file path.
        content: Text content to write.

    Returns:
        dict confirming the write.
    """
    try:
        file_path = Path(path).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "result": f"Wrote {len(content):,} characters to {file_path}",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def move_file(src: str, dest: str) -> dict:
    """Move or rename a file or directory.

    Args:
        src:  Source path.
        dest: Destination path.

    Returns:
        dict confirming the operation.
    """
    try:
        src_path = Path(src).resolve()
        dest_path = Path(dest).resolve()

        if not src_path.exists():
            return {"success": False, "result": None, "error": f"Source not found: {src_path}"}

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dest_path))
        return {
            "success": True,
            "result": f"Moved {src_path} → {dest_path}",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def delete_file(path: str) -> dict:
    """Delete a file or an empty directory.

    For safety this function does **not** recursively delete non-empty
    directories.  Use ``shutil.rmtree`` manually if that's needed.

    Args:
        path: Path to the file or empty directory to remove.

    Returns:
        dict confirming deletion.
    """
    try:
        target = Path(path).resolve()
        if not target.exists():
            return {"success": False, "result": None, "error": f"Path not found: {target}"}

        if target.is_file():
            target.unlink()
        elif target.is_dir():
            target.rmdir()  # only works if empty — intentional safety guard
        else:
            return {"success": False, "result": None, "error": f"Unknown path type: {target}"}

        return {"success": True, "result": f"Deleted {target}", "error": None}
    except OSError as exc:
        return {"success": False, "result": None,
                "error": f"Cannot delete (directory not empty?): {exc}"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def list_directory(path: str = ".") -> dict:
    """List all files and sub-directories inside a directory.

    Args:
        path: Directory path (defaults to current working directory).

    Returns:
        dict with ``result`` containing a list of entry dicts, each with
        ``name``, ``type`` ('file' or 'dir'), and ``size`` (bytes, for files).
    """
    try:
        dir_path = Path(path).resolve()
        if not dir_path.exists():
            return {"success": False, "result": None, "error": f"Directory not found: {dir_path}"}
        if not dir_path.is_dir():
            return {"success": False, "result": None, "error": f"Not a directory: {dir_path}"}

        entries = []
        for entry in sorted(dir_path.iterdir()):
            info = {
                "name": entry.name,
                "type": "dir" if entry.is_dir() else "file",
            }
            if entry.is_file():
                info["size"] = entry.stat().st_size
            entries.append(info)

        return {"success": True, "result": entries, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for this module."""
    return [
        {
            "name": "read_file",
            "description": "Read and return the text content of a file at the given path.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file."
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write text content to a file, creating parent directories if needed.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Destination file path."
                    },
                    "content": {
                        "type": "string",
                        "description": "The text content to write to the file."
                    }
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "move_file",
            "description": "Move or rename a file or directory from src to dest.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "src": {
                        "type": "string",
                        "description": "Source file or directory path."
                    },
                    "dest": {
                        "type": "string",
                        "description": "Destination path."
                    }
                },
                "required": ["src", "dest"]
            }
        },
        {
            "name": "delete_file",
            "description": "Delete a file or an empty directory. Will not recursively delete non-empty directories for safety.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file or empty directory to delete."
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "list_directory",
            "description": "List all files and subdirectories inside a directory, with file sizes.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path. Defaults to current working directory."
                    }
                },
                "required": []
            }
        },
    ]
