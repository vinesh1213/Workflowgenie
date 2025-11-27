from typing import Dict, Any
import uuid


class ReminderTool:
    """In-memory reminder tool. Stores reminders for tasks."""
    
    def __init__(self):
        self._reminders = []

    def create_reminder(self, task_id: int, remind_at: str) -> Dict[str, Any]:
        """Create a reminder for a task at a specific time."""
        r = {
            "id": str(uuid.uuid4()),
            "task_id": task_id,
            "remind_at": remind_at
        }
        self._reminders.append(r)
        return r

    def list_reminders(self) -> list:
        """Return all reminders."""
        return list(self._reminders)
    
    def clear_reminders(self) -> None:
        """Clear all reminders (for stateless operation)."""
        self._reminders.clear()
