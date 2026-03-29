"""
project_setup.py — MCP tool implementation for initializing a new project.

Creates the project folder at F:/Dev/<name>, copies requirements.md,
runs git init, and creates a private GitHub repo via the REST API.
"""

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from tools.config import DEV_ROOT
from tools import state

SCHEMA = {
    "name": "setup_project",
    "description": (
        "Create a new project folder at F:/Dev/<project_name>, copy requirements.md "
        "into it, initialize a git repository, and create a private GitHub repository. "
        "Call this once you have decided on the project name."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "project_name": {
                "type": "string",
                "description": (
                    "Lowercase kebab-case name for the project "
                    "(e.g. 'todo-api', 'chat-dashboard'). "
                    "Must be valid as a GitHub repository name."
                ),
            },
            "requirements": {
                "type": "string",
                "description": "Full contents of the requirements document to copy into the project.",
            },
        },
        "required": ["project_name", "requirements"],
    },
}


def _github_api(method: str, path: str, body: dict | None = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set in .env")
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API {method} {path} → {e.code}: {e.read().decode()}") from e


def execute(input_data: dict[str, Any]) -> str:
    raw_name = input_data["project_name"].strip().lower()
    project_name = re.sub(r"[^a-z0-9-]", "-", raw_name).strip("-")
    requirements_text = input_data.get("requirements", "")

    if not project_name:
        return "Error: project_name is empty after sanitization."

    project_dir = DEV_ROOT / project_name
    lines: list[str] = []

    # Create directory
    project_dir.mkdir(parents=True, exist_ok=True)
    lines.append(f"Created: {project_dir}")

    # Write requirements.md
    if requirements_text:
        (project_dir / "requirements.md").write_text(requirements_text, encoding="utf-8")
        lines.append("Written: requirements.md")

    # Register as active project
    state.set_project_dir(project_dir)
    lines.append(f"Active project set to: {project_dir}")

    # git init
    git_result = subprocess.run(
        ["git", "init"], cwd=project_dir, capture_output=True, text=True
    )
    if git_result.returncode == 0:
        lines.append("git init: success")
    else:
        lines.append(f"git init failed: {git_result.stderr.strip()}")
        return "\n".join(lines)

    # Get GitHub username
    try:
        user = _github_api("GET", "/user")
        github_username = user["login"]
        lines.append(f"Authenticated as: {github_username}")
    except RuntimeError as e:
        lines.append(f"GitHub auth failed: {e}")
        return "\n".join(lines)

    # Create private repo
    try:
        repo = _github_api("POST", "/user/repos", {
            "name": project_name,
            "private": True,
            "auto_init": False,
        })
        clone_url = repo["clone_url"]
        lines.append(f"GitHub repo created: {repo['html_url']}")
    except RuntimeError as e:
        lines.append(f"GitHub repo creation failed: {e}")
        return "\n".join(lines)

    # Set authenticated remote
    token = os.environ.get("GITHUB_TOKEN", "")
    auth_url = clone_url.replace("https://", f"https://x-access-token:{token}@")
    subprocess.run(
        ["git", "remote", "add", "origin", auth_url],
        cwd=project_dir, capture_output=True,
    )
    lines.append(f"Remote set: {clone_url}")
    lines.append(f"\nPROJECT_DIR: {project_dir}")
    return "\n".join(lines)
