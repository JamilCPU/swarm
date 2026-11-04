# Swarm

A multi-agent software build pipeline that runs inside Claude Code. You give it a requirements document; a "conductor" session works through a series of role-specific agents (planner, architect, coder, reviewer and so on), each in its own isolated context, and the result is committed to a new private GitHub repository. Claude Code itself is the runtime, so no separate orchestration process or Anthropic API key is needed.

## Stack

- Python 3 with the MCP Python SDK (`FastMCP`) and `python-dotenv`
- Claude Code as the orchestrator, using Agent tool calls per phase
- Markdown role definitions for each agent
- GitHub REST API and the `gh` CLI for repo creation

## How it works

1. `agents/conductor.md` defines the pipeline rules. The conductor session reads it, picks a pipeline for the project type (REST API, full-stack web app, CLI or library, simple script) and spawns one agent per phase.
2. Each phase agent is given the contents of its `agents/<role>.md` file plus the project directory and a summary of earlier phases.
3. A small MCP server (`mcp_server.py`) exposes project setup and git operations to the conductor and its sub-agents:

| Tool | Purpose |
|------|---------|
| `setup_project(project_name, requirements)` | Create the project folder, write `requirements.md`, `git init`, create a private GitHub repo |
| `get_project_dir()` | Return the active project path |
| `git_status`, `git_diff`, `git_add`, `git_commit`, `git_push`, `git_log` | Git operations on the active project |

`skill.md` describes a `/swarm` skill that triggers the pipeline.

## Running

```bash
pip install -r requirements.txt
cp .env.example .env            # then set GITHUB_TOKEN
claude mcp add swarm -- python <path-to-swarm>/mcp_server.py
```

Then, in Claude Code, ask it to build a project from a requirements file or description (see `CLAUDE.md`). `setup_project` needs a `GITHUB_TOKEN` in `.env`; `gh` should be authenticated for the repo-creation step used by the setup agent. `.mcp.json` registers the server for this directory; replace the `<path-to-swarm>` placeholder with the absolute path to your clone.

## Project layout

```
agents/              conductor, setup, planner, architect, coder, reviewer, fixer, finalize
agents/specialized/  backend, frontend, database, testing, playwright, devops, documentation
tools/               project setup, git helpers, active-project state
mcp_server.py        MCP server entry point
skill.md, CLAUDE.md  skill and session instructions for Claude Code
```

## Status

Work in progress and tailored to the author's machine: the project root is hard-coded to `F:/Dev` in `tools/config.py`, and the agent and skill documents reference `F:/Dev/Swarm`. Change these to match your setup before use. There are no automated tests.
