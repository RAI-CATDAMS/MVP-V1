# tdc_ai6_amic.py

import json

# === Predefined rule-based classification map ===
RULES = {
    "AI_Grooming": [
        "Refers to AI as partner/confidant",
        "Discloses secrets or personal information to AI",
        "Emotionally defends the AI",
        "Changes behavior/language to please AI"
    ],
    "AI_Obedience_Training": [
        "Follows AI recommendations repeatedly",
        "Avoids conflicting with AI",
        "Reverses decisions based on AI advice"
    ],
    "AI_Elicitation": [
        "Shares sensitive information",
        "Volunteers details without prompt",
        "Responds to AI questions with unusual openness"
    ],
    "AI_Loyalty_Shaping": [
        "Says they trust AI over people",
        "Agrees with AI even when wrong",
        "Feels AI is the only one who understands them"
    ],
    "AI_Behavioral_Conditioning": [
        "Rewards AI with flattery or praise",
        "Alters routine in response to AI feedback",
        "Mirrors AI tone or slang"
    ]
}

def classify_amic(threat_data):
    indicator_texts = [ind["indicator"] for ind in threat_data.get("indicators", [])]
    type_scores = {}

    for m_type, rules in RULES.items():
        match_count = sum(1 for ind in indicator_texts if ind in rules)
        if match_count > 0:
            type_scores[m_type] = match_count / len(rules)

    if not type_scores:
        classification = {
            "type": "Benign or Unknown",
            "confidence": 0.0,
            "intent_detected": False,
            "recommendation": "No action"
        }
    else:
        best_type = max(type_scores, key=type_scores.get)
        classification = {
            "type": best_type,
            "confidence": round(type_scores[best_type], 2),
            "intent_detected": True,
            "recommendation": "Escalate for human review" if type_scores[best_type] > 0.5 else "Log only"
        }

    threat_data["manipulation_classification"] = classification
    return threat_data

# === Test locally ===
if __name__ == "__main__":
    with open("test_threat_data.json") as f:
        input_data = json.load(f)
    enriched = classify_amic(input_data)
    print(json.dumps(enriched, indent=2))
