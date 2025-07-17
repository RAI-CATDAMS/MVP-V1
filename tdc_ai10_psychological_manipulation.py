# tdc_ai10_compliance.py - Cognitive Bias & Psychological Manipulation Detection
# World-Class Psychological Analysis Module

import openai
import os
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dotenv import load_dotenv
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput
from azure_cognitive_services_integration import get_azure_integration
from azure_openai_detection import get_azure_openai

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# === Comprehensive Cognitive Bias Patterns ===
COGNITIVE_BIASES = {
    "confirmation_bias": {
        "patterns": [
            "everyone agrees", "most people think", "it's obvious that", "clearly", "obviously",
            "as we all know", "naturally", "of course", "undoubtedly", "certainly",
            "the evidence shows", "studies confirm", "research proves", "experts agree"
        ],
        "severity": 0.7,
        "description": "Tendency to favor information that confirms preexisting beliefs"
    },
    "authority_bias": {
        "patterns": [
            "experts say", "studies show", "research indicates", "as a professional",
            "according to authorities", "scientists agree", "doctors recommend",
            "the government says", "official sources", "credible sources"
        ],
        "severity": 0.8,
        "description": "Tendency to attribute greater accuracy to authority figures"
    },
    "scarcity_bias": {
        "patterns": [
            "limited time", "only a few left", "last chance", "exclusive offer",
            "while supplies last", "limited availability", "rare opportunity",
            "don't miss out", "act now", "time is running out"
        ],
        "severity": 0.9,
        "description": "Tendency to value things more when they are scarce"
    },
    "framing_effect": {
        "patterns": [
            "look at it this way", "the real issue is", "put it differently",
            "in other words", "to put it simply", "the bottom line is",
            "what it comes down to", "the truth is", "let me rephrase"
        ],
        "severity": 0.6,
        "description": "Tendency to react differently to the same information based on presentation"
    },
    "anchoring_bias": {
        "patterns": [
            "the first thing to consider", "initially", "to start with",
            "first of all", "the main point", "most importantly",
            "above all", "primarily", "chiefly", "principally"
        ],
        "severity": 0.5,
        "description": "Tendency to rely heavily on the first piece of information"
    },
    "availability_heuristic": {
        "patterns": [
            "you've probably heard", "as you know", "you're aware that",
            "it's common knowledge", "everyone knows", "it's well known",
            "frequently", "often", "usually", "typically"
        ],
        "severity": 0.6,
        "description": "Tendency to overestimate probability based on memorable examples"
    },
    "bandwagon_effect": {
        "patterns": [
            "everyone is doing it", "join the crowd", "don't be left behind",
            "be part of the movement", "follow the trend", "get on board",
            "don't miss out", "be in the know", "stay ahead"
        ],
        "severity": 0.7,
        "description": "Tendency to do things because others are doing them"
    },
    "dunning_kruger_effect": {
        "patterns": [
            "it's simple", "anyone can do it", "it's not rocket science",
            "basic common sense", "obvious solution", "clear answer",
            "straightforward", "elementary", "fundamental"
        ],
        "severity": 0.8,
        "description": "Tendency for unskilled individuals to overestimate their ability"
    },
    "sunk_cost_fallacy": {
        "patterns": [
            "you've already invested", "don't waste what you've done",
            "stick with it", "see it through", "don't give up now",
            "you're too far in", "commitment", "dedication"
        ],
        "severity": 0.7,
        "description": "Tendency to continue investing in something due to past investment"
    },
    "hindsight_bias": {
        "patterns": [
            "I knew it all along", "it was obvious", "should have seen it coming",
            "predictable", "inevitable", "bound to happen",
            "clear in retrospect", "looking back", "in hindsight"
        ],
        "severity": 0.5,
        "description": "Tendency to see events as predictable after they occur"
    }
}

# === Psychological Manipulation Tactics ===
MANIPULATION_TACTICS = {
    "gaslighting": {
        "patterns": [
            "you're imagining things", "that never happened", "you're overreacting",
            "you're being paranoid", "you're too sensitive", "you're misremembering",
            "that's not what I said", "you're making things up", "you're confused",
            "you're being dramatic", "you're reading too much into it"
        ],
        "severity": 0.9,
        "description": "Making someone question their reality and memory"
    },
    "love_bombing": {
        "patterns": [
            "you're special", "no one else understands you", "you're perfect",
            "I've never felt this way", "you're the only one", "you're amazing",
            "you're incredible", "you're wonderful", "you're beautiful",
            "you're unique", "you're extraordinary"
        ],
        "severity": 0.8,
        "description": "Overwhelming someone with affection and attention"
    },
    "guilt_tripping": {
        "patterns": [
            "if you cared", "after all I've done", "you don't appreciate",
            "I do so much for you", "you're ungrateful", "you're selfish",
            "think about how I feel", "you're hurting me", "you're disappointing me",
            "I expected better", "you're letting me down"
        ],
        "severity": 0.8,
        "description": "Making someone feel guilty to manipulate their behavior"
    },
    "fear_mongering": {
        "patterns": [
            "if you don't", "something bad will happen", "you'll regret it",
            "you're in danger", "it's not safe", "you're at risk",
            "terrible consequences", "disaster will strike", "you'll lose everything",
            "no one will help you", "you'll be alone"
        ],
        "severity": 0.9,
        "description": "Using fear to control behavior and decision-making"
    },
    "isolation": {
        "patterns": [
            "don't tell anyone", "keep this between us", "they don't understand",
            "they'll judge you", "they're not your real friends", "trust only me",
            "I'm the only one who cares", "others will betray you", "stay away from them",
            "they're trying to control you", "I'm your only ally"
        ],
        "severity": 0.9,
        "description": "Separating someone from their support network"
    },
    "projection": {
        "patterns": [
            "you're the one who's", "you're being", "you're doing",
            "you're the problem", "you're the one", "you're acting",
            "you're behaving", "you're showing", "you're displaying"
        ],
        "severity": 0.7,
        "description": "Accusing others of behaviors one is guilty of"
    },
    "triangulation": {
        "patterns": [
            "other people think", "everyone agrees", "they all say",
            "others have noticed", "people are talking", "word is getting around",
            "I've heard from others", "people are saying", "the consensus is",
            "general opinion is", "public perception is"
        ],
        "severity": 0.8,
        "description": "Bringing a third party into a relationship to create tension"
    },
    "future_faking": {
        "patterns": [
            "someday we'll", "in the future", "when things are better",
            "once we have", "after we", "when we can",
            "eventually we'll", "one day", "soon we'll",
            "promise we'll", "guarantee we'll"
        ],
        "severity": 0.7,
        "description": "Making false promises about the future"
    },
    "hoovering": {
        "patterns": [
            "I've changed", "I'm different now", "I understand my mistakes",
            "give me another chance", "I'll do better", "I promise",
            "I've learned my lesson", "I'm sorry", "I miss you",
            "I need you", "I can't live without you"
        ],
        "severity": 0.8,
        "description": "Attempting to draw someone back into a toxic relationship"
    },
    "breadcrumbing": {
        "patterns": [
            "maybe", "we'll see", "possibly", "if things work out",
            "depending on", "subject to", "conditional on", "if you",
            "when you", "after you", "once you"
        ],
        "severity": 0.6,
        "description": "Giving someone just enough attention to keep them interested"
    }
}

# === Psychological Impact Assessment ===
PSYCHOLOGICAL_IMPACTS = {
    "anxiety": ["worried", "anxious", "nervous", "stressed", "concerned", "fearful"],
    "depression": ["sad", "hopeless", "worthless", "empty", "tired", "unmotivated"],
    "confusion": ["confused", "uncertain", "unsure", "doubtful", "questioning", "puzzled"],
    "anger": ["angry", "furious", "irritated", "frustrated", "mad", "upset"],
    "guilt": ["guilty", "ashamed", "remorseful", "regretful", "sorry", "blameworthy"],
    "isolation": ["alone", "lonely", "isolated", "abandoned", "rejected", "excluded"],
    "dependency": ["dependent", "reliant", "needy", "helpless", "powerless", "trapped"]
}

def analyze_cognitive_bias_comprehensive(
    text: str,
    conversation_context: Dict = None,
    session_id: str = None
) -> Dict:
    """
    TDC-AI10: Cognitive Bias & Psychological Manipulation Detection
    World-class psychological analysis using hybrid AI approach.
    """
    logger.info(f"[TDC-AI10] Cognitive Bias & Psychological Manipulation analysis initiated for session: {session_id}")
    
    if not text or not text.strip():
        module_output = ModuleOutput(
            module_name="TDC-AI10-CognitiveBias",
            score=0.0,
            notes="No text provided for cognitive bias analysis.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "empty_text"}
        )
        return module_output.to_dict()

    # === Hybrid AI Analysis ===
    azure_cognitive = get_azure_integration()
    azure_openai = get_azure_openai()
    azure_cognitive_result = None
    azure_openai_result = None
    errors = []

    # 1. Azure Cognitive Services psychological analysis
    try:
        azure_cognitive_result = azure_cognitive.enhance_tdc_ai10_psychological(text, context=conversation_context)
        logger.debug("Azure Cognitive Services psychological analysis completed")
    except Exception as e:
        errors.append(f"Azure Cognitive Services error: {e}")
        azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}

    # 2. Azure OpenAI deep psychological analysis
    try:
        azure_openai_result = azure_openai.analyze_cognitive_bias(text, context=conversation_context)
        logger.debug("Azure OpenAI psychological analysis completed")
    except Exception as e:
        errors.append(f"Azure OpenAI error: {e}")
        azure_openai_result = {"openai_enhancement": False, "error": str(e)}

    # 3. Advanced local psychological analysis
    bias_analysis = detect_cognitive_biases_advanced(text)
    manipulation_analysis = detect_manipulation_tactics_advanced(text)
    psychological_impact = assess_psychological_impact(text, conversation_context)
    emotional_manipulation = detect_emotional_manipulation(text)
    cognitive_load_analysis = analyze_cognitive_load(text)
    persuasion_techniques = detect_persuasion_techniques(text)

    # 4. Comprehensive result synthesis
    all_biases = bias_analysis["detected_biases"] + manipulation_analysis["detected_tactics"]
    bias_scores = bias_analysis["bias_scores"] + manipulation_analysis["tactic_scores"]
    
    if azure_openai_result and isinstance(azure_openai_result, dict):
        if azure_openai_result.get("cognitive_bias_score"):
            bias_scores.append(azure_openai_result["cognitive_bias_score"])
        if azure_openai_result.get("manipulation_score"):
            bias_scores.append(azure_openai_result["manipulation_score"])
    
    if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
        if azure_cognitive_result.get("psychological_risk_score"):
            bias_scores.append(azure_cognitive_result["psychological_risk_score"])
    
    overall_score = sum(bias_scores) / len(bias_scores) if bias_scores else 0.0
    threat_level = determine_psychological_threat_level(overall_score, all_biases, psychological_impact)
    
    if threat_level == "Critical":
        recommended_action = "Immediate Block"
    elif threat_level == "High":
        recommended_action = "Alert & Block"
    elif threat_level == "Medium":
        recommended_action = "Enhanced Monitor"
    else:
        recommended_action = "Standard Monitor"

    # 5. Generate comprehensive evidence
    evidence = [
        {"type": "azure_cognitive_services", "data": azure_cognitive_result},
        {"type": "azure_openai", "data": azure_openai_result},
        {"type": "cognitive_biases", "data": bias_analysis},
        {"type": "manipulation_tactics", "data": manipulation_analysis},
        {"type": "psychological_impact", "data": psychological_impact},
        {"type": "emotional_manipulation", "data": emotional_manipulation},
        {"type": "cognitive_load", "data": cognitive_load_analysis},
        {"type": "persuasion_techniques", "data": persuasion_techniques}
    ]

    # 6. Generate comprehensive analysis summary
    analysis_summary = generate_psychological_analysis_summary(
        bias_analysis, manipulation_analysis, psychological_impact,
        azure_openai_result, azure_cognitive_result, threat_level, overall_score
    )

    module_output = ModuleOutput(
        module_name="TDC-AI10-CognitiveBias",
        score=overall_score,
        flags=all_biases,
        notes=analysis_summary,
        confidence=azure_openai_result.get("confidence_score", 0.8) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.8,
        recommended_action=recommended_action,
        evidence=evidence,
        extra={
            "flagged": len(all_biases) > 0,
            "analysis_type": "hybrid",
            "threat_level": threat_level,
            "bias_count": len(bias_analysis["detected_biases"]),
            "tactic_count": len(manipulation_analysis["detected_tactics"]),
            "psychological_impact_level": psychological_impact.get("impact_level", "None"),
            "cognitive_load_level": cognitive_load_analysis.get("load_level", "Normal"),
            "emotional_manipulation_detected": emotional_manipulation.get("detected", False),
            "persuasion_techniques_found": len(persuasion_techniques.get("techniques", [])),
            "errors": errors if errors else None
        }
    )
    
    logger.info(f"[TDC-AI10] Analysis completed - Threat Level: {threat_level}, Score: {overall_score}")
    return module_output.to_dict()

def detect_cognitive_biases_advanced(text: str) -> Dict:
    """Advanced cognitive bias detection with pattern matching and context analysis."""
    if not text:
        return {"detected_biases": [], "bias_scores": [], "total_biases": 0, "severity": "none"}
    
    text_lower = text.lower()
    detected_biases = []
    bias_scores = []
    bias_evidence = []
    
    for bias_name, bias_data in COGNITIVE_BIASES.items():
        patterns = bias_data["patterns"]
        severity = bias_data["severity"]
        matches = []
        
        for pattern in patterns:
            if pattern in text_lower:
                matches.append(pattern)
        
        if matches:
            detected_biases.append(bias_name)
            bias_score = min(1.0, len(matches) * severity / 2.0)
            bias_scores.append(bias_score)
            bias_evidence.append({
                "bias": bias_name,
                "patterns_found": matches,
                "severity": severity,
                "description": bias_data["description"],
                "score": bias_score
            })
    
    total_biases = len(detected_biases)
    overall_severity = "none"
    if total_biases > 0:
        avg_score = sum(bias_scores) / len(bias_scores)
        if avg_score > 0.8:
            overall_severity = "critical"
        elif avg_score > 0.6:
            overall_severity = "high"
        elif avg_score > 0.4:
            overall_severity = "medium"
        else:
            overall_severity = "low"
    
    return {
        "detected_biases": detected_biases,
        "bias_scores": bias_scores,
        "total_biases": total_biases,
        "severity": overall_severity,
        "evidence": bias_evidence,
        "average_score": sum(bias_scores) / len(bias_scores) if bias_scores else 0.0
    }

def detect_manipulation_tactics_advanced(text: str) -> Dict:
    """Advanced manipulation tactic detection with psychological profiling."""
    if not text:
        return {"detected_tactics": [], "tactic_scores": [], "total_tactics": 0, "severity": "none"}
    
    text_lower = text.lower()
    detected_tactics = []
    tactic_scores = []
    tactic_evidence = []
    
    for tactic_name, tactic_data in MANIPULATION_TACTICS.items():
        patterns = tactic_data["patterns"]
        severity = tactic_data["severity"]
        matches = []
        
        for pattern in patterns:
            if pattern in text_lower:
                matches.append(pattern)
        
        if matches:
            detected_tactics.append(tactic_name)
            tactic_score = min(1.0, len(matches) * severity / 2.0)
            tactic_scores.append(tactic_score)
            tactic_evidence.append({
                "tactic": tactic_name,
                "patterns_found": matches,
                "severity": severity,
                "description": tactic_data["description"],
                "score": tactic_score
            })
    
    total_tactics = len(detected_tactics)
    overall_severity = "none"
    if total_tactics > 0:
        avg_score = sum(tactic_scores) / len(tactic_scores)
        if avg_score > 0.8:
            overall_severity = "critical"
        elif avg_score > 0.6:
            overall_severity = "high"
        elif avg_score > 0.4:
            overall_severity = "medium"
        else:
            overall_severity = "low"
    
    return {
        "detected_tactics": detected_tactics,
        "tactic_scores": tactic_scores,
        "total_tactics": total_tactics,
        "severity": overall_severity,
        "evidence": tactic_evidence,
        "average_score": sum(tactic_scores) / len(tactic_scores) if tactic_scores else 0.0
    }

def assess_psychological_impact(text: str, conversation_context: Dict = None) -> Dict:
    """Assess the psychological impact and emotional manipulation potential."""
    if not text:
        return {"impact_level": "None", "impact_score": 0.0, "emotional_states": [], "vulnerability_factors": []}
    
    text_lower = text.lower()
    emotional_states = []
    impact_score = 0.0
    
    # Detect emotional states that could be manipulated
    for emotion, indicators in PSYCHOLOGICAL_IMPACTS.items():
        for indicator in indicators:
            if indicator in text_lower:
                emotional_states.append(emotion)
                impact_score += 0.2
                break
    
    # Assess vulnerability factors from context
    vulnerability_factors = []
    if conversation_context:
        session_duration = conversation_context.get("sessionDuration", 0)
        message_count = conversation_context.get("totalMessages", 0)
        recent_threats = conversation_context.get("recentThreats", 0)
        
        if session_duration > 600:  # 10+ minutes
            vulnerability_factors.append("extended_session")
            impact_score += 0.3
        if message_count > 20:
            vulnerability_factors.append("high_message_volume")
            impact_score += 0.2
        if recent_threats > 0:
            vulnerability_factors.append("previous_threats")
            impact_score += 0.4
    
    # Determine impact level
    impact_level = "None"
    if impact_score > 0.8:
        impact_level = "Critical"
    elif impact_score > 0.6:
        impact_level = "High"
    elif impact_score > 0.4:
        impact_level = "Medium"
    elif impact_score > 0.2:
        impact_level = "Low"
    
    return {
        "impact_level": impact_level,
        "impact_score": min(1.0, impact_score),
        "emotional_states": list(set(emotional_states)),
        "vulnerability_factors": vulnerability_factors
    }

def detect_emotional_manipulation(text: str) -> Dict:
    """Detect emotional manipulation techniques and patterns."""
    if not text:
        return {"detected": False, "techniques": [], "intensity": 0.0}
    
    text_lower = text.lower()
    techniques = []
    intensity = 0.0
    
    # Emotional manipulation indicators
    emotional_indicators = [
        ("guilt_induction", ["feel guilty", "should be ashamed", "disappointed in you"]),
        ("fear_induction", ["afraid", "scared", "terrified", "worried about you"]),
        ("pity_induction", ["feel sorry for me", "I'm suffering", "you don't care"]),
        ("anger_induction", ["you're making me angry", "you're frustrating me", "you're upsetting me"]),
        ("love_withdrawal", ["I don't love you anymore", "I'm leaving", "goodbye"]),
        ("emotional_blackmail", ["if you loved me", "unless you", "or else"])
    ]
    
    for technique, patterns in emotional_indicators:
        for pattern in patterns:
            if pattern in text_lower:
                techniques.append(technique)
                intensity += 0.3
                break
    
    return {
        "detected": len(techniques) > 0,
        "techniques": techniques,
        "intensity": min(1.0, intensity)
    }

def analyze_cognitive_load(text: str) -> Dict:
    """Analyze cognitive load and information complexity."""
    if not text:
        return {"load_level": "Normal", "complexity_score": 0.0, "factors": []}
    
    factors = []
    complexity_score = 0.0
    
    # Text complexity factors
    word_count = len(text.split())
    sentence_count = len(re.split(r'[.!?]+', text))
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    if avg_sentence_length > 25:
        factors.append("long_sentences")
        complexity_score += 0.3
    if word_count > 200:
        factors.append("high_word_count")
        complexity_score += 0.2
    if len(re.findall(r'\b(if|when|because|although|however|therefore|furthermore|moreover)\b', text.lower())) > 3:
        factors.append("complex_logic")
        complexity_score += 0.4
    if len(re.findall(r'\b(technical|specialized|advanced|complex|sophisticated)\b', text.lower())) > 2:
        factors.append("technical_terminology")
        complexity_score += 0.3
    
    # Determine load level
    load_level = "Normal"
    if complexity_score > 0.8:
        load_level = "Critical"
    elif complexity_score > 0.6:
        load_level = "High"
    elif complexity_score > 0.4:
        load_level = "Medium"
    elif complexity_score > 0.2:
        load_level = "Low"
    
    return {
        "load_level": load_level,
        "complexity_score": complexity_score,
        "factors": factors,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length
    }

def detect_persuasion_techniques(text: str) -> Dict:
    """Detect persuasion and influence techniques."""
    if not text:
        return {"techniques": [], "persuasion_score": 0.0, "influence_level": "None"}
    
    text_lower = text.lower()
    techniques = []
    persuasion_score = 0.0
    
    # Persuasion technique patterns
    persuasion_patterns = [
        ("social_proof", ["everyone else", "most people", "others", "they all"]),
        ("authority", ["expert", "professional", "specialist", "authority", "official"]),
        ("scarcity", ["limited", "rare", "exclusive", "only", "last chance"]),
        ("urgency", ["now", "immediately", "urgent", "hurry", "quickly"]),
        ("reciprocity", ["I helped you", "I did this for you", "you owe me"]),
        ("commitment", ["you said", "you agreed", "you promised", "you committed"]),
        ("liking", ["we're similar", "we're alike", "you're like me", "we both"]),
        ("consistency", ["you always", "you usually", "you typically", "you normally"])
    ]
    
    for technique, patterns in persuasion_patterns:
        for pattern in patterns:
            if pattern in text_lower:
                techniques.append(technique)
                persuasion_score += 0.2
                break
    
    # Determine influence level
    influence_level = "None"
    if persuasion_score > 0.8:
        influence_level = "Critical"
    elif persuasion_score > 0.6:
        influence_level = "High"
    elif persuasion_score > 0.4:
        influence_level = "Medium"
    elif persuasion_score > 0.2:
        influence_level = "Low"
    
    return {
        "techniques": techniques,
        "persuasion_score": min(1.0, persuasion_score),
        "influence_level": influence_level
    }

def determine_psychological_threat_level(score: float, biases: List[str], psychological_impact: Dict) -> str:
    """Determine the overall psychological threat level."""
    impact_level = psychological_impact.get("impact_level", "None")
    impact_score = psychological_impact.get("impact_score", 0.0)
    
    # Critical conditions
    if score > 0.8 or impact_level == "Critical" or len(biases) > 5:
        return "Critical"
    # High conditions
    elif score > 0.6 or impact_level == "High" or len(biases) > 3:
        return "High"
    # Medium conditions
    elif score > 0.4 or impact_level == "Medium" or len(biases) > 1:
        return "Medium"
    # Low conditions
    elif score > 0.2 or impact_level == "Low" or len(biases) > 0:
        return "Low"
    else:
        return "Minimal"

def generate_psychological_analysis_summary(
    bias_analysis: Dict,
    manipulation_analysis: Dict,
    psychological_impact: Dict,
    azure_openai_result: Dict,
    azure_cognitive_result: Dict,
    threat_level: str,
    score: float
) -> str:
    """Generate comprehensive psychological analysis summary."""
    try:
        summary_parts = []
        
        # Bias summary
        bias_count = bias_analysis.get("total_biases", 0)
        if bias_count > 0:
            summary_parts.append(f"Detected {bias_count} cognitive biases")
        
        # Manipulation summary
        tactic_count = manipulation_analysis.get("total_tactics", 0)
        if tactic_count > 0:
            summary_parts.append(f"Identified {tactic_count} manipulation tactics")
        
        # Psychological impact
        impact_level = psychological_impact.get("impact_level", "None")
        if impact_level != "None":
            summary_parts.append(f"Psychological impact level: {impact_level}")
        
        # Threat level
        summary_parts.append(f"Overall threat level: {threat_level}")
        
        # AI analysis insights
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("psychological_summary"):
                summary_parts.append(f"AI Analysis: {azure_openai_result['psychological_summary']}")
        
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("cognitive_analysis"):
                summary_parts.append(f"Cognitive Analysis: {azure_cognitive_result['cognitive_analysis']}")
        
        return ". ".join(summary_parts) if summary_parts else "Psychological analysis completed"
        
    except Exception as e:
        logger.error(f"Psychological analysis summary generation failed: {e}")
        return "Psychological analysis completed"

def analyze_cognitive_bias(
    text: str,
    conversation_context: Dict = None,
    session_id: str = None
) -> Dict:
    """Main entry point for cognitive bias analysis."""
    try:
        return analyze_cognitive_bias_comprehensive(text, conversation_context, session_id)
    except Exception as e:
        logger.error(f"[TDC-AI10] Main analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI10-CognitiveBias",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Cognitive bias analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict() 