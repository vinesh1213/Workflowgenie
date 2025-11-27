"""
Demo: Show exact prompt strings sent to LLM for a sample /run request.
This demonstrates the template substitution and JSON contract enforcement.

Usage:
    python demo_prompt_strings.py
"""

import json
from agents.planner_agent import PLANNER_PROMPT


def demo_exact_prompts():
    """Show the exact prompt strings sent to each agent."""
    
    print("\n" + "="*80)
    print("DEMO: EXACT PROMPT STRINGS SENT TO LLM")
    print("="*80)
    
    # Sample user input
    user_input = "Send internship form by tomorrow, read React docs, prepare presentation for Friday"
    
    print(f"\n📝 USER INPUT: {user_input}")
    print("\n" + "-"*80)
    
    # ============================================================================
    # AGENT 1: TASK EXTRACTOR
    # ============================================================================
    print("\n[1] TASK EXTRACTOR AGENT")
    print("-" * 80)
    
    task_extractor_prompt = """You MUST respond with ONLY a valid JSON array. No other text, no markdown, no explanations.

Return exactly this format:
[
  {"title": "task name", "due": "ISO date/time or null", "priority": "High|Medium|Low"},
  ...
]

Extract tasks from this text:
""" + user_input
    
    print("PROMPT SENT TO LLM:")
    print(task_extractor_prompt)
    print("\n✅ Expected JSON output structure (strict contract):")
    print(json.dumps([
        {"title": "Send internship form", "due": "2025-11-26T23:59:59", "priority": "High"},
        {"title": "Read React docs", "due": "2025-11-28T23:59:59", "priority": "Medium"},
        {"title": "Prepare presentation", "due": "2025-11-28T23:59:59", "priority": "High"}
    ], indent=2))
    
    # ============================================================================
    # AGENT 2: PLANNER (Shows template substitution)
    # ============================================================================
    print("\n" + "-"*80)
    print("\n[2] PLANNER AGENT (Template Substitution)")
    print("-" * 80)
    
    # Mock tasks that would come from memory after task_extractor runs
    mock_tasks = [
        {
            "id": 1732560000000,
            "title": "Send internship form",
            "created_at": "2025-11-25T10:00:00.000000",
            "due": "2025-11-26T23:59:59",
            "priority": "High",
            "done": False
        },
        {
            "id": 1732560001000,
            "title": "Read React docs",
            "created_at": "2025-11-25T10:00:01.000000",
            "due": "2025-11-28T23:59:59",
            "priority": "Medium",
            "done": False
        },
        {
            "id": 1732560002000,
            "title": "Prepare presentation",
            "created_at": "2025-11-25T10:00:02.000000",
            "due": "2025-11-28T23:59:59",
            "priority": "High",
            "done": False
        }
    ]
    
    print("TEMPLATE (with escaped braces to prevent format() conflicts):")
    print(PLANNER_PROMPT)
    
    print("\n" + "="*80)
    print("RUNTIME SUBSTITUTION")
    print("="*80)
    print("\nCode: prompt = PLANNER_PROMPT.format(tasks_json=json.dumps(tasks, indent=2))")
    print("\nTasks JSON being injected:")
    tasks_json_str = json.dumps(mock_tasks, indent=2)
    print(tasks_json_str)
    
    print("\n" + "="*80)
    print("FINAL PROMPT SENT TO LLM (after substitution):")
    print("="*80)
    final_planner_prompt = PLANNER_PROMPT.format(tasks_json=tasks_json_str)
    print(final_planner_prompt)
    
    print("\n✅ Expected JSON output structure (strict contract):")
    print(json.dumps({
        "events": [
            {
                "title": "Send internship form",
                "start_time": "2025-11-26T09:00:00",
                "duration_mins": 30,
                "notes": "High priority - deadline today"
            },
            {
                "title": "Read React docs",
                "start_time": "2025-11-27T14:00:00",
                "duration_mins": 120,
                "notes": "Medium priority"
            },
            {
                "title": "Prepare presentation",
                "start_time": "2025-11-28T10:00:00",
                "duration_mins": 90,
                "notes": "High priority - Friday presentation"
            }
        ],
        "assumptions": [
            "Assumed work hours 09:00-17:00",
            "High priority tasks scheduled earlier in day",
            "Medium priority tasks scheduled in afternoon"
        ]
    }, indent=2))
    
    # ============================================================================
    # AGENT 3: REMINDER AGENT (Logic-based, no LLM)
    # ============================================================================
    print("\n" + "-"*80)
    print("\n[3] REMINDER AGENT (No LLM - Logic-based)")
    print("-" * 80)
    print("""
This agent doesn't call LLM. Instead, it:
1. Reads tasks from memory
2. Checks: is task due within 2 days from now?
3. If yes: create reminder 1 hour before due_time
4. Return reminders list

Expected output structure:
""")
    print(json.dumps({
        "reminders": [
            {
                "id": "uuid-1234",
                "task_id": 1732560000000,
                "remind_at": "2025-11-26T22:59:59",
                "task_title": "Send internship form"
            },
            {
                "id": "uuid-5678",
                "task_id": 1732560001000,
                "remind_at": "2025-11-28T22:59:59",
                "task_title": "Read React docs"
            }
        ]
    }, indent=2))
    
    # ============================================================================
    # AGENT 4: REPORTER AGENT (LLM + Memory)
    # ============================================================================
    print("\n" + "-"*80)
    print("\n[4] REPORTER AGENT")
    print("-" * 80)
    
    reporter_prompt = """You MUST respond with ONLY a valid JSON object. No other text, no markdown, no explanations.

Return exactly this format:
{
    "summary": "brief summary of workflow",
    "completed_count": <number>,
    "pending_count": <number>,
    "top_actions": ["action 1", "action 2"]
}

Based on these tasks and events, create a brief report:

Tasks:
""" + json.dumps(mock_tasks, indent=2) + """

Your report:"""
    
    print("PROMPT SENT TO LLM:")
    print(reporter_prompt)
    
    print("\n✅ Expected JSON output structure (strict contract):")
    print(json.dumps({
        "summary": "Extracted 3 tasks: 2 high-priority (form & presentation) due within 3 days, 1 medium-priority (React docs). Scheduled across 3 days.",
        "completed_count": 0,
        "pending_count": 3,
        "top_actions": [
            "Complete internship form by tomorrow (2025-11-26)",
            "Block 2 hours for React docs study (2025-11-27)",
            "Prepare presentation slides (2025-11-28)"
        ]
    }, indent=2))
    
    # ============================================================================
    # FULL WORKFLOW PIPELINE
    # ============================================================================
    print("\n" + "="*80)
    print("FULL WORKFLOW PIPELINE")
    print("="*80)
    print("""
POST /run → user_input="Send internship form by tomorrow..."
    ↓
[1] TaskExtractorAgent.llm(prompt)
    Input: "Extract tasks from this text: ..."
    Output JSON: [{"title": "...", "due": "...", "priority": "..."}]
    Stores in memory.store_task(task)
    Returns: {"added": [task1, task2, task3]}
    ↓
[2] PlannerAgent.llm(PLANNER_PROMPT.format(tasks_json=...))
    Input: Template with actual task JSON injected
    Output JSON: {"events": [...], "assumptions": [...]}
    Calls: calendar_tool.add_event() for each event
    Returns: {"events": [...], "assumptions": [...]}
    ↓
[3] ReminderAgent (no LLM)
    Reads: memory.list_tasks()
    Logic: Find tasks due within 2 days
    Calls: reminder_tool.create_reminder(task_id, remind_at)
    Returns: {"reminders": [...]}
    ↓
[4] ReporterAgent.llm(prompt)
    Input: "Based on these tasks and events, create a report..."
    Output JSON: {"summary": "...", "completed_count": N, ...}
    Returns: {"summary": "...", ...}
    ↓
Flask endpoint collects: {
    "task_extractor_agent": {"added": [...]},
    "planner_agent": {"events": [...], "assumptions": [...]},
    "reminder_agent": {"reminders": [...]},
    "reporter_agent": {"summary": "...", ...}
}
    ↓
Clears: calendar.clear_events() + reminder.clear_reminders() + memory.clear_db()
    ↓
Returns JSON response to UI
""")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print("\nKey insights:")
    print("1. Task Extractor: Direct string concatenation for simplicity")
    print("2. Planner: TEMPLATE substitution with escaped braces {{ }} to protect JSON structure")
    print("3. Reminder: Pure Python logic, no LLM call")
    print("4. Reporter: Direct string concatenation")
    print("5. All agents enforce strict JSON contracts via prompts + safe_parse_json()")


if __name__ == "__main__":
    demo_exact_prompts()
