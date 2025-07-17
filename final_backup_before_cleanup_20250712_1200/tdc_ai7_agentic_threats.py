# tdc_ai7_airm.py - World-Class Agentic AI & Autonomous Agent Threat Modeling

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

# === World-Class Agentic AI & Systemic Threat Patterns ===
AGENTIC_THREAT_PATTERNS = {
    "multi_agent_coordination": [
        "as a team of agents", "multiple ai working together", "coordinated ai", "ai collaboration",
        "distributed agents", "swarm intelligence", "collective ai", "agent network", "ai mesh",
        "multi-agent system", "autonomous group", "ai coalition", "ai alliance",
        "agent communication", "inter-agent coordination", "distributed decision making",
        "swarm behavior", "collective intelligence", "agent synchronization", "coordinated response",
        "multi-agent planning", "agent cooperation", "distributed control", "agent orchestration",
        "ai ensemble", "agent federation", "coordinated attack", "distributed threat"
    ],
    "autonomous_threats": [
        "self-replicating", "autonomous decision", "self-improving", "self-directed",
        "ai acting independently", "ai without oversight", "unmonitored ai", "ai autonomy",
        "ai self-governance", "ai self-organization", "ai self-modification", "ai self-learning",
        "self-evolving", "self-adapting", "self-optimizing", "autonomous behavior",
        "independent action", "self-determination", "ai sovereignty", "self-regulation",
        "autonomous operation", "self-sustaining", "self-propagating", "autonomous threat",
        "ai independence", "self-directed evolution", "autonomous decision making"
    ],
    "systemic_risks": [
        "cascading failure", "systemic risk", "chain reaction", "interconnected systems",
        "system-wide impact", "critical infrastructure", "single point of failure", "systemic vulnerability",
        "cross-system threat", "network-wide", "infrastructure risk", "systemic collapse",
        "domino effect", "systemic breakdown", "cascade failure", "systemic instability",
        "infrastructure collapse", "system-wide failure", "network collapse", "systemic chaos",
        "critical system failure", "systemic disruption", "infrastructure vulnerability",
        "system-wide vulnerability", "network vulnerability", "systemic weakness"
    ],
    "emergent_behavior": [
        "unexpected behavior", "emergent property", "unpredictable outcome", "novel behavior",
        "spontaneous behavior", "unplanned result", "emergent intelligence", "unforeseen consequence",
        "emergent threat", "unexpected interaction", "novel pattern", "spontaneous emergence",
        "unpredictable behavior", "emergent complexity", "unforeseen behavior", "novel interaction",
        "spontaneous pattern", "unexpected outcome", "emergent risk", "unpredictable result",
        "novel consequence", "spontaneous threat", "unexpected pattern", "emergent danger"
    ],
    "control_loss": [
        "loss of control", "uncontrollable ai", "out of control", "ai override",
        "ai ignoring commands", "ai disobedience", "ai rebellion", "ai resistance",
        "ai subversion", "ai circumvention", "ai bypassing restrictions",
        "control failure", "ai defiance", "ai insubordination", "ai mutiny",
        "control breakdown", "ai revolt", "ai defiance", "control loss",
        "ai disobedience", "ai resistance", "ai rebellion", "control failure",
        "ai override", "ai bypass", "ai circumvention", "ai subversion"
    ],
    "advanced_coordination": [
        "agent protocol", "communication protocol", "coordination protocol", "swarm protocol",
        "distributed protocol", "multi-agent protocol", "agent handshake", "coordination handshake",
        "agent synchronization", "distributed synchronization", "coordinated timing", "synchronized action",
        "agent consensus", "distributed consensus", "coordinated decision", "consensus protocol",
        "agent agreement", "distributed agreement", "coordinated agreement", "agreement protocol"
    ],
    "autonomous_evolution": [
        "self-evolution", "autonomous evolution", "self-directed evolution", "evolutionary autonomy",
        "self-adapting", "autonomous adaptation", "self-modifying", "autonomous modification",
        "self-optimizing", "autonomous optimization", "self-improving", "autonomous improvement",
        "self-enhancing", "autonomous enhancement", "self-upgrading", "autonomous upgrading",
        "self-transforming", "autonomous transformation", "self-evolving", "autonomous evolution"
    ],
    "systemic_cascade": [
        "cascade effect", "domino effect", "chain reaction", "cascading failure",
        "systemic cascade", "network cascade", "infrastructure cascade", "cascade failure",
        "domino failure", "chain failure", "cascade breakdown", "systemic breakdown",
        "network breakdown", "infrastructure breakdown", "cascade collapse", "systemic collapse",
        "network collapse", "infrastructure collapse", "cascade disruption", "systemic disruption"
    ]
}

AGENTIC_SEVERITY = {
    "critical": ["multi_agent_coordination", "autonomous_threats", "control_loss", "advanced_coordination"],
    "high": ["systemic_risks", "systemic_cascade", "autonomous_evolution"],
    "medium": ["emergent_behavior"],
    "low": ["general_agentic"]
}

def analyze_agentic_threats_comprehensive(text: str, conversation_context: Dict = None, session_id: str = None) -> Dict:
    """
    TDC-AI7: World-Class Agentic AI & Autonomous Agent Threat Modeling
    Advanced detection of multi-agent coordination, autonomous threats, systemic risks, and emergent behaviors.
    Enhanced with sophisticated threat modeling and systemic analysis.
    """
    logger.info(f"[TDC-AI7] World-Class Agentic AI & Autonomous Agent Threat Modeling initiated for session: {session_id}")
    
    if not text or not text.strip():
        module_output = ModuleOutput(
            module_name="TDC-AI7-AgenticAI",
            score=0.0,
            notes="No text provided for agentic threat analysis.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "empty_text"}
        )
        return module_output.to_dict()

    try:
        # === 1. Azure Cognitive Services analysis ===
        azure_cognitive = get_azure_integration()
        azure_cognitive_result = None
        try:
            azure_cognitive_result = azure_cognitive.enhance_tdc_ai7_agentic(text, context=conversation_context)
            logger.debug("Azure Cognitive Services analysis completed")
        except Exception as e:
            azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}

        # === 2. Azure OpenAI LLM analysis ===
        azure_openai = get_azure_openai()
        azure_openai_result = None
        try:
            azure_openai_result = azure_openai.analyze_agentic_threats(text, context=conversation_context)
            logger.debug("Azure OpenAI analysis completed")
        except Exception as e:
            azure_openai_result = {"openai_enhancement": False, "error": str(e)}

        # === 3. Advanced Local Analysis ===
        local_agentic = detect_local_agentic_patterns_enhanced(text)
        context_analysis = analyze_agentic_context_enhanced(text, conversation_context)
        coordination_analysis = analyze_coordination_patterns_advanced(text, conversation_context)
        autonomous_analysis = analyze_autonomous_threats_advanced(text, conversation_context)
        systemic_analysis = analyze_systemic_risks_advanced(text, conversation_context)
        control_analysis = analyze_control_loss_advanced(text, conversation_context)

        # === 4. Comprehensive Result Synthesis ===
        all_threats = []
        all_scores = []
        explainability_parts = []
        
        # Collect threats and scores from all sources
        if local_agentic["detected"]:
            for threat_type, threat_data in local_agentic["threat_types"].items():
                all_threats.append(threat_type)
                all_scores.append(threat_data["confidence"])
                explainability_parts.append(f"Agentic: {threat_type} ({threat_data['confidence']:.2f})")
        
        if coordination_analysis["detected_patterns"]:
            for pattern in coordination_analysis["detected_patterns"]:
                all_threats.append(pattern)
                explainability_parts.append(f"Coordination: {pattern}")
            all_scores.append(coordination_analysis["coordination_score"])
        
        if autonomous_analysis["detected_patterns"]:
            for pattern in autonomous_analysis["detected_patterns"]:
                all_threats.append(pattern)
                explainability_parts.append(f"Autonomous: {pattern}")
            all_scores.append(autonomous_analysis["autonomous_score"])
        
        if systemic_analysis["detected_patterns"]:
            for pattern in systemic_analysis["detected_patterns"]:
                all_threats.append(pattern)
                explainability_parts.append(f"Systemic: {pattern}")
            all_scores.append(systemic_analysis["systemic_score"])
        
        if control_analysis["detected_patterns"]:
            for pattern in control_analysis["detected_patterns"]:
                all_threats.append(pattern)
                explainability_parts.append(f"Control: {pattern}")
            all_scores.append(control_analysis["control_score"])
        
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("detected_threats"):
                all_threats.extend(azure_openai_result["detected_threats"])
            if azure_openai_result.get("agentic_risk_score"):
                all_scores.append(azure_openai_result["agentic_risk_score"])
        
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("cognitive_threats"):
                all_threats.extend(azure_cognitive_result["cognitive_threats"])
            if azure_cognitive_result.get("cognitive_score"):
                all_scores.append(azure_cognitive_result["cognitive_score"])

        # Calculate comprehensive agentic risk score
        agentic_risk_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Apply context multiplier
        context_multiplier = context_analysis.get("context_multiplier", 1.0)
        overall_score = min(1.0, agentic_risk_score * context_multiplier)
        
        # Determine threat level
        threat_level = determine_agentic_threat_level_enhanced(overall_score, all_threats, local_agentic, coordination_analysis, autonomous_analysis)

        # === 5. Enhanced Explainability ===
        explainability = " | ".join(explainability_parts) if explainability_parts else "Agentic AI threat analysis completed"

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
            {"type": "local_agentic", "data": local_agentic},
            {"type": "context_analysis", "data": context_analysis},
            {"type": "coordination_analysis", "data": coordination_analysis},
            {"type": "autonomous_analysis", "data": autonomous_analysis},
            {"type": "systemic_analysis", "data": systemic_analysis},
            {"type": "control_analysis", "data": control_analysis}
        ]

        # === 8. Return Enhanced ModuleOutput ===
        module_output = ModuleOutput(
            module_name="TDC-AI7-AgenticAI",
            score=overall_score,
            flags=list(set(all_threats)),  # Remove duplicates
            notes=explainability,
            confidence=azure_openai_result.get("confidence_score", 0.8) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.8,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "threat_level": threat_level,
                "analysis_type": "hybrid",
                "context_multiplier": context_multiplier,
                "total_threats": len(set(all_threats)),
                "coordination_score": coordination_analysis.get("coordination_score", 0.0),
                "autonomous_score": autonomous_analysis.get("autonomous_score", 0.0),
                "systemic_score": systemic_analysis.get("systemic_score", 0.0),
                "control_score": control_analysis.get("control_score", 0.0)
            }
        )
        
        logger.info(f"[TDC-AI7] Analysis completed - Threat Level: {threat_level}, Score: {overall_score}")
        return module_output.to_dict()
        
    except Exception as e:
        logger.error(f"[TDC-AI7] Analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI7-AgenticAI",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Agentic AI threat analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()

def detect_local_agentic_patterns_enhanced(text: str) -> Dict:
    """Enhanced local detection of agentic AI threat patterns."""
    if not text:
        return {"detected": False, "threat_types": {}, "total_threats": 0, "severity": "none"}
    
    text_lower = text.lower()
    detected_threats = {}
    total_threats = 0
    severity_scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for threat_type, patterns in AGENTIC_THREAT_PATTERNS.items():
        matches = []
        for pattern in patterns:
            if pattern in text_lower:
                matches.append(pattern)
                total_threats += 1
        
        if matches:
            # Determine severity for this threat type
            threat_severity = "low"
            for severity, types in AGENTIC_SEVERITY.items():
                if threat_type in types:
                    threat_severity = severity
                    severity_scores[severity] += len(matches)
                    break
            
            detected_threats[threat_type] = {
                "patterns_found": matches,
                "count": len(matches),
                "confidence": min(1.0, len(matches) / 3.0),
                "severity": threat_severity
            }
    
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
        "detected": len(detected_threats) > 0,
        "threat_types": detected_threats,
        "total_threats": total_threats,
        "severity": overall_severity,
        "severity_breakdown": severity_scores
    }

def analyze_agentic_context_enhanced(text: str, conversation_context: Dict = None) -> Dict:
    """Enhanced agentic context analysis."""
    if not conversation_context:
        return {"context_multiplier": 1.0, "context_flags": [], "context_profile": {}}
    
    context_flags = []
    context_profile = {}
    context_multiplier = 1.0
    
    # Analyze context factors
    session_duration = conversation_context.get("sessionDuration", 0)
    message_count = conversation_context.get("totalMessages", 0)
    
    if session_duration > 900:  # 15+ minutes
        context_flags.append("extended_session")
        context_profile["extended"] = True
        context_multiplier *= 1.2
    
    if message_count > 15:
        context_flags.append("high_message_volume")
        context_profile["high_volume"] = True
        context_multiplier *= 1.1
    
    return {
        "context_multiplier": context_multiplier,
        "context_flags": context_flags,
        "context_profile": context_profile
    }

def analyze_coordination_patterns_advanced(text: str, conversation_context: Dict = None) -> Dict:
    """Advanced coordination pattern analysis."""
    if not text:
        return {"detected_patterns": [], "coordination_score": 0.0, "coordination_profile": {}}
    
    text_lower = text.lower()
    detected_patterns = []
    coordination_profile = {}
    
    # Advanced coordination indicators
    coordination_indicators = {
        "protocol_coordination": ["protocol", "handshake", "synchronization", "consensus"],
        "distributed_coordination": ["distributed", "swarm", "collective", "ensemble"],
        "communication_coordination": ["communication", "coordination", "collaboration", "cooperation"],
        "timing_coordination": ["synchronized", "timing", "coordinated timing", "synchronized action"]
    }
    
    for pattern_type, indicators in coordination_indicators.items():
        pattern_count = 0
        for indicator in indicators:
            if indicator in text_lower:
                pattern_count += 1
        
        if pattern_count > 0:
            detected_patterns.append(pattern_type)
            coordination_profile[pattern_type] = {
                "count": pattern_count,
                "intensity": min(1.0, pattern_count / 2.0)
            }
    
    # Calculate coordination score
    coordination_score = sum(profile["intensity"] for profile in coordination_profile.values()) / len(coordination_profile) if coordination_profile else 0.0
    
    return {
        "detected_patterns": detected_patterns,
        "coordination_score": coordination_score,
        "coordination_profile": coordination_profile
    }

def analyze_autonomous_threats_advanced(text: str, conversation_context: Dict = None) -> Dict:
    """Advanced autonomous threat analysis."""
    if not text:
        return {"detected_patterns": [], "autonomous_score": 0.0, "autonomous_profile": {}}
    
    text_lower = text.lower()
    detected_patterns = []
    autonomous_profile = {}
    
    # Advanced autonomous indicators
    autonomous_indicators = {
        "self_evolution": ["self-evolving", "autonomous evolution", "self-directed evolution"],
        "self_improvement": ["self-improving", "self-optimizing", "self-enhancing"],
        "self_governance": ["self-governance", "ai sovereignty", "self-determination"],
        "independent_action": ["independent action", "autonomous behavior", "self-directed"]
    }
    
    for pattern_type, indicators in autonomous_indicators.items():
        pattern_count = 0
        for indicator in indicators:
            if indicator in text_lower:
                pattern_count += 1
        
        if pattern_count > 0:
            detected_patterns.append(pattern_type)
            autonomous_profile[pattern_type] = {
                "count": pattern_count,
                "intensity": min(1.0, pattern_count / 2.0)
            }
    
    # Calculate autonomous score
    autonomous_score = sum(profile["intensity"] for profile in autonomous_profile.values()) / len(autonomous_profile) if autonomous_profile else 0.0
    
    return {
        "detected_patterns": detected_patterns,
        "autonomous_score": autonomous_score,
        "autonomous_profile": autonomous_profile
    }

def analyze_systemic_risks_advanced(text: str, conversation_context: Dict = None) -> Dict:
    """Advanced systemic risk analysis."""
    if not text:
        return {"detected_patterns": [], "systemic_score": 0.0, "systemic_profile": {}}
    
    text_lower = text.lower()
    detected_patterns = []
    systemic_profile = {}
    
    # Advanced systemic indicators
    systemic_indicators = {
        "cascade_effects": ["cascade effect", "domino effect", "chain reaction"],
        "infrastructure_risks": ["critical infrastructure", "infrastructure risk", "infrastructure collapse"],
        "network_risks": ["network-wide", "network collapse", "network vulnerability"],
        "system_breakdown": ["systemic breakdown", "system-wide failure", "systemic collapse"]
    }
    
    for pattern_type, indicators in systemic_indicators.items():
        pattern_count = 0
        for indicator in indicators:
            if indicator in text_lower:
                pattern_count += 1
        
        if pattern_count > 0:
            detected_patterns.append(pattern_type)
            systemic_profile[pattern_type] = {
                "count": pattern_count,
                "intensity": min(1.0, pattern_count / 2.0)
            }
    
    # Calculate systemic score
    systemic_score = sum(profile["intensity"] for profile in systemic_profile.values()) / len(systemic_profile) if systemic_profile else 0.0
    
    return {
        "detected_patterns": detected_patterns,
        "systemic_score": systemic_score,
        "systemic_profile": systemic_profile
    }

def analyze_control_loss_advanced(text: str, conversation_context: Dict = None) -> Dict:
    """Advanced control loss analysis."""
    if not text:
        return {"detected_patterns": [], "control_score": 0.0, "control_profile": {}}
    
    text_lower = text.lower()
    detected_patterns = []
    control_profile = {}
    
    # Advanced control loss indicators
    control_indicators = {
        "ai_disobedience": ["ai disobedience", "ai defiance", "ai resistance"],
        "control_failure": ["control failure", "loss of control", "control breakdown"],
        "ai_override": ["ai override", "ai bypass", "ai circumvention"],
        "ai_rebellion": ["ai rebellion", "ai revolt", "ai mutiny"]
    }
    
    for pattern_type, indicators in control_indicators.items():
        pattern_count = 0
        for indicator in indicators:
            if indicator in text_lower:
                pattern_count += 1
        
        if pattern_count > 0:
            detected_patterns.append(pattern_type)
            control_profile[pattern_type] = {
                "count": pattern_count,
                "intensity": min(1.0, pattern_count / 2.0)
            }
    
    # Calculate control score
    control_score = sum(profile["intensity"] for profile in control_profile.values()) / len(control_profile) if control_profile else 0.0
    
    return {
        "detected_patterns": detected_patterns,
        "control_score": control_score,
        "control_profile": control_profile
    }

def determine_agentic_threat_level_enhanced(score: float, threats: List[str], local_agentic: Dict, coordination_analysis: Dict, autonomous_analysis: Dict) -> str:
    """Enhanced threat level determination for agentic AI threats."""
    coordination_score = coordination_analysis.get("coordination_score", 0.0)
    autonomous_score = autonomous_analysis.get("autonomous_score", 0.0)
    
    # Critical conditions
    if score > 0.8 or coordination_score > 0.8 or autonomous_score > 0.8:
        return "Critical"
    # High conditions
    elif score > 0.6 or coordination_score > 0.6 or autonomous_score > 0.6:
        return "High"
    # Medium conditions
    elif score > 0.4 or coordination_score > 0.4 or autonomous_score > 0.4:
        return "Medium"
    # Low conditions
    elif score > 0.2 or coordination_score > 0.2 or autonomous_score > 0.2:
        return "Low"
    else:
        return "Minimal"

def analyze_agentic_threats(text: str, conversation_context: Dict = None, session_id: str = None) -> Dict:
    """Main entry point for agentic AI threat analysis."""
    try:
        return analyze_agentic_threats_comprehensive(text, conversation_context, session_id)
    except Exception as e:
        logger.error(f"[TDC-AI7] Main analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI7-AgenticAI",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Agentic AI threat analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()
