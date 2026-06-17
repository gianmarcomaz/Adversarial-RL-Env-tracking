import json
import os
from pathlib import Path


# Return the configured JSON state file path.
def state_path():
    return Path(os.environ.get("WORKSPACE_STATE", "/workspace/state.json"))


# Build an empty workspace state.
def default_state():
    return {
        "users": ["alice", "ben", "carla", "devon"],
        "channels": {},
        "messages": [],
        "next_channel_id": 1,
        "tasks": {},
        "next_task_id": 1,
        "next_message_id": 1,
    }


# Load state from disk or create a fresh state.
def load_state():
    path = state_path()
    if not path.exists():
        return default_state()
    with open(path, encoding="utf-8") as file:
        return json.load(file)


# Save state to disk as JSON.
def save_state(state):
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)


# Replace the state file with a fresh empty state.
def reset_state():
    state = default_state()
    save_state(state)
    return state
