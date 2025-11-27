

class Tool:
    """Minimal Tool shim.

    Subclass and expose methods that tool users will call. Kept intentionally
    small so it maps to the project's existing tool classes (CalendarTool,
    ReminderTool).
    """

    def __init__(self, name: str = "tool"):
        self.name = name
