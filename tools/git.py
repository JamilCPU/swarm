"""
git.py — MCP tool implementations for git operations.

All commands run in the active project directory (set by setup_project).
"""

import subprocess
from typing import Any

from tools import state


def _git(args: list[str]) -> str:
    cwd = state.get_project_dir()
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    parts = []
    if result.stdout.strip():
        parts.append(result.stdout.rstrip())
    if result.stderr.strip():
        parts.append(f"stderr: {result.stderr.rstrip()}")
    parts.append(f"exit code: {result.returncode}")
    return "\n".join(parts) if parts else "(no output)"


def execute(name: str, input_data: dict[str, Any]) -> str:
    if name == "git_status":
        return _git(["status"])

    if name == "git_diff":
        args = ["diff"]
        if input_data.get("staged"):
            args.append("--cached")
        return _git(args)

    if name == "git_add":
        paths = input_data.get("paths") or []
        return _git(["add"] + paths if paths else ["add", "-A"])

    if name == "git_commit":
        return _git(["commit", "-m", input_data["message"]])

    if name == "git_push":
        branch = input_data.get("branch", "main")
        return _git(["push", "--set-upstream", "origin", branch])

    if name == "git_log":
        limit = input_data.get("limit", 10)
        return _git(["log", f"-{limit}", "--oneline"])

    return f"Unknown git tool: '{name}'"
