from datetime import datetime, timezone

from services.state import load_state, save_state


class SlackService:
    # Initialize empty Slack-like workspace state.
    def __init__(self):
        self.state = load_state()
        self.users = self.state["users"]
        self.channels = self.state["channels"]
        self.messages = self.state["messages"]

    # Persist current Slack state to disk.
    def _save(self):
        latest = load_state()
        for key in ["users", "channels", "messages", "next_channel_id", "next_message_id"]:
            latest[key] = self.state[key]
        save_state(latest)
        self.state = latest
        self.users = self.state["users"]
        self.channels = self.state["channels"]
        self.messages = self.state["messages"]

    # Return all channels in the workspace.
    def list_channels(self):
        return list(self.channels.values())

    # Accept either a channel id or a channel name.
    def get_channel_messages(self, channel_id):
        resolved_id = channel_id
        for cid, channel in self.channels.items():
            if channel["name"] == channel_id:
                resolved_id = cid
                break
        # Return messages for the resolved channel, in insertion order.
        return [m for m in self.messages if m["channel_id"] == resolved_id]

    # Add a message or threaded reply to a channel.
    def post_message(self, channel_id, text, thread_id=None):
        message_id = f"m{self.state['next_message_id']}"
        self.state["next_message_id"] += 1
        message = {
            "id": message_id,
            "channel_id": channel_id,
            "user": "agent",
            "text": text,
            "thread_id": thread_id,
            "reactions": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.messages.append(message)
        self._save()
        return message

    # Replace the text of an existing message.
    def update_message(self, message_id, text):
        for message in self.messages:
            if message["id"] == message_id:
                message["text"] = text
                self._save()
                return message
        return None

    # Add an emoji reaction to an existing message.
    def add_reaction(self, message_id, emoji):
        for message in self.messages:
            if message["id"] == message_id:
                if emoji not in message["reactions"]:
                    message["reactions"].append(emoji)
                    self._save()
                return message
        return None

    # Create a new channel with a readable name.
    def create_channel(self, name):
        channel_id = f"c{self.state['next_channel_id']}"
        self.state["next_channel_id"] += 1
        clean_name = name.lstrip("#")
        channel = {"id": channel_id, "name": clean_name}
        self.channels[channel_id] = channel
        self._save()
        return channel

    # Find messages whose text includes the query.
    def search_messages(self, query):
        query_lower = query.lower()
        return [message for message in self.messages if query_lower in message["text"].lower()]
