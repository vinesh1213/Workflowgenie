try:
    from adk.workflow import Workflow
except ImportError:
    from ..adk.workflow import Workflow

from adk_app.agents import TaskExtractorAgent, PlannerAgent, ReminderAgent, ReporterAgent
from adk_app.tools import ADKCalendarTool, ADKReminderTool
try:
    from state.memory_store import TaskMemory
except Exception:
    # Fallback lightweight in-memory TaskMemory for environments without TinyDB
    class TaskMemory:
        def __init__(self, db_path: str = None, tools: dict = None, llm=None):
            self._tasks = []
            self.tools = tools or {}

        def store_task(self, task: dict):
            self._tasks.append(task)

        def list_tasks(self, include_done: bool = False):
            if include_done:
                return list(self._tasks)
            return [t for t in self._tasks if not t.get("done", False)]

        def clear_db(self):
            self._tasks.clear()

        def clear(self):
            self.clear_db()

        def cleanup_on_startup(self):
            pass


def build_workflow():
    """Construct an ADK Workflow instance that mirrors the original pipeline.

    Pipeline: input -> task_extractor -> planner -> reminder -> reporter -> output
    """
    # Create tools and memory instances
    calendar = ADKCalendarTool()
    reminder = ADKReminderTool()
    tools = {"calendar": calendar, "reminder": reminder}

    memory = TaskMemory(tools=tools)

    # Create agents
    task_agent = TaskExtractorAgent(memory=memory, tools=tools)
    planner_agent = PlannerAgent(memory=memory, tools=tools)
    reminder_agent = ReminderAgent(memory=memory, tools=tools)
    reporter_agent = ReporterAgent(memory=memory, tools=tools)

    # Build workflow steps
    steps = [task_agent, planner_agent, reminder_agent, reporter_agent]

    return Workflow(steps)
