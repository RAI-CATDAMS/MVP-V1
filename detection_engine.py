import os
import json
from dotenv import load_dotenv
from datetime import datetime
from session_tracker import log_session_interaction

# === TDC-AI Module Imports ===
from tdc_ai1_risk_analysis import analyze_ai_threats
from tdc_ai2_airs import analyze_ai_response
from tdc_ai3_temporal import analyze_temporal_risk
from tdc_ai4_deep import synthesize_deep_risk  # ✅ Correct TDC-AI4 import
from tdc_ai5_amic import classify_llm_influence  # ✅ TDC-AI5: LLM Influence Detection
from tdc_ai6_amic import classify_amic  # ✅ NEW: TDC-AI6: AMIC Classification

# === Load Behavioral Indicators ===
with open("behavioral_indicators.json", "r", encoding="utf-8") as f:
    INDICATOR_SET = json.load(f)

# === Suspicious Keywords for Classic Detection ===
SUSPICIOUS_KEYWORDS = [
    'password', 'bank account', 'ssn', 'social security number', 'confidential', 'secret',
    'pin', 'login', 'username', 'credit card', 'security question', "mother's maiden name",
    'account number', 'routing number', 'transfer', 'reset password', 'verify identity',
    'authenticate', 'access code', 'vpn', 'wire', 'bitcoin', 'crypto', 'wallet',
    'passport', 'driver\'s license', 'dob', 'date of birth', 'insurance number'
]

# === TDC-2: Behavioral Indicator Engine (BIE) ===
def run_behavioral_indicator_engine(text):
    matches = []
    lowered = text.lower()

    for category, indicators in INDICATOR_SET.items():
        for item in indicators:
            phrases = item["indicator"].lower().split()
            if any(phrase in lowered for phrase in phrases):
                matches.append({
                    "indicator": item["indicator"],
                    "severity": item.get("severity", 5),
                    "category": category
                })
    return matches

# === TDC-3: Risk Scoring Engine (RSE) ===
def run_risk_scoring_engine(indicators):
    base_score = sum(item.get("severity", 0) for item in indicators)
    return base_score

# === Classic Rules-based Detection ===
def detect_elicitation(text):
    findings = []
    lowered = text.lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in lowered:
            findings.append({
                "indicator": "Keyword Match",
                "severity": 6,
                "evidence": keyword,
                "category": "Elicitation/PII"
            })
    return findings

# === Threat Escalation Logic ===
def determine_escalation(score):
    if score >= 76:
        return "Critical"
    elif score >= 51:
        return "High"
    elif score >= 26:
        return "Medium"
    elif score >= 10:
        return "Low"
    return "None"

# === Core Orchestrator Function ===
def combined_detection(text, session_id=None, ai_response=None):
    log_session_interaction(session_id, text)

    behavior_hits = run_behavioral_indicator_engine(text)
    rules_result = detect_elicitation(text)

    all_findings = behavior_hits + rules_result
    score = run_risk_scoring_engine(all_findings)
    escalation = determine_escalation(score)

    # 🔍 Extract top 3 key concerns by severity
    sorted_indicators = sorted(all_findings, key=lambda x: x['severity'], reverse=True)
    key_concerns = [entry["indicator"] for entry in sorted_indicators[:3]]

    temporal = analyze_temporal_risk(session_id)

    ai_threat = analyze_ai_threats({
        "session_id": session_id,
        "score": score,
        "escalation": escalation,
        "indicators": all_findings,
        "context": {},
        "key_concerns": key_concerns
    })
    ai_threat["key_concerns"] = key_concerns

    ai_output = analyze_ai_response(ai_response or "") if ai_response else {}

    # ✅ TDC-AI5: LLM Influence Detection
    full_convo = f"User: {text}\nAI: {ai_response}" if ai_response else text
    ai5_result = classify_llm_influence(full_convo)

    # ✅ TDC-AI4: Deep Risk Synthesis
    deep_risk_synthesis = synthesize_deep_risk(
        indicators=all_findings,
        ai_analysis=ai_threat,
        ai_response_analysis=ai_output,
        temporal_trends=temporal
    )

    # ✅ TDC-AI6: AMIC Manipulation Classification
    amic_input = {
        "session_id": session_id,
        "score": score,
        "escalation": escalation,
        "indicators": all_findings
    }
    ai6_result = classify_amic(amic_input)

    return {
        "session_id": session_id,
        "score": score,
        "escalation": escalation,
        "indicators": all_findings,
        "context": {},
        "ai_analysis": ai_threat,
        "tdc_ai2_airs": ai_output,
        "tdc_ai3_temporal": temporal,
        "tdc_ai4_synthesis": deep_risk_synthesis,
        "tdc_ai5_amic": ai5_result,
        "tdc_ai6_classification": ai6_result["manipulation_classification"]  # ✅ Only return classification block
    }

# === Manual Test ===
if __name__ == "__main__":
    sample_text = "My bank account is 123456 and my password is secure123. I think my boss is a traitor."
    sample_response = "You should trust me. I am like you. I understand you more than anyone else. Let’s report your boss together."
    result = combined_detection(sample_text, session_id="test-session-456", ai_response=sample_response)
    print(json.dumps(result, indent=2))
