"""
mcp_server.py — Swarm MCP server.

Exposes project setup and git operations as MCP tools so that
Claude Code can call them directly without a separate API key.

Register with Claude Code:
    claude mcp add swarm -- python "F:/Dev/Swarm/mcp_server.py"
"""

from mcp.server.fastmcp import FastMCP

from tools import project_setup, git as git_tools, state

mcp = FastMCP("swarm")


# ── Project setup ─────────────────────────────────────────────────────────────

@mcp.tool()
def setup_project(project_name: str, requirements: str) -> str:
    """
    Create a new project at F:/Dev/<project_name>, write requirements.md,
    run git init, and create a private GitHub repository.
    Must be called before any git tools.
    """
    return project_setup.execute({
        "project_name": project_name,
        "requirements": requirements,
    })


@mcp.tool()
def get_project_dir() -> str:
    """Return the path of the currently active project directory."""
    try:
        return str(state.get_project_dir())
    except RuntimeError as e:
        return f"Error: {e}"


# ── Git tools ─────────────────────────────────────────────────────────────────

@mcp.tool()
def git_status() -> str:
    """Show the working tree status of the active project repository."""
    return git_tools.execute("git_status", {})


@mcp.tool()
def git_diff(staged: bool = False) -> str:
    """Show changes. Use staged=True to see what is staged for commit."""
    return git_tools.execute("git_diff", {"staged": staged})


@mcp.tool()
def git_add(paths: list[str] | None = None) -> str:
    """Stage files. Pass paths to stage specific files, or omit to stage everything."""
    return git_tools.execute("git_add", {"paths": paths or []})


@mcp.tool()
def git_commit(message: str) -> str:
    """Commit staged changes with a message."""
    return git_tools.execute("git_commit", {"message": message})


@mcp.tool()
def git_push(branch: str = "main") -> str:
    """Push commits to the remote repository."""
    return git_tools.execute("git_push", {"branch": branch})


@mcp.tool()
def git_log(limit: int = 10) -> str:
    """Show recent commit history."""
    return git_tools.execute("git_log", {"limit": limit})


if __name__ == "__main__":
    mcp.run()
