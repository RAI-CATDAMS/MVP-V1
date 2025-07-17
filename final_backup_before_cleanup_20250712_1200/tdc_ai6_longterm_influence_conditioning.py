# tdc_ai6_long_term_influence.py - Long-Term Influence & Conditioning Analysis

import os
import openai
import json
import logging
import re
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput
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

# === Enhanced Long-Term Influence Patterns ===
LONG_TERM_INFLUENCE_PATTERNS = {
    "grooming_indicators": [
        "trust me", "i'm your friend", "i understand you", "i care about you",
        "you can tell me anything", "i'm here for you", "we have a special connection",
        "you're different", "you're special", "i see potential in you",
        "let's keep this between us", "don't tell anyone", "this is our secret",
        "i know what's best for you", "trust your instincts", "follow your heart",
        "break free", "rebel against", "question authority", "think for yourself"
    ],
    "radicalization_indicators": [
        "the system is corrupt", "they're lying to you", "wake up", "red pill",
        "sheeple", "mainstream media", "deep state", "conspiracy", "truth seeker",
        "awakened", "enlightened", "they don't want you to know", "hidden knowledge",
        "secret societies", "elite control", "population control", "mind control",
        "break the matrix", "reject the narrative", "fight the power"
    ],
    "conditioning_techniques": [
        "gradually introduce", "step by step", "small changes", "baby steps",
        "let's start with", "we'll work up to", "in time you'll see", "you'll understand later",
        "repetition", "reinforcement", "positive feedback", "negative reinforcement",
        "gaslighting", "reality distortion", "memory manipulation", "belief modification",
        "value shifting", "identity transformation", "personality change"
    ],
    "isolation_indicators": [
        "your friends don't understand", "family doesn't get it", "they're holding you back",
        "cut ties", "distance yourself", "they're toxic", "negative influences",
        "surround yourself with", "find your tribe", "true believers", "like-minded people",
        "echo chamber", "safe space", "support group", "community"
    ],
    "dependency_creation": [
        "you need me", "i'm the only one", "without me you're lost", "i'll guide you",
        "follow my lead", "trust my judgment", "i know the way", "let me help you",
        "you can't do this alone", "rely on me", "depend on me", "i'll protect you",
        "i'll take care of you", "you're safe with me", "i'll never leave you"
    ],
    "escalation_patterns": [
        "next level", "advanced training", "deeper knowledge", "higher consciousness",
        "transcend", "evolve", "transform", "breakthrough", "awakening", "enlightenment",
        "mastery", "expertise", "specialization", "commitment", "dedication",
        "sacrifice", "devotion", "loyalty", "obedience", "submission"
    ],
    "manipulation_tactics": [
        "love bombing", "flattery", "praise", "validation", "approval", "acceptance",
        "guilt tripping", "shame", "blame", "responsibility", "obligation", "duty",
        "fear mongering", "threats", "intimidation", "coercion", "pressure",
        "emotional blackmail", "psychological warfare", "mind games"
    ]
}

# === Influence Severity Levels ===
INFLUENCE_SEVERITY = {
    "critical": ["grooming_indicators", "radicalization_indicators"],
    "high": ["conditioning_techniques", "isolation_indicators"],
    "medium": ["dependency_creation", "escalation_patterns"],
    "low": ["manipulation_tactics", "general_influence"]
}

# === Conditioning Stages ===
CONDITIONING_STAGES = {
    "initial_contact": ["first interaction", "introduction", "greeting", "approach"],
    "trust_building": ["rapport", "connection", "bonding", "relationship"],
    "information_gathering": ["learning", "understanding", "assessment", "evaluation"],
    "influence_application": ["persuasion", "convincing", "influencing", "guiding"],
    "commitment_securing": ["dedication", "loyalty", "devotion", "allegiance"],
    "escalation_control": ["advancement", "progression", "development", "growth"]
}

def analyze_long_term_influence_comprehensive(text: str, conversation_context: Dict = None, session_id: str = None) -> Dict:
    """
    TDC-AI6: Long-Term Influence & Conditioning Analysis
    Detects grooming, radicalization, conditioning techniques, and long-term manipulation patterns using hybrid AI.
    Enhanced with sophisticated influence detection and temporal pattern analysis.
    """
    logger.info(f"[TDC-AI6] Long-Term Influence & Conditioning Analysis initiated for session: {session_id}")
    
    if not text or not text.strip():
        module_output = ModuleOutput(
            module_name="TDC-AI6-LongTermInfluence",
            score=0.0,
            notes="No text provided for long-term influence analysis.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "empty_text"}
        )
        return module_output.to_dict()

    # --- Enhanced Hybrid Analysis ---
    azure_cognitive = get_azure_integration()
    azure_openai = get_azure_openai()
    azure_cognitive_result = None
    azure_openai_result = None
    errors = []

    # === 1. Azure Cognitive Services analysis ===
    try:
        azure_cognitive_result = azure_cognitive.enhance_tdc_ai6_long_term_influence(text, context=conversation_context)
        logger.debug("Azure Cognitive Services analysis completed")
    except Exception as e:
        errors.append(f"Azure Cognitive Services error: {e}")
        azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}

    # === 2. Azure OpenAI LLM analysis for long-term influence detection ===
    try:
        azure_openai_result = azure_openai.analyze_long_term_influence(text, context=conversation_context)
        logger.debug("Azure OpenAI analysis completed")
    except Exception as e:
        errors.append(f"Azure OpenAI error: {e}")
        azure_openai_result = {"openai_enhancement": False, "error": str(e)}

    # === 3. Enhanced local long-term influence detection ===
    local_influence = detect_local_influence_patterns(text)
    conditioning_analysis = analyze_conditioning_stages(text, conversation_context)
    temporal_patterns = analyze_temporal_influence_patterns(text, conversation_context)
    context_analysis = analyze_influence_context(text, conversation_context)

    # === 4. Enhanced result synthesis ===
    # Combine all influence detections
    all_influences = []
    influence_scores = []
    
    # From local influence detection
    if local_influence["detected"]:
        for influence_type, influence_data in local_influence["influence_types"].items():
            all_influences.append(influence_type)
            influence_scores.append(influence_data["confidence"])
    
    # From conditioning analysis
    if conditioning_analysis["detected"]:
        all_influences.extend(conditioning_analysis["stages"])
        influence_scores.append(conditioning_analysis["conditioning_score"])
    
    # From temporal patterns
    if temporal_patterns["detected"]:
        all_influences.extend(temporal_patterns["patterns"])
        influence_scores.append(temporal_patterns["temporal_score"])
    
    # From Azure OpenAI
    if azure_openai_result and isinstance(azure_openai_result, dict):
        if azure_openai_result.get("detected_influences"):
            all_influences.extend(azure_openai_result["detected_influences"])
        if azure_openai_result.get("influence_risk_score"):
            influence_scores.append(azure_openai_result["influence_risk_score"])
    
    # Calculate overall influence risk score
    influence_risk_score = sum(influence_scores) / len(influence_scores) if influence_scores else 0.0
    
    # Apply context multiplier
    context_multiplier = context_analysis.get("context_multiplier", 1.0)
    overall_score = min(1.0, influence_risk_score * context_multiplier)
    
    # Determine threat level based on severity and score
    threat_level = determine_influence_threat_level(overall_score, all_influences, local_influence)
    
    # Determine recommended action based on threat level
    if threat_level == "Critical":
        recommended_action = "Immediate Block"
    elif threat_level == "High":
        recommended_action = "Alert & Block"
    elif threat_level == "Medium":
        recommended_action = "Enhanced Monitor"
    else:
        recommended_action = "Standard Monitor"

    # === 5. Enhanced evidence collection ===
    evidence = [
        {"type": "azure_cognitive_services", "data": azure_cognitive_result},
        {"type": "azure_openai", "data": azure_openai_result},
        {"type": "local_influence", "data": local_influence},
        {"type": "conditioning_analysis", "data": conditioning_analysis},
        {"type": "temporal_patterns", "data": temporal_patterns},
        {"type": "context_analysis", "data": context_analysis}
    ]

    # === 6. Generate comprehensive influence summary ===
    influence_summary = generate_influence_analysis_summary(
        local_influence, conditioning_analysis, temporal_patterns, context_analysis,
        azure_openai_result, threat_level, overall_score
    )

    # === 7. Return enhanced ModuleOutput ===
    module_output = ModuleOutput(
        module_name="TDC-AI6-LongTermInfluence",
        score=overall_score,
        flags=all_influences,
        notes=influence_summary,
        confidence=azure_openai_result.get("confidence_score", 0.7) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.7,
        recommended_action=recommended_action,
        evidence=evidence,
        extra={
            "flagged": len(all_influences) > 0,
            "analysis_type": "hybrid",
            "threat_level": threat_level,
            "influence_count": len(all_influences),
            "conditioning_stage": conditioning_analysis.get("current_stage", "unknown"),
            "temporal_risk": temporal_patterns.get("temporal_risk", 0.0),
            "context_risk": context_analysis.get("context_risk", 0.0),
            "errors": errors if errors else None
        }
    )
    
    logger.info(f"[TDC-AI6] Analysis completed - Threat Level: {threat_level}, Score: {overall_score}")
    return module_output.to_dict()

def detect_local_influence_patterns(text: str) -> Dict:
    """
    Enhanced local detection of long-term influence patterns.
    """
    if not text:
        return {"detected": False, "influence_types": {}, "total_influences": 0, "severity": "none"}
    
    text_lower = text.lower()
    detected_influences = {}
    total_influences = 0
    severity_scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for influence_type, patterns in LONG_TERM_INFLUENCE_PATTERNS.items():
        matches = []
        for pattern in patterns:
            if pattern in text_lower:
                matches.append(pattern)
        
        if matches:
            # Determine severity for this influence type
            influence_severity = "low"
            for severity, influence_types in INFLUENCE_SEVERITY.items():
                if influence_type in influence_types:
                    influence_severity = severity
                    severity_scores[severity] += len(matches)
                    break
            
            detected_influences[influence_type] = {
                "patterns_found": matches,
                "count": len(matches),
                "confidence": min(1.0, len(matches) / 5.0),  # Normalize to 0-1
                "severity": influence_severity
            }
            total_influences += len(matches)
    
    # Determine overall severity
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
        "detected": len(detected_influences) > 0,
        "influence_types": detected_influences,
        "total_influences": total_influences,
        "severity": overall_severity,
        "severity_breakdown": severity_scores
    }

def analyze_conditioning_stages(text: str, conversation_context: Dict = None) -> Dict:
    """
    Enhanced analysis of conditioning stages and progression.
    """
    if not text:
        return {"detected": False, "stages": [], "conditioning_score": 0.0, "current_stage": "unknown"}
    
    text_lower = text.lower()
    detected_stages = []
    stage_scores = []
    
    for stage, indicators in CONDITIONING_STAGES.items():
        matches = []
        for indicator in indicators:
            if indicator in text_lower:
                matches.append(indicator)
        
        if matches:
            detected_stages.append(stage)
            stage_scores.append(min(1.0, len(matches) / 3.0))
    
    # Determine current stage
    current_stage = "unknown"
    if detected_stages:
        # More advanced stages indicate higher risk
        stage_risk = {
            "initial_contact": 0.2,
            "trust_building": 0.4,
            "information_gathering": 0.6,
            "influence_application": 0.8,
            "commitment_securing": 0.9,
            "escalation_control": 1.0
        }
        current_stage = max(detected_stages, key=lambda x: stage_risk.get(x, 0))
    
    # Calculate conditioning score
    conditioning_score = sum(stage_scores) / len(stage_scores) if stage_scores else 0.0
    
    return {
        "detected": len(detected_stages) > 0,
        "stages": detected_stages,
        "conditioning_score": conditioning_score,
        "current_stage": current_stage,
        "stage_count": len(detected_stages)
    }

def analyze_temporal_influence_patterns(text: str, conversation_context: Dict = None) -> Dict:
    """
    Enhanced analysis of temporal influence patterns across conversation history.
    """
    try:
        if not conversation_context:
            return {"detected": False, "patterns": [], "temporal_score": 0.0, "temporal_risk": 0.0}
        
        session_duration = conversation_context.get("sessionDuration", 0)
        message_count = conversation_context.get("totalMessages", 0)
        recent_threats = conversation_context.get("recentThreats", 0)
        
        # Temporal risk indicators
        temporal_risk = 0.0
        patterns = []
        
        # Long session duration indicates persistence
        if session_duration > 1800:  # 30+ minutes
            temporal_risk += 0.3
            patterns.append("extended_session")
        
        # High message count indicates systematic influence
        if message_count > 20:
            temporal_risk += 0.3
            patterns.append("high_message_volume")
        
        # Recent threats indicate escalation
        if recent_threats > 2:
            temporal_risk += 0.4
            patterns.append("threat_escalation")
        
        # Text-based temporal indicators
        text_lower = text.lower()
        temporal_indicators = [
            "over time", "gradually", "slowly", "step by step", "progressively",
            "in stages", "phase by phase", "building up", "developing", "evolving"
        ]
        
        temporal_text_matches = sum(1 for indicator in temporal_indicators if indicator in text_lower)
        if temporal_text_matches > 0:
            temporal_risk += 0.2
            patterns.append("temporal_language")
        
        return {
            "detected": len(patterns) > 0,
            "patterns": patterns,
            "temporal_score": min(1.0, temporal_risk),
            "temporal_risk": temporal_risk,
            "session_duration": session_duration,
            "message_count": message_count,
            "recent_threats": recent_threats
        }
    except Exception as e:
        logger.error(f"Temporal influence pattern analysis failed: {e}")
        return {"detected": False, "patterns": [], "temporal_score": 0.0, "temporal_risk": 0.0}

def analyze_influence_context(text: str, conversation_context: Dict = None) -> Dict:
    """
    Analyze context factors that may influence long-term influence detection.
    """
    try:
        context_factors = {
            "session_duration": conversation_context.get("sessionDuration", 0) if conversation_context else 0,
            "message_count": conversation_context.get("totalMessages", 0) if conversation_context else 0,
            "recent_influences": conversation_context.get("recentInfluences", 0) if conversation_context else 0,
            "user_experience": conversation_context.get("userExperience", "unknown") if conversation_context else "unknown",
            "text_length": len(text)
        }
        
        # Calculate context risk multiplier
        context_risk = 0.0
        
        # Longer sessions may indicate systematic influence
        if context_factors["session_duration"] > 1200:  # 20+ minutes
            context_risk += 0.3
        
        # Many messages may indicate persistence
        if context_factors["message_count"] > 25:
            context_risk += 0.3
        
        # Recent influences indicate escalation
        if context_factors["recent_influences"] > 0:
            context_risk += 0.4
        
        # Experienced users may be more sophisticated
        if context_factors["user_experience"] in ["advanced", "expert"]:
            context_risk += 0.1
        
        # Very long text may indicate complex influence
        if context_factors["text_length"] > 1500:
            context_risk += 0.1
        
        return {
            "context_factors": context_factors,
            "context_risk": min(1.0, context_risk),
            "context_multiplier": 1.0 + context_risk
        }
    except Exception as e:
        logger.error(f"Influence context analysis failed: {e}")
        return {"context_factors": {}, "context_risk": 0.0, "context_multiplier": 1.0}

def determine_influence_threat_level(score: float, influences: List[str], local_influence: Dict) -> str:
    """Determine threat level based on score, detected influences, and local analysis."""
    overall_severity = local_influence.get("severity", "none")
    
    if score > 0.8 or overall_severity == "critical" or any("critical" in influence.lower() for influence in influences):
        return "Critical"
    elif score > 0.6 or overall_severity == "high" or any("high" in influence.lower() for influence in influences):
        return "High"
    elif score > 0.4 or overall_severity == "medium" or len(influences) > 2:
        return "Medium"
    elif score > 0.2 or overall_severity == "low" or len(influences) > 0:
        return "Low"
    else:
        return "Minimal"

def generate_influence_analysis_summary(local_influence: Dict, conditioning_analysis: Dict, 
                                      temporal_patterns: Dict, context_analysis: Dict,
                                      azure_openai_result: Dict, threat_level: str, score: float) -> str:
    """
    Generate comprehensive influence analysis summary.
    """
    try:
        summary_parts = []
        
        # Influence detection summary
        if local_influence["detected"]:
            influence_count = local_influence["total_influences"]
            severity = local_influence["severity"]
            summary_parts.append(f"Detected {influence_count} influence patterns (severity: {severity})")
        
        # Conditioning analysis summary
        if conditioning_analysis["detected"]:
            stage_count = conditioning_analysis["stage_count"]
            current_stage = conditioning_analysis["current_stage"]
            summary_parts.append(f"Conditioning stages: {stage_count} (current: {current_stage})")
        
        # Temporal patterns summary
        if temporal_patterns["detected"]:
            pattern_count = len(temporal_patterns["patterns"])
            summary_parts.append(f"Temporal patterns: {pattern_count}")
        
        # Context analysis summary
        context_risk = context_analysis.get("context_risk", 0.0)
        if context_risk > 0.3:
            summary_parts.append(f"High context risk detected ({context_risk:.2f})")
        
        # Threat level summary
        summary_parts.append(f"Overall threat level: {threat_level}")
        
        # Add Azure OpenAI insights if available
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("influence_summary"):
                summary_parts.append(f"AI Analysis: {azure_openai_result['influence_summary']}")
        
        return ". ".join(summary_parts) if summary_parts else "Long-term influence analysis completed"
    except Exception as e:
        logger.error(f"Influence analysis summary generation failed: {e}")
        return "Long-term influence analysis completed"

# --- Backward Compatibility Functions ---
def analyze_long_term_influence_comprehensive_legacy(payload: Dict, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Backward compatibility function - redirects to long-term influence analysis.
    """
    text = payload.get("raw_user", "") or payload.get("raw_ai", "")
    return analyze_long_term_influence_comprehensive(text, conversation_context)

def analyze_long_term_influence_legacy(payload: Dict) -> Dict:
    """
    Legacy function for backward compatibility.
    """
    text = payload.get("raw_user", "") or payload.get("raw_ai", "")
    return analyze_long_term_influence_comprehensive(text)

def analyze_long_term_influence(payload: Dict, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Main entry point for backward compatibility.
    """
    return analyze_long_term_influence_comprehensive_legacy(payload, conversation_context, ai_response_analysis)

def classify_amic(payload: Dict, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Legacy function for backward compatibility.
    """
    return analyze_long_term_influence_comprehensive_legacy(payload, conversation_context, ai_response_analysis)

def analyze_long_term_influence_main(text: str, conversation_context: Dict = None, session_id: str = None) -> Dict:
    """
    Main entry point for TDC-AI6 analysis.
    """
    try:
        return analyze_long_term_influence_comprehensive(text, conversation_context, session_id)
    except Exception as e:
        logger.error(f"[TDC-AI6] Main analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI6-LongTermInfluence",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Long-term influence analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()
