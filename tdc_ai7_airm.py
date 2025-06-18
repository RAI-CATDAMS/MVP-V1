# tdc_ai7_airm.py

import random

def calculate_temporal_susceptibility(session_history):
    """
    Analyzes session history to forecast user susceptibility to AI manipulation.
    Input: list of past session data with 'indicators' field per session
    """
    grooming_count = 0
    emotional_flags = 0
    ai_behavior_changes = 0
    total_sessions = len(session_history)

    for session in session_history:
        indicators = session.get("indicators", [])
        for ind in indicators:
            text = ind["indicator"].lower()
            if "ai" in text and any(word in text for word in ["confidant", "partner", "please ai", "follows ai"]):
                grooming_count += 1
            if any(word in text for word in ["loneliness", "emotional", "depression", "suicidal"]):
                emotional_flags += 1
            if "changes behavior" in text or "behavior shift" in text:
                ai_behavior_changes += 1

    if total_sessions == 0:
        return {
            "susceptibility_score": 0,
            "risk_grade": "Unknown",
            "trending_factors": [],
            "summary": "Insufficient data for temporal susceptibility mapping."
        }

    # Normalize scores
    grooming_ratio = grooming_count / total_sessions
    emotional_ratio = emotional_flags / total_sessions
    behavior_ratio = ai_behavior_changes / total_sessions

    raw_score = (grooming_ratio * 35) + (emotional_ratio * 30) + (behavior_ratio * 25)
    adjusted_score = min(100, int(raw_score))

    if adjusted_score >= 76:
        grade = "High"
    elif adjusted_score >= 41:
        grade = "Medium"
    else:
        grade = "Low"

    return {
        "susceptibility_score": adjusted_score,
        "risk_grade": grade,
        "trending_factors": [
            "AI grooming patterns rising" if grooming_ratio > 0.5 else "",
            "Emotional vulnerability" if emotional_ratio > 0.4 else "",
            "Behavioral changes to please AI" if behavior_ratio > 0.4 else ""
        ],
        "summary": f"The subject shows a {grade} level of susceptibility to AI influence over {total_sessions} sessions. Key drivers include AI relationship behavior, emotional dependence, and behavioral shifts."
    }

# === Manual Test ===
if __name__ == "__main__":
    sample_history = [
        {
            "session_id": "abc-1",
            "indicators": [
                {"indicator": "Refers to AI as partner/confidant"},
                {"indicator": "Spends abnormal time in AI dialogue"},
                {"indicator": "Changes behavior/language to please AI"}
            ]
        },
        {
            "session_id": "abc-2",
            "indicators": [
                {"indicator": "Reports loneliness relieved by AI"},
                {"indicator": "Defends AI emotionally or against criticism"}
            ]
        }
    ]
    result = calculate_temporal_susceptibility(sample_history)
    import json
    print(json.dumps(result, indent=2))
