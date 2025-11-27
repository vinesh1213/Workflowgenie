from typing import Dict, Any
from datetime import datetime
import logging
from utils import extract_json_array

logger = logging.getLogger(__name__)


async def task_extractor_agent(inputs: Dict[str, Any], memory, tools: Dict, llm) -> Dict:
    text = inputs.get("text", "")

    prompt = """You MUST respond with ONLY a valid JSON array. No other text, no markdown, no explanations.

Return exactly this format:
[
  {"title": "task name", "due": "ISO date/time or null", "priority": "High|Medium|Low"},
  ...
]

CRITICAL RULES:
- If the task text mentions duration (e.g., "30 minutes", "2 hours", "1.5 hours"), INCLUDE IT IN THE TASK TITLE
- If the task text mentions a deadline or date, extract it to the "due" field
- Preserve all time/duration information in the title if not explicitly a deadline

Extract tasks from this text:
""" + text

    # Use async LLM
    raw = await llm.generate(prompt, temperature=0.0, max_tokens=512)
    logger.info("TaskExtractor LLM output: %s", raw)

    tasks_json = extract_json_array(raw, default=[])

    tasks = []
    for task_obj in tasks_json:
        if not isinstance(task_obj, dict):
            continue

        title = (task_obj.get("title") or "").strip()
        if not title:
            continue

        due = task_obj.get("due")
        if due and isinstance(due, str):
            due = due.strip() if due.strip().lower() not in ("null", "none", "n/a") else None

        priority = task_obj.get("priority", "Medium")
        if priority not in ("High", "Medium", "Low"):
            priority = "Medium"

        task = {
            "id": int(datetime.utcnow().timestamp() * 1000),
            "title": title,
            "created_at": datetime.utcnow().isoformat(),
            "due": due,
            "priority": priority,
            "done": False,
        }

        if hasattr(memory, 'store_task'):
            # TinyDB operations are blocking; run in a thread
            import asyncio
            await asyncio.to_thread(memory.store_task, task)
        tasks.append(task)

    return {"added": tasks}