---
name: notebooklm
description: NotebookLM CLI wrapper via `node {baseDir}/scripts/notebooklm.mjs`. Use for auth, notebooks, chat, sources, notes, sharing, research, and artifact generation/download including audio podcasts and video explainers.
---

# NotebookLM CLI Wrapper

## Required parameters
- `node` and `notebooklm` available on PATH.
- NotebookLM CLI authenticated (run `login` if needed).

## Quick start
- Wrapper script: `scripts/notebooklm.mjs` (invokes `notebooklm` CLI).
- Run from the skill directory or use an absolute `{baseDir}` path.

```bash
node {baseDir}/scripts/notebooklm.mjs status
node {baseDir}/scripts/notebooklm.mjs login
node {baseDir}/scripts/notebooklm.mjs list
node {baseDir}/scripts/notebooklm.mjs use <notebook_id>
node {baseDir}/scripts/notebooklm.mjs ask "Summarize the key takeaways" --notebook <notebook_id>
```

## Request & output
- Command form: `node {baseDir}/scripts/notebooklm.mjs <command> [args...]`.
- Prefer `--json` for machine-readable output.
- For long-running tasks, use `--exec-timeout <seconds>`; `--timeout` is reserved for wait/poll commands.

## Video Generation

Generate AI-powered video explainers:

```bash
# Generate a video explainer
node {baseDir}/scripts/notebooklm.mjs generate video "Explain the key concepts" --notebook <notebook_id> --style anime

# Download the generated video
node {baseDir}/scripts/notebooklm.mjs download video ./video.mp4 --notebook <notebook_id> --latest
```

**Available styles:** auto, classic, whiteboard, kawaii, anime, watercolor, retro-print, heritage, paper-craft

**Note:** Video generation typically takes 15-45 minutes. For long-running tasks, use subagent mode or check status later with `artifact list`.

## References
- `references/cli-commands.md`

## Assets
- None.
