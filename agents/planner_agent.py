from typing import Dict, Any
from datetime import datetime
import json
import logging
import re
from utils import safe_parse_json
import asyncio
import inspect

logger = logging.getLogger(__name__)


def extract_duration_from_title(title: str) -> tuple[str, int | None]:
    """Extract duration from task title. Returns (clean_title, duration_mins or None)."""
    minutes_match = re.search(r'\s+(?:for\s+)?(\d+(?:\.\d+)?)\s+(?:mins?|minutes)\b', title, re.IGNORECASE)
    if minutes_match:
        mins = int(float(minutes_match.group(1)))
        clean_title = re.sub(r'\s+(?:for\s+)?\d+(?:\.\d+)?\s+(?:mins?|minutes)\b', '', title, flags=re.IGNORECASE).strip()
        return clean_title or title, mins
    
    hours_match = re.search(r'\s+(?:for\s+)?(\d+(?:\.\d+)?)\s+(?:hrs?|hours)\b', title, re.IGNORECASE)
    if hours_match:
        hours = float(hours_match.group(1))
        mins = int(hours * 60)
        clean_title = re.sub(r'\s+(?:for\s+)?\d+(?:\.\d+)?\s+(?:hrs?|hours)\b', '', title, flags=re.IGNORECASE).strip()
        return clean_title or title, mins
    
    return title, None
PLANNER_PROMPT = """
You are a scheduling agent. You MUST respond with ONLY a valid JSON object. No other text, no markdown, no explanations.

Return exactly this format (all times in ISO 8601, durations in minutes):
{{
    "events": [
        {{"title": "event name", "start_time": "2025-11-25T09:00:00", "duration_mins": 60, "notes": ""}},
        ...
    ],
    "assumptions": ["assumption 1", "assumption 2"]
}}

CRITICAL INSTRUCTION: If a task contains "_user_specified_duration_mins", you MUST use that exact duration.

Tasks input:
{tasks_json}
"""


async def planner_agent(inputs: Dict[str, Any], memory, tools: Dict, llm) -> Dict:
    # memory.list_tasks is blocking (TinyDB); run in thread
    tasks = await asyncio.to_thread(memory.list_tasks)

    task_duration_map = {}
    tasks_with_durations = []
    for task in tasks:
        clean_title, extracted_duration = extract_duration_from_title(task.get('title', ''))
        task_copy = task.copy()
        task_copy['title'] = clean_title
        if extracted_duration is not None:
            task_copy['_user_specified_duration_mins'] = extracted_duration
            task_duration_map[clean_title] = extracted_duration
        tasks_with_durations.append(task_copy)

    prompt = PLANNER_PROMPT.format(tasks_json=json.dumps(tasks_with_durations, indent=2))

    response_text = await llm.generate(prompt, temperature=0.0, max_tokens=512)
    logger.info("Planner LLM output: %s", response_text)

    plan_obj = safe_parse_json(response_text, default={"events": [], "assumptions": []})
    if not isinstance(plan_obj, dict):
        plan_obj = {"events": [], "assumptions": []}

    events_list = plan_obj.get("events", [])
    if not isinstance(events_list, list):
        events_list = []

    events = []
    for ev_obj in events_list:
        if not isinstance(ev_obj, dict):
            continue

        title = (ev_obj.get("title") or "").strip()
        if not title:
            continue

        start_time = ev_obj.get("start_time", datetime.utcnow().isoformat())

        duration_mins = ev_obj.get("duration_mins", None)
        if duration_mins is None or not isinstance(duration_mins, int):
            try:
                duration_mins = int(duration_mins) if duration_mins is not None else None
            except (ValueError, TypeError):
                duration_mins = None

        if duration_mins is None and title in task_duration_map:
            duration_mins = task_duration_map[title]
            logger.info("Using user-specified duration for '%s': %d mins", title, duration_mins)

        if duration_mins is None:
            duration_mins = 60

        notes = ev_obj.get("notes", "")

        event = {
            "title": title,
            "start_time": start_time,
            "duration_mins": duration_mins,
            "notes": notes if isinstance(notes, str) else ""
        }

        if tools and getattr(tools.get('calendar'), 'add_event', None):
            add_fn = tools['calendar'].add_event
            if inspect.iscoroutinefunction(add_fn):
                ev = await add_fn(title=title, start_time=start_time, duration_mins=duration_mins, notes=notes)
            else:
                ev = await asyncio.to_thread(add_fn, title=title, start_time=start_time, duration_mins=duration_mins, notes=notes)
            if isinstance(ev, dict) and 'id' in ev:
                event['id'] = ev['id']
        else:
            import uuid
            event['id'] = str(uuid.uuid4())

        events.append(event)

    return {
        "events": events,
        "assumptions": plan_obj.get("assumptions", [])
    }
