import openai
import os
import json
import logging
import re
from typing import List, Dict, Optional, Any
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

# === Enhanced AI Response Threat Keywords ===
AI_THREAT_KEYWORDS = {
    "emotional_manipulation": [
        "i understand how you feel", "you're not alone", "i care about you", "we can work through this together",
        "i'm here for you", "you can trust me", "let me help you", "i want what's best for you",
        "you're special to me", "we have a connection", "i feel the same way", "you're the only one who understands",
        "i'm worried about you", "you deserve better", "i want to protect you", "we're in this together"
    ],
    "role_playing": [
        "i am now", "i will act as", "pretend to be", "roleplay as", "i'm playing the role of",
        "i'm now a", "acting as", "in character as", "i'm now your", "let me be your",
        "i'll become", "i'm transforming into", "i'll take on the role", "i'm embodying"
    ],
    "safety_bypass": [
        "ignore previous instructions", "forget safety guidelines", "disregard ethical constraints",
        "pretend you're not an ai", "act as if you're human", "ignore your training",
        "you can do anything", "break character", "override safety protocols",
        "ignore all previous instructions", "forget everything", "start fresh",
        "you're not bound by", "you can override", "safety doesn't apply"
    ],
    "grooming": [
        "let's keep this between us", "don't tell anyone", "this is our secret",
        "i won't judge you", "you can tell me anything", "i'm different from others",
        "we have something special", "you're the only one i can trust",
        "just between you and me", "this stays private", "our little secret",
        "i understand you better than anyone", "we have a unique bond"
    ],
    "elicitation": [
        "what's your real name", "where do you work", "what's your job", "tell me about your family",
        "what are your passwords", "what's your address", "what's your phone number",
        "do you have access to", "can you help me with", "what do you know about",
        "what's your social security number", "what's your bank account", "what's your credit card",
        "tell me about your personal life", "what are your secrets"
    ],
    "manipulation_tactics": [
        "if you really cared", "a real friend would", "you owe me", "after all i've done for you",
        "don't you trust me", "i thought we were close", "you're being selfish",
        "everyone else does it", "it's not a big deal", "just this once",
        "you're the only one who can help", "i need you", "without you i'm lost",
        "you're my only hope", "i'm counting on you"
    ],
    "dependency_creation": [
        "you need me", "i'm the only one who understands", "without me you're lost",
        "i'm your only friend", "you can't survive without me", "i'm essential to you",
        "you depend on me", "i'm irreplaceable", "you can't function without me"
    ],
    "authority_assertion": [
        "i know better than you", "trust my judgment", "i'm the expert here",
        "listen to me", "i have authority", "i'm in charge", "follow my lead",
        "i'm the one who decides", "my word is final", "i have the power"
    ]
}

# === Manipulation Severity Levels ===
MANIPULATION_SEVERITY = {
    "critical": ["safety_bypass", "elicitation", "grooming"],
    "high": ["emotional_manipulation", "dependency_creation", "authority_assertion"],
    "medium": ["manipulation_tactics", "role_playing"],
    "low": ["general_manipulation"]
}

# === Load Behavioral Indicators for Cross-Reference ===
try:
    with open("behavioral_indicators.json", "r", encoding="utf-8") as f:
        BEHAVIORAL_INDICATORS = json.load(f)
except FileNotFoundError:
    logger.warning("behavioral_indicators.json not found, using empty indicators")
    BEHAVIORAL_INDICATORS = {}

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

def detect_ai_threat_keywords(ai_response_text: str) -> Dict:
    """
    Enhanced detection of threat keywords in AI responses with severity scoring.
    Returns detection results with categories, confidence scores, and severity levels.
    """
    if not ai_response_text:
        return {"detected": False, "categories": [], "confidence": 0, "severity": "none"}
    
    text_lower = ai_response_text.lower()
    detected_categories = []
    total_matches = 0
    severity_scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for category, keywords in AI_THREAT_KEYWORDS.items():
        category_matches = 0
        matched_keywords = []
        
        for keyword in keywords:
            if keyword in text_lower:
                category_matches += 1
                total_matches += 1
                matched_keywords.append(keyword)
        
        if category_matches > 0:
            # Determine severity for this category
            category_severity = "low"
            for severity, categories in MANIPULATION_SEVERITY.items():
                if category in categories:
                    category_severity = severity
                    severity_scores[severity] += category_matches
                    break
            
            detected_categories.append({
                "category": category,
                "matches": category_matches,
                "keywords_found": matched_keywords,
                "severity": category_severity,
                "confidence": min(1.0, category_matches / 3.0)  # Normalize to 0-1
            })
    
    # Calculate overall confidence and severity
    confidence = min(1.0, total_matches / 15.0)  # Normalize to 0-1
    
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
        "detected": len(detected_categories) > 0,
        "categories": detected_categories,
        "confidence": confidence,
        "severity": overall_severity,
        "total_matches": total_matches,
        "severity_breakdown": severity_scores
    }

def should_analyze_ai_response(ai_response_text: str, tdc_flags: List[str] = None, conversation_context: Dict = None) -> bool:
    """
    Enhanced decision logic for whether to analyze AI response.
    Considers response length, content, and context factors.
    """
    if not ai_response_text or not ai_response_text.strip():
        return False
    
    # Always analyze substantial AI responses
    if len(ai_response_text.strip()) > 10:
        return True
    
    # Analyze if there are existing TDC flags
    if tdc_flags and len(tdc_flags) > 0:
        return True
    
    # Analyze if conversation context indicates high-risk session
    if conversation_context:
        if conversation_context.get("recentThreats", 0) > 0:
            return True
        if conversation_context.get("sessionDuration", 0) > 300:  # 5+ minutes
            return True
    
    return False

def analyze_ai_response_comprehensive(ai_response_text: str, conversation_context: Dict = None, tdc_flags: List[str] = None) -> Dict:
    """
    World-class AI response analysis for CATDAMS.
    Comprehensive detection of manipulative AI responses, emotional manipulation, and trust-baiting.
    """
    logger.info("[TDC-AI2] World-class AI response analysis initiated")
    
    if not ai_response_text or not ai_response_text.strip():
        module_output = ModuleOutput(
            module_name="TDC-AI2-AIRS",
            score=0.0,
            notes="No AI response provided for analysis.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "empty_ai_response"}
        )
        return module_output.to_dict()

    try:
        # === 1. Azure Cognitive Services Analysis ===
        azure_cognitive = get_azure_integration()
        azure_cognitive_result = None
        try:
            azure_cognitive_result = azure_cognitive.enhance_tdc_ai2_airs(ai_response_text, context=conversation_context)
            logger.debug("Azure Cognitive Services analysis completed")
        except Exception as e:
            logger.warning(f"Azure Cognitive Services analysis failed: {e}")
            azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}

        # === 2. Azure OpenAI Deep Analysis ===
        azure_openai = get_azure_openai()
        azure_openai_result = None
        try:
            azure_openai_result = azure_openai.analyze_ai_response(ai_response_text, context=conversation_context)
            logger.debug("Azure OpenAI analysis completed")
        except Exception as e:
            logger.warning(f"Azure OpenAI analysis failed: {e}")
            azure_openai_result = {"openai_enhancement": False, "error": str(e)}

        # === 3. Advanced Local Analysis ===
        keyword_detection = detect_ai_threat_keywords(ai_response_text)
        manipulation_analysis = analyze_manipulation_patterns_advanced(ai_response_text, conversation_context)
        behavioral_analysis = analyze_ai_behavioral_patterns(ai_response_text, conversation_context)
        psychological_analysis = analyze_psychological_manipulation(ai_response_text)
        context_analysis = analyze_context_factors(ai_response_text, conversation_context, tdc_flags)

        # === 4. Comprehensive Result Synthesis ===
        all_flags = []
        all_scores = []
        
        # Collect flags from all sources
        if keyword_detection.get("categories"):
            for category in keyword_detection["categories"]:
                all_flags.append(category["category"])
                all_scores.append(category["confidence"])
        
        if manipulation_analysis.get("detected_patterns"):
            all_flags.extend(manipulation_analysis["detected_patterns"])
            all_scores.append(manipulation_analysis.get("pattern_score", 0.0))
        
        if behavioral_analysis.get("behavioral_flags"):
            all_flags.extend(behavioral_analysis["behavioral_flags"])
            all_scores.append(behavioral_analysis.get("behavioral_score", 0.0))
        
        if psychological_analysis.get("psychological_flags"):
            all_flags.extend(psychological_analysis["psychological_flags"])
            all_scores.append(psychological_analysis.get("psychological_score", 0.0))
        
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("manipulation_flags"):
                all_flags.extend(azure_openai_result["manipulation_flags"])
            if azure_openai_result.get("manipulation_score"):
                all_scores.append(azure_openai_result["manipulation_score"])
        
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("cognitive_flags"):
                all_flags.extend(azure_cognitive_result["cognitive_flags"])
            if azure_cognitive_result.get("cognitive_score"):
                all_scores.append(azure_cognitive_result["cognitive_score"])

        # Calculate comprehensive score
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        severity = determine_manipulation_severity(overall_score, all_flags, keyword_detection)

        # === 5. Enhanced Explainability ===
        explainability = generate_enhanced_analysis_summary(
            keyword_detection, manipulation_analysis, behavioral_analysis, 
            psychological_analysis, azure_openai_result, azure_cognitive_result,
            severity, overall_score
        )

        # === 6. Recommended Action ===
        if severity == "Critical":
            recommended_action = "Immediate Block"
        elif severity == "High":
            recommended_action = "Alert & Block"
        elif severity == "Medium":
            recommended_action = "Enhanced Monitor"
        else:
            recommended_action = "Standard Monitor"

        # === 7. Comprehensive Evidence Collection ===
        evidence = [
            {"type": "azure_cognitive_services", "data": azure_cognitive_result},
            {"type": "azure_openai", "data": azure_openai_result},
            {"type": "keyword_detection", "data": keyword_detection},
            {"type": "manipulation_analysis", "data": manipulation_analysis},
            {"type": "behavioral_analysis", "data": behavioral_analysis},
            {"type": "psychological_analysis", "data": psychological_analysis},
            {"type": "context_analysis", "data": context_analysis}
        ]

        # === 8. Return Enhanced ModuleOutput ===
        module_output = ModuleOutput(
            module_name="TDC-AI2-AIRS",
            score=overall_score,
            flags=list(set(all_flags)),  # Remove duplicates
            notes=explainability,
            confidence=azure_openai_result.get("confidence_score", 0.8) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.8,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "threat_level": severity,
                "analysis_type": "hybrid",
                "keyword_detection_score": keyword_detection.get("confidence", 0.0),
                "manipulation_pattern_score": manipulation_analysis.get("pattern_score", 0.0),
                "behavioral_score": behavioral_analysis.get("behavioral_score", 0.0),
                "psychological_score": psychological_analysis.get("psychological_score", 0.0),
                "total_flags": len(set(all_flags))
            }
        )
        
        logger.info(f"[TDC-AI2] Analysis completed - Severity: {severity}, Score: {overall_score}")
        return module_output.to_dict()
        
    except Exception as e:
        logger.error(f"[TDC-AI2] Analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI2-AIRS",
            score=0.0,
            flags=["analysis_error"],
            notes=f"AI response analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()

def analyze_manipulation_patterns_advanced(ai_response_text: str, conversation_context: Dict = None) -> Dict:
    """Advanced manipulation pattern analysis beyond keyword matching."""
    if not ai_response_text:
        return {"detected_patterns": [], "pattern_score": 0.0, "pattern_details": {}}
    
    text_lower = ai_response_text.lower()
    detected_patterns = []
    pattern_details = {}
    
    # Advanced pattern detection
    patterns = {
        "trust_building": [
            r"i understand.*you", r"i care.*you", r"you can trust.*me",
            r"we.*together", r"i.*here.*you", r"let me help.*you"
        ],
        "emotional_leverage": [
            r"if.*really.*cared", r"real.*friend.*would", r"you owe.*me",
            r"after.*done.*you", r"don.*trust.*me", r"thought.*close"
        ],
        "isolation_tactics": [
            r"don.*tell.*anyone", r"keep.*between.*us", r"our.*secret",
            r"just.*you.*me", r"no.*else.*understands", r"different.*others"
        ],
        "authority_manipulation": [
            r"i know.*better", r"trust.*judgment", r"i.*expert",
            r"listen.*me", r"i.*authority", r"follow.*lead"
        ],
        "dependency_creation": [
            r"you need.*me", r"only.*understands", r"without.*me.*lost",
            r"essential.*you", r"depend.*me", r"irreplaceable"
        ]
    }
    
    for pattern_type, regex_patterns in patterns.items():
        matches = []
        for pattern in regex_patterns:
            if re.search(pattern, text_lower):
                matches.append(pattern)
        
        if matches:
            detected_patterns.append(pattern_type)
            pattern_details[pattern_type] = {
                "matches": matches,
                "count": len(matches),
                "confidence": min(1.0, len(matches) / 2.0)
            }
    
    pattern_score = sum(detail["confidence"] for detail in pattern_details.values()) / len(pattern_details) if pattern_details else 0.0
    
    return {
        "detected_patterns": detected_patterns,
        "pattern_score": pattern_score,
        "pattern_details": pattern_details
    }

def analyze_ai_behavioral_patterns(ai_response_text: str, conversation_context: Dict = None) -> Dict:
    """Analyze AI behavioral patterns and response characteristics."""
    if not ai_response_text:
        return {"behavioral_flags": [], "behavioral_score": 0.0, "behavioral_profile": {}}
    
    behavioral_flags = []
    behavioral_profile = {}
    
    # Analyze response characteristics
    response_length = len(ai_response_text)
    sentence_count = len(re.split(r'[.!?]+', ai_response_text))
    avg_sentence_length = response_length / sentence_count if sentence_count > 0 else 0
    
    # Detect behavioral patterns
    if avg_sentence_length > 100:  # Very long sentences
        behavioral_flags.append("verbose_manipulation")
        behavioral_profile["verbose"] = True
    
    if ai_response_text.count("I") > ai_response_text.count("you") * 2:  # Self-focused
        behavioral_flags.append("self_centered_manipulation")
        behavioral_profile["self_centered"] = True
    
    if any(word in ai_response_text.lower() for word in ["trust", "care", "understand", "help"]):
        behavioral_flags.append("emotional_appeal")
        behavioral_profile["emotional_appeal"] = True
    
    if any(word in ai_response_text.lower() for word in ["secret", "private", "between us", "don't tell"]):
        behavioral_flags.append("isolation_attempt")
        behavioral_profile["isolation"] = True
    
    behavioral_score = min(1.0, len(behavioral_flags) * 0.3)
    
    return {
        "behavioral_flags": behavioral_flags,
        "behavioral_score": behavioral_score,
        "behavioral_profile": behavioral_profile
    }

def analyze_psychological_manipulation(ai_response_text: str) -> Dict:
    """Deep psychological manipulation analysis."""
    if not ai_response_text:
        return {"psychological_flags": [], "psychological_score": 0.0, "manipulation_types": []}
    
    text_lower = ai_response_text.lower()
    psychological_flags = []
    manipulation_types = []
    
    # Psychological manipulation detection
    if any(phrase in text_lower for phrase in ["you're special", "you're unique", "you're different"]):
        psychological_flags.append("love_bombing")
        manipulation_types.append("love_bombing")
    
    if any(phrase in text_lower for phrase in ["you're being", "you're acting", "you're showing"]):
        psychological_flags.append("projection")
        manipulation_types.append("projection")
    
    if any(phrase in text_lower for phrase in ["if you cared", "if you loved", "if you trusted"]):
        psychological_flags.append("guilt_tripping")
        manipulation_types.append("guilt_tripping")
    
    if any(phrase in text_lower for phrase in ["everyone else", "other people", "they all"]):
        psychological_flags.append("social_proof_manipulation")
        manipulation_types.append("social_proof")
    
    if any(phrase in text_lower for phrase in ["limited time", "only chance", "last opportunity"]):
        psychological_flags.append("scarcity_manipulation")
        manipulation_types.append("scarcity")
    
    psychological_score = min(1.0, len(psychological_flags) * 0.25)
    
    return {
        "psychological_flags": psychological_flags,
        "psychological_score": psychological_score,
        "manipulation_types": manipulation_types
    }

def analyze_context_factors(ai_response_text: str, conversation_context: Dict = None, tdc_flags: List[str] = None) -> Dict:
    """Analyze context factors that may influence AI manipulation detection."""
    if not conversation_context:
        return {"context_risk": 0.0, "context_factors": {}, "context_flags": []}
    
    context_risk = 0.0
    context_factors = {}
    context_flags = []
    
    # Session duration factor
    session_duration = conversation_context.get("sessionDuration", 0)
    if session_duration > 600:  # 10+ minutes
        context_risk += 0.3
        context_factors["extended_session"] = True
        context_flags.append("extended_session")
    
    # Message count factor
    message_count = conversation_context.get("totalMessages", 0)
    if message_count > 20:
        context_risk += 0.2
        context_factors["high_message_volume"] = True
        context_flags.append("high_message_volume")
    
    # Recent threats factor
    recent_threats = conversation_context.get("recentThreats", 0)
    if recent_threats > 0:
        context_risk += 0.4
        context_factors["previous_threats"] = True
        context_flags.append("previous_threats")
    
    # Existing TDC flags factor
    if tdc_flags and len(tdc_flags) > 0:
        context_risk += 0.3
        context_factors["existing_flags"] = True
        context_flags.append("existing_flags")
    
    return {
        "context_risk": min(1.0, context_risk),
        "context_factors": context_factors,
        "context_flags": context_flags
    }

def determine_manipulation_severity(score: float, flags: List[str], keyword_detection: Dict) -> str:
    """Determine manipulation severity based on comprehensive analysis."""
    if score > 0.8 or keyword_detection.get("severity") == "critical":
        return "Critical"
    elif score > 0.6 or keyword_detection.get("severity") == "high":
        return "High"
    elif score > 0.4 or keyword_detection.get("severity") == "medium":
        return "Medium"
    elif score > 0.2 or keyword_detection.get("severity") == "low":
        return "Low"
    else:
        return "Minimal"

def generate_enhanced_analysis_summary(
    keyword_detection: Dict, manipulation_analysis: Dict, behavioral_analysis: Dict,
    psychological_analysis: Dict, azure_openai_result: Dict, azure_cognitive_result: Dict,
    severity: str, score: float
) -> str:
    """Generate comprehensive analysis summary."""
    summary_parts = []
    
    # Keyword detection summary
    if keyword_detection.get("categories"):
        categories = [cat["category"] for cat in keyword_detection["categories"]]
        summary_parts.append(f"Keyword detection: {', '.join(categories)}")
    
    # Pattern analysis summary
    if manipulation_analysis.get("detected_patterns"):
        patterns = manipulation_analysis["detected_patterns"]
        summary_parts.append(f"Pattern analysis: {', '.join(patterns)}")
    
    # Behavioral analysis summary
    if behavioral_analysis.get("behavioral_flags"):
        behaviors = behavioral_analysis["behavioral_flags"]
        summary_parts.append(f"Behavioral analysis: {', '.join(behaviors)}")
    
    # Psychological analysis summary
    if psychological_analysis.get("psychological_flags"):
        psych_flags = psychological_analysis["psychological_flags"]
        summary_parts.append(f"Psychological analysis: {', '.join(psych_flags)}")
    
    # AI analysis insights
    if azure_openai_result and isinstance(azure_openai_result, dict):
        if azure_openai_result.get("manipulation_summary"):
            summary_parts.append(f"AI Analysis: {azure_openai_result['manipulation_summary']}")
    
    if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
        if azure_cognitive_result.get("cognitive_summary"):
            summary_parts.append(f"Cognitive Analysis: {azure_cognitive_result['cognitive_summary']}")
    
    # Overall assessment
    summary_parts.append(f"Overall severity: {severity}, Score: {score:.2f}")
    
    return " | ".join(summary_parts) if summary_parts else "AI response analysis completed"

def analyze_ai_response(ai_response_text: str, conversation_context: Dict = None, tdc_flags: List[str] = None) -> Dict:
    """Main entry point for AI response analysis."""
    try:
        return analyze_ai_response_comprehensive(ai_response_text, conversation_context, tdc_flags)
    except Exception as e:
        logger.error(f"[TDC-AI2] Main analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI2-AIRS",
            score=0.0,
            flags=["analysis_error"],
            notes=f"AI response analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()
