# Commitments Tracking

You are helping a small tech company keep its task board accurate. The Slack workspace has several active channels, and some work may already be represented on the board under slightly different wording.

## Your Task

Review the workspace and task board, then make sure outstanding commitments are represented as actionable tasks with clear titles and the correct owners. Avoid creating duplicate tasks or tasks for FYIs, completed work, hypotheticals, declined asks, or casual discussion.

## Tools available to you

You have terminal commands for a Slack workspace and a task board.

- `slack list_channels`
- `slack get_channel_messages <channel_id_or_name>`
- `slack search_messages <query>`
- `slack post_message <channel_id> <text> [--thread-id <message_id>]`
- `slack update_message <message_id> <text>`
- `slack add_reaction <message_id> <emoji>`
- `slack create_channel <name>`
- `tasks list_tasks`
- `tasks get_task <task_id>`
- `tasks create_task <title> <description> <assignee> <status>`
- `tasks update_task <task_id> [--title <title>] [--description <description>] [--assignee <assignee>] [--status <status>]`
- `tasks delete_task <task_id>`
