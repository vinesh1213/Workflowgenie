"""ADK entrypoint for Agent Engine deployment.

This module exposes `run(entry_input)` which Agent Engine can call as the
workflow entry point. It also provides a small CLI for local testing.
"""
import asyncio
from typing import Dict, Any
try:
    from adk.workflow import run_workflow
except ImportError:
    from ..adk.workflow import run_workflow

from adk_app.workflow import build_workflow


async def _run_async(inputs: Dict[str, Any]) -> Dict[str, Any]:
    wf = build_workflow()
    # session can carry runtime metadata
    session = {"env": "local"}
    result = await run_workflow(wf, inputs, session=session)
    return result


async def run(request: Dict[str, Any]) -> Dict[str, Any]:
    """Async entrypoint expected by Agent Engine."""
    return await _run_async(request)


def run_sync(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for local invocation. Does NOT override async `run`.

    The Agent Engine expects `async def run(request: dict) -> dict` to be
    importable at module level. We keep a sync helper named `run_sync` for
    convenience when running locally.
    """
    return asyncio.run(_run_async(inputs))


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Input text for the workflow")
    args = parser.parse_args()

    payload = {"text": args.text or ""}
    out = run_sync(payload)
    print(json.dumps(out, indent=2))
