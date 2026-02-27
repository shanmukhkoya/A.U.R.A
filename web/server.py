"""Flask Web Server — provides a beautiful UI for the Autonomous Agent."""
import os
import sys
import json
import threading
import queue
import time
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.core import AutonomousAgent
from agent.config import Config

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# Global state for the running agent
agent_state = {
    "running": False,
    "agent": None,
    "log_queue": None,
    "report": None,
    "error": None,
    "stop_event": None,
}


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/providers", methods=["GET"])
def get_providers():
    """Return available providers and their models."""
    config = Config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml"))
    
    providers = {
        "ollama": {
            "name": "Ollama (Local)",
            "models": ["llama3", "mistral", "phi3", "gemma2", "llama3.1", "qwen2"],
            "requires_key": False,
            "active_model": config.get("ollama.model", "llama3"),
        },
        "openai": {
            "name": "OpenAI",
            "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            "requires_key": True,
            "active_model": config.get("openai.model", "gpt-4o-mini"),
        },
        "anthropic": {
            "name": "Anthropic",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
            "requires_key": True,
            "active_model": config.get("anthropic.model", "claude-3-5-sonnet-20241022"),
        },
        "google": {
            "name": "Google Gemini",
            "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            "requires_key": True,
            "active_model": config.get("google.model", "gemini-2.0-flash"),
        },
    }
    
    # Check Ollama availability
    try:
        from agent.providers.ollama import OllamaProvider
        ollama = OllamaProvider()
        if ollama.is_available():
            available_models = ollama.list_models()
            if available_models:
                providers["ollama"]["models"] = available_models
            providers["ollama"]["available"] = True
        else:
            providers["ollama"]["available"] = False
    except Exception:
        providers["ollama"]["available"] = False

    return jsonify({
        "providers": providers,
        "active_provider": config.provider_name,
    })


@app.route("/api/run", methods=["POST"])
def run_agent():
    """Start the autonomous agent with the given goal."""
    if agent_state["running"]:
        return jsonify({"error": "Agent is already running"}), 400

    data = request.json
    goal = data.get("goal", "").strip()
    provider = data.get("provider", "ollama")
    model = data.get("model", "")
    depth = data.get("depth", "detailed")

    if not goal:
        return jsonify({"error": "No goal provided"}), 400

    # Create config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    config = Config(config_path)
    config._config["provider"] = provider
    if model:
        if provider not in config._config:
            config._config[provider] = {}
        config._config[provider]["model"] = model
    if "agent" not in config._config:
        config._config["agent"] = {}
    config._config["agent"]["research_depth"] = depth

    # Setup agent
    log_q = queue.Queue()
    stop_event = threading.Event()
    agent_state["log_queue"] = log_q
    agent_state["running"] = True
    agent_state["report"] = None
    agent_state["error"] = None
    agent_state["stop_event"] = stop_event

    def log_callback(phase, message):
        if stop_event.is_set():
            raise InterruptedError("Agent stopped by user")
        log_q.put({"phase": phase, "message": message, "time": time.time()})

    def run_in_thread():
        try:
            agent = AutonomousAgent(config)
            agent.set_log_callback(log_callback)
            agent_state["agent"] = agent
            report = agent.run(goal)
            if not stop_event.is_set():
                filepath = agent.save_report(report)
                agent_state["report"] = {"content": report, "filepath": filepath}
        except InterruptedError:
            log_q.put({"phase": "info", "message": "⏹ Agent stopped by user.", "time": time.time()})
        except Exception as e:
            agent_state["error"] = str(e)
            log_q.put({"phase": "error", "message": f"❌ Error: {e}", "time": time.time()})
        finally:
            agent_state["running"] = False
            log_q.put(None)  # Signal end

    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()

    return jsonify({"status": "started", "goal": goal})


@app.route("/api/stop", methods=["POST"])
def stop_agent():
    """Stop the currently running agent."""
    stop_event = agent_state.get("stop_event")
    if stop_event and agent_state["running"]:
        stop_event.set()
        return jsonify({"status": "stopping"})
    return jsonify({"status": "not_running"}), 400


@app.route("/api/stream")
def stream_logs():
    """SSE endpoint for real-time log streaming."""
    def event_stream():
        log_q = agent_state.get("log_queue")
        if not log_q:
            yield f"data: {json.dumps({'phase': 'error', 'message': 'No active agent'})}\n\n"
            return

        while True:
            try:
                entry = log_q.get(timeout=60)
                if entry is None:
                    # Agent is done
                    if agent_state.get("report"):
                        yield f"data: {json.dumps({'phase': 'done', 'report': agent_state['report']['content'], 'filepath': agent_state['report']['filepath']})}\n\n"
                    elif agent_state.get("error"):
                        yield f"data: {json.dumps({'phase': 'error', 'message': agent_state['error']})}\n\n"
                    break
                yield f"data: {json.dumps(entry)}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'phase': 'heartbeat', 'message': '...'})}\n\n"

    return Response(event_stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/status")
def get_status():
    """Get current agent status."""
    agent = agent_state.get("agent")
    return jsonify({
        "running": agent_state["running"],
        "state": agent.get_status() if agent else None,
        "report": agent_state.get("report"),
        "error": agent_state.get("error"),
    })


@app.route("/api/reports")
def list_reports():
    """List all generated reports."""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    if not os.path.exists(output_dir):
        return jsonify({"reports": []})
    
    reports = []
    for f in sorted(os.listdir(output_dir), reverse=True):
        if f.endswith(".md"):
            filepath = os.path.join(output_dir, f)
            reports.append({
                "filename": f,
                "size": os.path.getsize(filepath),
                "modified": os.path.getmtime(filepath),
            })
    return jsonify({"reports": reports})


@app.route("/api/reports/<filename>")
def get_report(filename):
    """Get a specific report's content."""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return jsonify({"content": f.read(), "filename": filename})
    return jsonify({"error": "Report not found"}), 404


if __name__ == "__main__":
    print("\n  🤖 Autonomous Agent Web UI")
    print("  ─────────────────────────")
    print("  Open http://localhost:5000 in your browser\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
