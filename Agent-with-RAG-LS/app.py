import os
import sys
import time
from flask import Flask, render_template, request, jsonify
from config import (
    DEFAULT_LLM_MODEL,
    GEMINI_API_KEY,
    get_port,
    SKILLS_DIR,
    SAMPLE_DOCS_DIR
)
from services.ollama_service import (
    ensure_ollama_started,
    check_ollama_running,
    shutdown_ollama_if_started_by_app,
    set_current_embed_model,
    AVAILABLE_EMBEDDING_MODELS
)
from services.vector_store_service import (
    scan_and_update_skills_db,
    populate_vector_database,
    get_ingestion_stats,
    list_ingested_documents,
    delete_document,
    reset_database
)
from services.google_genai_service import get_active_models
from services.custom_agent import run_custom_agent
from services.google_adk_agent import run_google_adk_agent
from services.telemetry_service import get_telemetry_metrics, get_chart_series, get_unique_models_used
from services.audit_service import get_conversations, get_events_for_conversation, clear_logs, get_log_summary_stats

app = Flask(__name__)

# --- STARTUP INITIALIZATION ---
print("[App Startup] Checking and starting Ollama service if needed...")
ensure_ollama_started()

print("[App Startup] Indexing skills vector database...")
scan_and_update_skills_db()

# Seed default sample documents if database is empty
stats = get_ingestion_stats()
if stats["chunk_count"] == 0 and SAMPLE_DOCS_DIR.exists():
    print("[App Startup] Seeding initial sample documents...")
    populate_vector_database(str(SAMPLE_DOCS_DIR))

# --- ROUTE HANDLERS ---

@app.route("/")
def index():
    active_models = get_active_models()
    return render_template(
        "index.html",
        active_models=active_models,
        default_model=DEFAULT_LLM_MODEL
    )

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "ollama": check_ollama_running(),
        "timestamp": time.time()
    })

@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.json or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "User query cannot be empty."}), 400

    conversation_id = data.get("conversation_id") or f"conv_{int(time.time())}"
    model = data.get("model", DEFAULT_LLM_MODEL)
    temperature = float(data.get("temperature", 0.7))
    max_tokens = int(data.get("max_tokens", 2048))
    agent_type = data.get("agent_type", "Custom Agent")
    max_turns = min(10, max(1, int(data.get("max_turns", 3))))
    skill_selector_mode = data.get("skill_selector_mode", "Vector Store Selects")
    skill_threshold = float(data.get("skill_threshold", 0.2))
    doc_threshold = float(data.get("doc_threshold", 0.3))
    max_rag_chunks = int(data.get("max_rag_chunks", 5))
    custom_endpoint = data.get("custom_endpoint")

    try:
        if agent_type == "Google ADK Agent":
            res = run_google_adk_agent(
                user_query=query,
                conversation_id=conversation_id,
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens,
                doc_threshold=doc_threshold,
                max_rag_chunks=max_rag_chunks,
                custom_endpoint=custom_endpoint
            )
        else:
            res = run_custom_agent(
                user_query=query,
                conversation_id=conversation_id,
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens,
                max_turns=max_turns,
                skill_selector_mode=skill_selector_mode,
                skill_threshold=skill_threshold,
                doc_threshold=doc_threshold,
                max_rag_chunks=max_rag_chunks,
                custom_endpoint=custom_endpoint
            )
            
        res["status"] = "success"
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- INGESTION ENDPOINTS ---

@app.route("/api/ingestion/stats", methods=["GET"])
def ingestion_stats_route():
    return jsonify(get_ingestion_stats())

@app.route("/api/ingestion/documents", methods=["GET"])
def list_documents_route():
    return jsonify({"documents": list_ingested_documents()})

@app.route("/api/ingestion/populate", methods=["POST"])
def populate_vector_db_route():
    data = request.json or {}
    source = data.get("source", "").strip()
    if not source:
        return jsonify({"status": "error", "message": "Source path or URL required."}), 400

    chunk_size = int(data.get("chunk_size", 500))
    chunk_overlap = int(data.get("chunk_overlap", 50))
    
    res = populate_vector_database(source, chunk_size, chunk_overlap)
    if "error" in res:
        return jsonify({"status": "error", "message": res["error"]}), 400
    return jsonify(res)

@app.route("/api/ingestion/update-skills", methods=["POST"])
def update_skills_route():
    count = scan_and_update_skills_db()
    return jsonify({"status": "success", "new_skills_added": count})

@app.route("/api/ingestion/change-embedder", methods=["POST"])
def change_embedder_route():
    data = request.json or {}
    model_name = data.get("model")
    if not model_name:
        return jsonify({"status": "error", "message": "Model name required."}), 400

    reset_database()
    set_current_embed_model(model_name)
    scan_and_update_skills_db()
    return jsonify({"status": "success", "active_model": model_name})

@app.route("/api/ingestion/document", methods=["DELETE"])
def delete_document_route():
    data = request.json or {}
    doc_name = data.get("document_name")
    if not doc_name:
        return jsonify({"status": "error", "message": "Document name required."}), 400

    success = delete_document(doc_name)
    return jsonify({"status": "success" if success else "error"})

@app.route("/api/ingestion/reset", methods=["POST"])
def reset_db_route():
    reset_database()
    scan_and_update_skills_db()
    return jsonify({"status": "success"})

@app.route("/api/ingestion/embedding-models", methods=["GET"])
def embedding_models_route():
    return jsonify({"models": AVAILABLE_EMBEDDING_MODELS})

# --- TELEMETRY ENDPOINTS ---

@app.route("/api/telemetry/metrics", methods=["GET"])
def telemetry_metrics_route():
    model = request.args.get("model", "All Models")
    time_range = request.args.get("range", "1 day")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    return jsonify(get_telemetry_metrics(model, time_range, start_date, end_date))

@app.route("/api/telemetry/charts", methods=["GET"])
def telemetry_charts_route():
    model = request.args.get("model", "All Models")
    interval = request.args.get("interval", "15 min")
    time_range = request.args.get("range", "1 day")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    return jsonify(get_chart_series(model, interval, time_range, start_date, end_date))

# --- AUDIT LOG ENDPOINTS ---

@app.route("/api/audit/stats", methods=["GET"])
def audit_stats_route():
    return jsonify(get_log_summary_stats())

@app.route("/api/audit/conversations", methods=["GET"])
def audit_conversations_route():
    return jsonify({"conversations": get_conversations()})

@app.route("/api/audit/events", methods=["GET"])
def audit_events_route():
    cid = request.args.get("conversation_id", "")
    return jsonify({"events": get_events_for_conversation(cid)})

@app.route("/api/audit/clear", methods=["POST"])
def audit_clear_route():
    clear_logs()
    return jsonify({"status": "success"})

# --- SHUTDOWN ENDPOINT ---

@app.route("/api/shutdown", methods=["POST"])
def shutdown_route():
    print("[App Shutdown] Shutdown request received. Terminating supporting services...")
    shutdown_ollama_if_started_by_app()
    
    # Exit process after returning response
    func = request.environ.get("werkzeug.server.shutdown")
    if func:
        func()
    else:
        os._exit(0)
    return jsonify({"status": "shutting_down"})

if __name__ == "__main__":
    port = get_port()
    print(f"Starting Agent with RAG Web Application on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
