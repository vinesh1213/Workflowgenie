"""Local ADK workflow simulator for validation and testing.

Runs the ADK workflow with a test input and performs basic assertions to
validate agent outputs (JSON shapes and expected fields).
"""
import asyncio
import json
from adk_app.workflow import build_workflow


TEST_INPUT = {"text": "Finish report by 5pm, study React 2 hours, walk 30 minutes"}


async def run_sim():
    wf = build_workflow()

    # Run workflow step-by-step to capture each agent's output for debugging.
    data = TEST_INPUT
    step_outputs = []
    for step in wf.steps:
        print(f"Running step: {getattr(step, 'name', repr(step))}")
        out = await step.run(data, session={})
        print("-> Step output:\n", json.dumps(out, indent=2))
        step_outputs.append((getattr(step, 'name', repr(step)), out))
        # pass the agent's dict output as the next input
        data = out if isinstance(out, dict) else {"result": out}

    result = data
    print("Workflow final output:\n", json.dumps(result, indent=2))

    # Basic assertions focused on task extraction (planner/reminder may be empty in fallback)
    if len(step_outputs) < 1:
        raise AssertionError("No steps were executed")

    task_step_name, task_out = step_outputs[0]
    tasks = task_out.get("added") if isinstance(task_out, dict) else None
    if not tasks or not isinstance(tasks, list) or len(tasks) == 0:
        raise AssertionError("Task extractor output missing or empty")

    print(f"Task extractor added {len(tasks)} task(s).")

    # Planner
    if len(step_outputs) > 1:
        _, planner_out = step_outputs[1]
        events = planner_out.get("events") if isinstance(planner_out, dict) else []
        print(f"Planner produced {len(events) if isinstance(events, list) else 0} event(s).")

    # Reminder
    if len(step_outputs) > 2:
        _, reminder_out = step_outputs[2]
        rem_list = reminder_out.get("reminders") if isinstance(reminder_out, dict) else []
        print(f"Reminders created: {len(rem_list)}")

    # Reporter
    if len(step_outputs) > 3:
        _, reporter_out = step_outputs[3]
        print("Reporter output snippet:\n", json.dumps(reporter_out, indent=2))

    print("Simulation assertions passed.")


if __name__ == "__main__":
    asyncio.run(run_sim())
