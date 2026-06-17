from services.state import load_state, save_state


class TaskManagerService:
    # Initialize empty task manager state.
    def __init__(self):
        self.state = load_state()
        self.tasks = self.state["tasks"]

    # Persist current task state to disk.
    def _save(self):
        latest = load_state()
        for key in ["tasks", "next_task_id"]:
            latest[key] = self.state[key]
        save_state(latest)
        self.state = latest
        self.tasks = self.state["tasks"]

    # Create a task and store it in memory.
    def create_task(self, title, description, assignee, status):
        task_id = f"t{self.state['next_task_id']}"
        self.state["next_task_id"] += 1
        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "assignee": assignee,
            "status": status,
        }
        self.tasks[task_id] = task
        self._save()
        return task

    # Return one task by id.
    def get_task(self, task_id):
        return self.tasks.get(task_id)

    # Delete one task by id.
    def delete_task(self, task_id):
        task = self.tasks.pop(task_id, None)
        self._save()
        return task

    # Return all tasks in insertion order.
    def list_tasks(self):
        return list(self.tasks.values())

    # Update known fields on an existing task.
    def update_task(self, task_id, **fields):
        task = self.tasks.get(task_id)
        if task is None:
            return None
        for key, value in fields.items():
            if key in task and key != "task_id":
                task[key] = value
        self._save()
        return task
