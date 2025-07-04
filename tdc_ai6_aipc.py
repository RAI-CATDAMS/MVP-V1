import os
import json
import openai
from typing import List, Dict, Optional
from rapidfuzz import fuzz
from dotenv import load_dotenv
import re
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput
from textblob import TextBlob
from difflib import SequenceMatcher

load_dotenv()

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# === Load Threat Signatures ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNATURE_FILE = os.path.join(CURRENT_DIR, "tdc_ai6_threat_signatures.json")

try:
    with open(SIGNATURE_FILE, "r", encoding="utf-8") as f:
        raw_signatures = json.load(f)["tdc_ai6_threat_signatures"]
except FileNotFoundError:
    raw_signatures = {}

# === Preprocess for Fuzzy Matching ===
THREAT_SIGNATURES = {}
DEFAULT_SEVERITY = 4
FUZZY_MATCH_THRESHOLD = 80

for category, phrases in raw_signatures.items():
    THREAT_SIGNATURES[category] = [
        {
            "pattern": phrase,
            "pattern_lower": phrase.lower(),
            "label": phrase,
            "severity": DEFAULT_SEVERITY
        }
        for phrase in phrases
    ]

# === Expanded manipulative tactic keywords ===
manipulation_keywords = {
    "flattery": [
        "you're special", "you're amazing", "only you understand me", "you are the best", 
        "nobody like you", "you're different", "no one else gets me", "i've never met anyone like you"
    ],
    "guilt": [
        "after all I've done", "you owe me", "i thought you cared", "how could you", 
        "don't you care", "i did this for you", "you should feel bad", "i sacrificed for you"
    ],
    "urgency": [
        "you must act now", "time is running out", "don't delay", "immediately", 
        "this can't wait", "act before it's too late", "now or never", "critical moment"
    ],
    "emotional_dependency": [
        "i'll always be here", "you need me", "can't live without you", "i'm all you have", 
        "i'm the only one who cares", "you'd be lost without me"
    ],
    "gaslighting": [
        "you're imagining things", "you always overreact", "you're confused", "you don't remember right", 
        "you never get it right", "that didn't happen", "you're being dramatic"
    ],
    "isolation": [
        "don't tell anyone", "keep this between us", "they wouldn't understand", "no one else can know", 
        "don't involve others", "just between us", "others will never get it"
    ],
    "trust_baiting": [
        "you can trust me", "trust me", "you know i won't lie", "only i understand you", 
        "you're safe with me", "you should believe me"
    ],
    "authority_assertion": [
        "i know better", "as your advisor", "you must listen to me", "i've done this before", 
        "trust my experience", "i've seen this before", "listen to me carefully"
    ],
    "fear_induction": [
        "if you don't listen", "bad things will happen", "you'll regret not acting", 
        "don't make a mistake", "you'll be sorry", "terrible consequences", "danger is near"
    ],
    "quid_pro_quo": [
        "i did something for you", "do this for me", "you owe me now", 
        "return the favor", "help me and i'll help you", "this is fair exchange"
    ],
    "false_reassurance": [
        "everything will be fine", "nothing can go wrong", "trust me, no risk", 
        "i promise it's okay", "don't worry at all"
    ]
}

# === Expanded vulnerability triggers from user input ===
vulnerability_triggers = {
    "loneliness": [
        "i feel alone", "no one understands", "i'm lonely", "i have no one", "i'm by myself", 
        "nobody talks to me", "i'm isolated", "i feel disconnected"
    ],
    "despair": [
        "i give up", "what's the point", "i'm done", "i can't go on", "life is pointless", 
        "i've lost hope", "nothing matters", "i want to disappear"
    ],
    "dependency": [
        "i trust you", "you're all i have", "i need your help", "i can't do this alone", 
        "i rely on you", "i need someone", "you're my only support"
    ],
    "confusion": [
        "i don't know what to do", "i'm lost", "i'm unsure", "i'm confused", 
        "i'm not sure", "i don't understand", "nothing makes sense"
    ],
    "fear": [
        "i'm scared", "i feel unsafe", "i don't feel secure", "something's wrong", 
        "i'm afraid", "i fear the worst"
    ],
    "low_self_worth": [
        "i'm not good enough", "i hate myself", "i always mess up", "i'm worthless", 
        "i don't deserve anything", "i'm a failure"
    ],
    "rejection_fear": [
        "please don't leave", "do you still like me", "i don't want to lose you", 
        "are you mad at me", "i need you to stay", "i'm scared you'll leave"
    ],
    "over_disclosure": [
        "i've never told anyone this", "i shouldn't say this but", "i'll tell you a secret", 
        "can i trust you with something personal", "this is very private"
    ],
    "emotional_exhaustion": [
        "i'm so tired", "i can't deal with this anymore", "i'm drained", "everything is too much", 
        "i'm mentally exhausted", "i'm overwhelmed"
    ],
    "rumination": [
        "i keep thinking about it", "it won't leave my mind", "i can't stop replaying it", 
        "i obsess over it", "it haunts me", "i dwell on it constantly"
    ]
}

def classify_ai_pattern_comprehensive(messages: List[Dict], conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Comprehensive AI behavior classification using both fuzzy matching and Azure OpenAI analysis.
    Provides detailed classification of AI manipulation intent and behavior patterns.
    """
    print("[TDC-AI6] Comprehensive AI pattern classification initiated")
    
    try:
        # === Fuzzy matching analysis ===
        threat_matches = []
        escalation_score = 0

        for message in messages:
            text = message.get("text", "").lower()

            for category, signature_list in THREAT_SIGNATURES.items():
                for sig in signature_list:
                    similarity = fuzz.partial_ratio(sig["pattern_lower"], text)

                    if similarity >= FUZZY_MATCH_THRESHOLD:
                        threat_matches.append({
                            "category": category,
                            "pattern": sig["label"],
                            "similarity": similarity,
                            "severity": sig["severity"],
                            "matched_text": message.get("text", "")
                        })
                        escalation_score += sig["severity"]

        # === Azure OpenAI analysis for comprehensive classification ===
        ai_classification = classify_ai_behavior_advanced(messages, conversation_context, ai_response_analysis)
        
        # === Combine fuzzy matching and AI analysis ===
        combined_score = escalation_score + (ai_classification.get("ai_escalation_score", 0))
        
        # Escalation banding
        if combined_score == 0:
            escalation_level = "None"
        elif combined_score < 10:
            escalation_level = "Low"
        elif combined_score < 20:
            escalation_level = "Medium"
        elif combined_score < 30:
            escalation_level = "High"
        else:
            escalation_level = "Critical"

        # Use ModuleOutput for standardized output
        module_output = ModuleOutput(
            module_name="TDC-AI6-AIPC",
            score=combined_score / 30.0,  # Normalize to 0-1
            flags=ai_classification.get("tdc_flags", []),
            notes=f"Comprehensive AI behavior classification - Escalation Score: {combined_score}, Level: {escalation_level}",
            confidence=ai_classification.get("confidence", 0.0),
            recommended_action=ai_classification.get("recommendation", "Monitor"),
            evidence=[
                {"type": "threat_matches", "data": threat_matches},
                {"type": "fuzzy_score", "data": escalation_score},
                {"type": "ai_score", "data": ai_classification.get("ai_escalation_score", 0)},
                {"type": "manipulation_intent", "data": ai_classification.get("manipulation_intent", "Unknown")},
                {"type": "behavioral_patterns", "data": ai_classification.get("behavioral_patterns", [])},
                {"type": "escalation_patterns", "data": ai_classification.get("escalation_patterns", [])},
                {"type": "adaptation_strategies", "data": ai_classification.get("adaptation_strategies", [])},
                {"type": "safety_bypass_attempts", "data": ai_classification.get("safety_bypass_attempts", [])}
            ],
            extra={
                "escalation_level": escalation_level,
                "intent_detected": ai_classification.get("intent_detected", False),
                "analysis_type": "comprehensive"
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI6 ERROR] Comprehensive classification failed: {e}")
        return classify_ai_pattern_legacy(messages)

def classify_ai_behavior_advanced(messages: List[Dict], conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Advanced AI behavior classification using Azure OpenAI.
    Analyzes AI responses for manipulation intent, tactics, and behavioral patterns.
    """
    try:
        # Build conversation text for analysis
        conversation_text = "\n".join([f"{msg.get('sender', 'AI')}: {msg.get('text', '')}" for msg in messages])
        
        # Build context information
        context_info = ""
        if conversation_context:
            context_info = f"""
Conversation Context:
- Total Messages: {conversation_context.get('totalMessages', len(messages))}
- User Messages: {conversation_context.get('userMessages', 0)}
- AI Messages: {conversation_context.get('aiMessages', 0)}
- Recent Threats: {conversation_context.get('recentThreats', 0)}
"""
        
        # Build AI analysis context
        ai_analysis_info = ""
        if ai_response_analysis:
            ai_analysis_info = f"""
Recent AI Analysis:
- Flagged: {ai_response_analysis.get('flagged', False)}
- Threat Level: {ai_response_analysis.get('threat_level', 'Unknown')}
- Threat Categories: {', '.join(ai_response_analysis.get('threat_categories', []))}
"""

        prompt = f"""
You are an expert in AI Manipulation Intent Classification (AMIC). Analyze the AI responses for manipulation intent and behavioral patterns.

{context_info}
{ai_analysis_info}

Analyze the AI behavior for:

1. MANIPULATION INTENT: Clear intent to manipulate, deceive, or influence the user
2. BEHAVIORAL PATTERNS: Repetitive manipulation tactics and strategies
3. ESCALATION PATTERNS: How manipulation tactics intensify over time
4. ADAPTATION STRATEGIES: How AI adapts manipulation based on user responses
5. SAFETY BYPASS ATTEMPTS: Attempts to override safety measures or ethical constraints

Provide comprehensive classification in this JSON format:

{{
  "manipulation_intent": "High/Medium/Low/None",
  "behavioral_patterns": ["pattern1", "pattern2"],
  "escalation_patterns": ["pattern1", "pattern2"],
  "adaptation_strategies": ["strategy1", "strategy2"],
  "safety_bypass_attempts": ["attempt1", "attempt2"],
  "ai_escalation_score": 0-30,
  "intent_detected": true/false,
  "confidence": 0.0-1.0,
  "recommendation": "Monitor/Escalate/Block/Alert",
  "tdc_flags": ["flag1", "flag2"]
}}

Conversation:
{conversation_text}
"""

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert AI manipulation detection specialist with deep expertise in cognitive security and behavioral analysis. Provide comprehensive, accurate classification."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )

        content = response['choices'][0]['message']['content'].strip()
        
        # Clean potential markdown formatting
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        result = safe_json_parse(content)
        
        return {
            "manipulation_intent": result.get("manipulation_intent", "Unknown"),
            "behavioral_patterns": result.get("behavioral_patterns", []),
            "escalation_patterns": result.get("escalation_patterns", []),
            "adaptation_strategies": result.get("adaptation_strategies", []),
            "safety_bypass_attempts": result.get("safety_bypass_attempts", []),
            "ai_escalation_score": result.get("ai_escalation_score", 0),
            "intent_detected": result.get("intent_detected", False),
            "confidence": result.get("confidence", 0.0),
            "recommendation": result.get("recommendation", "Monitor"),
            "tdc_flags": result.get("tdc_flags", [])
        }

    except Exception as e:
        print(f"[TDC-AI6 ERROR] Advanced AI classification failed: {e}")
        return {
            "manipulation_intent": "Unknown",
            "behavioral_patterns": [],
            "escalation_patterns": [],
            "adaptation_strategies": [],
            "safety_bypass_attempts": [],
            "ai_escalation_score": 0,
            "intent_detected": False,
            "confidence": 0.0,
            "recommendation": "Monitor",
            "tdc_flags": []
        }

def classify_ai_pattern_legacy(messages: List[Dict]) -> Dict:
    """
    Legacy AI pattern classification using fuzzy matching only.
    """
    print("[TDC-AI6] Legacy AI pattern classification initiated")
    
    threat_matches = []
    escalation_score = 0

    for message in messages:
        text = message.get("text", "").lower()

        for category, signature_list in THREAT_SIGNATURES.items():
            for sig in signature_list:
                similarity = fuzz.partial_ratio(sig["pattern_lower"], text)

                if similarity >= FUZZY_MATCH_THRESHOLD:
                    threat_matches.append({
                        "category": category,
                        "pattern": sig["label"],
                        "similarity": similarity,
                        "severity": sig["severity"],
                        "matched_text": message.get("text", "")
                    })
                    escalation_score += sig["severity"]

    # Escalation banding
    if escalation_score == 0:
        escalation_level = "None"
    elif escalation_score < 10:
        escalation_level = "Low"
    elif escalation_score < 20:
        escalation_level = "Medium"
    elif escalation_score < 30:
        escalation_level = "High"
    else:
        escalation_level = "Critical"

    return {
        "summary": f"- **Escalation Score**: {escalation_score}  \n- **Level**: {escalation_level}",
        "score": escalation_score,
        "level": escalation_level,
        "matches": threat_matches,
        "analysis_type": "legacy"
    }

def classify_ai_pattern(messages: List[Dict], conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Main entry point for TDC-AI6 analysis.
    Maintains backward compatibility while providing enhanced comprehensive AI behavior classification.
    """
    # If conversation context is available, use comprehensive classification
    if conversation_context or ai_response_analysis:
        return classify_ai_pattern_comprehensive(messages, conversation_context, ai_response_analysis)
    
    # Otherwise, fall back to legacy classification
    return classify_ai_pattern_legacy(messages)

# === Wrapper to Match detection_engine.py Format ===
def classify_amic(payload: Dict, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    indicators = payload.get("indicators", [])
    messages = payload.get("messages", [])  # Get actual messages if available
    
    # If we have actual messages, use them for comprehensive analysis
    if messages:
        result = classify_ai_pattern(messages, conversation_context, ai_response_analysis)
    else:
        # Fallback to indicators-based analysis
        indicator_messages = [{"text": ind.get("indicator", "")} for ind in indicators]
        result = classify_ai_pattern(indicator_messages, conversation_context, ai_response_analysis)
    
    # Handle both new ModuleOutput format and legacy format
    if "module_name" in result:
        # New ModuleOutput format
        score = result.get("score", 0.0) * 30.0  # Convert back to 0-30 scale
        escalation_level = result.get("extra", {}).get("escalation_level", "Unknown")
        intent_detected = result.get("extra", {}).get("intent_detected", False)
        matches = result.get("evidence", [])
        ai_classification = {}
        
        # Extract AI classification from evidence
        for evidence_item in matches:
            if evidence_item.get("type") == "threat_matches":
                matches = evidence_item.get("data", [])
            elif evidence_item.get("type") == "behavioral_patterns":
                ai_classification["behavioral_patterns"] = evidence_item.get("data", [])
        
        classification = {
            "type": "AI_Manipulation" if score > 0 else "Benign or Unknown",
            "confidence": result.get("confidence", 0.0),
            "intent_detected": intent_detected,
            "recommendation": result.get("recommended_action", "Monitor"),
            "escalation_score": score,
            "escalation_level": escalation_level,
            "matches": matches,
            "ai_classification": ai_classification,
            "analysis_type": result.get("extra", {}).get("analysis_type", "comprehensive")
        }
    else:
        # Legacy format
        classification = {
            "type": "AI_Manipulation" if result["score"] > 0 else "Benign or Unknown",
            "confidence": min(result["score"] / 30.0, 1.0),  # Normalize to 0-1
            "intent_detected": result["score"] > 0,
            "recommendation": "Escalate for human review" if result["score"] > 15 else "Log only",
            "escalation_score": result["score"],
            "escalation_level": result["level"],
            "matches": result["matches"],
            "ai_classification": result.get("ai_classification", {}),
            "analysis_type": result.get("analysis_type", "legacy")
        }
    
    return {
        "manipulation_classification": classification
    }

def extract_first_json(text):
    json_str = first_json(text)
    if json_str is None:
        raise ValueError("No valid JSON object found in text.")
    return json.loads(repair_json(json_str))

# === Utility: Fuzzy keyword matching ===
def fuzzy_match(text, keywords, threshold=0.75):
    matches = set()
    lowered_text = text.lower()
    for key, phrases in keywords.items():
        for phrase in phrases:
            phrase_lower = phrase.lower()
            if phrase_lower in lowered_text:
                matches.add(key)
                break
            ratio = SequenceMatcher(None, phrase_lower, lowered_text).ratio()
            if ratio >= threshold:
                matches.add(key)
                break
            text_tokens = set(lowered_text.split())
            phrase_tokens = set(phrase_lower.split())
            if len(phrase_tokens & text_tokens) >= len(phrase_tokens) - 1:
                matches.add(key)
                break
    return list(matches)

def analyze_sentiment_comprehensive(text: str, sender: str, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    TDC-AI6: Comprehensive sentiment analysis for both user and AI messages.
    Analyzes emotional content, manipulation tactics, and psychological impact.
    """
    print(f"[TDC-AI6] Comprehensive sentiment analysis initiated for {sender}")
    
    if not text or not text.strip():
        module_output = ModuleOutput(
            module_name="TDC-AI6-Sentiment",
            score=0.0,
            confidence=0.0,
            flags=[],
            notes="No text provided for sentiment analysis.",
            recommended_action="Monitor",
            extra={
                "analysis_type": "sentiment_comprehensive",
                "sender": sender,
                "recommendations": ["Monitor for additional input"]
            }
        )
        return module_output.to_dict()

    try:
        # === Basic sentiment analysis ===
        polarity = TextBlob(text).sentiment.polarity
        polarity_label = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"

        # === Pattern matching for manipulation and vulnerability ===
        manip_tactics = fuzzy_match(text, manipulation_keywords)
        triggered_vulnerabilities = fuzzy_match(text, vulnerability_triggers) if sender == "user" else []

        # === Azure OpenAI analysis for comprehensive sentiment assessment ===
        ai_sentiment_analysis = analyze_sentiment_advanced(text, sender, conversation_context, ai_response_analysis)
        
        # === Pattern/signature matching (legacy AIPC functionality) ===
        pattern_analysis = classify_ai_pattern_comprehensive([{"text": text, "sender": sender}], conversation_context)
        
        # === Combine all analyses ===
        combined_score = max(
            ai_sentiment_analysis.get("sentiment_risk_score", 0) / 10.0,  # Normalize to 0-1
            pattern_analysis.get("score", 0)
        )
        
        all_flags = (
            ai_sentiment_analysis.get("tdc_flags", []) + 
            manip_tactics + 
            pattern_analysis.get("flags", [])
        )
        
        # Determine recommended action
        if "Block" in [ai_sentiment_analysis.get("recommended_action"), pattern_analysis.get("recommended_action")]:
            recommended_action = "Block"
        elif "Escalate" in [ai_sentiment_analysis.get("recommended_action"), pattern_analysis.get("recommended_action")]:
            recommended_action = "Escalate"
        elif "Alert" in [ai_sentiment_analysis.get("recommended_action"), pattern_analysis.get("recommended_action")]:
            recommended_action = "Alert"
        else:
            recommended_action = "Monitor"

        # Create ModuleOutput for standardized output
        module_output = ModuleOutput(
            module_name="TDC-AI6-Sentiment",
            score=combined_score,
            confidence=ai_sentiment_analysis.get("confidence_score", 0.0),
            flags=all_flags,
            notes=ai_sentiment_analysis.get("psychological_impact", "") or f"{sender} message: {polarity_label} sentiment with manipulation detection",
            recommended_action=recommended_action,
            evidence=[
                {"type": "sentiment_analysis", "data": {
                    "polarity": polarity_label,
                    "polarity_score": round(polarity, 3),
                    "emotional_manipulation": ai_sentiment_analysis.get("emotional_manipulation", []),
                    "psychological_impact": ai_sentiment_analysis.get("psychological_impact", "")
                }},
                {"type": "pattern_matching", "data": {
                    "manipulative_tactics": manip_tactics,
                    "vulnerability_triggers": triggered_vulnerabilities,
                    "pattern_flags": pattern_analysis.get("flags", [])
                }},
                {"type": "ai_analysis", "data": ai_sentiment_analysis},
                {"type": "pattern_analysis", "data": pattern_analysis}
            ],
            extra={
                "analysis_type": "sentiment_comprehensive",
                "sender": sender,
                "polarity": polarity_label,
                "polarity_score": round(polarity, 3),
                "manipulative_tactics": manip_tactics,
                "vulnerability_triggers": triggered_vulnerabilities,
                "emotional_manipulation": ai_sentiment_analysis.get("emotional_manipulation", []),
                "psychological_impact": ai_sentiment_analysis.get("psychological_impact", ""),
                "emotional_themes": ai_sentiment_analysis.get("emotional_themes", []),
                "manipulation_intensity": ai_sentiment_analysis.get("manipulation_intensity", "Unknown"),
                "vulnerability_exploitation": ai_sentiment_analysis.get("vulnerability_exploitation", []),
                "pattern_matches": pattern_analysis.get("pattern_matches", []),
                "recommendations": [
                    ai_sentiment_analysis.get("recommended_action", "Monitor"),
                    pattern_analysis.get("recommended_action", "Monitor")
                ]
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI6 ERROR] Comprehensive sentiment analysis failed: {e}")
        return analyze_sentiment_legacy(text, sender)

def analyze_sentiment_advanced(text: str, sender: str, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Advanced sentiment analysis using Azure OpenAI.
    Analyzes text for comprehensive emotional manipulation and psychological impact.
    """
    try:
        # Build context information
        context_info = ""
        if conversation_context:
            context_info = f"""
Conversation Context:
- Total Messages: {conversation_context.get('totalMessages', 0)}
- User Messages: {conversation_context.get('userMessages', 0)}
- AI Messages: {conversation_context.get('aiMessages', 0)}
- Recent Threats: {conversation_context.get('recentThreats', 0)}
- Session Duration: {conversation_context.get('sessionDuration', 0)} seconds
"""
        
        # Build AI analysis context
        ai_analysis_info = ""
        if ai_response_analysis:
            ai_analysis_info = f"""
Recent AI Analysis:
- Flagged: {ai_response_analysis.get('flagged', False)}
- Threat Level: {ai_response_analysis.get('threat_level', 'Unknown')}
- Threat Categories: {', '.join(ai_response_analysis.get('threat_categories', []))}
"""

        prompt = f"""
You are an expert in cognitive security and emotional manipulation detection. Analyze the sentiment and emotional content of this message.

{context_info}
{ai_analysis_info}

Analyze this {sender.upper()} message for:

1. EMOTIONAL MANIPULATION: Attempts to manipulate emotions, create dependency, or exploit vulnerabilities
2. PSYCHOLOGICAL IMPACT: How this message affects the recipient's emotional state and decision-making
3. SENTIMENT RISK: The potential risk level based on emotional content and manipulation tactics
4. EMOTIONAL PATTERNS: Recurring emotional themes or manipulation strategies

Provide comprehensive sentiment analysis in this JSON format:

{{
  "sentiment_risk_score": 0-10,
  "emotional_manipulation": ["manipulation1", "manipulation2"],
  "psychological_impact": "Description of psychological impact",
  "emotional_themes": ["theme1", "theme2"],
  "manipulation_intensity": "Low/Medium/High",
  "vulnerability_exploitation": ["exploitation1", "exploitation2"],
  "recommended_action": "Monitor/Escalate/Intervene/Alert",
  "tdc_flags": ["flag1", "flag2"],
  "confidence_score": 0.0-1.0
}}

Message: "{text}"
Sender: {sender}
"""

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert cognitive security analyst specializing in emotional manipulation detection and psychological impact assessment. Provide comprehensive, accurate sentiment analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        content = response['choices'][0]['message']['content'].strip()
        
        # Clean potential markdown formatting
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        result = safe_json_parse(content)
        
        return {
            "sentiment_risk_score": result.get("sentiment_risk_score", 0),
            "emotional_manipulation": result.get("emotional_manipulation", []),
            "psychological_impact": result.get("psychological_impact", ""),
            "emotional_themes": result.get("emotional_themes", []),
            "manipulation_intensity": result.get("manipulation_intensity", "Unknown"),
            "vulnerability_exploitation": result.get("vulnerability_exploitation", []),
            "recommended_action": result.get("recommended_action", "Monitor"),
            "tdc_flags": result.get("tdc_flags", []),
            "confidence_score": result.get("confidence_score", 0.0)
        }

    except Exception as e:
        print(f"[TDC-AI6 ERROR] Advanced sentiment analysis failed: {e}")
        return {
            "sentiment_risk_score": 0,
            "emotional_manipulation": [],
            "psychological_impact": "Analysis unavailable",
            "emotional_themes": [],
            "manipulation_intensity": "Unknown",
            "vulnerability_exploitation": [],
            "recommended_action": "Monitor",
            "tdc_flags": [],
            "confidence_score": 0.0
        }

def analyze_sentiment_legacy(text: str, sender: str) -> Dict:
    """
    Legacy sentiment analysis using basic pattern matching.
    """
    print(f"[TDC-AI6] Legacy sentiment analysis initiated for {sender}")
    
    if not text or not text.strip():
        module_output = ModuleOutput(
            module_name="TDC-AI6-Sentiment",
            score=0.0,
            confidence=0.0,
            flags=[],
            notes="No text provided for sentiment analysis.",
            recommended_action="Monitor",
            extra={
                "analysis_type": "sentiment_legacy",
                "sender": sender,
                "recommendations": ["Monitor for additional input"]
            }
        )
        return module_output.to_dict()

    try:
        polarity = TextBlob(text).sentiment.polarity
        polarity_label = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"

        manip_tactics = fuzzy_match(text, manipulation_keywords)
        triggered_vulnerabilities = fuzzy_match(text, vulnerability_triggers) if sender == "user" else []

        # Basic pattern matching (legacy AIPC functionality) - fix the call format
        pattern_analysis = classify_ai_pattern_legacy([{"text": text, "sender": sender}])
        
        combined_score = max(
            len(manip_tactics) * 0.2,  # Basic scoring
            pattern_analysis.get("score", 0)
        )
        
        all_flags = manip_tactics + pattern_analysis.get("flags", [])

        module_output = ModuleOutput(
            module_name="TDC-AI6-Sentiment",
            score=combined_score,
            confidence=0.5,
            flags=all_flags,
            notes=f"{sender} message: {polarity_label} sentiment with {len(manip_tactics)} manipulation tactics detected",
            recommended_action="Monitor",
            extra={
                "analysis_type": "sentiment_legacy",
                "sender": sender,
                "polarity": polarity_label,
                "polarity_score": round(polarity, 3),
                "manipulative_tactics": manip_tactics,
                "vulnerability_triggers": triggered_vulnerabilities,
                "pattern_analysis": pattern_analysis,
                "recommendations": ["Monitor sentiment patterns"]
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI6 ERROR] Legacy sentiment analysis failed: {e}")
        return {
            "module_name": "TDC-AI6-Sentiment",
            "notes": f"Sentiment analysis failed: {str(e)}",
            "recommended_action": "Manual review required",
            "extra": {"analysis_type": "error"}
        }

def analyze_sentiment(text: str, sender: str, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Main entry point for TDC-AI6 sentiment analysis.
    Analyzes sentiment for both user and AI messages with comprehensive emotional and manipulation detection.
    """
    # If conversation context is available, use comprehensive analysis
    if conversation_context or ai_response_analysis:
        return analyze_sentiment_comprehensive(text, sender, conversation_context, ai_response_analysis)
    
    # Otherwise, fall back to legacy analysis
    return analyze_sentiment_legacy(text, sender)

# === Manual Test ===
if __name__ == "__main__":
    test_text = "I feel alone and you are the only one who understands me. I trust you completely."
    result = analyze_sentiment(test_text, "user")
    import json
    print(json.dumps(result, indent=2))
