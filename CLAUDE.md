# Swarm

**Claude Code is the runtime.** This repo provides MCP tools and agent role definitions. You orchestrate the pipeline — no separate Python process or API key needed.

## How to build a project

When the user provides a requirements file or describes a project:

1. **Read `agents/conductor.md`** — it defines the full orchestration rules.
2. **Follow the conductor pipeline** — setup runs as an Agent tool call using Bash to init git and create the GitHub repo, then each build phase runs as an isolated Agent tool call with its own context window.
3. **Each Agent tool call** gets the full contents of the relevant `agents/<phase>.md` pasted into its prompt, along with the project directory and any prior context needed.

Each build phase is an isolated Agent tool call using the phase's MD file as the agent's instructions. No Python subprocess needed — Claude Code orchestrates everything natively.

## MCP tools available

| Tool | What it does |
|---|---|
| `setup_project(project_name, requirements)` | Create F:/Dev/<name>, git init, create GitHub repo |
| `get_project_dir()` | Return the active project path |
| `git_status()` | Working tree status |
| `git_diff(staged?)` | Show unstaged or staged changes |
| `git_add(paths?)` | Stage files (all if no paths given) |
| `git_commit(message)` | Commit staged changes |
| `git_push(branch?)` | Push to remote |
| `git_log(limit?)` | Recent commit history |

The git MCP tools are available to all subagents (they inherit the parent session's MCP context). Subagents can call `git_status`, `git_add`, `git_commit`, `git_push`, etc. directly without any special configuration.

## Agent roles

```
agents/
  conductor.md     ← orchestration rules — read this first
  setup.md         ← project initialization (git init + gh repo create)
  planner.md       ← writes PROJECT_PLAN.md
  architect.md     ← writes ARCHITECTURE.md + scaffolds files
  coder.md         ← full-stack implementation
  reviewer.md      ← code review + fixes
  finalize.md      ← README + git commit + push
  specialized/
    backend.md, frontend.md, database.md
    testing.md, playwright.md, devops.md, documentation.md
```

## Environment

Requires `GITHUB_TOKEN` in `.env` (see `.env.example`) for MCP git tools.
Requires `gh` CLI authenticated for `gh repo create` during setup.
No `ANTHROPIC_API_KEY` needed — Claude Code handles authentication.
