from typing import Dict, Any
try:
    # Prefer installed ADK if available
    from adk.agent import Agent
except ImportError:
    # Fallback to local shim
    from ..adk.agent import Agent

from agents import task_extractor_agent, planner_agent, reminder_agent, reporter_agent
from llm import LLM


class TaskExtractorAgent(Agent):
    def __init__(self, memory, tools):
        super().__init__("task_extractor")
        self.memory = memory
        self.tools = tools
        self.llm = LLM()

    async def run(self, input: Dict[str, Any], session) -> Dict[str, Any]:
        # Call the async agent implementation directly
        return await task_extractor_agent(input, self.memory, self.tools, self.llm)


class PlannerAgent(Agent):
    def __init__(self, memory, tools):
        super().__init__("planner")
        self.memory = memory
        self.tools = tools
        self.llm = LLM()

    async def run(self, input: Dict[str, Any], session) -> Dict[str, Any]:
        return await planner_agent(input, self.memory, self.tools, self.llm)


class ReminderAgent(Agent):
    def __init__(self, memory, tools):
        super().__init__("reminder")
        self.memory = memory
        self.tools = tools
        self.llm = LLM()

    async def run(self, input: Dict[str, Any], session) -> Dict[str, Any]:
        return await reminder_agent(input, self.memory, self.tools, self.llm)


class ReporterAgent(Agent):
    def __init__(self, memory, tools):
        super().__init__("reporter")
        self.memory = memory
        self.tools = tools
        self.llm = LLM()

    async def run(self, input: Dict[str, Any], session) -> Dict[str, Any]:
        return await reporter_agent(input, self.memory, self.tools, self.llm)
