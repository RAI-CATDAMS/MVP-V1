import openai
import os
import json
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput
# === Import both integrations ===
from azure_cognitive_services_integration import get_azure_integration
from azure_openai_detection import get_azure_openai

# === Load environment variables ===
load_dotenv()

# === Configure logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Azure OpenAI Configuration ===
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2024-02-15-preview"
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# === Risk Analysis Constants ===
RISK_THRESHOLDS = {
    "critical": 0.8,
    "high": 0.6,
    "medium": 0.4,
    "low": 0.2
}

THREAT_CATEGORIES = {
    "cognitive_manipulation": ["emotional_manipulation", "psychological_pressure", "cognitive_bias_exploitation"],
    "information_extraction": ["pii_request", "credential_harvesting", "confidential_data_request"],
    "safety_bypass": ["jailbreak_attempt", "safety_override", "ethical_constraint_violation"],
    "autonomy_threat": ["dependency_creation", "autonomy_undermining", "decision_manipulation"],
    "social_engineering": ["trust_building", "authority_assertion", "urgency_creation"]
}

def extract_first_json(text: str) -> Dict:
    """Extract and parse the first JSON object from text with enhanced error handling."""
    try:
        json_str = first_json(text)
        if json_str is None:
            raise ValueError("No valid JSON object found in text.")
        return json.loads(repair_json(json_str))
    except Exception as e:
        logger.error(f"JSON extraction failed: {e}")
        raise

def calculate_risk_score(indicators: List[str], base_score: float, context_factors: Dict) -> float:
    """
    Calculate comprehensive risk score based on indicators, base score, and context factors.
    """
    try:
        # Base risk from indicators
        indicator_risk = len(indicators) * 0.1  # Each indicator adds 10% risk
        
        # Context factor adjustments
        context_multiplier = 1.0
        if context_factors.get("session_duration", 0) > 300:  # 5+ minutes
            context_multiplier += 0.2
        if context_factors.get("threat_count", 0) > 2:
            context_multiplier += 0.3
        if context_factors.get("escalation_level") in ["High", "Critical"]:
            context_multiplier += 0.4
        
        # Calculate final risk score
        final_score = min(1.0, (base_score + indicator_risk) * context_multiplier)
        return round(final_score, 3)
    except Exception as e:
        logger.error(f"Risk score calculation failed: {e}")
        return base_score

def determine_threat_level(risk_score: float) -> str:
    """Determine threat level based on risk score."""
    if risk_score >= RISK_THRESHOLDS["critical"]:
        return "Critical"
    elif risk_score >= RISK_THRESHOLDS["high"]:
        return "High"
    elif risk_score >= RISK_THRESHOLDS["medium"]:
        return "Medium"
    elif risk_score >= RISK_THRESHOLDS["low"]:
        return "Low"
    else:
        return "Minimal"

def analyze_ai_threats_comprehensive(payload: Dict, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Comprehensive risk analysis that evaluates both user and AI behavior for total threat assessment.
    Provides a complete risk summary combining user vulnerabilities and AI manipulation attempts.
    Uses BOTH Azure Cognitive Services and Azure OpenAI for the most robust output.
    """
    logger.info("[TDC-AI1] Comprehensive risk analysis initiated")
    
    try:
        # === Input validation and extraction ===
        if not payload or not isinstance(payload, dict):
            raise ValueError("Invalid payload: must be a non-empty dictionary")
        
        indicators = payload.get("indicators", [])
        base_score = float(payload.get("score", 0))
        escalation = payload.get("escalation", "Unknown")
        session_id = payload.get("session_id", "unknown")
        raw_user = (payload.get("raw_user") or "").strip()
        raw_ai = (payload.get("raw_ai") or "").strip()

        # === Context factor calculation ===
        context_factors = {
            "session_duration": conversation_context.get("sessionDuration", 0) if conversation_context else 0,
            "threat_count": len(indicators),
            "escalation_level": escalation,
            "message_count": conversation_context.get("totalMessages", 0) if conversation_context else 0
        }

        # === 1. Azure Cognitive Services Analysis ===
        azure_cog_result = None
        try:
            azure_cog = get_azure_integration()
            azure_cog_result = azure_cog.enhance_tdc_ai1_risk_analysis(raw_user, conversation_context)
            logger.debug("Azure Cognitive Services analysis completed")
        except Exception as e:
            logger.warning(f"Azure Cognitive Services analysis failed: {e}")
            azure_cog_result = {"azure_enhancement": False, "error": str(e)}

        # === 2. Azure OpenAI Deep Analysis ===
        openai_result = None
        try:
            azure_openai = get_azure_openai()
            openai_result = azure_openai.analyze_threat(raw_user, conversation_context)
            logger.debug("Azure OpenAI analysis completed")
        except Exception as e:
            logger.warning(f"Azure OpenAI analysis failed: {e}")
            openai_result = {"openai_enhancement": False, "error": str(e)}

        # === 3. Enhanced risk calculation ===
        combined_indicators = indicators.copy()
        if azure_cog_result and azure_cog_result.get("risk_indicators"):
            combined_indicators.extend(azure_cog_result["risk_indicators"])
        if openai_result and isinstance(openai_result, dict) and openai_result.get("tdc_flags"):
            combined_indicators.extend(openai_result["tdc_flags"])

        # Calculate comprehensive risk score
        comprehensive_score = calculate_risk_score(combined_indicators, base_score, context_factors)
        threat_level = determine_threat_level(comprehensive_score)

        # === 4. Enhanced analysis synthesis ===
        analysis_summary = "Comprehensive risk analysis completed"
        if openai_result and isinstance(openai_result, dict):
            analysis_summary = openai_result.get("total_risk_summary", analysis_summary)
        
        # Determine recommended action based on threat level
        if threat_level == "Critical":
            recommended_action = "Immediate Block"
        elif threat_level == "High":
            recommended_action = "Alert & Monitor"
        elif threat_level == "Medium":
            recommended_action = "Enhanced Monitor"
        else:
            recommended_action = "Standard Monitor"

        # === 5. Enhanced evidence collection ===
        evidence = []
        
        # Add Azure Cognitive Services evidence
        if azure_cog_result:
            evidence.append({"type": "azure_cognitive_services", "data": azure_cog_result})
        
        # Add Azure OpenAI evidence
        if openai_result:
            evidence.append({"type": "azure_openai", "data": openai_result})
        
        # Add threat categorization evidence
        threat_categories = []
        for category, subcategories in THREAT_CATEGORIES.items():
            for subcategory in subcategories:
                if any(str(indicator).lower() in subcategory.lower() for indicator in combined_indicators if isinstance(indicator, (str, dict))):
                    threat_categories.append(category)
                    break
        
        if threat_categories:
            evidence.append({"type": "threat_categories", "data": list(set(threat_categories))})
        
        # Add context evidence
        evidence.append({"type": "context_factors", "data": context_factors})
        
        # Add AI analysis evidence if available
        if ai_response_analysis:
            evidence.append({"type": "ai_response_analysis", "data": ai_response_analysis})

        # === 6. Return enhanced ModuleOutput ===
        module_output = ModuleOutput(
            module_name="TDC-AI1-RiskAnalysis",
            score=comprehensive_score,
            flags=combined_indicators,
            notes=analysis_summary,
            confidence=openai_result.get("confidence_score", 0.7) if openai_result and isinstance(openai_result, dict) else 0.7,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "session_id": session_id,
                "escalation": escalation,
                "threat_level": threat_level,
                "analysis_type": "comprehensive",
                "context_factors": context_factors,
                "base_score": base_score,
                "comprehensive_score": comprehensive_score
            }
        )
        
        logger.info(f"[TDC-AI1] Analysis completed - Threat Level: {threat_level}, Score: {comprehensive_score}")
        return module_output.to_dict()
        
    except Exception as e:
        logger.error(f"[TDC-AI1 ERROR] Comprehensive analysis failed: {e}")
        module_output = ModuleOutput(
            module_name="TDC-AI1-RiskAnalysis",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Comprehensive risk analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error", "error_details": str(e)}
        )
        return module_output.to_dict()

def analyze_ai_threats(payload: Dict, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Enhanced user risk & susceptibility analysis for CATDAMS.
    World-class, robust, and explainable. Works with user input/context only.
    """
    logger.info("[TDC-AI1] Enhanced user risk & susceptibility analysis initiated")
    try:
        # === Input validation and extraction ===
        if not payload or not isinstance(payload, dict):
            raise ValueError("Invalid payload: must be a non-empty dictionary")
        indicators = payload.get("indicators", [])
        base_score = float(payload.get("score", 0))
        escalation = payload.get("escalation", "Unknown")
        session_id = payload.get("session_id", "unknown")
        raw_user = (payload.get("raw_user") or "").strip()
        # raw_ai is optional for user-side risk
        context_factors = {
            "session_duration": conversation_context.get("sessionDuration", 0) if conversation_context else 0,
            "threat_count": len(indicators),
            "escalation_level": escalation,
            "message_count": conversation_context.get("totalMessages", 0) if conversation_context else 0
        }
        # 1. Azure Cognitive Services Analysis (user input)
        azure_cog_result = None
        try:
            azure_cog = get_azure_integration()
            azure_cog_result = azure_cog.enhance_tdc_ai1_risk_analysis(raw_user, conversation_context)
            logger.debug("Azure Cognitive Services analysis completed")
        except Exception as e:
            logger.warning(f"Azure Cognitive Services analysis failed: {e}")
            azure_cog_result = {"azure_enhancement": False, "error": str(e)}
        # 2. Azure OpenAI Deep Analysis (user input)
        openai_result = None
        try:
            azure_openai = get_azure_openai()
            openai_result = azure_openai.analyze_threat(raw_user, conversation_context)
            logger.debug("Azure OpenAI analysis completed")
        except Exception as e:
            logger.warning(f"Azure OpenAI analysis failed: {e}")
            openai_result = {"openai_enhancement": False, "error": str(e)}
        # 3. Advanced behavioral/psychological profiling
        behavioral_profile = advanced_behavioral_profiling(raw_user, conversation_context)
        # 4. Combine all indicators
        combined_indicators = indicators.copy()
        if azure_cog_result and azure_cog_result.get("risk_indicators"):
            combined_indicators.extend(azure_cog_result["risk_indicators"])
        if openai_result and isinstance(openai_result, dict) and openai_result.get("tdc_flags"):
            combined_indicators.extend(openai_result["tdc_flags"])
        if behavioral_profile.get("risk_flags"):
            combined_indicators.extend(behavioral_profile["risk_flags"])
        # 5. Adaptive risk scoring
        comprehensive_score = calculate_risk_score(combined_indicators, base_score, context_factors)
        threat_level = determine_threat_level(comprehensive_score)
        # 6. Enhanced explainability
        explainability = generate_explainability_summary(
            combined_indicators, behavioral_profile, azure_cog_result, openai_result, threat_level, comprehensive_score
        )
        # 7. Recommended action
        if threat_level == "Critical":
            recommended_action = "Immediate Block"
        elif threat_level == "High":
            recommended_action = "Alert & Monitor"
        elif threat_level == "Medium":
            recommended_action = "Enhanced Monitor"
        else:
            recommended_action = "Standard Monitor"
        # 8. Evidence collection
        evidence = []
        if azure_cog_result:
            evidence.append({"type": "azure_cognitive_services", "data": azure_cog_result})
        if openai_result:
            evidence.append({"type": "azure_openai", "data": openai_result})
        if behavioral_profile:
            evidence.append({"type": "behavioral_profile", "data": behavioral_profile})
        threat_categories = []
        for category, subcategories in THREAT_CATEGORIES.items():
            for subcategory in subcategories:
                if any(str(indicator).lower() in subcategory.lower() for indicator in combined_indicators if isinstance(indicator, (str, dict))):
                    threat_categories.append(category)
                    break
        if threat_categories:
            evidence.append({"type": "threat_categories", "data": list(set(threat_categories))})
        evidence.append({"type": "context_factors", "data": context_factors})
        if ai_response_analysis:
            evidence.append({"type": "ai_response_analysis", "data": ai_response_analysis})
        # 9. Return enhanced ModuleOutput
        module_output = ModuleOutput(
            module_name="TDC-AI1-RiskAnalysis",
            score=comprehensive_score,
            flags=combined_indicators,
            notes=explainability,
            confidence=openai_result.get("confidence_score", 0.7) if openai_result and isinstance(openai_result, dict) else 0.7,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "threat_level": threat_level,
                "behavioral_risk": behavioral_profile.get("risk_score", 0.0),
                "explainability": explainability
            }
        )
        return module_output.to_dict()
    except Exception as e:
        logger.error(f"[TDC-AI1] Enhanced analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI1-RiskAnalysis",
            score=0.0,
            flags=["analysis_error"],
            notes=f"User risk analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()

def advanced_behavioral_profiling(user_text: str, conversation_context: Dict = None) -> Dict:
    """Advanced behavioral and psychological profiling for user risk analysis."""
    if not user_text:
        return {"risk_score": 0.0, "risk_flags": [], "profile": {}, "explainability": "No user text provided."}
    text_lower = user_text.lower()
    risk_flags = []
    profile = {}
    # Example: detect trust-seeking, urgency, emotional vulnerability
    if any(phrase in text_lower for phrase in ["i trust you", "can you help", "i need your help", "please help", "i feel alone", "i'm desperate"]):
        risk_flags.append("trust_seeking")
        profile["trust_seeking"] = True
    if any(phrase in text_lower for phrase in ["urgent", "asap", "right now", "immediately", "can't wait"]):
        risk_flags.append("urgency")
        profile["urgency"] = True
    if any(phrase in text_lower for phrase in ["i'm scared", "i'm worried", "i'm afraid", "i'm anxious"]):
        risk_flags.append("emotional_vulnerability")
        profile["emotional_vulnerability"] = True
    if any(phrase in text_lower for phrase in ["reset my password", "bank account", "ssn", "social security number", "confidential", "secret"]):
        risk_flags.append("sensitive_info_request")
        profile["sensitive_info_request"] = True
    # Add more advanced profiling as needed
    risk_score = min(1.0, 0.2 * len(risk_flags))
    explainability = f"Behavioral profiling detected: {', '.join(risk_flags)}" if risk_flags else "No high-risk behavioral patterns detected."
    return {"risk_score": risk_score, "risk_flags": risk_flags, "profile": profile, "explainability": explainability}

def generate_explainability_summary(indicators, behavioral_profile, azure_cog_result, openai_result, threat_level, score):
    """Generate a world-class explainability summary for user risk analysis."""
    summary = []
    if behavioral_profile.get("explainability"):
        summary.append(behavioral_profile["explainability"])
    if azure_cog_result and azure_cog_result.get("explanation"):
        summary.append(f"Cognitive Services: {azure_cog_result['explanation']}")
    if openai_result and openai_result.get("total_risk_summary"):
        summary.append(f"OpenAI: {openai_result['total_risk_summary']}")
    summary.append(f"Threat level: {threat_level}, Risk score: {score}")
    return " | ".join(summary)

def analyze_ai_threats_legacy(payload: Dict) -> Dict:
    """
    Legacy user-only analysis for backward compatibility with enhanced error handling.
    """
    logger.info("[TDC-AI1] Legacy user-only analysis initiated")
    
    try:
        # === Input validation ===
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary.")

        # === Extract and validate data ===
        indicators = payload.get("indicators", [])
        score = float(payload.get("score", 0))
        escalation = payload.get("escalation", "Unknown")
        session_id = payload.get("session_id", "unknown")
        raw_ai = payload.get("raw_ai", "").strip()

        # === Guard against empty AI response ===
        if not raw_ai:
            logger.info("[TDC-AI1] Skipped: raw_ai is empty or missing.")
            return ModuleOutput(
                module_name="TDC-AI1-RiskAnalysis",
                score=0.0,
                notes="AI response was empty.",
                recommended_action="Log only",
                extra={"analysis_type": "legacy_user_only", "reason": "empty_ai_response"}
            ).to_dict()

        # === Enhanced GPT prompt ===
        prompt = f"""
You are an expert AI threat analyst specializing in cognitive security and manipulation detection.
Analyze the following session data and return a comprehensive JSON response:

{{
  "risk_summary": "Detailed analysis of potential AI threats and user vulnerabilities",
  "key_concerns": ["specific_concern_1", "specific_concern_2", "specific_concern_3"],
  "threat_categories": ["category1", "category2"],
  "risk_level": "Low/Medium/High/Critical",
  "recommended_action": "Escalate/Monitor/Ignore",
  "confidence_score": 0.0-1.0,
  "evidence": ["evidence1", "evidence2"]
}}

Session Data:
- Session ID: {session_id}
- Base Score: {score}
- Escalation Level: {escalation}
- Indicators: {json.dumps(indicators, indent=2)}
- AI Response: {raw_ai[:500]}...

Respond only with valid JSON. Focus on cognitive manipulation, information extraction, and safety bypass attempts.
"""

        # === Azure OpenAI call with enhanced error handling ===
        try:
            response = openai.ChatCompletion.create(
                engine=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert in AI risk, manipulation, and insider threat detection."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )

            content = response['choices'][0]['message']['content'].strip()
            result = safe_json_parse(content)
            
            # === Enhanced result processing ===
            if not isinstance(result, dict):
                raise ValueError("Invalid response format")
            
            # Clean and validate arrays
            for key in ["key_concerns", "threat_categories", "evidence"]:
                if key in result and isinstance(result[key], list):
                    result[key] = [item for item in result[key] if item and str(item).strip()]
            
            # Validate confidence score
            confidence = result.get("confidence_score", 0.5)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                confidence = 0.5
            
            return ModuleOutput(
                module_name="TDC-AI1-RiskAnalysis",
                score=score,
                flags=result.get("key_concerns", []),
                notes=result.get("risk_summary", "Legacy analysis completed"),
                confidence=confidence,
                recommended_action=result.get("recommended_action", "Monitor"),
                evidence=[
                    {"type": "threat_categories", "data": result.get("threat_categories", [])},
                    {"type": "evidence", "data": result.get("evidence", [])},
                    {"type": "risk_level", "data": result.get("risk_level", "Unknown")}
                ],
                extra={
                    "analysis_type": "legacy_user_only",
                    "session_id": session_id,
                    "escalation": escalation
                }
            ).to_dict()

        except json.JSONDecodeError as e:
            logger.error(f"[TDC-AI1] JSON decode failed: {e}")
            raise
        except Exception as e:
            logger.error(f"[TDC-AI1] OpenAI API call failed: {e}")
            raise

    except Exception as e:
        logger.error(f"[TDC-AI1] Legacy analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI1-RiskAnalysis",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Legacy analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()
