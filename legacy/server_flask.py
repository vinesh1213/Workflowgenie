from flask import Flask, request, jsonify, send_from_directory
import os
import logging
from dotenv import load_dotenv
from workflows.workflow import build_workflow, run
from state.memory_store import TaskMemory
from llm import LLM
from tools.calendar_tool import CalendarTool
from tools.reminder_tool import ReminderTool

# Load .env after module-level imports so import ordering rules are preserved.
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask("workflowgenie")

    logger.info("Flask server startup: initializing LLM, tools and memory")
    llm = LLM()
    calendar = CalendarTool()
    reminder = ReminderTool()
    tools = {"calendar": calendar, "reminder": reminder}
    memory = TaskMemory(tools=tools, llm=llm)
    memory.cleanup_on_startup()
    workflow = build_workflow()

    app.config["llm"] = llm
    app.config["tools"] = tools
    app.config["memory"] = memory
    app.config["workflow"] = workflow

    @app.route("/", methods=["GET"])
    def root():
        try:
            static_path = os.path.join(app.root_path, "static", "index.html")
            if os.path.exists(static_path):
                return send_from_directory("static", "index.html")
        except Exception:
            pass

        return jsonify({
            "message": "WorkFlowGenie API",
            "endpoints": {
                "GET /health": "Health check",
                "POST /run": "Run workflow (body: {\"text\": \"...\"})",
                "GET /tasks": "List tasks (query: ?include_done=true)",
                "POST /tasks/<id>/done": "Mark task done",
                "GET /events": "List calendar events",
                "GET /reminders": "List reminders"
            }
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/run", methods=["POST"])
    def run_endpoint():
        data = request.get_json(force=True)
        text = data.get("text") if data else None
        if not text:
            return jsonify({"error": "missing 'text' in body"}), 400
        
        calendar = CalendarTool()
        reminder = ReminderTool()
        tools = {"calendar": calendar, "reminder": reminder}
        memory = TaskMemory(tools=tools, llm=app.config.get("llm"))
        memory.cleanup_on_startup()
        workflow = app.config.get("workflow")
        
        try:
            result = run(workflow, memory=memory, inputs={"text": text})
            # Result captured; DB already cleared by workflow.run()
            calendar.clear_events()
            reminder.clear_reminders()
            return jsonify({"ok": True, "result": result})
        except Exception as e:
            logger.exception("Workflow run failed")
            try:
                calendar.clear_events()
                reminder.clear_reminders()
            except Exception:
                pass
            return jsonify({"error": str(e)}), 500

    @app.route("/tasks", methods=["GET"])
    def tasks():
        include_done = request.args.get("include_done", "false").lower() in ("1", "true", "yes")
        memory: TaskMemory = app.config.get("memory")
        return jsonify({"tasks": memory.list_tasks(include_done=include_done)})

    @app.route("/tasks/<int:task_id>/done", methods=["POST"])
    def mark_done(task_id):
        memory: TaskMemory = app.config.get("memory")
        memory.mark_done(task_id)
        return jsonify({"ok": True})

    @app.route("/events", methods=["GET"])
    def events():
        tools = app.config.get("tools")
        return jsonify({"events": tools["calendar"].list_events()})

    @app.route("/reminders", methods=["GET"])
    def reminders():
        tools = app.config.get("tools")
        return jsonify({"reminders": tools["reminder"].list_reminders()})

    @app.route("/clear_db", methods=["POST"])
    def clear_db():
        from state.memory_store import TaskMemory
        mem = TaskMemory()
        mem.clear_db()
        return jsonify({"status": "ok", "message": "Database cleared"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
