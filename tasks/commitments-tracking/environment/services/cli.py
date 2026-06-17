import argparse
import json

from seed import seed_workspace
from services.slack import SlackService
from services.state import state_path
from services.tasks import TaskManagerService


# Seed the workspace once if no state file exists.
def ensure_seeded():
    if not state_path().exists():
        seed_workspace()


# Print a service result as JSON.
def print_json(result):
    print(json.dumps(result, indent=2))


# Run a Slack command.
def run_slack(args):
    slack = SlackService()
    if args.command == "list_channels":
        result = slack.list_channels()
    elif args.command == "get_channel_messages":
        result = slack.get_channel_messages(args.channel_id)
    elif args.command == "post_message":
        result = slack.post_message(args.channel_id, args.text, args.thread_id)
    elif args.command == "update_message":
        result = slack.update_message(args.message_id, args.text)
    elif args.command == "add_reaction":
        result = slack.add_reaction(args.message_id, args.emoji)
    elif args.command == "create_channel":
        result = slack.create_channel(args.name)
    elif args.command == "search_messages":
        result = slack.search_messages(args.query)
    print_json(result)


# Run a task-board command.
def run_tasks(args):
    tasks = TaskManagerService()
    if args.command == "create_task":
        result = tasks.create_task(args.title, args.description, args.assignee, args.status)
    elif args.command == "get_task":
        result = tasks.get_task(args.task_id)
    elif args.command == "delete_task":
        result = tasks.delete_task(args.task_id)
    elif args.command == "list_tasks":
        result = tasks.list_tasks()
    elif args.command == "update_task":
        fields = {k: v for k, v in vars(args).items() if k in {"title", "description", "assignee", "status"} and v is not None}
        result = tasks.update_task(args.task_id, **fields)
    print_json(result)


# Add Slack subcommands to the parser.
def add_slack_commands(subparsers):
    slack = subparsers.add_parser("slack")
    commands = slack.add_subparsers(dest="command", required=True)
    commands.add_parser("list_channels")
    get_messages = commands.add_parser("get_channel_messages")
    get_messages.add_argument("channel_id")
    post = commands.add_parser("post_message")
    post.add_argument("channel_id")
    post.add_argument("text")
    post.add_argument("--thread-id", default=None)
    update = commands.add_parser("update_message")
    update.add_argument("message_id")
    update.add_argument("text")
    reaction = commands.add_parser("add_reaction")
    reaction.add_argument("message_id")
    reaction.add_argument("emoji")
    create = commands.add_parser("create_channel")
    create.add_argument("name")
    search = commands.add_parser("search_messages")
    search.add_argument("query")
    slack.set_defaults(handler=run_slack)


# Add task-board subcommands to the parser.
def add_task_commands(subparsers):
    tasks = subparsers.add_parser("tasks")
    commands = tasks.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create_task")
    create.add_argument("title")
    create.add_argument("description")
    create.add_argument("assignee")
    create.add_argument("status")
    get = commands.add_parser("get_task")
    get.add_argument("task_id")
    delete = commands.add_parser("delete_task")
    delete.add_argument("task_id")
    commands.add_parser("list_tasks")
    update = commands.add_parser("update_task")
    update.add_argument("task_id")
    update.add_argument("--title")
    update.add_argument("--description")
    update.add_argument("--assignee")
    update.add_argument("--status")
    tasks.set_defaults(handler=run_tasks)


# Parse command-line arguments and dispatch to a service.
def main():
    ensure_seeded()
    parser = argparse.ArgumentParser(description="Knowledge-work service CLI")
    subparsers = parser.add_subparsers(dest="service", required=True)
    add_slack_commands(subparsers)
    add_task_commands(subparsers)
    args = parser.parse_args()
    args.handler(args)


# Run the CLI when called as a script.
if __name__ == "__main__":
    main()
