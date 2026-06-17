# Minimal Knowledge Work RL Environment

This repo defines a Harbor task for a small knowledge-work eval over Slack-like messages and a task board.

## Layout

services/slack.py - JSON-backed Slack-like service with channels, messages, threads, reactions, and search.
services/tasks.py - JSON-backed task manager service with create, read, update, delete, and list methods.
services/cli.py - Terminal CLI used by agents through `slack` and `tasks` commands in the Harbor container.
seed.py - Writes the seeded workspace to the configured state file.
tasks/commitments-tracking/ - Harbor task with instruction, Docker environment, oracle solution, and verifier.
analysis/summarize_runs.py - Parses Harbor reward files into pass rates and failed-check counts.
legacy/ - Previous hand-rolled OpenRouter harness, retired from the eval path.
make_writeup.py - Generates the Word write-up and figures.

## Setup

Install Harbor and keep your OpenRouter key in `.env`:

```bash
uv tool install harbor
echo "OPENROUTER_API_KEY=..." > .env
```

## Reproduce

Run the oracle:

```bash
harbor run -p tasks/commitments-tracking -a oracle --env-file .env
```

Run the required target model:

```bash
harbor run -p tasks/commitments-tracking -a terminus-2 -m openrouter/google/gemma-4-26b-a4b-it:free -n 2 --max-retries 2 --env-file .env
```

The comparison model still needs to be confirmed and run after Docker is available.
