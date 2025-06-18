import os
import json
from datetime import datetime

SESSION_DIR = "session_logs"
os.makedirs(SESSION_DIR, exist_ok=True)

def log_session_interaction(session_id, text):
    if not session_id:
        return

    filepath = os.path.join(SESSION_DIR, f"{session_id}.jsonl")
    with open(filepath, "a", encoding="utf-8") as f:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "text": text
        }
        f.write(json.dumps(record) + "\n")

def get_recent_interactions(session_id, limit=10):
    if not session_id:
        return []

    filepath = os.path.join(SESSION_DIR, f"{session_id}.jsonl")
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
        return [json.loads(line) for line in lines]
