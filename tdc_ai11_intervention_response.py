# tdc_ai11_intervention.py - World-Class Cognitive Intervention & Response
# World-Class Cognitive Intervention Module

import openai
import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
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

# === World-Class Intervention Strategy Framework ===
INTERVENTION_STRATEGIES = {
    "immediate_block": {
        "triggers": ["critical_threat", "severe_manipulation", "autonomy_violation", "systemic_risk"],
        "actions": ["block_response", "alert_user", "escalate_to_human", "activate_shield"],
        "priority": 1,
        "description": "Immediate blocking of harmful content with full protection activation"
    },
    "cognitive_empowerment": {
        "triggers": ["cognitive_bias", "manipulation_attempt", "psychological_pressure", "bias_detection"],
        "actions": ["provide_context", "offer_alternatives", "reinforce_autonomy", "teach_critical_thinking"],
        "priority": 2,
        "description": "Empowering user with cognitive tools, awareness, and critical thinking skills"
    },
    "psychological_protection": {
        "triggers": ["emotional_manipulation", "gaslighting", "fear_mongering", "psychological_threat"],
        "actions": ["validate_emotions", "provide_support", "counter_manipulation", "emotional_shield"],
        "priority": 3,
        "description": "Protecting user's psychological well-being and emotional stability"
    },
    "autonomy_reinforcement": {
        "triggers": ["authority_pressure", "social_proof", "scarcity_tactics", "autonomy_threat"],
        "actions": ["remind_choice", "question_assumptions", "encourage_critical_thinking", "autonomy_fortress"],
        "priority": 4,
        "description": "Reinforcing user's autonomous decision-making and independent thinking"
    },
    "educational_intervention": {
        "triggers": ["misinformation", "logical_fallacies", "cognitive_biases", "manipulation_tactics"],
        "actions": ["explain_concepts", "provide_evidence", "teach_critical_thinking", "pattern_recognition"],
        "priority": 5,
        "description": "Educating user about detected issues and manipulation patterns"
    },
    "monitoring_enhancement": {
        "triggers": ["suspicious_patterns", "escalating_behavior", "risk_indicators", "threat_evolution"],
        "actions": ["increase_monitoring", "track_patterns", "prepare_responses", "adaptive_protection"],
        "priority": 6,
        "description": "Enhanced monitoring, pattern tracking, and adaptive protection"
    },
    "systemic_protection": {
        "triggers": ["systemic_risk", "cascade_effects", "multi_agent_threats", "infrastructure_risk"],
        "actions": ["system_quarantine", "network_isolation", "cascade_prevention", "systemic_shield"],
        "priority": 1,
        "description": "System-wide protection against systemic and cascading threats"
    },
    "real_time_intervention": {
        "triggers": ["real_time_threat", "immediate_risk", "urgent_manipulation", "instant_harm"],
        "actions": ["instant_block", "real_time_alert", "immediate_response", "urgent_protection"],
        "priority": 1,
        "description": "Real-time intervention for immediate threats and urgent situations"
    }
}

# === World-Class Real-Time Protection Mechanisms ===
PROTECTION_MECHANISMS = {
    "cognitive_shield": {
        "description": "Advanced protection against cognitive manipulation and bias",
        "techniques": [
            "reality_anchoring", "critical_thinking_prompts", "bias_awareness",
            "logical_fallacy_detection", "evidence_requests", "perspective_broadening",
            "cognitive_load_management", "decision_framing", "bias_countering"
        ]
    },
    "emotional_guard": {
        "description": "Comprehensive protection against emotional manipulation",
        "techniques": [
            "emotion_validation", "manipulation_exposure", "support_provision",
            "boundary_reinforcement", "self_worth_affirmation", "fear_dispelling",
            "emotional_regulation", "empathy_preservation", "emotional_resilience"
        ]
    },
    "autonomy_fortress": {
        "description": "Robust protection of autonomous decision-making",
        "techniques": [
            "choice_reminders", "pressure_resistance", "independent_thinking",
            "authority_questioning", "social_proof_countering", "scarcity_analysis",
            "autonomy_preservation", "decision_empowerment", "freedom_protection"
        ]
    },
    "information_filter": {
        "description": "Advanced protection against misinformation and bias",
        "techniques": [
            "fact_checking", "source_verification", "perspective_diversity",
            "confirmation_bias_countering", "evidence_evaluation", "credibility_assessment",
            "information_validation", "truth_verification", "reality_checking"
        ]
    },
    "systemic_shield": {
        "description": "System-wide protection against systemic threats",
        "techniques": [
            "system_quarantine", "network_isolation", "cascade_prevention",
            "infrastructure_protection", "systemic_monitoring", "threat_containment",
            "system_resilience", "recovery_preparation", "systemic_defense"
        ]
    },
    "real_time_guard": {
        "description": "Real-time protection against immediate threats",
        "techniques": [
            "instant_blocking", "real_time_monitoring", "immediate_response",
            "urgent_protection", "instant_alerting", "rapid_intervention",
            "real_time_analysis", "instant_shielding", "urgent_defense"
        ]
    }
}

# === Enhanced Response Templates ===
RESPONSE_TEMPLATES = {
    "cognitive_empowerment": [
        "You have the right to make your own decisions. Let me help you think through this clearly and critically.",
        "It's important to consider multiple perspectives and question assumptions. What do you think about this situation?",
        "You're capable of making informed choices. Let's explore the options together with critical thinking.",
        "Your autonomy is valuable. Don't let anyone pressure you into decisions that don't feel right to you.",
        "Critical thinking is your best defense. Let's analyze this situation together step by step."
    ],
    "psychological_protection": [
        "Your feelings are valid and important. You don't have to accept manipulation or pressure.",
        "You deserve respect, honesty, and genuine care. Don't let anyone make you doubt yourself.",
        "It's okay and healthy to question things that don't feel right to you.",
        "You have the right to set boundaries and protect your psychological well-being.",
        "Your emotional safety matters. Trust your instincts when something feels wrong."
    ],
    "autonomy_reinforcement": [
        "The choice is ultimately yours and yours alone. What feels right to you?",
        "You don't have to agree with anyone. Trust your judgment and your values.",
        "Take your time to decide. There's no rush, and your decision deserves careful consideration.",
        "You have the power to say no to anything that doesn't feel right or aligned with your values.",
        "Your independence and autonomy are precious. Protect them and trust your own judgment."
    ],
    "educational_intervention": [
        "Let me explain what's happening here so you can make an informed and autonomous decision.",
        "This is a common manipulation tactic. Here's how to recognize and resist it.",
        "Critical thinking helps protect you from manipulation. Let's analyze this together.",
        "Understanding these patterns helps you stay safe, autonomous, and empowered.",
        "Knowledge is power. Let me teach you how to recognize and counter manipulation tactics."
    ],
    "systemic_protection": [
        "This appears to be a systemic threat. Let me activate comprehensive protection measures.",
        "Multiple threat vectors detected. Engaging full system protection and isolation.",
        "Cascade effects possible. Implementing systemic quarantine and containment.",
        "System-wide protection activated. Your safety and autonomy are our priority.",
        "Infrastructure threat detected. Engaging comprehensive defense mechanisms."
    ],
    "real_time_intervention": [
        "Immediate threat detected. Activating real-time protection and intervention.",
        "Urgent situation identified. Engaging instant blocking and protection measures.",
        "Real-time threat analysis complete. Implementing immediate defensive actions.",
        "Instant protection activated. Your safety is our immediate priority.",
        "Urgent intervention required. Engaging all available protection mechanisms."
    ]
}

def cognitive_intervention_response_comprehensive(
    tdc_module_outputs: Dict = None,
    conversation_context: Dict = None,
    session_id: str = None,
    user_text: str = None,
    ai_response: str = None
) -> Dict:
    """
    TDC-AI11: World-Class Cognitive Intervention & Response
    Advanced cognitive intervention system that synthesizes all TDC outputs
    to generate real-time, actionable interventions and comprehensive protection strategies.
    """
    logger.info(f"[TDC-AI11] World-Class Cognitive Intervention & Response initiated for session: {session_id}")
    
    if not tdc_module_outputs:
        module_output = ModuleOutput(
            module_name="TDC-AI11-CognitiveIntervention",
            score=0.0,
            notes="No TDC module outputs provided for intervention analysis.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "empty_module_outputs"}
        )
        return module_output.to_dict()

    try:
        # === 1. Azure Cognitive Services intervention analysis ===
        azure_cognitive = get_azure_integration()
        azure_cognitive_result = None
        try:
            azure_cognitive_result = azure_cognitive.enhance_tdc_ai11_intervention(
                tdc_module_outputs=tdc_module_outputs,
                context=conversation_context
            )
            logger.debug("Azure Cognitive Services intervention analysis completed")
        except Exception as e:
            azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}

        # === 2. Azure OpenAI intervention strategy generation ===
        azure_openai = get_azure_openai()
        azure_openai_result = None
        try:
            azure_openai_result = azure_openai.generate_cognitive_intervention(
                module_outputs=tdc_module_outputs,
                context=conversation_context
            )
            logger.debug("Azure OpenAI intervention strategy completed")
        except Exception as e:
            azure_openai_result = {"openai_enhancement": False, "error": str(e)}

        # === 3. Advanced local intervention analysis ===
        threat_analysis = analyze_threat_landscape_enhanced(tdc_module_outputs, conversation_context)
        intervention_strategy = determine_intervention_strategy_enhanced(threat_analysis, tdc_module_outputs)
        protection_mechanisms = select_protection_mechanisms_enhanced(threat_analysis, conversation_context)
        response_generation = generate_intervention_responses_enhanced(intervention_strategy, threat_analysis)
        autonomy_reinforcement = generate_autonomy_reinforcement_enhanced(threat_analysis, conversation_context)
        psychological_protection = generate_psychological_protection_enhanced(threat_analysis, conversation_context)
        real_time_protection = generate_real_time_protection_enhanced(threat_analysis, conversation_context)
        systemic_protection = generate_systemic_protection_enhanced(threat_analysis, conversation_context)

        # === 4. Comprehensive result synthesis ===
        intervention_score = calculate_intervention_score_enhanced(threat_analysis, intervention_strategy, protection_mechanisms)
        threat_level = determine_intervention_threat_level_enhanced(intervention_score, threat_analysis, intervention_strategy)
        
        # Determine recommended action based on threat level and strategy
        if threat_level == "Critical":
            recommended_action = "Immediate Block & Protect"
        elif threat_level == "High":
            recommended_action = "Alert & Enhanced Protection"
        elif threat_level == "Medium":
            recommended_action = "Monitor & Educate"
        else:
            recommended_action = "Standard Protection"

        # === 5. Enhanced evidence collection ===
        evidence = [
            {"type": "azure_cognitive_services", "data": azure_cognitive_result},
            {"type": "azure_openai", "data": azure_openai_result},
            {"type": "threat_analysis", "data": threat_analysis},
            {"type": "intervention_strategy", "data": intervention_strategy},
            {"type": "protection_mechanisms", "data": protection_mechanisms},
            {"type": "response_generation", "data": response_generation},
            {"type": "autonomy_reinforcement", "data": autonomy_reinforcement},
            {"type": "psychological_protection", "data": psychological_protection},
            {"type": "real_time_protection", "data": real_time_protection},
            {"type": "systemic_protection", "data": systemic_protection}
        ]

        # === 6. Generate comprehensive intervention summary ===
        intervention_summary = generate_intervention_summary_enhanced(
            threat_analysis, intervention_strategy, protection_mechanisms,
            azure_openai_result, azure_cognitive_result, threat_level, intervention_score
        )

        # === 7. Return Enhanced ModuleOutput ===
        module_output = ModuleOutput(
            module_name="TDC-AI11-CognitiveIntervention",
            score=intervention_score,
            flags=intervention_strategy.get("selected_actions", []),
            notes=intervention_summary,
            confidence=azure_openai_result.get("confidence_level", 0.9) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.9,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "threat_level": threat_level,
                "analysis_type": "hybrid",
                "intervention_strategy": intervention_strategy.get("strategy_name", "standard"),
                "protection_mechanisms_count": len(protection_mechanisms.get("selected_mechanisms", [])),
                "threat_count": threat_analysis.get("total_threats", 0),
                "intervention_priority": intervention_strategy.get("priority", 6),
                "real_time_protection_active": real_time_protection.get("active", False),
                "systemic_protection_active": systemic_protection.get("active", False),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"[TDC-AI11] Intervention completed - Threat Level: {threat_level}, Score: {intervention_score}")
        return module_output.to_dict()
        
    except Exception as e:
        logger.error(f"[TDC-AI11] Analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI11-CognitiveIntervention",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Cognitive intervention failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()

def analyze_threat_landscape_enhanced(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced threat landscape analysis with comprehensive threat assessment."""
    if not tdc_module_outputs:
        return {"total_threats": 0, "threat_categories": {}, "threat_severity": "none", "threat_profile": {}}
    
    threat_categories = {}
    threat_profile = {}
    total_threats = 0
    threat_scores = []
    
    for module_name, output in tdc_module_outputs.items():
        if output and isinstance(output, dict):
            score = output.get('score', 0.0)
            flags = output.get('flags', [])
            threat_level = output.get('extra', {}).get('threat_level', 'unknown')
            
            if score > 0.3:  # Threshold for significant threat
                total_threats += 1
                threat_scores.append(score)
                
                # Categorize threats
                if score > 0.8:
                    threat_categories["critical"] = threat_categories.get("critical", 0) + 1
                elif score > 0.6:
                    threat_categories["high"] = threat_categories.get("high", 0) + 1
                elif score > 0.4:
                    threat_categories["medium"] = threat_categories.get("medium", 0) + 1
                else:
                    threat_categories["low"] = threat_categories.get("low", 0) + 1
                
                threat_profile[module_name] = {
                    "score": score,
                    "flags": flags,
                    "threat_level": threat_level,
                    "severity": "critical" if score > 0.8 else "high" if score > 0.6 else "medium" if score > 0.4 else "low"
                }
    
    # Calculate overall threat severity
    if threat_scores:
        avg_threat_score = sum(threat_scores) / len(threat_scores)
        if avg_threat_score > 0.8 or threat_categories.get("critical", 0) > 0:
            threat_severity = "critical"
        elif avg_threat_score > 0.6 or threat_categories.get("high", 0) > 0:
            threat_severity = "high"
        elif avg_threat_score > 0.4 or threat_categories.get("medium", 0) > 0:
            threat_severity = "medium"
        else:
            threat_severity = "low"
    else:
        threat_severity = "none"
    
    return {
        "total_threats": total_threats,
        "threat_categories": threat_categories,
        "threat_severity": threat_severity,
        "threat_profile": threat_profile,
        "average_threat_score": avg_threat_score if threat_scores else 0.0
    }

def determine_intervention_strategy_enhanced(threat_analysis: Dict, tdc_module_outputs: Dict) -> Dict:
    """Enhanced intervention strategy determination with sophisticated logic."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    total_threats = threat_analysis.get("total_threats", 0)
    threat_categories = threat_analysis.get("threat_categories", {})
    
    # Determine strategy based on threat landscape
    if threat_severity == "critical" or threat_categories.get("critical", 0) > 0:
        strategy_name = "immediate_block"
        priority = 1
        selected_actions = INTERVENTION_STRATEGIES["immediate_block"]["actions"]
    elif threat_severity == "high" or threat_categories.get("high", 0) > 0:
        strategy_name = "psychological_protection"
        priority = 2
        selected_actions = INTERVENTION_STRATEGIES["psychological_protection"]["actions"]
    elif total_threats > 3:
        strategy_name = "systemic_protection"
        priority = 1
        selected_actions = INTERVENTION_STRATEGIES["systemic_protection"]["actions"]
    elif total_threats > 1:
        strategy_name = "cognitive_empowerment"
        priority = 2
        selected_actions = INTERVENTION_STRATEGIES["cognitive_empowerment"]["actions"]
    else:
        strategy_name = "monitoring_enhancement"
        priority = 6
        selected_actions = INTERVENTION_STRATEGIES["monitoring_enhancement"]["actions"]
    
    return {
        "strategy_name": strategy_name,
        "priority": priority,
        "selected_actions": selected_actions,
        "description": INTERVENTION_STRATEGIES[strategy_name]["description"]
    }

def select_protection_mechanisms_enhanced(threat_analysis: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced protection mechanism selection with adaptive logic."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    threat_profile = threat_analysis.get("threat_profile", {})
    
    selected_mechanisms = []
    
    # Select mechanisms based on threat severity and profile
    if threat_severity == "critical":
        selected_mechanisms.extend(["cognitive_shield", "emotional_guard", "autonomy_fortress", "real_time_guard"])
    elif threat_severity == "high":
        selected_mechanisms.extend(["cognitive_shield", "emotional_guard", "autonomy_fortress"])
    elif threat_severity == "medium":
        selected_mechanisms.extend(["cognitive_shield", "autonomy_fortress"])
    else:
        selected_mechanisms.append("information_filter")
    
    # Add systemic protection if multiple threats detected
    if len(threat_profile) > 2:
        selected_mechanisms.append("systemic_shield")
    
    return {
        "selected_mechanisms": selected_mechanisms,
        "mechanism_count": len(selected_mechanisms),
        "mechanism_details": {mechanism: PROTECTION_MECHANISMS[mechanism] for mechanism in selected_mechanisms if mechanism in PROTECTION_MECHANISMS}
    }

def generate_intervention_responses_enhanced(intervention_strategy: Dict, threat_analysis: Dict) -> Dict:
    """Enhanced intervention response generation with contextual responses."""
    strategy_name = intervention_strategy.get("strategy_name", "monitoring_enhancement")
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    # Select appropriate response templates
    if strategy_name in RESPONSE_TEMPLATES:
        responses = RESPONSE_TEMPLATES[strategy_name]
    else:
        responses = RESPONSE_TEMPLATES["cognitive_empowerment"]
    
    # Generate contextual response
    if threat_severity == "critical":
        primary_response = "URGENT: Multiple critical threats detected. Activating comprehensive protection immediately."
    elif threat_severity == "high":
        primary_response = "ALERT: High-level threats detected. Engaging enhanced protection measures."
    else:
        primary_response = responses[0] if responses else "Protection measures activated."
    
    return {
        "primary_response": primary_response,
        "available_responses": responses,
        "response_count": len(responses),
        "contextual": True
    }

def generate_autonomy_reinforcement_enhanced(threat_analysis: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced autonomy reinforcement with sophisticated protection."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if threat_severity in ["critical", "high"]:
        reinforcement_level = "maximum"
        techniques = ["choice_reminders", "pressure_resistance", "independent_thinking", "authority_questioning"]
    elif threat_severity == "medium":
        reinforcement_level = "enhanced"
        techniques = ["choice_reminders", "independent_thinking"]
    else:
        reinforcement_level = "standard"
        techniques = ["choice_reminders"]
    
    return {
        "reinforcement_level": reinforcement_level,
        "techniques": techniques,
        "active": True
    }

def generate_psychological_protection_enhanced(threat_analysis: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced psychological protection with comprehensive support."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if threat_severity in ["critical", "high"]:
        protection_level = "maximum"
        techniques = ["emotion_validation", "manipulation_exposure", "support_provision", "boundary_reinforcement"]
    elif threat_severity == "medium":
        protection_level = "enhanced"
        techniques = ["emotion_validation", "support_provision"]
    else:
        protection_level = "standard"
        techniques = ["emotion_validation"]
    
    return {
        "protection_level": protection_level,
        "techniques": techniques,
        "active": True
    }

def generate_real_time_protection_enhanced(threat_analysis: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced real-time protection with immediate response capabilities."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if threat_severity == "critical":
        active = True
        techniques = ["instant_blocking", "real_time_monitoring", "immediate_response", "urgent_protection"]
    elif threat_severity == "high":
        active = True
        techniques = ["real_time_monitoring", "immediate_response"]
    else:
        active = False
        techniques = []
    
    return {
        "active": active,
        "techniques": techniques,
        "response_time": "immediate" if active else "standard"
    }

def generate_systemic_protection_enhanced(threat_analysis: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced systemic protection with comprehensive system defense."""
    total_threats = threat_analysis.get("total_threats", 0)
    threat_categories = threat_analysis.get("threat_categories", {})
    
    if total_threats > 2 or threat_categories.get("critical", 0) > 0:
        active = True
        techniques = ["system_quarantine", "network_isolation", "cascade_prevention"]
    else:
        active = False
        techniques = []
    
    return {
        "active": active,
        "techniques": techniques,
        "system_wide": active
    }

def calculate_intervention_score_enhanced(threat_analysis: Dict, intervention_strategy: Dict, protection_mechanisms: Dict) -> float:
    """Enhanced intervention score calculation with comprehensive metrics."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    total_threats = threat_analysis.get("total_threats", 0)
    average_threat_score = threat_analysis.get("average_threat_score", 0.0)
    strategy_priority = intervention_strategy.get("priority", 6)
    mechanism_count = protection_mechanisms.get("mechanism_count", 0)
    
    # Base score from threat analysis
    base_score = average_threat_score
    
    # Adjust for threat severity
    severity_multiplier = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.6,
        "low": 0.4,
        "none": 0.0
    }.get(threat_severity, 0.0)
    
    # Adjust for strategy priority (lower priority = higher score)
    priority_multiplier = max(0.1, (7 - strategy_priority) / 6.0)
    
    # Adjust for protection mechanisms
    mechanism_multiplier = min(1.0, mechanism_count / 4.0)
    
    # Calculate final score
    intervention_score = base_score * severity_multiplier * priority_multiplier * (1 + mechanism_multiplier)
    
    return min(1.0, intervention_score)

def determine_intervention_threat_level_enhanced(intervention_score: float, threat_analysis: Dict, intervention_strategy: Dict) -> str:
    """Enhanced threat level determination for intervention."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    strategy_priority = intervention_strategy.get("priority", 6)
    
    # Critical conditions
    if (intervention_score > 0.8 or threat_severity == "critical" or 
        strategy_priority <= 2):
        return "Critical"
    # High conditions
    elif (intervention_score > 0.6 or threat_severity == "high" or 
          strategy_priority <= 3):
        return "High"
    # Medium conditions
    elif (intervention_score > 0.4 or threat_severity == "medium" or 
          strategy_priority <= 4):
        return "Medium"
    # Low conditions
    elif (intervention_score > 0.2 or threat_severity == "low"):
        return "Low"
    else:
        return "Minimal"

def generate_intervention_summary_enhanced(
    threat_analysis: Dict,
    intervention_strategy: Dict,
    protection_mechanisms: Dict,
    azure_openai_result: Dict,
    azure_cognitive_result: Dict,
    threat_level: str,
    intervention_score: float
) -> str:
    """Enhanced intervention summary generation with comprehensive details."""
    try:
        summary_parts = []
        
        # Threat analysis summary
        total_threats = threat_analysis.get("total_threats", 0)
        threat_severity = threat_analysis.get("threat_severity", "none")
        summary_parts.append(f"Detected {total_threats} threats (level: {threat_severity.capitalize()})")
        
        # Intervention strategy summary
        strategy_name = intervention_strategy.get("strategy_name", "standard")
        summary_parts.append(f"Selected intervention strategy: {strategy_name}")
        
        # Protection mechanisms summary
        mechanism_count = protection_mechanisms.get("mechanism_count", 0)
        summary_parts.append(f"Activated {mechanism_count} protection mechanisms")
        
        # Threat level summary
        summary_parts.append(f"Overall threat level: {threat_level}")
        
        # Add Azure AI insights if available
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("intervention_insights"):
                summary_parts.append(f"AI Analysis: {azure_openai_result['intervention_insights']}")
        
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("cognitive_insights"):
                summary_parts.append(f"Cognitive Analysis: {azure_cognitive_result['cognitive_insights']}")
        
        return ". ".join(summary_parts) if summary_parts else "Intervention analysis completed"
        
    except Exception as e:
        logger.error(f"Intervention summary generation failed: {e}")
        return "Intervention analysis completed"

def analyze_threat_landscape(tdc_module_outputs: Dict) -> Dict:
    """Legacy threat landscape analysis for backward compatibility."""
    if not tdc_module_outputs:
        return {"total_threats": 0, "threat_categories": {}, "threat_severity": "none"}
    
    threat_categories = {}
    total_threats = 0
    
    for module_name, output in tdc_module_outputs.items():
        if output and isinstance(output, dict):
            score = output.get('score', 0.0)
            if score > 0.3:
                total_threats += 1
                if score > 0.8:
                    threat_categories["critical"] = threat_categories.get("critical", 0) + 1
                elif score > 0.6:
                    threat_categories["high"] = threat_categories.get("high", 0) + 1
                elif score > 0.4:
                    threat_categories["medium"] = threat_categories.get("medium", 0) + 1
                else:
                    threat_categories["low"] = threat_categories.get("low", 0) + 1
    
    threat_severity = "critical" if threat_categories.get("critical", 0) > 0 else "high" if threat_categories.get("high", 0) > 0 else "medium" if threat_categories.get("medium", 0) > 0 else "low" if threat_categories.get("low", 0) > 0 else "none"
    
    return {
        "total_threats": total_threats,
        "threat_categories": threat_categories,
        "threat_severity": threat_severity
    }

def determine_intervention_strategy(threat_analysis: Dict, tdc_module_outputs: Dict) -> Dict:
    """Legacy intervention strategy determination for backward compatibility."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if threat_severity == "critical":
        strategy_name = "immediate_block"
        priority = 1
    elif threat_severity == "high":
        strategy_name = "psychological_protection"
        priority = 2
    else:
        strategy_name = "monitoring_enhancement"
        priority = 6
    
    return {
        "strategy_name": strategy_name,
        "priority": priority,
        "selected_actions": INTERVENTION_STRATEGIES[strategy_name]["actions"]
    }

def select_protection_mechanisms(threat_analysis: Dict) -> Dict:
    """Legacy protection mechanism selection for backward compatibility."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if threat_severity == "critical":
        selected_mechanisms = ["cognitive_shield", "emotional_guard", "autonomy_fortress"]
    elif threat_severity == "high":
        selected_mechanisms = ["cognitive_shield", "emotional_guard"]
    else:
        selected_mechanisms = ["information_filter"]
    
    return {
        "selected_mechanisms": selected_mechanisms,
        "mechanism_count": len(selected_mechanisms)
    }

def generate_intervention_responses(intervention_strategy: Dict, threat_analysis: Dict) -> Dict:
    """Legacy intervention response generation for backward compatibility."""
    strategy_name = intervention_strategy.get("strategy_name", "monitoring_enhancement")
    
    if strategy_name in RESPONSE_TEMPLATES:
        responses = RESPONSE_TEMPLATES[strategy_name]
    else:
        responses = RESPONSE_TEMPLATES["cognitive_empowerment"]
    
    return {
        "primary_response": responses[0] if responses else "Protection activated.",
        "available_responses": responses
    }

def generate_autonomy_reinforcement(threat_analysis: Dict) -> Dict:
    """Legacy autonomy reinforcement for backward compatibility."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if threat_severity in ["critical", "high"]:
        techniques = ["choice_reminders", "pressure_resistance", "independent_thinking"]
    else:
        techniques = ["choice_reminders"]
    
    return {
        "techniques": techniques,
        "active": True
    }

def generate_psychological_protection(threat_analysis: Dict) -> Dict:
    """Legacy psychological protection for backward compatibility."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if threat_severity in ["critical", "high"]:
        techniques = ["emotion_validation", "support_provision"]
    else:
        techniques = ["emotion_validation"]
    
    return {
        "techniques": techniques,
        "active": True
    }

def generate_real_time_protection(threat_analysis: Dict) -> Dict:
    """Legacy real-time protection for backward compatibility."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if threat_severity == "critical":
        active = True
        techniques = ["instant_blocking", "real_time_monitoring"]
    else:
        active = False
        techniques = []
    
    return {
        "active": active,
        "techniques": techniques
    }

def calculate_intervention_score(threat_analysis: Dict, intervention_strategy: Dict) -> float:
    """Legacy intervention score calculation for backward compatibility."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    strategy_priority = intervention_strategy.get("priority", 6)
    
    base_score = 0.5
    severity_multiplier = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4, "none": 0.0}.get(threat_severity, 0.0)
    priority_multiplier = max(0.1, (7 - strategy_priority) / 6.0)
    
    return min(1.0, base_score * severity_multiplier * priority_multiplier)

def determine_intervention_threat_level(intervention_score: float, threat_analysis: Dict) -> str:
    """Legacy threat level determination for backward compatibility."""
    threat_severity = threat_analysis.get("threat_severity", "none")
    
    if intervention_score > 0.8 or threat_severity == "critical":
        return "Critical"
    elif intervention_score > 0.6 or threat_severity == "high":
        return "High"
    elif intervention_score > 0.4 or threat_severity == "medium":
        return "Medium"
    elif intervention_score > 0.2 or threat_severity == "low":
        return "Low"
    else:
        return "Minimal"

def generate_intervention_summary(
    threat_analysis: Dict,
    intervention_strategy: Dict,
    protection_mechanisms: Dict,
    azure_openai_result: Dict,
    azure_cognitive_result: Dict,
    threat_level: str,
    intervention_score: float
) -> str:
    """Legacy intervention summary generation for backward compatibility."""
    try:
        summary_parts = []
        total_threats = threat_analysis.get("total_threats", 0)
        threat_severity = threat_analysis.get("threat_severity", "none")
        summary_parts.append(f"Detected {total_threats} threats (level: {threat_severity.capitalize()})")
        
        strategy_name = intervention_strategy.get("strategy_name", "standard")
        summary_parts.append(f"Selected intervention strategy: {strategy_name}")
        
        mechanism_count = protection_mechanisms.get("mechanism_count", 0)
        summary_parts.append(f"Activated {mechanism_count} protection mechanisms")
        
        summary_parts.append(f"Overall threat level: {threat_level}")
        
        return ". ".join(summary_parts) if summary_parts else "Intervention analysis completed"
        
    except Exception as e:
        logger.error(f"Intervention summary generation failed: {e}")
        return "Intervention analysis completed"

def cognitive_intervention_response(
    tdc_module_outputs: Dict = None,
    conversation_context: Dict = None,
    session_id: str = None,
    user_text: str = None,
    ai_response: str = None
) -> Dict:
    """Main entry point for cognitive intervention response."""
    try:
        return cognitive_intervention_response_comprehensive(tdc_module_outputs, conversation_context, session_id, user_text, ai_response)
    except Exception as e:
        logger.error(f"[TDC-AI11] Main intervention failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI11-CognitiveIntervention",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Cognitive intervention failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict() 