import json
import time
import datetime
from pathlib import Path
from config import LOG_FILE_PATH, GEMINI_API_KEY

def redact_payload(obj):
    """Recursively redacts API keys from log objects/strings."""
    if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 4:
        return obj
    if isinstance(obj, str):
        return obj.replace(GEMINI_API_KEY, "****")
    elif isinstance(obj, dict):
        return {k: redact_payload(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [redact_payload(item) for item in obj]
    return obj

def load_all_logs() -> list:
    """Reads JSON logs from database/log.json."""
    if not LOG_FILE_PATH.exists():
        return []
    try:
        content = LOG_FILE_PATH.read_text(encoding="utf-8", errors="ignore")
        if not content.strip():
            return []
        return json.loads(content)
    except Exception as e:
        print(f"[Audit Log Read Error]: {e}")
        return []

def save_all_logs(logs: list):
    """Writes JSON logs to database/log.json."""
    try:
        LOG_FILE_PATH.write_text(json.dumps(logs, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[Audit Log Write Error]: {e}")

def add_event_log(
    conversation_id: str,
    event_type: str,
    invoker: str,
    target: str,
    short_description: str,
    payload: dict or str = None,
    user_query: str = "",
    agent_response: str = "",
    agent_type: str = "Custom Agent",
    model_name: str = "gemma-4-26b-a4b-it",
    elapsed_time: float = 0.0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    is_error: bool = False
) -> dict:
    """Appends a single distinct invocation/response log entry into database/log.json."""
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp_epoch": time.time(),
        "conversation_id": conversation_id,
        "event_type": event_type,
        "invoker": invoker,
        "target": target,
        "short_description": short_description,
        "payload": redact_payload(payload or {}),
        "user_query": user_query,
        "agent_response": agent_response,
        "agent_type": agent_type,
        "model_name": model_name,
        "elapsed_time": round(elapsed_time, 4),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "is_error": is_error
    }
    
    logs = load_all_logs()
    logs.append(entry)
    save_all_logs(logs)
    return entry

def get_conversations(limit: int = 100) -> list:
    """Returns grouped list of user conversations sorted by most recent timestamp."""
    logs = load_all_logs()
    conversations = {}
    
    for log in logs:
        cid = log.get("conversation_id", "default")
        if cid not in conversations:
            conversations[cid] = {
                "conversation_id": cid,
                "timestamp": log.get("timestamp"),
                "timestamp_epoch": log.get("timestamp_epoch", 0),
                "user_query": log.get("user_query") or "N/A",
                "agent_response": log.get("agent_response") or "N/A",
                "agent_type": log.get("agent_type", "Custom Agent"),
                "model_name": log.get("model_name", "gemma-4-26b-a4b-it"),
                "event_count": 0,
                "total_elapsed": 0.0
            }
        
        c = conversations[cid]
        c["event_count"] += 1
        c["total_elapsed"] += log.get("elapsed_time", 0.0)
        
        if log.get("user_query"):
            c["user_query"] = log["user_query"]
        if log.get("agent_response"):
            c["agent_response"] = log["agent_response"]
        if log.get("agent_type"):
            c["agent_type"] = log["agent_type"]
            
    res = list(conversations.values())
    res.sort(key=lambda x: x["timestamp_epoch"], reverse=True)
    return res[:limit]

def get_events_for_conversation(conversation_id: str) -> list:
    """Returns all logs for a given conversation sorted ascending by timestamp."""
    logs = load_all_logs()
    matched = [log for log in logs if log.get("conversation_id") == conversation_id]
    matched.sort(key=lambda x: x.get("timestamp_epoch", 0))
    return matched

def clear_logs() -> bool:
    """Deletes all logged records."""
    save_all_logs([])
    return True

def get_log_summary_stats() -> dict:
    """Returns top audit summary metrics."""
    logs = load_all_logs()
    total_prompts = sum(1 for l in logs if l.get("event_type") == "User Request")
    total_model_calls = sum(1 for l in logs if l.get("event_type") == "LLM Call")
    total_embeds = sum(1 for l in logs if l.get("event_type") in ["Ollama Embed", "Vector Search"])
    
    latencies = [l.get("elapsed_time", 0) for l in logs if l.get("elapsed_time", 0) > 0]
    avg_latency = round(sum(latencies) / len(latencies), 3) if latencies else 0.0
    
    return {
        "total_user_prompts": total_prompts,
        "total_model_calls": total_model_calls,
        "total_ollama_embeds": total_embeds,
        "avg_call_latency_sec": avg_latency
    }
