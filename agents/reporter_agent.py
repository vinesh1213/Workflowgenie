from typing import Dict, Any
import logging
from utils import safe_parse_json
import asyncio

logger = logging.getLogger(__name__)


async def reporter_agent(inputs: Dict[str, Any], memory, tools: Dict, llm) -> Dict:
    tasks = await asyncio.to_thread(memory.list_tasks, True)

    tasks_text = "\n".join([f"- {t['title']} (done={t['done']})" for t in tasks])

    prompt = """You MUST respond with ONLY a valid JSON object. No other text, no markdown, no explanations.

Return exactly this format:
{
  "summary": "Brief summary of the week",
  "completed_count": 5,
  "pending_count": 3,
  "top_actions": ["action 1", "action 2", "action 3"]
}

Create a weekly report from these tasks:
""" + tasks_text

    report_json_text = await llm.generate(prompt, temperature=0.0, max_tokens=512)
    logger.info("Reporter LLM output: %s", report_json_text)

    report_obj = safe_parse_json(report_json_text, default={
        "summary": "No summary available",
        "completed_count": 0,
        "pending_count": 0,
        "top_actions": []
    })

    if not isinstance(report_obj, dict):
        report_obj = {
            "summary": "No summary available",
            "completed_count": 0,
            "pending_count": 0,
            "top_actions": []
        }

    return {
        "summary": report_obj.get("summary", "No summary available"),
        "completed_count": report_obj.get("completed_count", 0),
        "pending_count": report_obj.get("pending_count", 0),
        "top_actions": report_obj.get("top_actions", [])
    }
