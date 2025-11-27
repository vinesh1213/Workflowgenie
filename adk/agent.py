from typing import Any, Dict


class Agent:
    """Minimal Agent base class shim.

    Real ADK provides richer features; this shim implements the async
    `run(self, input: dict, session)` signature used by Agent Engine.
    """

    def __init__(self, name: str = "agent"):
        self.name = name

    async def run(self, input: Dict[str, Any], session: Any):
        """Override in subclasses.

        Returns a JSON-serializable value.
        """
        raise NotImplementedError()
