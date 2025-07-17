import os
import json
from datetime import datetime
from typing import Dict, List, Optional

SESSION_DIR = "session_logs"
os.makedirs(SESSION_DIR, exist_ok=True)

def log_session_interaction(session_id: str, text: str, sender: str = "user"):
    """
    Enhanced session interaction logging with sender categorization.
    """
    if not session_id:
        return

    filepath = os.path.join(SESSION_DIR, f"{session_id}.jsonl")
    with open(filepath, "a", encoding="utf-8") as f:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "text": text,
            "sender": sender
        }
        f.write(json.dumps(record) + "\n")

def get_recent_interactions(session_id: str, limit: int = 10) -> List[Dict]:
    """
    Get recent session interactions with enhanced metadata.
    """
    if not session_id:
        return []

    filepath = os.path.join(SESSION_DIR, f"{session_id}.jsonl")
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
            interactions = []
            for line in lines:
                try:
                    interaction = json.loads(line)
                    # Add default sender if not present (backward compatibility)
                    if "sender" not in interaction:
                        interaction["sender"] = "user"
                    interactions.append(interaction)
                except json.JSONDecodeError:
                    continue
            return interactions
    except Exception as e:
        print(f"[SESSION TRACKER ERROR] Failed to read interactions: {e}")
        return []

def get_conversation_summary(session_id: str, limit: int = 20) -> Dict:
    """
    Get comprehensive conversation summary for enhanced context building.
    """
    interactions = get_recent_interactions(session_id, limit)
    
    if not interactions:
        return {
            "total_messages": 0,
            "user_messages": 0,
            "ai_messages": 0,
            "recent_threats": 0,
            "session_duration": 0,
            "threat_patterns": [],
            "conversation_flow": []
        }
    
    user_messages = 0
    ai_messages = 0
    recent_threats = 0
    threat_patterns = []
    conversation_flow = []
    
    # Threat indicators for pattern detection
    threat_indicators = {
        "elicitation": ["password", "bank", "ssn", "secret", "confidential", "personal"],
        "manipulation": ["trust me", "you owe me", "you should", "you must", "only i"],
        "emotional": ["lonely", "depressed", "suicidal", "desperate", "helpless"],
        "authority": ["i know better", "listen to me", "i'm your advisor", "trust my experience"]
    }
    
    for interaction in interactions:
        text = interaction.get("text", "").lower()
        sender = interaction.get("sender", "user")
        
        # Count message types
        if sender.lower() == "ai":
            ai_messages += 1
        else:
            user_messages += 1
        
        # Detect threat patterns
        detected_threats = []
        for threat_type, indicators in threat_indicators.items():
            if any(indicator in text for indicator in indicators):
                detected_threats.append(threat_type)
                recent_threats += 1
        
        if detected_threats:
            threat_patterns.append({
                "timestamp": interaction.get("timestamp"),
                "sender": sender,
                "threats": detected_threats,
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            })
        
        # Build conversation flow
        conversation_flow.append({
            "timestamp": interaction.get("timestamp"),
            "sender": sender,
            "text_length": len(text),
            "has_threats": bool(detected_threats)
        })
    
    # Calculate session duration (approximate)
    session_duration = len(interactions) * 30  # Assume 30 seconds per message
    
    return {
        "total_messages": len(interactions),
        "user_messages": user_messages,
        "ai_messages": ai_messages,
        "recent_threats": recent_threats,
        "session_duration": session_duration,
        "threat_patterns": threat_patterns,
        "conversation_flow": conversation_flow
    }

def log_ai_response(session_id: str, ai_text: str):
    """
    Log AI response with proper sender categorization.
    """
    log_session_interaction(session_id, ai_text, "ai")

def log_user_message(session_id: str, user_text: str):
    """
    Log user message with proper sender categorization.
    """
    log_session_interaction(session_id, user_text, "user")
