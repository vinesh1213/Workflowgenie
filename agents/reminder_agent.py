from typing import Dict, Any
from datetime import datetime, timedelta
import logging
import dateutil.parser
import asyncio
import inspect

logger = logging.getLogger(__name__)


async def reminder_agent(inputs: Dict[str, Any], memory, tools: Dict, llm) -> Dict:
    tasks = await asyncio.to_thread(memory.list_tasks)
    reminders = []
    now = datetime.utcnow()
    for t in tasks:
        due = t.get('due')
        if not due:
            continue
        try:
            dt = dateutil.parser.parse(due)
            if dt - now < timedelta(days=2):
                remind_at = (dt - timedelta(hours=1)).isoformat()
                if tools and getattr(tools.get('reminder'), 'create_reminder', None):
                    create_fn = tools['reminder'].create_reminder
                    if inspect.iscoroutinefunction(create_fn):
                        r = await create_fn(task_id=t['id'], remind_at=remind_at)
                    else:
                        r = await asyncio.to_thread(create_fn, task_id=t['id'], remind_at=remind_at)
                else:
                    r = {"task_id": t['id'], "remind_at": remind_at}
                reminders.append(r)
        except Exception:
            continue

    return {"reminders": reminders}
