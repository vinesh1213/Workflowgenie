from typing import Dict, Any
import uuid


class CalendarTool:
    """In-memory calendar tool. Stores events with title, start_time, duration_mins, notes."""
    
    def __init__(self):
        self._calendar = []

    def add_event(self, title: str, start_time: str, duration_mins: int = 60, notes: str = "") -> Dict[str, Any]:
        """Add an event to the calendar."""
        event = {
            "id": str(uuid.uuid4()),
            "title": title,
            "start_time": start_time,
            "duration_mins": duration_mins,
            "notes": notes if isinstance(notes, str) else ""
        }
        self._calendar.append(event)
        return event

    def list_events(self) -> list:
        """Return all events."""
        return list(self._calendar)
    
    def clear_events(self) -> None:
        """Clear all events (for stateless operation)."""
        self._calendar.clear()
