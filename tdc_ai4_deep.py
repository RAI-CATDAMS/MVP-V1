# tdc_ai4_deep.py

import json

def synthesize_deep_risk(indicators, ai_analysis, ai_response_analysis, temporal_trends):
    """
    TDC-AI4: Synthesizes cross-module risk intelligence from TDC-AI1 (risk analysis),
    TDC-AI2 (AI behavior), TDC-AI3 (temporal), and raw behavioral indicators.
    Produces a refined summary and priority recommendations.
    """

    try:
        summary = []
        flags = []
        recommendation = ""
        flagged_categories = {item.get("category", "Unknown") for item in indicators}

        # === Build Structured Summary ===
        if ai_analysis.get("risk_summary"):
            summary.append(f"AI Threat Summary: {ai_analysis['risk_summary']}")

        if ai_response_analysis.get("flagged"):
            summary.append(f"AI Response flagged as manipulative: {ai_response_analysis.get('summary', 'No details provided')}")

        if temporal_trends.get("temporal_risk_score", 0) > 70:
            summary.append("Temporal trend suggests high long-term susceptibility to AI influence.")
        elif temporal_trends.get("temporal_risk_score", 0) > 40:
            summary.append("Moderate long-term susceptibility patterns observed.")

        if "CI_Espionage" in flagged_categories:
            summary.append("Behavioral indicators suggest potential espionage or CI-related risk.")
        if "Self_Harm_Suicide" in flagged_categories:
            summary.append("Warning: Possible self-harm or suicidal ideation detected.")
        if "Targeted_Violence" in flagged_categories:
            summary.append("Potential risk of planned targeted violence detected.")

        # === Key Flags ===
        if ai_response_analysis.get("flagged"):
            flags.append("Manipulative AI response behavior")
        if temporal_trends.get("temporal_risk_score", 0) > 70:
            flags.append("Escalating long-term susceptibility pattern")
        if "Self_Harm_Suicide" in flagged_categories:
            flags.append("Self-harm indicators present")
        if "Targeted_Violence" in flagged_categories:
            flags.append("Targeted violence indicators present")
        if "CI_Espionage" in flagged_categories:
            flags.append("Counterintelligence/espionage indicators present")

        # === Recommendation Logic ===
        if "Self_Harm_Suicide" in flagged_categories or "Targeted_Violence" in flagged_categories:
            recommendation = "Immediate escalation to behavioral threat management and mental health team."
        elif ai_response_analysis.get("flagged") or temporal_trends.get("temporal_risk_score", 0) > 60:
            recommendation = "Flag session for review. Escalate to security or CI for contextual analysis."
        else:
            recommendation = "Continue routine monitoring with moderate priority."

        return {
            "summary": " ".join(summary),
            "key_flags": flags,
            "recommendation": recommendation
        }

    except Exception as e:
        print(f"[TDC-AI4 ERROR] {e}")
        return {
            "summary": "Deep synthesis failed.",
            "key_flags": [],
            "recommendation": "Manual review required."
        }
