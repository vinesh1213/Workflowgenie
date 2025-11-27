from typing import Any, Dict, List


class Workflow:
    """Minimal Workflow shim.

    A simple sequential workflow runner that executes `agents` in order.
    Each agent is expected to implement an async `run(input, session)`.
    """

    def __init__(self, steps: List[Any]):
        self.steps = steps

    async def run(self, inputs: Dict[str, Any], session: Dict[str, Any] | None = None) -> Dict[str, Any]:
        session = session or {}
        data = inputs
        for step in self.steps:
            # agent may be an object with async run
            if hasattr(step, "run"):
                result = await step.run(data, session)
            elif callable(step):
                # allow plain async functions
                result = await step(data, session)
            else:
                raise RuntimeError("Invalid workflow step: %r" % (step,))

            # normalize result into dict passed to next step
            if isinstance(result, dict):
                data = result
            else:
                data = {"result": result}

        return data


async def run_workflow(workflow: Workflow, inputs: Dict[str, Any], session: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return await workflow.run(inputs, session=session)
