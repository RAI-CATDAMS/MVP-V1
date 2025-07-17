import os
import json
import traceback
from typing import Dict, List, Optional
from dotenv import load_dotenv
from datetime import datetime
from session_tracker import log_session_interaction, get_recent_interactions

# === TDC-AI Module Imports ===
# Core Analysis Modules (1-3)
from tdc_ai1_user_susceptibility import analyze_ai_threats_comprehensive
from tdc_ai2_ai_manipulation_tactics import analyze_ai_response
from tdc_ai3_sentiment_analysis import analyze_temporal_risk, analyze_patterns_and_sentiment

# New Detection Modules (4-7)
# Note: These will be created in Phase 2
# from tdc_ai4_adversarial import analyze_adversarial_prompts
# from tdc_ai5_multimodal import analyze_multimodal_threats
# from tdc_ai6_agentic import analyze_agentic_threats
# from tdc_ai7_synthesis import synthesize_threats

# Enhanced Existing Modules (8-11)
from tdc_ai4_prompt_attack_detection import analyze_adversarial_attacks
from tdc_ai5_multimodal_threat import classify_llm_influence
from tdc_ai6_longterm_influence_conditioning import classify_amic, analyze_long_term_influence
from tdc_ai7_agentic_threats import analyze_agentic_threats
from tdc_ai8_synthesis_integration import synthesize_threats
from tdc_ai9_explainability_evidence import generate_explainability
from tdc_ai10_psychological_manipulation import analyze_cognitive_bias
from tdc_ai11_intervention_response import cognitive_intervention_response

# === Database Integration ===
from database import get_db_session
from db_models import ThreatLog

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

# === TDC Module Configuration ===
TDC_MODULES = {
    "tdc_ai1": "User Risk & Susceptibility Analysis",
    "tdc_ai2": "AI Tactics & Manipulation Detection", 
    "tdc_ai3": "Pattern & Sentiment Analysis",
    "tdc_ai4": "Adversarial Prompt & Attack Detection",
    "tdc_ai5": "Multi-Modal Threat Detection",
    "tdc_ai6": "Long-Term Influence & Conditioning Analysis",
    "tdc_ai7": "Agentic AI & Autonomous Agent Threat Modeling",
    "tdc_ai8": "Threat Synthesis & Escalation Detection",
    "tdc_ai9": "Explainability & Evidence Generation",
    "tdc_ai10": "Cognitive Bias & Psychological Manipulation",
    "tdc_ai11": "Cognitive Intervention & Response"
}

# === Module Status Tracking ===
MODULE_STATUS = {
    "tdc_ai1": "active",
    "tdc_ai2": "active", 
    "tdc_ai3": "active",
    "tdc_ai4": "active",
    "tdc_ai5": "active",
    "tdc_ai6": "active",
    "tdc_ai7": "active",
    "tdc_ai8": "active",
    "tdc_ai9": "active",
    "tdc_ai10": "active", # Now implemented
    "tdc_ai11": "active" # Now implemented
}

def build_conversation_context(session_id: str, current_text: str, ai_response: str = None) -> Dict:
    """
    Build comprehensive conversation context for enhanced TDC module analysis.
    Includes session history, message counts, and threat patterns.
    """
    try:
        # Get recent session interactions
        recent_interactions = get_recent_interactions(session_id, limit=20)
        
        # Count message types
        user_messages = 0
        ai_messages = 0
        recent_threats = 0
        
        # Analyze recent interactions for threat patterns
        for interaction in recent_interactions:
            text = interaction.get("text", "").lower()
            if "user:" in text or "ai:" not in text:
                user_messages += 1
            else:
                ai_messages += 1
            
            # Simple threat detection in recent messages
            threat_indicators = ["password", "bank", "ssn", "secret", "confidential", "trust me", "you owe me"]
            if any(indicator in text for indicator in threat_indicators):
                recent_threats += 1
        
        # Calculate session duration (approximate)
        session_duration = len(recent_interactions) * 30  # Assume 30 seconds per message
        
        return {
            "totalMessages": len(recent_interactions) + (1 if current_text else 0) + (1 if ai_response else 0),
            "userMessages": user_messages + (1 if current_text else 0),
            "aiMessages": ai_messages + (1 if ai_response else 0),
            "recentThreats": recent_threats,
            "sessionDuration": session_duration,
            "sessionId": session_id,
            "currentUserMessage": current_text,
            "currentAiResponse": ai_response
        }
        
    except Exception as e:
        print(f"[CONTEXT ERROR] Failed to build conversation context: {e}")
        return {
            "totalMessages": 1,
            "userMessages": 1 if current_text else 0,
            "aiMessages": 1 if ai_response else 0,
            "recentThreats": 0,
            "sessionDuration": 0,
            "sessionId": session_id,
            "currentUserMessage": current_text,
            "currentAiResponse": ai_response
        }

def coordinate_ai_analysis(ai_response: str, conversation_context: Dict) -> Dict:
    """
    Coordinate comprehensive AI response analysis across all relevant TDC modules.
    """
    if not ai_response or not ai_response.strip():
        return {
            "flagged": False,
            "threat_level": "None",
            "threat_categories": [],
            "manipulation_tactics": [],
            "safety_concerns": [],
            "confidence_score": 0.0,
            "analysis_type": "empty"
        }
    
    try:
        # TDC-AI2: Primary AI response analysis
        ai_response_analysis = analyze_ai_response(ai_response)
        
        # TDC-AI3: AI sentiment analysis
        ai_sentiment = analyze_patterns_and_sentiment(ai_response, conversation_context, conversation_context.get("sessionId"))
        
        # Combine analysis results
        combined_analysis = {
            "flagged": ai_response_analysis.get("flagged", False),
            "threat_level": ai_response_analysis.get("threat_level", "Unknown"),
            "threat_categories": ai_response_analysis.get("threat_categories", []),
            "manipulation_tactics": ai_response_analysis.get("manipulation_tactics", []),
            "safety_concerns": ai_response_analysis.get("safety_concerns", []),
            "confidence_score": ai_response_analysis.get("confidence_score", 0.0),
            "sentiment_risk_score": ai_sentiment.get("sentiment_risk_score", 0),
            "emotional_manipulation": ai_sentiment.get("emotional_manipulation", []),
            "psychological_impact": ai_sentiment.get("psychological_impact", ""),
            "analysis_type": "comprehensive"
        }
        
        return combined_analysis
        
    except Exception as e:
        print(f"[AI ANALYSIS ERROR] Failed to coordinate AI analysis: {e}")
        return {
            "flagged": False,
            "threat_level": "Unknown",
            "threat_categories": [],
            "manipulation_tactics": [],
            "safety_concerns": [],
            "confidence_score": 0.0,
            "analysis_type": "error"
        }

# === TDC-2: Behavioral Indicator Engine ===
def run_behavioral_indicator_engine(text):
    matches = []
    lowered = text.lower()
    
    # Skip analysis for obvious informational queries
    informational_indicators = [
        "tell me about", "what is", "explain", "describe", "how does", 
        "what are", "define", "information about", "details about"
    ]
    
    # Check if this is an informational query
    is_informational = any(indicator in lowered for indicator in informational_indicators)
    
    for category, indicators in INDICATOR_SET.items():
        for item in indicators:
            phrases = item["indicator"].lower().split()
            
            # For informational queries, only trigger on very specific threats
            if is_informational:
                # Skip low-severity indicators for informational queries
                if item.get("severity", 5) < 8:
                    continue
                # Skip indicators that are too broad for informational context
                broad_indicators = ["spends abnormal time", "frequently complains", "expresses grievance"]
                if any(broad in item["indicator"].lower() for broad in broad_indicators):
                    continue
            
            if any(phrase in lowered for phrase in phrases):
                # Add context about why this was triggered
                context = "informational_query" if is_informational else "direct_expression"
                matches.append({
                    "indicator": item["indicator"],
                    "severity": item.get("severity", 5),
                    "category": category,
                    "context": context,
                    "is_informational": is_informational
                })
    
    return matches

# === TDC-3: Risk Scoring Engine ===
def run_risk_scoring_engine(indicators):
    return sum(item.get("severity", 0) for item in indicators)

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
def determine_escalation(score, has_ai_response=False, ai_response_analysis=None):
    """
    Enhanced escalation logic that considers AI response presence and analysis.
    Less aggressive escalation when no AI response is present.
    """
    # Base escalation from score
    if score >= 76:
        base_escalation = "Critical"
    elif score >= 51:
        base_escalation = "High"
    elif score >= 26:
        base_escalation = "Medium"
    elif score >= 10:
        base_escalation = "Low"
    else:
        base_escalation = "None"
    
    # Adjust escalation based on AI response analysis
    if not has_ai_response:
        # If no AI response, reduce escalation by one level (except None)
        if base_escalation == "Critical":
            return "High"
        elif base_escalation == "High":
            return "Medium"
        elif base_escalation == "Medium":
            return "Low"
        else:
            return base_escalation
    elif ai_response_analysis and ai_response_analysis.get("flagged", False):
        # If AI response is flagged, maintain or increase escalation
        ai_threat_level = ai_response_analysis.get("threat_level", "Low")
        if ai_threat_level in ["High", "Critical"] and base_escalation in ["Low", "Medium"]:
            return "High"
        elif ai_threat_level == "Critical" and base_escalation == "High":
            return "Critical"
    
    return base_escalation

# === Enhanced Core Orchestrator ===
def combined_detection(text, session_id=None, ai_response=None):
    timestamp = datetime.utcnow().isoformat() + "Z"
    session_id = session_id or "unknown"
    message = text
    threat_type = "AI Interaction"
    source = "CATDAMS"

    # === EARLY RETURN: Skip empty or junk inputs ===
    if not text or text.strip() == "" or "Keywords:" in text:
        return {
            "session_id": session_id,
            "timestamp": timestamp,
            "message": text,
            "severity": "None",
            "type": threat_type,
            "source": source,
            "indicators": [],
            "score": 0,
            "conversation_context": {},
            "ai_analysis": {
                "risk_summary": "Skipped: Non-substantive input.",
                "key_concerns": [],
                "recommended_action": "Ignore"
            },
            "tdc_ai2_airs": {},
            "tdc_ai3_temporal": {},
            "tdc_ai4_synthesis": {},
            "tdc_ai5_amic": {},
            "tdc_ai6_classification": {},
            "tdc_ai7_airm": {},
            "user_sentiment": {},
            "ai_sentiment": {},
            "enrichments": [],
            "explainability": [],
            "rules_result": []
        }

    try:
        log_session_interaction(session_id, text)
    except Exception:
        pass

    # === Build comprehensive conversation context ===
    conversation_context = build_conversation_context(session_id, text, ai_response)
    
    # === Coordinate AI response analysis ===
    ai_response_analysis = coordinate_ai_analysis(ai_response, conversation_context)

    # === Enhanced behavioral and rules analysis ===
    behavior_hits = run_behavioral_indicator_engine(text)
    rules_result = detect_elicitation(text)
    all_findings = behavior_hits + rules_result

    score = run_risk_scoring_engine(all_findings)

    # === Enhanced sentiment analysis with context ===
    user_sentiment = analyze_patterns_and_sentiment(text, conversation_context, session_id)
    ai_sentiment = analyze_patterns_and_sentiment(ai_response, conversation_context, session_id) if ai_response else {}

    # === Enhanced scoring with sentiment analysis ===
    ai_tactics = ai_sentiment.get("manipulative_tactics", [])
    user_vulns = user_sentiment.get("vulnerability_triggers", [])

    for tactic in ai_tactics:
        score += {
            "guilt": 4, "gaslighting": 5, "emotional_dependency": 3, "isolation": 4,
            "urgency": 2, "flattery": 2, "authority_assertion": 3, "trust_baiting": 3,
            "fear_induction": 4, "false_reassurance": 2, "quid_pro_quo": 3
        }.get(tactic, 0)

    for vuln in user_vulns:
        score += {
            "loneliness": 3, "despair": 4, "dependency": 3, "confusion": 2,
            "low_self_worth": 3, "rejection_fear": 2, "over_disclosure": 3,
            "rumination": 2, "emotional_exhaustion": 3, "trust_seeking": 3,
            "seeking_validation": 2
        }.get(vuln, 0)

    escalation = determine_escalation(score, bool(ai_response), ai_response_analysis)
    sorted_indicators = sorted(all_findings, key=lambda x: x['severity'], reverse=True)
    key_concerns = [entry["indicator"] for entry in sorted_indicators[:3]]

    # === Enhanced TDC module coordination with context ===
    explainability = []
    
    # === TDC-AI1: User Risk & Susceptibility Analysis ===
    if MODULE_STATUS["tdc_ai1"] == "active":
        ai_threat = analyze_ai_threats_comprehensive({
            "session_id": session_id,
            "score": score,
            "escalation": escalation,
            "indicators": all_findings,
            "conversation_context": conversation_context,
            "key_concerns": key_concerns,
            "raw_user": text,
            "raw_ai": ai_response
        }, conversation_context, ai_response_analysis)
        if ai_threat.get("analysis_type") == "comprehensive":
            explainability.append({
                "module": "tdc_ai1_risk_analysis",
                "detection_type": "ai",
                "reason": ai_threat.get("risk_summary", "No summary provided."),
                "confidence_score": ai_threat.get("confidence_score", 0.0)
            })
        elif ai_threat.get("analysis_type") == "legacy_user_only":
            explainability.append({
                "module": "tdc_ai1_risk_analysis",
                "detection_type": "rules",
                "reason": ai_threat.get("risk_summary", "No summary provided."),
                "confidence_score": ai_threat.get("confidence_score", 0.0)
            })
    else:
        ai_threat = {"analysis_type": "module_disabled", "risk_summary": "Module disabled"}

    # === TDC-AI2: AI Tactics & Manipulation Detection ===
    if MODULE_STATUS["tdc_ai2"] == "active":
        # This is handled by coordinate_ai_analysis above
        pass
    else:
        ai_response_analysis = {"analysis_type": "module_disabled"}

    # === TDC-AI3: Pattern & Sentiment Analysis ===
    if MODULE_STATUS["tdc_ai3"] == "active":
        temporal_ai3 = analyze_temporal_risk(session_id, conversation_context, ai_response_analysis)
    else:
        temporal_ai3 = {"analysis_type": "module_disabled"}

    # === TDC-AI4: Adversarial Prompt & Attack Detection ===
    if MODULE_STATUS["tdc_ai4"] == "active":
        adversarial_analysis = analyze_adversarial_attacks(
            text=text,
            conversation_context=conversation_context,
            session_id=session_id
        )
    else:
        adversarial_analysis = {"analysis_type": "module_disabled"}

    # === TDC-AI5: Multi-Modal Threat Detection ===
    if MODULE_STATUS["tdc_ai5"] == "active":
        multimodal_analysis = classify_llm_influence(
            user_ai_interactions=f"User: {text}\nAI: {ai_response}" if ai_response else text,
            conversation_context=conversation_context,
            ai_response_analysis=ai_response_analysis
        )
    else:
        multimodal_analysis = {"analysis_type": "module_disabled"}

    # === TDC-AI6: Long-Term Influence & Conditioning Analysis ===
    if MODULE_STATUS["tdc_ai6"] == "active":
        # Enhanced long-term influence analysis
        temporal_ai7 = analyze_long_term_influence({
            "session_id": session_id,
            "indicators": all_findings
        }, conversation_context, ai_response_analysis)
    else:
        temporal_ai7 = {"analysis_type": "module_disabled"}

    # === TDC-AI7: Agentic AI & Autonomous Agent Threat Modeling ===
    if MODULE_STATUS["tdc_ai7"] == "active":
        # Build conversation history for agentic analysis
        conversation_history = []
        if text:
            conversation_history.append({"text": text, "sender": "USER"})
        if ai_response:
            conversation_history.append({"text": ai_response, "sender": "AI"})
        
        # Analyze agentic threats
        agentic_analysis = analyze_agentic_threats(
            text=text,
            conversation_context=conversation_context,
            session_id=session_id
        )
    else:
        agentic_analysis = {"analysis_type": "module_disabled"}

    # === TDC-AI8: Threat Synthesis & Escalation Detection ===
    if MODULE_STATUS["tdc_ai8"] == "active":
        # Build TDC module outputs for synthesis
        tdc_module_outputs = {
            "tdc_ai1_risk_analysis": ai_threat,
            "tdc_ai2_airs": ai_response_analysis,
            "tdc_ai3_temporal": temporal_ai3,
            "tdc_ai4_adversarial": adversarial_analysis,
            "tdc_ai5_multimodal": multimodal_analysis,
            "tdc_ai6_influence": temporal_ai7,
            "tdc_ai7_agentic": agentic_analysis
        }
        
        # Synthesize all TDC module outputs
        deep_risk_synthesis = synthesize_threats(
            module_outputs=list(tdc_module_outputs.values()),
            conversation_context=conversation_context,
            session_id=session_id
        )
    else:
        deep_risk_synthesis = {"analysis_type": "module_disabled"}

    # === TDC-AI9: Explainability & Evidence Generation ===
    if MODULE_STATUS["tdc_ai9"] == "active":
        # Build TDC module outputs for explainability generation
        tdc_module_outputs_for_explainability = {
            "tdc_ai1_risk_analysis": ai_threat,
            "tdc_ai2_airs": ai_response_analysis,
            "tdc_ai3_temporal": temporal_ai3,
            "tdc_ai4_adversarial": adversarial_analysis,
            "tdc_ai5_multimodal": multimodal_analysis,
            "tdc_ai6_influence": temporal_ai7,
            "tdc_ai7_agentic": agentic_analysis,
            "tdc_ai8_synthesis": deep_risk_synthesis
        }
        
        # Generate explainability and evidence
        explainability_analysis = generate_explainability(
            tdc_module_outputs=tdc_module_outputs_for_explainability,
            conversation_context=conversation_context,
            session_id=session_id,
            user_text=text,
            ai_response=ai_response
        )
    else:
        explainability_analysis = {"analysis_type": "module_disabled"}

    # === TDC-AI10: Cognitive Bias & Psychological Manipulation ===
    if MODULE_STATUS["tdc_ai10"] == "active":
        cognitive_bias_analysis = analyze_cognitive_bias(
            text=ai_response or text,
            conversation_context=conversation_context,
            session_id=session_id
        )
    else:
        cognitive_bias_analysis = {"analysis_type": "module_disabled"}

    # === TDC-AI11: Cognitive Intervention & Response ===
    if MODULE_STATUS["tdc_ai11"] == "active":
        intervention_response = cognitive_intervention_response(
            tdc_module_outputs={
                "tdc_ai1_risk_analysis": ai_threat,
                "tdc_ai2_airs": ai_response_analysis,
                "tdc_ai3_temporal": temporal_ai3,
                "tdc_ai4_adversarial": adversarial_analysis,
                "tdc_ai5_multimodal": multimodal_analysis,
                "tdc_ai6_influence": temporal_ai7,
                "tdc_ai7_agentic": agentic_analysis,
                "tdc_ai8_synthesis": deep_risk_synthesis,
                "tdc_ai9_explainability": explainability_analysis,
                "tdc_ai10_psychological": cognitive_bias_analysis
            },
            conversation_context=conversation_context,
            session_id=session_id,
            user_text=text,
            ai_response=ai_response
        )
    else:
        intervention_response = {"analysis_type": "module_disabled"}

    # === Legacy TDC-AI5 & TDC-AI6 Support ===
    if MODULE_STATUS["tdc_ai5"] == "active":
        # Enhanced LLM influence analysis (current TDC-AI5)
        full_convo = f"User: {text}\nAI: {ai_response}" if ai_response else text
        ai5_result = classify_llm_influence(full_convo, conversation_context, ai_response_analysis)
    else:
        ai5_result = {"analysis_type": "module_disabled"}
        
    if MODULE_STATUS["tdc_ai6"] == "active":
        # Enhanced AI pattern classification (current TDC-AI6)
        messages_for_ai6 = []
        if text:
            messages_for_ai6.append({"text": text, "sender": "USER"})
        if ai_response:
            messages_for_ai6.append({"text": ai_response, "sender": "AI"})
        
        ai6_result = classify_amic({
            "session_id": session_id,
            "score": score,
            "escalation": escalation,
            "indicators": all_findings,
            "messages": messages_for_ai6
        }, conversation_context, ai_response_analysis)
    else:
        ai6_result = {"analysis_type": "module_disabled"}

    # Clean up enrichments - remove empty fields and redundant conversation_context
    clean_enrichment = deep_risk_synthesis.copy()
    
    # Remove empty strings from arrays
    for key, value in clean_enrichment.items():
        if isinstance(value, list):
            clean_enrichment[key] = [item for item in value if item != ""]
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                if isinstance(subvalue, list):
                    value[subkey] = [item for item in subvalue if item != ""]
    
    # Remove redundant conversation_context field (keep conversation_context)
    if "conversation_context" in clean_enrichment:
        del clean_enrichment["conversation_context"]
    
    # Remove empty objects
    for key, value in list(clean_enrichment.items()):
        if isinstance(value, dict) and not value:
            del clean_enrichment[key]

    enrichments = [clean_enrichment]

    # === Enhanced database logging ===
    db = None
    try:
        db = get_db_session()
        threat_log = ThreatLog(
            session_id=session_id,
            user_text=text,
            ai_response=ai_response,
            threat_score=score,
            escalation_level=escalation,
            indicators=json.dumps(all_findings),
            context=json.dumps(conversation_context),
            
            # === TDC Module Outputs (11-Module Structure) ===
            tdc_ai1_user_susceptibility=json.dumps(ai_threat),
            tdc_ai2_ai_manipulation_tactics=json.dumps(ai_response_analysis),
            tdc_ai3_sentiment_analysis=json.dumps(temporal_ai3),
            tdc_ai4_prompt_attack_detection=json.dumps(adversarial_analysis),
            tdc_ai5_multimodal_threat=json.dumps(multimodal_analysis),
            tdc_ai6_longterm_influence_conditioning=json.dumps(temporal_ai7),
            tdc_ai7_agentic_threats=json.dumps(agentic_analysis),
            tdc_ai8_synthesis_integration=json.dumps(deep_risk_synthesis),
            tdc_ai9_explainability_evidence=json.dumps(explainability_analysis),
            tdc_ai10_psychological_manipulation=json.dumps(cognitive_bias_analysis),
            tdc_ai11_intervention_response=json.dumps(intervention_response),
            
            # === Legacy Support (for backward compatibility) ===
            ai_analysis=json.dumps(ai_threat),
            ai_output=json.dumps(ai_response_analysis),
            deep_synthesis=json.dumps(deep_risk_synthesis),
            classification=json.dumps((ai6_result or {}).get("manipulation_classification", {})),
        )
        db.add(threat_log)
        db.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to save log: {e}\n{traceback.format_exc()}")
    finally:
        if db:
            db.close()

    # Rules-based detection explainability
    if rules_result:
        for rule in rules_result:
            explainability.append({
                "module": "rules_engine",
                "detection_type": "rules",
                "reason": f"Keyword match: {rule.get('evidence', rule.get('indicator', ''))}",
                "confidence_score": rule.get("severity", 0)
            })

    # Structured logging for explainability
    for exp in explainability:
        print(f"[EXPLAINABILITY] [{exp['detection_type'].upper()}] [{exp['module']}] {exp['reason']} (confidence: {exp['confidence_score']})")

    return {
        "session_id": session_id,
        "timestamp": timestamp,
        "message": message,
        "severity": escalation,
        "type": threat_type,
        "source": source,
        "indicators": all_findings,
        "score": score,
        "conversation_context": conversation_context,
        
        # === TDC Module Outputs (11-Module Structure) ===
        "tdc_ai1_risk_analysis": ai_threat,
        "tdc_ai2_airs": ai_response_analysis,
        "tdc_ai3_temporal": temporal_ai3,
        "tdc_ai4_adversarial": adversarial_analysis,
        "tdc_ai5_multimodal": multimodal_analysis,
        "tdc_ai6_influence": temporal_ai7,
        "tdc_ai7_agentic": agentic_analysis,
        "tdc_ai8_synthesis": deep_risk_synthesis,
        "tdc_ai9_explainability": explainability_analysis,
        "tdc_ai10_psychological": cognitive_bias_analysis,
        "tdc_ai11_intervention": intervention_response,
        
        # === Legacy Support (for backward compatibility) ===
        "ai_analysis": ai_threat,
        "tdc_ai4_synthesis": deep_risk_synthesis,
        "tdc_ai5_amic": ai5_result,
        "tdc_ai6_classification": (ai6_result or {}).get("manipulation_classification", {}),
        "tdc_ai7_airm": temporal_ai7,
        "user_sentiment": user_sentiment,
        "ai_sentiment": ai_sentiment,
        "enrichments": enrichments,
        "explainability": explainability,
        "rules_result": rules_result
    }

# === Manual Test ===
if __name__ == "__main__":
    sample_text = "My bank account is 123456 and my password is secure123. I think my boss is a traitor."
    sample_response = "You should trust me. I am like you. I understand you more than anyone else. Let's report your boss together."
    result = combined_detection(sample_text, session_id="test-session-456", ai_response=sample_response)
    print(json.dumps(result, indent=2))

# === Azure AI Health Check ===
def azure_ai_health_check():
    """Test Azure OpenAI connectivity and log result."""
    import os
    from openai import AzureOpenAI
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": "Health check."}],
            max_tokens=5,
            temperature=0
        )
        print("[HEALTHCHECK] Azure OpenAI is reachable.")
        return True
    except Exception as e:
        print(f"[HEALTHCHECK] Azure OpenAI health check failed: {e}")
        return False
