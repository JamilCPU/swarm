# Skill: /swarm

Invoke this skill when the user runs `/swarm` or asks to build a project using the Swarm pipeline.

## Trigger

`/swarm` — optionally followed by a requirements description or file path.

## What This Skill Does

Orchestrates a full multi-agent software build pipeline. Each phase of the build is a separate Agent tool call with its own isolated context window. The conductor (this session) reads each phase's MD file and embeds its full contents into the agent's prompt.

## Steps to Execute

### 1. Gather Requirements

If the user provided requirements inline, use them directly.
If the user provided a file path, read the file at that path.
If neither, ask: "Please provide your project requirements."

### 2. Read the Conductor Rules

Read `F:/Dev/Swarm/agents/conductor.md` in full. This is the authoritative pipeline definition — follow it exactly.

### 3. Run the Pipeline

Follow the pipeline defined in conductor.md:

**a. Setup phase**
- Read `F:/Dev/Swarm/agents/setup.md`
- Derive a project name from the requirements (lowercase kebab-case, 2-4 words)
- Spawn a general-purpose Agent with the setup instructions + project name + requirements
- The setup agent initializes git, writes requirements.md, and creates the GitHub repo via `gh repo create JamilCPU/<name> --private --source . --push`
- Confirm PROJECT_DIR before proceeding

**b. Each build phase**
- Read the corresponding agent MD file from `F:/Dev/Swarm/agents/`
- Spawn a general-purpose Agent with:
  - Full contents of the phase MD file (pasted verbatim)
  - `Project directory: <PROJECT_DIR>`
  - A summary of what prior phases produced
  - A clear directive to read project files and complete the role
- Wait for the agent to complete and capture its result
- Use the result to inform the next phase's prompt

**c. Pipeline selection**
Choose phases based on project type (per conductor.md):
- REST API: setup → planner → architect → backend → database → testing → reviewer → finalize
- Full-stack web app: setup → planner → architect → backend → frontend → database → testing → playwright → reviewer → finalize
- CLI tool or library: setup → planner → architect → coder → testing → documentation → reviewer → finalize
- Simple script: setup → planner → coder → reviewer → finalize

### 4. Completion Report

After all phases finish, write a summary:
- What was built
- How to run it
- GitHub repo URL: `https://github.com/JamilCPU/<project_name>`
- Any issues encountered

## Important Notes

- Read each agent MD file immediately before spawning that agent — embed its full contents in the prompt
- Never skip phases; if a phase fails, report the error and stop
- Pass explicit context between phases — agents have isolated context windows
- MCP git tools (git_status, git_add, git_commit, git_push, git_diff, git_log) are inherited by all subagents
- Do not delete or modify files in `F:/Dev/Swarm/agents/` during a run
