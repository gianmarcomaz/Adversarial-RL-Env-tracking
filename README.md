# Apollo Commitments-Tracking Eval

This repo contains a Harbor knowledge-work eval where an agent reads a simulated Slack workspace and reconciles commitments onto a task board.

## Repo Layout

- `services/slack.py` - Slack-like service with the 7 required tools: `list_channels`, `get_channel_messages`, `post_message` with thread support, `update_message`, `add_reaction`, `create_channel`, and `search_messages`.
- `services/tasks.py` - Task Manager service with the 5 required tools: `create_task`, `get_task`, `delete_task`, `list_tasks`, and `update_task`.
- `services/cli.py` - Command-line wrapper used by Harbor agents through `slack` and `tasks`.
- `seed.py` - Builds the seeded workspace state.
- `tasks/commitments-tracking/` - Harbor task package with `instruction.md`, Docker environment, oracle solution, and deterministic verifier.
- `jobs/` - Recorded Harbor runs and `result.json` outputs.
- `make_writeup.py` - Regenerates the figures, `.docx` write-up, and `.html` copy.
- `analysis/` - Small helper scripts for summarizing runs.

## Completeness

- Slack service: all 7 required tools are implemented in both the root service and Harbor environment copy.
- Task Manager service: all 5 required tools are implemented; tasks contain `task_id`, `title`, `description`, `assignee`, and `status`.
- Runtime: Python 3.11+ compatible; the Harbor Dockerfile uses `python:3.11-slim`.
- Secrets: `.env` is ignored by git and Docker context.

## Setup

Install Harbor and put your OpenRouter key in `.env`:

```bash
uv tool install harbor
echo "OPENROUTER_API_KEY=..." > .env
```

## Reproduce Runs

The write-up metrics are computed from these recorded Harbor outputs:

- Target run: `jobs/2026-06-16__19-22-34/result.json`
- Comparison run: `jobs/2026-06-16__19-41-52/result.json`

Oracle:

```bash
harbor run -p tasks/commitments-tracking -a oracle --env-file .env --force-build
```

Target model, Gemma 4 26B:

```bash
harbor run -p tasks/commitments-tracking -a terminus-2 -m openrouter/google/gemma-4-26b-a4b-it --n-attempts 10 -n 1 --max-retries 6 --env-file .env
```

Comparison model, Gemma 4 31B:

```bash
harbor run -p tasks/commitments-tracking -a terminus-2 -m openrouter/google/gemma-4-31b-it --n-attempts 10 -n 1 --max-retries 6 --env-file .env
```

Regenerate the write-up and figures:

```bash
python make_writeup.py
```
