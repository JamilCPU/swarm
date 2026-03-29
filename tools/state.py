"""
state.py — Persists the current project directory between MCP tool calls.

setup_project writes here. All git tools read from here.
"""
from pathlib import Path

_STATE_FILE = Path(__file__).parent.parent / ".swarm_project"


def get_project_dir() -> Path:
    if not _STATE_FILE.exists():
        raise RuntimeError(
            "No active project. Call setup_project first."
        )
    path = Path(_STATE_FILE.read_text(encoding="utf-8").strip())
    if not path.exists():
        raise RuntimeError(f"Project directory no longer exists: {path}")
    return path


def set_project_dir(path: Path) -> None:
    _STATE_FILE.write_text(str(path), encoding="utf-8")
