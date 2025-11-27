import asyncio
try:
    from adk.tools import Tool
except ImportError:
    from ..adk.tools import Tool
from tools.calendar_tool import CalendarTool
from tools.reminder_tool import ReminderTool
from typing import Any, Dict


class ADKCalendarTool(Tool):
    def __init__(self):
        super().__init__("calendar")
        self._impl = CalendarTool()

    async def add_event(self, title: str, start_time: str, duration_mins: int = 60, notes: str = "") -> Dict[str, Any]:
        return await asyncio.to_thread(self._impl.add_event, title, start_time, duration_mins, notes)

    async def list_events(self) -> list:
        return await asyncio.to_thread(self._impl.list_events)

    async def clear_events(self) -> None:
        return await asyncio.to_thread(self._impl.clear_events)


class ADKReminderTool(Tool):
    def __init__(self):
        super().__init__("reminder")
        self._impl = ReminderTool()

    async def create_reminder(self, task_id: int, remind_at: str) -> Dict[str, Any]:
        return await asyncio.to_thread(self._impl.create_reminder, task_id, remind_at)

    async def list_reminders(self) -> list:
        return await asyncio.to_thread(self._impl.list_reminders)

    async def clear_reminders(self) -> None:
        return await asyncio.to_thread(self._impl.clear_reminders)
