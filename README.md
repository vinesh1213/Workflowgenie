# WorkflowGenie

A Multi-Agent Productivity Orchestrator Powered by Gemini

WorkflowGenie is a structured, JSON-first multi-agent system that extracts tasks, plans schedules, generates reminders, and produces weekly summaries using an LLM-backed workflow. It automates personal workflow management and produces deterministic JSON outputs suitable for reliable downstream processing.

---

## 📌 Track Selection (Kaggle Requirement)

**Track:** Concierge Agents
(Category: Agents useful for automating everyday personal workflows)

---

## 📝 Overview

WorkflowGenie takes natural-language instructions such as:

> I need to finish my internship form, study React for 2 hours, and email my professor before 5 PM.

Then the system automatically:

1. Extracts actionable tasks
2. Generates a structured schedule
3. Creates reminders
4. Produces a weekly report
5. Displays everything in a clean web UI

All LLM responses are **strict JSON**, ensuring reliability and predictable automation.

---

## 🧠 Architecture

### **1. Agents (Multi-Agent System)**

WorkflowGenie uses four independent agents, each using strict JSON-only prompts:

* **Task Extractor Agent**
  Converts natural language into structured task objects.

  Example:

  ```json
  [{"title": "...", "due": "ISO or null", "priority": "High|Medium|Low"}]
  ```

* **Planner Agent**
  Generates time-bound schedule events.

  Example:

  ```json
  {
    "events": [
      {
        "title": "...",
        "start_time": "2025-11-25T09:00:00",
        "duration_mins": 60,
        "notes": ""
      }
    ],
    "assumptions": []
  }
  ```

* **Reminder Agent**
  Creates reminder entries based on deadlines.

* **Reporter Agent**
  Produces a structured weekly summary.

---

## 🛠 Tools

Located in `/tools/`:

* **CalendarTool** — Stores schedule events
* **ReminderTool** — Stores reminder notifications

Both return and store JSON-only objects.

---

## 💾 Memory System

Located in `/state/memory_store.py`

* Uses **TinyDB** for lightweight persistent storage
* Stores tasks, events, and reminders
* `TaskMemory.clear()` (alias for `clear_db()`) resets all state
* The web UI has a **Clear DB** button for safe database resets

---

## 📐 JSON-First LLM Design

Each agent follows:

* Deterministic, schema-locked prompts
* `temperature=0.0`
* Strict JSON outputs only
* Automatic parsing with `safe_parse_json()`
* JSON repair/extraction on imperfect LLM responses

This guarantees clean UI rendering and predictable downstream execution.

---

## 🧩 ADK Concepts Used (Kaggle Requirements)

Your project includes:

* **✔ Multi-agent orchestration**
* **✔ Agent → Tool interactions**
* **✔ Session storage & persistent memory**
* **✔ Context engineering with JSON-only prompts**
* **✔ Observability via logging**
* **✔ Agent evaluation via JSON schema validation tests**

---

## ⚙ Environment & Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run locally (ADK workflow)

Run the ADK simulation (no external LLM key required — uses deterministic fallback):

```powershell
python -m adk_app.simulate
```

### 3. Legacy web UI (optional)

The original Flask-based web UI has been moved to `legacy/` for archival and local testing. To run it (optional):

```powershell
python legacy/server_flask.py
```

Then open the UI in your browser:

```
http://127.0.0.1:8080
```

### 4. Environment Variables

PowerShell:

```powershell
$env:GEMINI_API_KEY = "your_gemini_api_key"
```

Or create `.env`:

```
GEMINI_API_KEY=your_gemini_api_key
```

### LLM Fallback Behavior

If no `GEMINI_API_KEY` is provided, WorkflowGenie runs in deterministic offline mode.

---

## 🗂 File Structure

```
workflowgenie/
│
├── adk_app/                      # ADK-compatible app (entrypoint: adk_app.main.run)
│   ├── agents.py
│   ├── tools.py
│   ├── workflow.py
│   └── simulate.py
│
├── adk/                          # Local ADK shim for testing
│   ├── agent.py
│   ├── tools.py
│   └── workflow.py
│
├── agents/                       # Agent implementations (async)
│   ├── task_extractor_agent.py
│   ├── planner_agent.py
│   ├── reporter_agent.py
│   └── reminder_agent.py
│
├── tools/
│   ├── calendar_tool.py
│   └── reminder_tool.py
│
├── state/
│   └── memory_store.py
│
├── utils.py
├── llm.py
├── .gitignore
├── requirements.txt
├── README.md
└── legacy/
    └── server_flask.py               # Legacy Flask UI & server  (optional local testing)
```

---

## 🚀 Why It's Valuable

* JSON-only agent outputs
* Clean orchestration using LLM + tools
* Reliable for daily productivity management
* Browser UI for easy interaction
* Fully modular system (agents/tools/memory separable)

---

## 🔮 Future Work

* Google Calendar API integration
* Long-term memory with vector storage
* Multi-day & weekly planner
* Cloud deployment via Cloud Run

---
## 🧾 Submission Summary

```
.gitignore              # Git ignore rules
AUDIT_REPORT.md         # Detailed audit report
Dockerfile              # Docker deployment
README.md               # Project documentation
requirements.txt        # Python dependencies
llm.py                  # LLM wrapper (Gemini + fallback)
utils.py                # Utilities (JSON parsing)  
```
adk/                    # Local ADK shim
```
adk/__init__.py
adk/agent.py                  # Agent base class
adk/tools.py                  # Tool base class
adk/workflow.py               # Workflow orchestrator
```
adk_app/                # ADK application
```
adk_app/__init__.py
adk_app/agents.py                 # ADK Agent wrappers
adk_app/tools.py                  # ADK Tool wrappers
adk_app/workflow.py               # build_workflow()
adk_app/main.py                   # Entry point: async def run()
adk_app/simulate.py               # Local simulation
```
agents/                 # Core agent logic (now async)
```
agents/__init__.py
agents/task_extractor_agent.py   # async def
agents/planner_agent.py          # async def
agents/reminder_agent.py         # async def
agents/reporter_agent.py         # async def
```
tools/                  # Tool implementations
```
tools/__init__.py
tools/calendar_tool.py            # Calendar event store + clear()
tools/reminder_tool.py            # Reminder store + clear()
```
state/                  # State management
```
state/__init__.py
state/memory_store.py           # TinyDB-backed TaskMemory
```
legacy/                 # Archived Flask/web UI
```
legacy/server_flask.py
legacy/static/
    index.html
```
workflows/              # Legacy workflow (for Flask)
```
workflows/__init__.py
workflows/workflow.py            # Agent orchestration pipeline
```