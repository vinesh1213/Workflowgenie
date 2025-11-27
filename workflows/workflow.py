from typing import Dict, Any
from agents import task_extractor_agent, planner_agent, reminder_agent, reporter_agent


class Workflow:
    """Simple workflow definition."""
    def __init__(self, name: str):
        self.name = name
        self.steps = []  # list of (step_func, step_name) tuples
    
    def set_entrypoint(self, func):
        self.steps = [(func, func.__name__)]
    
    def add_step(self, func):
        self.steps.append((func, func.__name__))


def run(workflow: Workflow, memory: Any, inputs: Dict[str, Any]):
    """Execute workflow: run each step sequentially, collecting outputs.
    
    IMPORTANT: After all steps complete, the database is automatically cleared
    to ensure stateless operation (no leftover state between requests).
    """
    result = {}
    tools = memory.tools if hasattr(memory, 'tools') else {}
    llm = memory.llm if hasattr(memory, 'llm') else None
    
    try:
        for step_func, step_name in workflow.steps:
            try:
                output = step_func(inputs, memory, tools, llm)
                result[step_name] = output
            except Exception as e:
                import logging
                logging.getLogger(__name__).exception(f"Workflow step {step_name} failed: {e}")
                result[step_name] = {"error": str(e)}
    finally:
        # Auto-clear DB after workflow completes (stateless operation)
        if hasattr(memory, 'clear_db'):
            try:
                memory.clear_db()
            except Exception as e:
                import logging
                logging.getLogger(__name__).exception(f"Failed to clear DB after workflow: {e}")
    
    return result


def build_workflow() -> Workflow:
    """Build the WorkFlowGenie workflow."""
    w = Workflow("workflowgenie")
    w.set_entrypoint(task_extractor_agent)
    w.add_step(planner_agent)
    w.add_step(reminder_agent)
    w.add_step(reporter_agent)
    return w
