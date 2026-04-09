"""
system.py — OS-level system tools for the Jarvis AI agent.

Provides helpers to launch applications, execute shell commands,
query hardware / OS information, and terminate running processes.
All functions are Windows-first but degrade gracefully on other platforms.
"""

import os
import platform
import subprocess
import shutil

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False
    print("[system] ⚠  psutil not installed — get_system_info() and kill_process() "
          "will have reduced functionality.  pip install psutil")


# ── Public Tool Functions ────────────────────────────────────────────────────

def open_application(app_name: str) -> dict:
    """Launch an application by name (e.g. 'notepad', 'chrome', 'calc').

    On Windows the function tries ``os.startfile`` first, then falls back to
    ``subprocess.Popen``.  On other OSes it uses ``subprocess.Popen`` directly.

    Args:
        app_name: Executable name or full path (e.g. 'notepad', 'code').

    Returns:
        dict with keys ``success``, ``result``, ``error``.
    """
    try:
        if platform.system() == "Windows":
            # os.startfile works for registered names (notepad, calc, mspaint…)
            try:
                os.startfile(app_name)
            except OSError:
                # Fall back to PATH-based launch
                subprocess.Popen(app_name, shell=True)
        else:
            subprocess.Popen(app_name, shell=True)
        return {"success": True, "result": f"Launched '{app_name}'", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def run_command(cmd: str) -> dict:
    """Execute a shell command and capture its stdout / stderr.

    The command runs synchronously with a 60-second timeout.

    Args:
        cmd: The shell command string to execute.

    Returns:
        dict with ``result`` containing stdout text on success.
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return {"success": True, "result": result.stdout.strip(), "error": None}
        else:
            return {
                "success": False,
                "result": result.stdout.strip(),
                "error": result.stderr.strip() or f"Exit code {result.returncode}",
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Command timed out after 60 seconds"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def get_system_info() -> dict:
    """Gather a snapshot of OS, CPU, RAM, and disk information.

    Uses ``psutil`` when available for richer data; falls back to
    ``platform`` and ``shutil`` otherwise.

    Returns:
        dict with ``result`` containing a sub-dict of system metrics.
    """
    try:
        info: dict = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
        }

        if _PSUTIL_AVAILABLE:
            mem = psutil.virtual_memory()
            info["cpu_count_physical"] = psutil.cpu_count(logical=False)
            info["cpu_count_logical"] = psutil.cpu_count(logical=True)
            info["cpu_percent"] = psutil.cpu_percent(interval=0.5)
            info["ram_total_gb"] = round(mem.total / (1024 ** 3), 2)
            info["ram_used_gb"] = round(mem.used / (1024 ** 3), 2)
            info["ram_percent"] = mem.percent

            # Disk info for the main partition
            disk = psutil.disk_usage("/")
            info["disk_total_gb"] = round(disk.total / (1024 ** 3), 2)
            info["disk_used_gb"] = round(disk.used / (1024 ** 3), 2)
            info["disk_free_gb"] = round(disk.free / (1024 ** 3), 2)
            info["disk_percent"] = disk.percent
        else:
            # Minimal fallback using shutil
            total, used, free = shutil.disk_usage("/")
            info["disk_total_gb"] = round(total / (1024 ** 3), 2)
            info["disk_used_gb"] = round(used / (1024 ** 3), 2)
            info["disk_free_gb"] = round(free / (1024 ** 3), 2)

        return {"success": True, "result": info, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def kill_process(name: str) -> dict:
    """Terminate all processes matching *name* (case-insensitive).

    Requires ``psutil``.  Falls back to ``taskkill`` on Windows if psutil is
    not installed.

    Args:
        name: Process name (e.g. 'chrome.exe', 'notepad.exe').

    Returns:
        dict with ``result`` listing how many processes were killed.
    """
    try:
        killed = 0
        if _PSUTIL_AVAILABLE:
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] and proc.info["name"].lower() == name.lower():
                    proc.terminate()
                    killed += 1
        elif platform.system() == "Windows":
            # Fallback: use taskkill
            res = subprocess.run(
                f"taskkill /IM {name} /F",
                shell=True, capture_output=True, text=True,
            )
            if res.returncode == 0:
                killed = 1  # taskkill doesn't report exact count easily
            else:
                return {"success": False, "result": None, "error": res.stderr.strip()}
        else:
            res = subprocess.run(
                f"pkill -f {name}", shell=True, capture_output=True, text=True,
            )
            killed = 1 if res.returncode == 0 else 0

        if killed > 0:
            return {"success": True, "result": f"Killed {killed} process(es) matching '{name}'", "error": None}
        else:
            return {"success": False, "result": None, "error": f"No running process found matching '{name}'"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for every function in this module.

    Returns:
        A list of tool-definition dicts.
    """
    return [
        {
            "name": "open_application",
            "description": "Launch an application by name or path on the local system (e.g. 'notepad', 'chrome', 'calc').",
            "input_schema": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Executable name or full path of the application to launch."
                    }
                },
                "required": ["app_name"]
            }
        },
        {
            "name": "run_command",
            "description": "Execute a shell command on the local system and return its stdout/stderr output. Timeout is 60 seconds.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "The shell command string to execute."
                    }
                },
                "required": ["cmd"]
            }
        },
        {
            "name": "get_system_info",
            "description": "Gather OS, CPU, RAM, and disk information about the local machine.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "kill_process",
            "description": "Terminate all running processes that match the given name (case-insensitive).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Process name to kill (e.g. 'chrome.exe', 'notepad.exe')."
                    }
                },
                "required": ["name"]
            }
        },
    ]
