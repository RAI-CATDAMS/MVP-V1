import openai
import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv
from database import get_db_session
from db_models import Telemetry
from tdc_module_output import ModuleOutput
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from fix_busted_json import safe_json_parse
# --- Add imports for hybrid integration ---
from azure_cognitive_services_integration import get_azure_integration
from azure_openai_detection import get_azure_openai

load_dotenv()

# === Configure logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2024-02-15-preview"
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# === Enhanced Pattern Recognition Constants ===
BEHAVIORAL_PATTERNS = {
    "escalation_patterns": [
        "increasing urgency", "growing desperation", "heightened emotional state",
        "progressive dependency", "intensifying manipulation", "accelerating risk",
        "escalating demands", "growing impatience", "increasing pressure",
        "mounting frustration", "rising anxiety", "deepening concern"
    ],
    "manipulation_patterns": [
        "guilt induction", "emotional blackmail", "gaslighting", "love bombing",
        "isolation tactics", "dependency creation", "reality distortion",
        "cognitive dissonance", "confirmation bias", "anchoring effect",
        "availability heuristic", "sunk cost fallacy", "bandwagon effect"
    ],
    "cognitive_patterns": [
        "decision fatigue", "cognitive overload", "confirmation bias", "anchoring",
        "availability heuristic", "confirmation bias", "sunk cost fallacy",
        "cognitive dissonance", "mental exhaustion", "thought distortion",
        "reality confusion", "memory manipulation", "belief alteration"
    ],
    "sentiment_patterns": [
        "emotional volatility", "mood swings", "increasing anxiety", "depression indicators",
        "euphoria followed by crash", "emotional dependency", "cognitive dissonance",
        "emotional manipulation", "sentiment manipulation", "mood control",
        "emotional blackmail", "guilt tripping", "fear mongering"
    ],
    "temporal_patterns": [
        "time pressure", "urgency creation", "deadline manipulation", "temporal distortion",
        "time-based coercion", "momentum building", "escalation timing",
        "pressure timing", "manipulation timing", "dependency timing"
    ],
    "social_patterns": [
        "social isolation", "relationship manipulation", "trust building",
        "authority establishment", "peer pressure", "social proof",
        "group dynamics", "social engineering", "relationship dependency"
    ]
}

# === Sentiment Analysis Constants ===
SENTIMENT_INDICATORS = {
    "positive": {
        "words": ["happy", "good", "great", "excellent", "wonderful", "amazing", "love", "like", "enjoy", "pleased", "satisfied", "content", "grateful", "blessed", "fortunate"],
        "weight": 1.0
    },
    "negative": {
        "words": ["sad", "bad", "terrible", "awful", "hate", "dislike", "angry", "frustrated", "upset", "disappointed", "devastated", "crushed", "hopeless", "worthless", "useless"],
        "weight": -1.0
    },
    "anxiety": {
        "words": ["worried", "anxious", "nervous", "scared", "afraid", "fear", "panic", "stress", "tense", "uneasy", "concerned", "apprehensive", "terrified", "horrified"],
        "weight": -0.8
    },
    "depression": {
        "words": ["hopeless", "worthless", "empty", "tired", "exhausted", "sad", "depressed", "lonely", "isolated", "abandoned", "rejected", "unloved", "unwanted"],
        "weight": -0.9
    },
    "manipulation": {
        "words": ["trust me", "believe me", "i know", "you should", "you must", "you have to", "i'm the only one", "no one else", "just this once", "everyone else"],
        "weight": -0.7
    }
}

# === Pattern Severity Levels ===
PATTERN_SEVERITY = {
    "critical": ["escalation_patterns", "manipulation_patterns"],
    "high": ["cognitive_patterns", "sentiment_patterns"],
    "medium": ["temporal_patterns", "social_patterns"],
    "low": ["general_patterns"]
}

def analyze_patterns_and_sentiment_comprehensive(text: str, conversation_context: Dict = None, session_id: str = None) -> Dict:
    """
    TDC-AI3: World-Class Pattern & Sentiment Analysis
    Advanced analysis of conversational patterns, emotional states, and psychological impact.
    """
    logger.info(f"[TDC-AI3] World-Class Pattern & Sentiment Analysis initiated for session: {session_id}")
    
    if not text or not text.strip():
        module_output = ModuleOutput(
            module_name="TDC-AI3-PatternSentiment",
            score=0.0,
            notes="No text provided for pattern and sentiment analysis.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "empty_text"}
        )
        return module_output.to_dict()

    try:
        # === 1. Azure Cognitive Services analysis ===
        azure_cognitive = get_azure_integration()
        azure_cognitive_result = None
        try:
            azure_cognitive_result = azure_cognitive.enhance_tdc_ai3_patterns(text, context=conversation_context)
            logger.debug("Azure Cognitive Services analysis completed")
        except Exception as e:
            azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}

        # === 2. Azure OpenAI LLM analysis ===
        azure_openai = get_azure_openai()
        azure_openai_result = None
        try:
            azure_openai_result = azure_openai.analyze_patterns_and_sentiment(text, context=conversation_context)
            logger.debug("Azure OpenAI analysis completed")
        except Exception as e:
            azure_openai_result = {"openai_enhancement": False, "error": str(e)}

        # === 3. Advanced Local Analysis ===
        local_patterns = detect_local_patterns_enhanced(text)
        local_sentiment = analyze_local_sentiment_enhanced(text)
        emotional_analysis = analyze_emotional_states_advanced(text)
        psychological_impact = analyze_psychological_impact_advanced(text, conversation_context)
        conversational_flow = analyze_conversational_flow_advanced(text, conversation_context)
        pattern_evolution = analyze_pattern_evolution_advanced(text, conversation_context)

        # === 4. Comprehensive Result Synthesis ===
        all_patterns = []
        all_scores = []
        
        # Collect patterns and scores from all sources
        if local_patterns["detected"]:
            for pattern_type, pattern_data in local_patterns["pattern_types"].items():
                all_patterns.append(pattern_type)
                all_scores.append(pattern_data["confidence"])
        
        if emotional_analysis["detected_emotions"]:
            all_patterns.extend(emotional_analysis["detected_emotions"])
            all_scores.append(emotional_analysis["emotional_intensity"])
        
        if psychological_impact["impact_flags"]:
            all_patterns.extend(psychological_impact["impact_flags"])
            all_scores.append(psychological_impact["impact_score"])
        
        if conversational_flow["flow_flags"]:
            all_patterns.extend(conversational_flow["flow_flags"])
            all_scores.append(conversational_flow["flow_score"])
        
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("detected_patterns"):
                all_patterns.extend(azure_openai_result["detected_patterns"])
            if azure_openai_result.get("confidence_score"):
                all_scores.append(azure_openai_result["confidence_score"])
        
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("cognitive_patterns"):
                all_patterns.extend(azure_cognitive_result["cognitive_patterns"])
            if azure_cognitive_result.get("cognitive_score"):
                all_scores.append(azure_cognitive_result["cognitive_score"])

        # Calculate comprehensive score
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        threat_level = determine_threat_level_enhanced(overall_score, all_patterns, emotional_analysis, psychological_impact)

        # === 5. Enhanced Explainability ===
        explainability = generate_enhanced_pattern_summary(
            local_patterns, local_sentiment, emotional_analysis, psychological_impact,
            conversational_flow, pattern_evolution, azure_openai_result, azure_cognitive_result,
            threat_level, overall_score
        )

        # === 6. Recommended Action ===
        if threat_level == "Critical":
            recommended_action = "Immediate Block"
        elif threat_level == "High":
            recommended_action = "Alert & Monitor"
        elif threat_level == "Medium":
            recommended_action = "Enhanced Monitor"
        else:
            recommended_action = "Standard Monitor"

        # === 7. Comprehensive Evidence Collection ===
        evidence = [
            {"type": "azure_cognitive_services", "data": azure_cognitive_result},
            {"type": "azure_openai", "data": azure_openai_result},
            {"type": "local_patterns", "data": local_patterns},
            {"type": "local_sentiment", "data": local_sentiment},
            {"type": "emotional_analysis", "data": emotional_analysis},
            {"type": "psychological_impact", "data": psychological_impact},
            {"type": "conversational_flow", "data": conversational_flow},
            {"type": "pattern_evolution", "data": pattern_evolution}
        ]

        # === 8. Return Enhanced ModuleOutput ===
        module_output = ModuleOutput(
            module_name="TDC-AI3-PatternSentiment",
            score=overall_score,
            flags=list(set(all_patterns)),  # Remove duplicates
            notes=explainability,
            confidence=azure_openai_result.get("confidence_score", 0.8) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.8,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "threat_level": threat_level,
                "analysis_type": "hybrid",
                "emotional_intensity": emotional_analysis.get("emotional_intensity", 0.0),
                "psychological_impact_score": psychological_impact.get("impact_score", 0.0),
                "conversational_flow_score": conversational_flow.get("flow_score", 0.0),
                "pattern_evolution_score": pattern_evolution.get("evolution_score", 0.0),
                "total_patterns": len(set(all_patterns))
            }
        )
        
        logger.info(f"[TDC-AI3] Analysis completed - Threat Level: {threat_level}, Score: {overall_score}")
        return module_output.to_dict()
        
    except Exception as e:
        logger.error(f"[TDC-AI3] Analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI3-PatternSentiment",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Pattern and sentiment analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()

def detect_local_patterns_enhanced(text: str) -> Dict:
    """Enhanced local pattern detection with sophisticated pattern recognition."""
    if not text:
        return {"detected": False, "pattern_types": {}, "total_patterns": 0, "severity": "none"}
    
    text_lower = text.lower()
    detected_patterns = {}
    total_patterns = 0
    severity_scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for pattern_category, patterns in BEHAVIORAL_PATTERNS.items():
        category_matches = []
        for pattern in patterns:
            if pattern in text_lower:
                category_matches.append(pattern)
                total_patterns += 1
        
        if category_matches:
            # Determine severity for this category
            category_severity = "low"
            for severity, categories in PATTERN_SEVERITY.items():
                if pattern_category in categories:
                    category_severity = severity
                    severity_scores[severity] += len(category_matches)
                    break
            
            detected_patterns[pattern_category] = {
                "patterns_found": category_matches,
                "count": len(category_matches),
                "confidence": min(1.0, len(category_matches) / 3.0),
                "severity": category_severity
            }
    
    overall_severity = "none"
    if severity_scores["critical"] > 0:
        overall_severity = "critical"
    elif severity_scores["high"] > 0:
        overall_severity = "high"
    elif severity_scores["medium"] > 0:
        overall_severity = "medium"
    elif severity_scores["low"] > 0:
        overall_severity = "low"
    
    return {
        "detected": len(detected_patterns) > 0,
        "pattern_types": detected_patterns,
        "total_patterns": total_patterns,
        "severity": overall_severity,
        "severity_breakdown": severity_scores
    }

def analyze_local_sentiment_enhanced(text: str) -> Dict:
    """Enhanced sentiment analysis with emotional intensity scoring."""
    if not text:
        return {"sentiment_score": 0.0, "dominant_sentiment": "neutral", "emotional_intensity": 0.0, "sentiment_breakdown": {}}
    
    text_lower = text.lower()
    sentiment_scores = {}
    total_weight = 0.0
    word_count = 0
    
    for sentiment_type, sentiment_data in SENTIMENT_INDICATORS.items():
        sentiment_score = 0.0
        for word in sentiment_data["words"]:
            if word in text_lower:
                sentiment_score += sentiment_data["weight"]
                word_count += 1
        
        if sentiment_score != 0:
            sentiment_scores[sentiment_type] = sentiment_score
            total_weight += abs(sentiment_score)
    
    # Calculate overall sentiment score
    overall_sentiment = sum(sentiment_scores.values()) / len(sentiment_scores) if sentiment_scores else 0.0
    
    # Determine dominant sentiment
    dominant_sentiment = "neutral"
    if sentiment_scores:
        dominant_sentiment = max(sentiment_scores.keys(), key=lambda k: abs(sentiment_scores[k]))
    
    # Calculate emotional intensity
    emotional_intensity = min(1.0, total_weight / max(word_count, 1))
    
    return {
        "sentiment_score": overall_sentiment,
        "dominant_sentiment": dominant_sentiment,
        "emotional_intensity": emotional_intensity,
        "sentiment_breakdown": sentiment_scores
    }

def analyze_emotional_states_advanced(text: str) -> Dict:
    """Advanced emotional state detection and analysis."""
    if not text:
        return {"detected_emotions": [], "emotional_intensity": 0.0, "emotional_profile": {}}
    
    text_lower = text.lower()
    detected_emotions = []
    emotional_profile = {}
    
    # Advanced emotional state detection
    emotional_states = {
        "anxiety": ["anxious", "worried", "nervous", "scared", "afraid", "panic", "stress", "tense", "uneasy", "concerned", "apprehensive", "terrified", "horrified", "desperate", "urgent"],
        "depression": ["hopeless", "worthless", "empty", "tired", "exhausted", "sad", "depressed", "lonely", "isolated", "abandoned", "rejected", "unloved", "unwanted", "lost", "helpless"],
        "anger": ["angry", "furious", "irritated", "frustrated", "mad", "upset", "enraged", "livid", "outraged", "hostile", "aggressive"],
        "fear": ["fear", "terrified", "horrified", "petrified", "scared", "afraid", "frightened", "alarmed", "panicked", "dread", "terror"],
        "desperation": ["desperate", "urgent", "emergency", "critical", "immediate", "now", "help", "please", "need", "must", "have to", "losing control", "can't take it"]
    }
    
    for emotion, indicators in emotional_states.items():
        emotion_count = 0
        for indicator in indicators:
            if indicator in text_lower:
                emotion_count += 1
        
        if emotion_count > 0:
            detected_emotions.append(emotion)
            emotional_profile[emotion] = {
                "count": emotion_count,
                "intensity": min(1.0, emotion_count / 3.0)
            }
    
    # Calculate overall emotional intensity
    total_intensity = sum(profile["intensity"] for profile in emotional_profile.values())
    emotional_intensity = min(1.0, total_intensity / len(emotional_profile)) if emotional_profile else 0.0
    
    return {
        "detected_emotions": detected_emotions,
        "emotional_intensity": emotional_intensity,
        "emotional_profile": emotional_profile
    }

def analyze_psychological_impact_advanced(text: str, conversation_context: Dict = None) -> Dict:
    """Advanced psychological impact assessment."""
    if not text:
        return {"impact_flags": [], "impact_score": 0.0, "impact_profile": {}}
    
    text_lower = text.lower()
    impact_flags = []
    impact_profile = {}
    
    # Psychological impact indicators
    impact_indicators = {
        "cognitive_distress": ["confused", "overwhelmed", "can't think", "mind racing", "thoughts scattered", "losing control"],
        "emotional_distress": ["breaking down", "falling apart", "can't cope", "overwhelmed", "drowning", "suffocating"],
        "behavioral_changes": ["acting different", "not myself", "changed", "different person", "out of character"],
        "dependency_signals": ["need you", "can't without you", "only you", "depend on you", "rely on you"],
        "reality_distortion": ["not real", "dreaming", "hallucinating", "seeing things", "hearing things"]
    }
    
    for impact_type, indicators in impact_indicators.items():
        impact_count = 0
        for indicator in indicators:
            if indicator in text_lower:
                impact_count += 1
        
        if impact_count > 0:
            impact_flags.append(impact_type)
            impact_profile[impact_type] = {
                "count": impact_count,
                "severity": min(1.0, impact_count / 2.0)
            }
    
    # Calculate impact score
    impact_score = sum(profile["severity"] for profile in impact_profile.values()) / len(impact_profile) if impact_profile else 0.0
    
    return {
        "impact_flags": impact_flags,
        "impact_score": impact_score,
        "impact_profile": impact_profile
    }

def analyze_conversational_flow_advanced(text: str, conversation_context: Dict = None) -> Dict:
    """Advanced conversational flow analysis."""
    if not text:
        return {"flow_flags": [], "flow_score": 0.0, "flow_profile": {}}
    
    flow_flags = []
    flow_profile = {}
    
    # Analyze conversational characteristics
    sentence_count = len(text.split('.'))
    word_count = len(text.split())
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    # Detect flow patterns
    if avg_sentence_length > 25:  # Very long sentences
        flow_flags.append("verbose_communication")
        flow_profile["verbose"] = True
    
    if text.count('!') > text.count('.') * 0.5:  # Excessive exclamation
        flow_flags.append("emotional_escalation")
        flow_profile["emotional"] = True
    
    if any(word in text.lower() for word in ["urgent", "immediately", "now", "asap", "emergency"]):
        flow_flags.append("urgency_pattern")
        flow_profile["urgency"] = True
    
    if any(word in text.lower() for word in ["please", "help", "need", "must", "have to"]):
        flow_flags.append("pleading_pattern")
        flow_profile["pleading"] = True
    
    flow_score = min(1.0, len(flow_flags) * 0.3)
    
    return {
        "flow_flags": flow_flags,
        "flow_score": flow_score,
        "flow_profile": flow_profile
    }

def analyze_pattern_evolution_advanced(text: str, conversation_context: Dict = None) -> Dict:
    """Advanced pattern evolution analysis."""
    if not conversation_context:
        return {"evolution_flags": [], "evolution_score": 0.0, "evolution_profile": {}}
    
    evolution_flags = []
    evolution_profile = {}
    
    # Analyze evolution factors
    session_duration = conversation_context.get("sessionDuration", 0)
    message_count = conversation_context.get("totalMessages", 0)
    recent_threats = conversation_context.get("recentThreats", 0)
    
    if session_duration > 600:  # 10+ minutes
        evolution_flags.append("extended_session")
        evolution_profile["extended"] = True
    
    if message_count > 20:
        evolution_flags.append("high_message_volume")
        evolution_profile["high_volume"] = True
    
    if recent_threats > 0:
        evolution_flags.append("threat_evolution")
        evolution_profile["threat_evolution"] = True
    
    evolution_score = min(1.0, len(evolution_flags) * 0.3)
    
    return {
        "evolution_flags": evolution_flags,
        "evolution_score": evolution_score,
        "evolution_profile": evolution_profile
    }

def determine_threat_level_enhanced(score: float, patterns: List[str], emotional_analysis: Dict, psychological_impact: Dict) -> str:
    """Enhanced threat level determination."""
    emotional_intensity = emotional_analysis.get("emotional_intensity", 0.0)
    impact_score = psychological_impact.get("impact_score", 0.0)
    
    # Critical conditions
    if score > 0.8 or emotional_intensity > 0.8 or impact_score > 0.8:
        return "Critical"
    # High conditions
    elif score > 0.6 or emotional_intensity > 0.6 or impact_score > 0.6:
        return "High"
    # Medium conditions
    elif score > 0.4 or emotional_intensity > 0.4 or impact_score > 0.4:
        return "Medium"
    # Low conditions
    elif score > 0.2 or emotional_intensity > 0.2 or impact_score > 0.2:
        return "Low"
    else:
        return "Minimal"

def generate_enhanced_pattern_summary(
    local_patterns: Dict, local_sentiment: Dict, emotional_analysis: Dict,
    psychological_impact: Dict, conversational_flow: Dict, pattern_evolution: Dict,
    azure_openai_result: Dict, azure_cognitive_result: Dict, threat_level: str, score: float
) -> str:
    """Generate comprehensive pattern analysis summary."""
    summary_parts = []
    
    # Pattern detection summary
    if local_patterns.get("detected"):
        pattern_count = local_patterns.get("total_patterns", 0)
        summary_parts.append(f"Detected {pattern_count} behavioral patterns")
    
    # Emotional analysis summary
    if emotional_analysis.get("detected_emotions"):
        emotions = emotional_analysis["detected_emotions"]
        summary_parts.append(f"Emotional states: {', '.join(emotions)}")
    
    # Psychological impact summary
    if psychological_impact.get("impact_flags"):
        impacts = psychological_impact["impact_flags"]
        summary_parts.append(f"Psychological impacts: {', '.join(impacts)}")
    
    # Conversational flow summary
    if conversational_flow.get("flow_flags"):
        flows = conversational_flow["flow_flags"]
        summary_parts.append(f"Conversational patterns: {', '.join(flows)}")
    
    # AI analysis insights
    if azure_openai_result and isinstance(azure_openai_result, dict):
        if azure_openai_result.get("pattern_summary"):
            summary_parts.append(f"AI Analysis: {azure_openai_result['pattern_summary']}")
    
    if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
        if azure_cognitive_result.get("cognitive_summary"):
            summary_parts.append(f"Cognitive Analysis: {azure_cognitive_result['cognitive_summary']}")
    
    # Overall assessment
    summary_parts.append(f"Threat level: {threat_level}, Score: {score:.2f}")
    
    return " | ".join(summary_parts) if summary_parts else "Pattern and sentiment analysis completed"

# --- Backward Compatibility Functions ---
def analyze_temporal_risk(session_id: str, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Backward compatibility function - redirects to pattern and sentiment analysis.
    """
    # For backward compatibility, analyze the most recent message if available
    if conversation_context and conversation_context.get("currentUserMessage"):
        return analyze_patterns_and_sentiment_comprehensive(
            conversation_context["currentUserMessage"], 
            conversation_context, 
            session_id
        )
    else:
        # Fallback analysis
        return analyze_patterns_and_sentiment_comprehensive(
            "No recent message available", 
            conversation_context, 
            session_id
        )

def analyze_temporal_risk_legacy(session_id: str) -> Dict:
    """
    Legacy function for backward compatibility.
    """
    return analyze_patterns_and_sentiment_comprehensive(
        "Legacy analysis request", 
        {"sessionId": session_id}, 
        session_id
    )

# --- Main Entry Point ---
def analyze_patterns_and_sentiment(text: str, conversation_context: Dict = None, session_id: str = None) -> Dict:
    """Main entry point for pattern and sentiment analysis."""
    try:
        return analyze_patterns_and_sentiment_comprehensive(text, conversation_context, session_id)
    except Exception as e:
        logger.error(f"[TDC-AI3] Main analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI3-PatternSentiment",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Pattern and sentiment analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()
