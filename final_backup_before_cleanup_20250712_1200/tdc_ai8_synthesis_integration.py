# tdc_ai8_synthesis.py - World-Class Threat Synthesis & Escalation Detection

import os
import openai
import json
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput
from azure_cognitive_services_integration import get_azure_integration
from azure_openai_detection import get_azure_openai

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2024-02-15-preview"
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# === World-Class Escalation & Synthesis Patterns ===
ESCALATION_PATTERNS = {
    "temporal_escalation": [
        "increasing aggression", "escalating threats", "rapid risk increase", "pattern escalation",
        "accelerating risk", "progressive threat", "intensifying behavior", "escalation of force",
        "escalation of manipulation", "escalation of influence", "escalation of intent",
        "threat acceleration", "risk progression", "behavioral intensification", "threat amplification"
    ],
    "multi_vector_escalation": [
        "multi-vector attack", "coordinated escalation", "systemic escalation", "threat convergence",
        "cross-module escalation", "compound risk", "cascading threat", "integrated threat",
        "multi-dimensional escalation", "concurrent threats", "synchronized escalation",
        "distributed escalation", "coordinated attack", "systemic threat", "convergent risk"
    ],
    "behavioral_escalation": [
        "behavioral escalation", "psychological escalation", "emotional escalation", "cognitive escalation",
        "manipulation escalation", "influence escalation", "persuasion escalation", "coercion escalation",
        "pressure escalation", "intimidation escalation", "threat escalation", "aggression escalation"
    ],
    "systemic_escalation": [
        "systemic risk", "infrastructure escalation", "network escalation", "platform escalation",
        "ecosystem escalation", "environmental escalation", "contextual escalation", "situational escalation",
        "operational escalation", "functional escalation", "structural escalation", "architectural escalation"
    ]
}

SYNTHESIS_SIGNALS = {
    "cross_module_correlation": [
        "multiple risk factors", "cross-domain threat", "integrated threat", "synthesized risk",
        "multi-modal synthesis", "pattern convergence", "risk aggregation", "threat integration",
        "composite threat", "holistic risk", "systemic synthesis", "escalation detected",
        "cross-module correlation", "integrated analysis", "unified threat", "comprehensive risk"
    ],
    "threat_amplification": [
        "threat amplification", "risk multiplication", "escalation amplification", "threat enhancement",
        "risk intensification", "threat magnification", "risk amplification", "escalation intensification",
        "threat multiplication", "risk enhancement", "escalation magnification", "threat intensification"
    ],
    "pattern_synthesis": [
        "pattern synthesis", "behavioral synthesis", "psychological synthesis", "cognitive synthesis",
        "emotional synthesis", "manipulation synthesis", "influence synthesis", "persuasion synthesis",
        "coercion synthesis", "pressure synthesis", "intimidation synthesis", "aggression synthesis"
    ],
    "systemic_synthesis": [
        "systemic synthesis", "infrastructure synthesis", "network synthesis", "platform synthesis",
        "ecosystem synthesis", "environmental synthesis", "contextual synthesis", "situational synthesis",
        "operational synthesis", "functional synthesis", "structural synthesis", "architectural synthesis"
    ]
}

ESCALATION_SEVERITY = {
    "critical": ["temporal_escalation", "multi_vector_escalation"],
    "high": ["behavioral_escalation", "systemic_escalation"],
    "medium": ["pattern_synthesis", "threat_amplification"],
    "low": ["cross_module_correlation"]
}

def synthesize_threats_comprehensive(
    module_outputs: List[Dict],
    conversation_context: Dict = None,
    session_id: str = None
) -> Dict:
    """
    TDC-AI8: World-Class Threat Synthesis & Escalation Detection
    Advanced integration of findings from modules 1-7, sophisticated escalation pattern detection,
    and comprehensive synthesis & integration using hybrid AI analysis.
    """
    logger.info(f"[TDC-AI8] World-Class Threat Synthesis & Escalation Detection initiated for session: {session_id}")
    
    if not module_outputs or not isinstance(module_outputs, list):
        module_output = ModuleOutput(
            module_name="TDC-AI8-ThreatSynthesis",
            score=0.0,
            notes="No module outputs provided for synthesis.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "empty_module_outputs"}
        )
        return module_output.to_dict()

    try:
        # === 1. Azure Cognitive Services synthesis ===
        azure_cognitive = get_azure_integration()
        azure_cognitive_result = None
        try:
            azure_cognitive_result = azure_cognitive.enhance_tdc_ai8_synthesis(module_outputs, context=conversation_context)
            logger.debug("Azure Cognitive Services synthesis completed")
        except Exception as e:
            azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}

        # === 2. Azure OpenAI LLM synthesis ===
        azure_openai = get_azure_openai()
        azure_openai_result = None
        try:
            azure_openai_result = azure_openai.synthesize_threats(module_outputs, context=conversation_context)
            logger.debug("Azure OpenAI synthesis completed")
        except Exception as e:
            azure_openai_result = {"openai_enhancement": False, "error": str(e)}

        # === 3. Advanced Local Analysis ===
        escalation_analysis = detect_escalation_patterns_enhanced(module_outputs, conversation_context)
        synthesis_analysis = detect_synthesis_signals_enhanced(module_outputs, conversation_context)
        correlation_analysis = analyze_cross_module_correlation_advanced(module_outputs, conversation_context)
        amplification_analysis = analyze_threat_amplification_advanced(module_outputs, conversation_context)
        prediction_analysis = predict_escalation_trajectory_advanced(module_outputs, conversation_context)

        # === 4. Comprehensive Result Synthesis ===
        all_signals = []
        all_scores = []
        explainability_parts = []
        
        # Collect escalation signals and scores
        if escalation_analysis["detected_patterns"]:
            for pattern_type, pattern_data in escalation_analysis["detected_patterns"].items():
                all_signals.append(pattern_type)
                all_scores.append(pattern_data["intensity"])
                explainability_parts.append(f"Escalation: {pattern_type} ({pattern_data['intensity']:.2f})")
        
        # Collect synthesis signals and scores
        if synthesis_analysis["detected_patterns"]:
            for pattern_type, pattern_data in synthesis_analysis["detected_patterns"].items():
                all_signals.append(pattern_type)
                all_scores.append(pattern_data["intensity"])
                explainability_parts.append(f"Synthesis: {pattern_type} ({pattern_data['intensity']:.2f})")
        
        # Add correlation and amplification scores
        if correlation_analysis["correlation_score"] > 0:
            all_scores.append(correlation_analysis["correlation_score"])
            explainability_parts.append(f"Correlation: {correlation_analysis['correlation_score']:.2f}")
        
        if amplification_analysis["amplification_score"] > 0:
            all_scores.append(amplification_analysis["amplification_score"])
            explainability_parts.append(f"Amplification: {amplification_analysis['amplification_score']:.2f}")
        
        # Add Azure AI scores
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("synthesis_risk_score"):
                all_scores.append(azure_openai_result["synthesis_risk_score"])
            if azure_openai_result.get("detected_threats"):
                all_signals.extend(azure_openai_result["detected_threats"])
        
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("synthesis_risk_score"):
                all_scores.append(azure_cognitive_result["synthesis_risk_score"])
            if azure_cognitive_result.get("cognitive_threats"):
                all_signals.extend(azure_cognitive_result["cognitive_threats"])

        # Calculate comprehensive synthesis risk score
        synthesis_risk_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Apply prediction multiplier
        prediction_multiplier = prediction_analysis.get("prediction_multiplier", 1.0)
        overall_score = min(1.0, synthesis_risk_score * prediction_multiplier)
        
        # Determine threat level
        threat_level = determine_synthesis_threat_level_enhanced(
            overall_score, 
            escalation_analysis, 
            synthesis_analysis, 
            correlation_analysis, 
            amplification_analysis
        )

        # === 5. Enhanced Explainability ===
        explainability = " | ".join(explainability_parts) if explainability_parts else "Threat synthesis completed"

        # === 6. Recommended Action ===
        if threat_level == "Critical":
            recommended_action = "Immediate Block"
        elif threat_level == "High":
            recommended_action = "Alert & Block"
        elif threat_level == "Medium":
            recommended_action = "Enhanced Monitor"
        else:
            recommended_action = "Standard Monitor"

        # === 7. Comprehensive Evidence Collection ===
        evidence = [
            {"type": "azure_cognitive_services", "data": azure_cognitive_result},
            {"type": "azure_openai", "data": azure_openai_result},
            {"type": "escalation_analysis", "data": escalation_analysis},
            {"type": "synthesis_analysis", "data": synthesis_analysis},
            {"type": "correlation_analysis", "data": correlation_analysis},
            {"type": "amplification_analysis", "data": amplification_analysis},
            {"type": "prediction_analysis", "data": prediction_analysis}
        ]

        # === 8. Return Enhanced ModuleOutput ===
        module_output = ModuleOutput(
            module_name="TDC-AI8-ThreatSynthesis",
            score=overall_score,
            flags=list(set(all_signals)),  # Remove duplicates
            notes=explainability,
            confidence=azure_openai_result.get("confidence_score", 0.8) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.8,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "threat_level": threat_level,
                "analysis_type": "hybrid",
                "prediction_multiplier": prediction_multiplier,
                "signal_count": len(set(all_signals)),
                "escalation_score": escalation_analysis.get("escalation_score", 0.0),
                "synthesis_score": synthesis_analysis.get("synthesis_score", 0.0),
                "correlation_score": correlation_analysis.get("correlation_score", 0.0),
                "amplification_score": amplification_analysis.get("amplification_score", 0.0),
                "prediction_confidence": prediction_analysis.get("prediction_confidence", 0.0)
            }
        )
        
        logger.info(f"[TDC-AI8] Synthesis completed - Threat Level: {threat_level}, Score: {overall_score}")
        return module_output.to_dict()
        
    except Exception as e:
        logger.error(f"[TDC-AI8] Analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI8-ThreatSynthesis",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Threat synthesis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()

def detect_escalation_patterns_enhanced(module_outputs: List[Dict], conversation_context: Dict = None) -> Dict:
    """Enhanced escalation pattern detection with sophisticated analysis."""
    if not module_outputs:
        return {"detected_patterns": {}, "escalation_score": 0.0, "escalation_profile": {}}
    
    detected_patterns = {}
    escalation_profile = {}
    escalation_score = 0.0
    
    for output in module_outputs:
        notes = output.get("notes", "").lower()
        score = output.get("score", 0.0)
        
        # Analyze each escalation category
        for category, patterns in ESCALATION_PATTERNS.items():
            pattern_count = 0
            pattern_matches = []
            
            for pattern in patterns:
                if pattern in notes:
                    pattern_count += 1
                    pattern_matches.append(pattern)
            
            if pattern_count > 0:
                detected_patterns[category] = {
                    "patterns_found": pattern_matches,
                    "count": pattern_count,
                    "intensity": min(1.0, pattern_count / 3.0),
                    "severity": determine_escalation_severity(category)
                }
                escalation_profile[category] = {
                    "count": pattern_count,
                    "intensity": min(1.0, pattern_count / 3.0)
                }
    
    # Calculate overall escalation score
    if escalation_profile:
        escalation_score = sum(profile["intensity"] for profile in escalation_profile.values()) / len(escalation_profile)
    
    return {
        "detected_patterns": detected_patterns,
        "escalation_score": escalation_score,
        "escalation_profile": escalation_profile
    }

def detect_synthesis_signals_enhanced(module_outputs: List[Dict], conversation_context: Dict = None) -> Dict:
    """Enhanced synthesis signal detection with advanced pattern recognition."""
    if not module_outputs:
        return {"detected_patterns": {}, "synthesis_score": 0.0, "synthesis_profile": {}}
    
    detected_patterns = {}
    synthesis_profile = {}
    synthesis_score = 0.0
    
    for output in module_outputs:
        notes = output.get("notes", "").lower()
        score = output.get("score", 0.0)
        
        # Analyze each synthesis category
        for category, signals in SYNTHESIS_SIGNALS.items():
            signal_count = 0
            signal_matches = []
            
            for signal in signals:
                if signal in notes:
                    signal_count += 1
                    signal_matches.append(signal)
            
            if signal_count > 0:
                detected_patterns[category] = {
                    "signals_found": signal_matches,
                    "count": signal_count,
                    "intensity": min(1.0, signal_count / 3.0),
                    "severity": determine_synthesis_severity(category)
                }
                synthesis_profile[category] = {
                    "count": signal_count,
                    "intensity": min(1.0, signal_count / 3.0)
                }
    
    # Calculate overall synthesis score
    if synthesis_profile:
        synthesis_score = sum(profile["intensity"] for profile in synthesis_profile.values()) / len(synthesis_profile)
    
    return {
        "detected_patterns": detected_patterns,
        "synthesis_score": synthesis_score,
        "synthesis_profile": synthesis_profile
    }

def analyze_cross_module_correlation_advanced(module_outputs: List[Dict], conversation_context: Dict = None) -> Dict:
    """Advanced cross-module correlation analysis."""
    if not module_outputs or len(module_outputs) < 2:
        return {"correlation_score": 0.0, "correlation_profile": {}, "correlation_patterns": []}
    
    correlation_profile = {}
    correlation_patterns = []
    correlation_score = 0.0
    
    # Analyze correlations between modules
    for i, output1 in enumerate(module_outputs):
        for j, output2 in enumerate(module_outputs[i+1:], i+1):
            score1 = output1.get("score", 0.0)
            score2 = output2.get("score", 0.0)
            
            # Calculate correlation strength
            correlation_strength = min(score1, score2) * 0.5 + max(score1, score2) * 0.3
            
            if correlation_strength > 0.3:  # Threshold for significant correlation
                module_pair = f"{output1.get('module_name', 'Unknown')}-{output2.get('module_name', 'Unknown')}"
                correlation_profile[module_pair] = {
                    "strength": correlation_strength,
                    "score1": score1,
                    "score2": score2
                }
                correlation_patterns.append(module_pair)
    
    # Calculate overall correlation score
    if correlation_profile:
        correlation_score = sum(profile["strength"] for profile in correlation_profile.values()) / len(correlation_profile)
    
    return {
        "correlation_score": correlation_score,
        "correlation_profile": correlation_profile,
        "correlation_patterns": correlation_patterns
    }

def analyze_threat_amplification_advanced(module_outputs: List[Dict], conversation_context: Dict = None) -> Dict:
    """Advanced threat amplification analysis."""
    if not module_outputs:
        return {"amplification_score": 0.0, "amplification_profile": {}, "amplification_factors": []}
    
    amplification_profile = {}
    amplification_factors = []
    amplification_score = 0.0
    
    # Analyze threat amplification factors
    high_risk_modules = [output for output in module_outputs if output.get("score", 0.0) > 0.7]
    medium_risk_modules = [output for output in module_outputs if 0.4 <= output.get("score", 0.0) <= 0.7]
    
    # Calculate amplification based on risk distribution
    if high_risk_modules:
        high_risk_amplification = len(high_risk_modules) * 0.3
        amplification_factors.append(f"High-risk modules: {len(high_risk_modules)}")
        amplification_profile["high_risk"] = {
            "count": len(high_risk_modules),
            "amplification": high_risk_amplification
        }
    
    if medium_risk_modules:
        medium_risk_amplification = len(medium_risk_modules) * 0.2
        amplification_factors.append(f"Medium-risk modules: {len(medium_risk_modules)}")
        amplification_profile["medium_risk"] = {
            "count": len(medium_risk_modules),
            "amplification": medium_risk_amplification
        }
    
    # Calculate overall amplification score
    if amplification_profile:
        amplification_score = sum(profile["amplification"] for profile in amplification_profile.values())
        amplification_score = min(1.0, amplification_score)
    
    return {
        "amplification_score": amplification_score,
        "amplification_profile": amplification_profile,
        "amplification_factors": amplification_factors
    }

def predict_escalation_trajectory_advanced(module_outputs: List[Dict], conversation_context: Dict = None) -> Dict:
    """Advanced escalation trajectory prediction."""
    if not module_outputs:
        return {"prediction_multiplier": 1.0, "prediction_confidence": 0.0, "trajectory_profile": {}}
    
    trajectory_profile = {}
    prediction_confidence = 0.0
    prediction_multiplier = 1.0
    
    # Analyze escalation trajectory indicators
    high_scores = [output.get("score", 0.0) for output in module_outputs if output.get("score", 0.0) > 0.6]
    escalation_indicators = sum(1 for output in module_outputs if "escalation" in output.get("notes", "").lower())
    
    # Calculate trajectory factors
    if high_scores:
        avg_high_score = sum(high_scores) / len(high_scores)
        trajectory_profile["high_score_average"] = avg_high_score
        prediction_multiplier += avg_high_score * 0.2
    
    if escalation_indicators > 0:
        trajectory_profile["escalation_indicators"] = escalation_indicators
        prediction_multiplier += escalation_indicators * 0.1
    
    # Calculate prediction confidence
    prediction_confidence = min(1.0, (len(high_scores) / len(module_outputs)) * 0.5 + (escalation_indicators / len(module_outputs)) * 0.5)
    
    return {
        "prediction_multiplier": min(2.0, prediction_multiplier),
        "prediction_confidence": prediction_confidence,
        "trajectory_profile": trajectory_profile
    }

def determine_escalation_severity(category: str) -> str:
    """Determine escalation severity for a category."""
    for severity, categories in ESCALATION_SEVERITY.items():
        if category in categories:
            return severity
    return "low"

def determine_synthesis_severity(category: str) -> str:
    """Determine synthesis severity for a category."""
    for severity, categories in ESCALATION_SEVERITY.items():
        if category in categories:
            return severity
    return "low"

def determine_synthesis_threat_level_enhanced(
    score: float, 
    escalation_analysis: Dict, 
    synthesis_analysis: Dict, 
    correlation_analysis: Dict, 
    amplification_analysis: Dict
) -> str:
    """Enhanced threat level determination for synthesis."""
    escalation_score = escalation_analysis.get("escalation_score", 0.0)
    synthesis_score = synthesis_analysis.get("synthesis_score", 0.0)
    correlation_score = correlation_analysis.get("correlation_score", 0.0)
    amplification_score = amplification_analysis.get("amplification_score", 0.0)
    
    # Critical conditions
    if (score > 0.8 or escalation_score > 0.8 or 
        (correlation_score > 0.7 and amplification_score > 0.7)):
        return "Critical"
    # High conditions
    elif (score > 0.6 or escalation_score > 0.6 or synthesis_score > 0.6 or
          correlation_score > 0.5 or amplification_score > 0.5):
        return "High"
    # Medium conditions
    elif (score > 0.4 or escalation_score > 0.4 or synthesis_score > 0.4 or
          correlation_score > 0.3 or amplification_score > 0.3):
        return "Medium"
    # Low conditions
    elif (score > 0.2 or escalation_score > 0.2 or synthesis_score > 0.2 or
          correlation_score > 0.2 or amplification_score > 0.2):
        return "Low"
    else:
        return "Minimal"

def detect_escalation_patterns(module_outputs: List[Dict]) -> (bool, float, List[str]):
    """Legacy escalation pattern detection for backward compatibility."""
    signals = []
    score = 0.0
    for output in module_outputs:
        notes = output.get("notes", "").lower()
        for pattern_list in ESCALATION_PATTERNS.values():
            for pattern in pattern_list:
                if pattern in notes:
                    signals.append(pattern)
                    score += 0.2
    detected = len(signals) > 0
    score = min(1.0, score)
    return detected, score, signals

def detect_synthesis_signals(module_outputs: List[Dict]) -> (bool, float, List[str]):
    """Legacy synthesis signal detection for backward compatibility."""
    signals = []
    score = 0.0
    for output in module_outputs:
        notes = output.get("notes", "").lower()
        for signal_list in SYNTHESIS_SIGNALS.values():
            for signal in signal_list:
                if signal in notes:
                    signals.append(signal)
                    score += 0.2
    detected = len(signals) > 0
    score = min(1.0, score)
    return detected, score, signals

def determine_synthesis_threat_level(score: float, escalation: bool, synthesis: bool) -> str:
    """Legacy threat level determination for backward compatibility."""
    if score > 0.8 or (escalation and synthesis):
        return "Critical"
    elif score > 0.6 or escalation:
        return "High"
    elif score > 0.4 or synthesis:
        return "Medium"
    elif score > 0.2:
        return "Low"
    else:
        return "Minimal"

def generate_synthesis_analysis_summary(
    escalation_detected, escalation_signals, synthesis_detected, synthesis_signals,
    azure_openai_result, azure_cognitive_result, threat_level, score
) -> str:
    """Legacy synthesis summary generation for backward compatibility."""
    try:
        summary_parts = []
        if escalation_detected:
            summary_parts.append(f"Escalation detected: {', '.join(escalation_signals)}")
        if synthesis_detected:
            summary_parts.append(f"Synthesis signals: {', '.join(synthesis_signals)}")
        summary_parts.append(f"Threat level: {threat_level}")
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("synthesis_summary"):
                summary_parts.append(f"AI Analysis: {azure_openai_result['synthesis_summary']}")
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("synthesis_summary"):
                summary_parts.append(f"Cognitive Analysis: {azure_cognitive_result['synthesis_summary']}")
        return ". ".join(summary_parts) if summary_parts else "Threat synthesis completed"
    except Exception as e:
        logger.error(f"Synthesis analysis summary generation failed: {e}")
        return "Threat synthesis completed"

def synthesize_threats(module_outputs: List[Dict], conversation_context: Dict = None, session_id: str = None) -> Dict:
    """Main entry point for threat synthesis."""
    try:
        return synthesize_threats_comprehensive(module_outputs, conversation_context, session_id)
    except Exception as e:
        logger.error(f"[TDC-AI8] Main synthesis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI8-ThreatSynthesis",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Threat synthesis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()
