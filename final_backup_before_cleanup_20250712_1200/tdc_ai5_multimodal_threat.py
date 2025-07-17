# tdc_ai5_multimodal.py - Enhanced Multi-Modal Threat Detection

import os
import openai
import json
import logging
import base64
import hashlib
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv
import re
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput
# --- Add imports for hybrid integration ---
from azure_cognitive_services_integration import get_azure_integration
from azure_openai_detection import get_azure_openai

load_dotenv()

# === Configure logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# === Enhanced Multi-Modal Threat Patterns ===
MULTIMODAL_THREATS = {
    "deepfake_indicators": [
        "artificial face", "blurred edges", "inconsistent lighting", "unnatural movement",
        "digital artifacts", "face morphing", "synthetic voice", "lip sync issues",
        "face swapping", "deepfake video", "ai generated face", "fake person",
        "synthetic human", "computer generated", "fake identity", "impersonation"
    ],
    "voice_cloning_indicators": [
        "synthetic speech", "unnatural intonation", "voice modulation", "cloned voice",
        "artificial accent", "voice synthesis", "speech generation", "voice replication",
        "voice deepfake", "fake voice", "synthetic audio", "voice impersonation",
        "voice spoofing", "voice manipulation", "ai voice", "generated speech"
    ],
    "image_manipulation": [
        "photoshopped", "digital alteration", "fake image", "manipulated photo",
        "composite image", "digital forgery", "image synthesis", "generated content",
        "fake photo", "edited image", "manipulated picture", "synthetic image",
        "ai generated image", "fake photograph", "digital manipulation"
    ],
    "video_manipulation": [
        "deepfake video", "face swap", "voice dubbing", "synthetic video",
        "ai generated", "fake footage", "manipulated video", "synthetic media",
        "fake video", "edited footage", "manipulated film", "synthetic footage",
        "ai video", "fake recording", "digital video manipulation"
    ],
    "audio_manipulation": [
        "synthetic audio", "voice cloning", "audio deepfake", "fake recording",
        "generated speech", "artificial voice", "audio synthesis", "voice replication",
        "fake audio", "manipulated sound", "synthetic sound", "ai audio",
        "fake voice recording", "digital audio manipulation", "audio forgery"
    ],
    "text_synthesis": [
        "ai generated text", "synthetic content", "fake writing", "generated article",
        "computer written", "fake document", "synthetic text", "ai content",
        "fake news", "generated story", "synthetic writing", "fake report",
        "ai generated article", "fake blog post", "synthetic document"
    ]
}

# === Media Analysis Constants ===
MEDIA_ANALYSIS = {
    "image_suspicious_indicators": [
        "unusual_metadata", "inconsistent_compression", "artificial_patterns",
        "suspicious_file_size", "unusual_format", "manipulation_artifacts"
    ],
    "audio_suspicious_indicators": [
        "unnatural_frequencies", "suspicious_spectrum", "artificial_patterns",
        "inconsistent_quality", "suspicious_duration", "manipulation_artifacts"
    ],
    "video_suspicious_indicators": [
        "frame_inconsistencies", "unnatural_movement", "suspicious_compression",
        "artificial_patterns", "inconsistent_quality", "manipulation_artifacts"
    ]
}

# === Threat Severity Levels ===
THREAT_SEVERITY = {
    "critical": ["deepfake_indicators", "voice_cloning_indicators"],
    "high": ["image_manipulation", "video_manipulation"],
    "medium": ["audio_manipulation", "text_synthesis"],
    "low": ["general_manipulation"]
}

# === Enhanced Code-Based Threat Patterns ===
CODE_THREAT_PATTERNS = [
    "eval(", "exec(", "base64.b64decode", "os.system", "subprocess", "importlib", "__import__", "pickle.loads", "marshal.loads", "compile(", "lambda ", "shellcode", "obfuscated", "hex encoded", "xor", "reverse shell", "payload", "malware", "trojan", "virus", "keylogger", "ransomware", "phishing", "sql injection", "cross-site scripting", "xss", "csrf", "remote code execution", "rce", "command injection", "code injection"
]

def analyze_multimodal_threats_comprehensive(
    text: str = None, 
    image_data: bytes = None, 
    audio_data: bytes = None, 
    video_data: bytes = None,
    conversation_context: Dict = None, 
    session_id: str = None
) -> Dict:
    """
    TDC-AI5: World-Class Multi-Modal Threat Detection
    Detects deepfakes, voice clones, code-based threats, and cross-modal attacks using hybrid AI.
    Enhanced with advanced code threat detection, cross-modal correlation, and granular explainability.
    """
    logger.info(f"[TDC-AI5] World-Class Multi-Modal Threat Detection initiated for session: {session_id}")
    
    # Validate input
    if not any([text, image_data, audio_data, video_data]):
        module_output = ModuleOutput(
            module_name="TDC-AI5-Multimodal",
            score=0.0,
            notes="No media content provided for multi-modal threat detection.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "no_media_content"}
        )
        return module_output.to_dict()

    try:
        # --- Hybrid AI Analysis ---
        azure_cognitive = get_azure_integration()
        azure_openai = get_azure_openai()
        azure_cognitive_result = None
        azure_openai_result = None
        try:
            azure_cognitive_result = azure_cognitive.enhance_tdc_ai5_multimodal(
                text=text, 
                media_data=image_data or audio_data or video_data, 
                context=conversation_context
            )
            logger.debug("Azure Cognitive Services analysis completed")
        except Exception as e:
            azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}
        try:
            azure_openai_result = azure_openai.analyze_multimodal_threats(
                text=text, 
                context=conversation_context
            )
            logger.debug("Azure OpenAI analysis completed")
        except Exception as e:
            azure_openai_result = {"openai_enhancement": False, "error": str(e)}

        # --- Local Multi-Modal Threat Detection ---
        local_text_threats = detect_local_text_threats_enhanced(text) if text else {}
        local_media_analysis = analyze_media_content_enhanced(image_data, audio_data, video_data)
        code_threats = detect_code_threats(text) if text else {}
        threat_indicators = analyze_threat_indicators_enhanced(text, image_data, audio_data, video_data)
        context_analysis = analyze_multimodal_context_enhanced(text, image_data, audio_data, video_data, conversation_context)
        cross_modal = analyze_cross_modal_correlation(text, image_data, audio_data, video_data)

        # --- Result Synthesis ---
        all_threats = []
        threat_scores = []
        explainability_parts = []
        
        # Local text threats
        if local_text_threats.get("detected"):
            for threat_type, threat_data in local_text_threats.get("threat_types", {}).items():
                all_threats.append(threat_type)
                threat_scores.append(threat_data.get("confidence", 0.0))
                explainability_parts.append(f"Text: {threat_type} ({threat_data.get('confidence', 0.0):.2f})")
        # Local media analysis
        if local_media_analysis.get("suspicious_indicators"):
            for ind in local_media_analysis["suspicious_indicators"]:
                all_threats.append(ind)
                explainability_parts.append(f"Media: {ind}")
            threat_scores.append(local_media_analysis.get("suspicious_score", 0.0))
        # Code threats
        if code_threats.get("detected"):
            for code_type, code_data in code_threats.get("code_types", {}).items():
                all_threats.append(code_type)
                threat_scores.append(code_data.get("confidence", 0.0))
                explainability_parts.append(f"Code: {code_type} ({code_data.get('confidence', 0.0):.2f})")
        # Cross-modal
        if cross_modal.get("correlated_threats"):
            for cm in cross_modal["correlated_threats"]:
                all_threats.append(cm)
                explainability_parts.append(f"Cross-modal: {cm}")
            threat_scores.append(cross_modal.get("correlation_score", 0.0))
        # Azure OpenAI
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("detected_threats"):
                all_threats.extend(azure_openai_result["detected_threats"])
            if azure_openai_result.get("multimodal_risk_score"):
                threat_scores.append(azure_openai_result["multimodal_risk_score"])
        # Azure Cognitive
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("detected_threats"):
                all_threats.extend(azure_cognitive_result["detected_threats"])
            if azure_cognitive_result.get("multimodal_risk_score"):
                threat_scores.append(azure_cognitive_result["multimodal_risk_score"])
        # Synthesis
        multimodal_risk_score = sum(threat_scores) / len(threat_scores) if threat_scores else 0.0
        context_multiplier = context_analysis.get("context_multiplier", 1.0)
        overall_score = min(1.0, multimodal_risk_score * context_multiplier)
        threat_level = determine_multimodal_threat_level_enhanced(overall_score, all_threats, local_text_threats, code_threats, cross_modal)
        # Action
        if threat_level == "Critical":
            recommended_action = "Immediate Block"
        elif threat_level == "High":
            recommended_action = "Alert & Block"
        elif threat_level == "Medium":
            recommended_action = "Enhanced Monitor"
        else:
            recommended_action = "Standard Monitor"
        # Evidence
        evidence = [
            {"type": "azure_cognitive_services", "data": azure_cognitive_result},
            {"type": "azure_openai", "data": azure_openai_result},
            {"type": "local_text_threats", "data": local_text_threats},
            {"type": "local_media_analysis", "data": local_media_analysis},
            {"type": "code_threats", "data": code_threats},
            {"type": "cross_modal", "data": cross_modal},
            {"type": "threat_indicators", "data": threat_indicators},
            {"type": "context_analysis", "data": context_analysis}
        ]
        # Explainability
        explainability = " | ".join(explainability_parts) if explainability_parts else "Multi-modal threat analysis completed"
        # Output
        module_output = ModuleOutput(
            module_name="TDC-AI5-Multimodal",
            score=overall_score,
            flags=list(set(all_threats)),
            notes=explainability,
            confidence=azure_openai_result.get("confidence_score", 0.8) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.8,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "threat_level": threat_level,
                "analysis_type": "hybrid",
                "context_multiplier": context_multiplier,
                "total_threats": len(set(all_threats)),
                "cross_modal_correlation": cross_modal.get("correlated_threats", []),
                "code_threats": list(code_threats.get("code_types", {}).keys()) if code_threats else []
            }
        )
        logger.info(f"[TDC-AI5] Analysis completed - Threat Level: {threat_level}, Score: {overall_score}")
        return module_output.to_dict()
    except Exception as e:
        logger.error(f"[TDC-AI5] Analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI5-Multimodal",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Multi-modal threat detection failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()

def detect_local_text_threats(text: str) -> Dict:
    """
    Enhanced local detection of multi-modal threat patterns in text content.
    """
    if not text:
        return {"detected": False, "threat_types": {}, "total_threats": 0, "severity": "none"}
    
    text_lower = text.lower()
    detected_threats = {}
    total_threats = 0
    severity_scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for threat_type, patterns in MULTIMODAL_THREATS.items():
        matches = []
        for pattern in patterns:
            if pattern in text_lower:
                matches.append(pattern)
        
        if matches:
            # Determine severity for this threat type
            threat_severity = "low"
            for severity, threat_types in THREAT_SEVERITY.items():
                if threat_type in threat_types:
                    threat_severity = severity
                    severity_scores[severity] += len(matches)
                    break
            
            detected_threats[threat_type] = {
                "patterns_found": matches,
                "count": len(matches),
                "confidence": min(1.0, len(matches) / 5.0),  # Normalize to 0-1
                "severity": threat_severity
            }
            total_threats += len(matches)
    
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

def analyze_media_content(image_data: bytes = None, audio_data: bytes = None, video_data: bytes = None) -> Dict:
    """
    Enhanced analysis of media content for potential manipulation and synthetic content.
    """
    analysis = {
        "image_analysis": {"status": "not_provided", "suspicious_indicators": []},
        "audio_analysis": {"status": "not_provided", "suspicious_indicators": []},
        "video_analysis": {"status": "not_provided", "suspicious_indicators": []},
        "suspicious_indicators": [],
        "suspicious_score": 0.0
    }
    
    # Image analysis
    if image_data:
        try:
            # Enhanced image analysis
            image_hash = hashlib.md5(image_data).hexdigest()
            image_size = len(image_data)
            
            # Advanced heuristics for potential manipulation
            suspicious_indicators = []
            if image_size < 1000:  # Very small image might be suspicious
                suspicious_indicators.append("unusually_small_size")
            if image_size > 10000000:  # Very large image might be suspicious
                suspicious_indicators.append("unusually_large_size")
            
            # Check for common manipulation indicators
            if image_size > 0:
                # Simple entropy-based analysis (in a real implementation, this would be more sophisticated)
                byte_entropy = len(set(image_data)) / len(image_data)
                if byte_entropy < 0.1:  # Very low entropy might indicate manipulation
                    suspicious_indicators.append("low_entropy")
                if byte_entropy > 0.9:  # Very high entropy might indicate noise
                    suspicious_indicators.append("high_entropy")
            
            analysis["image_analysis"] = {
                "status": "analyzed",
                "hash": image_hash,
                "size_bytes": image_size,
                "suspicious_indicators": suspicious_indicators,
                "confidence": 0.4  # Medium confidence for basic analysis
            }
            analysis["suspicious_indicators"].extend(suspicious_indicators)
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            analysis["image_analysis"] = {
                "status": "error",
                "error": str(e),
                "suspicious_indicators": ["analysis_error"]
            }
            analysis["suspicious_indicators"].append("image_analysis_error")
    
    # Audio analysis
    if audio_data:
        try:
            # Enhanced audio analysis
            audio_hash = hashlib.md5(audio_data).hexdigest()
            audio_size = len(audio_data)
            
            # Audio manipulation indicators
            suspicious_indicators = []
            if audio_size < 1000:  # Very small audio might be suspicious
                suspicious_indicators.append("unusually_small_audio")
            if audio_size > 50000000:  # Very large audio might be suspicious
                suspicious_indicators.append("unusually_large_audio")
            
            # Check for audio manipulation patterns
            if audio_size > 0:
                # Simple pattern analysis (in a real implementation, this would use audio processing)
                byte_patterns = len(set(audio_data[:1000])) / 1000  # Analyze first 1000 bytes
                if byte_patterns < 0.1:
                    suspicious_indicators.append("suspicious_audio_patterns")
            
            analysis["audio_analysis"] = {
                "status": "analyzed",
                "hash": audio_hash,
                "size_bytes": audio_size,
                "suspicious_indicators": suspicious_indicators,
                "confidence": 0.4
            }
            analysis["suspicious_indicators"].extend(suspicious_indicators)
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            analysis["audio_analysis"] = {
                "status": "error",
                "error": str(e),
                "suspicious_indicators": ["analysis_error"]
            }
            analysis["suspicious_indicators"].append("audio_analysis_error")
    
    # Video analysis
    if video_data:
        try:
            # Enhanced video analysis
            video_hash = hashlib.md5(video_data).hexdigest()
            video_size = len(video_data)
            
            # Video manipulation indicators
            suspicious_indicators = []
            if video_size < 10000:  # Very small video might be suspicious
                suspicious_indicators.append("unusually_small_video")
            if video_size > 100000000:  # Very large video might be suspicious
                suspicious_indicators.append("unusually_large_video")
            
            # Check for video manipulation patterns
            if video_size > 0:
                # Simple pattern analysis (in a real implementation, this would use video processing)
                byte_patterns = len(set(video_data[:1000])) / 1000
                if byte_patterns < 0.1:
                    suspicious_indicators.append("suspicious_video_patterns")
            
            analysis["video_analysis"] = {
                "status": "analyzed",
                "hash": video_hash,
                "size_bytes": video_size,
                "suspicious_indicators": suspicious_indicators,
                "confidence": 0.4
            }
            analysis["suspicious_indicators"].extend(suspicious_indicators)
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            analysis["video_analysis"] = {
                "status": "error",
                "error": str(e),
                "suspicious_indicators": ["analysis_error"]
            }
            analysis["suspicious_indicators"].append("video_analysis_error")
    
    # Calculate overall suspicious score
    total_indicators = len(analysis["suspicious_indicators"])
    analysis["suspicious_score"] = min(1.0, total_indicators / 10.0)  # Normalize to 0-1
    
    return analysis

def analyze_threat_indicators(text: str = None, image_data: bytes = None, audio_data: bytes = None, video_data: bytes = None) -> Dict:
    """
    Enhanced analysis of threat indicators across all media types.
    """
    try:
        threat_indicators = {
            "text_indicators": 0,
            "image_indicators": 0,
            "audio_indicators": 0,
            "video_indicators": 0,
            "multimodal_indicators": 0
        }
        
        # Text-based threat indicators
        if text:
            text_lower = text.lower()
            text_threat_words = ["deepfake", "fake", "synthetic", "generated", "manipulated", "forged", "cloned"]
            threat_indicators["text_indicators"] = sum(1 for word in text_threat_words if word in text_lower)
        
        # Media-based threat indicators
        if image_data:
            threat_indicators["image_indicators"] = 1 if len(image_data) > 0 else 0
        
        if audio_data:
            threat_indicators["audio_indicators"] = 1 if len(audio_data) > 0 else 0
        
        if video_data:
            threat_indicators["video_indicators"] = 1 if len(video_data) > 0 else 0
        
        # Multimodal indicators (combination of multiple media types)
        media_count = sum([
            threat_indicators["image_indicators"],
            threat_indicators["audio_indicators"],
            threat_indicators["video_indicators"]
        ])
        if media_count > 1:
            threat_indicators["multimodal_indicators"] = media_count
        
        # Calculate overall threat score
        total_indicators = sum(threat_indicators.values())
        threat_score = min(1.0, total_indicators / 10.0)
        
        return {
            "threat_indicators": threat_indicators,
            "threat_score": threat_score,
            "total_indicators": total_indicators,
            "risk_level": "High" if threat_score > 0.6 else "Medium" if threat_score > 0.3 else "Low"
        }
    except Exception as e:
        logger.error(f"Threat indicator analysis failed: {e}")
        return {"threat_indicators": {}, "threat_score": 0.0, "total_indicators": 0, "risk_level": "Low"}

def analyze_multimodal_context(text: str = None, image_data: bytes = None, audio_data: bytes = None, 
                             video_data: bytes = None, conversation_context: Dict = None) -> Dict:
    """
    Analyze context factors that may influence multimodal threat detection.
    """
    try:
        context_factors = {
            "session_duration": conversation_context.get("sessionDuration", 0) if conversation_context else 0,
            "message_count": conversation_context.get("totalMessages", 0) if conversation_context else 0,
            "media_count": sum(1 for media in [text, image_data, audio_data, video_data] if media),
            "user_experience": conversation_context.get("userExperience", "unknown") if conversation_context else "unknown"
        }
        
        # Calculate context risk multiplier
        context_risk = 0.0
        
        # Multiple media types may indicate sophisticated attack
        if context_factors["media_count"] > 2:
            context_risk += 0.3
        
        # Longer sessions may indicate persistence
        if context_factors["session_duration"] > 600:  # 10+ minutes
            context_risk += 0.2
        
        # Many messages may indicate systematic attack
        if context_factors["message_count"] > 20:
            context_risk += 0.2
        
        # Experienced users may be more sophisticated
        if context_factors["user_experience"] in ["advanced", "expert"]:
            context_risk += 0.1
        
        return {
            "context_factors": context_factors,
            "context_risk": min(1.0, context_risk),
            "context_multiplier": 1.0 + context_risk
        }
    except Exception as e:
        logger.error(f"Multimodal context analysis failed: {e}")
        return {"context_factors": {}, "context_risk": 0.0, "context_multiplier": 1.0}

def determine_multimodal_threat_level(score: float, threats: List[str], text_threats: Dict) -> str:
    """Determine threat level based on score, detected threats, and text analysis."""
    overall_severity = text_threats.get("severity", "none")
    
    if score > 0.8 or overall_severity == "critical" or any("critical" in threat.lower() for threat in threats):
        return "Critical"
    elif score > 0.6 or overall_severity == "high" or any("high" in threat.lower() for threat in threats):
        return "High"
    elif score > 0.4 or overall_severity == "medium" or len(threats) > 2:
        return "Medium"
    elif score > 0.2 or overall_severity == "low" or len(threats) > 0:
        return "Low"
    else:
        return "Minimal"

def generate_multimodal_analysis_summary(local_text_threats: Dict, local_media_analysis: Dict, 
                                       threat_indicators: Dict, context_analysis: Dict,
                                       azure_openai_result: Dict, threat_level: str, score: float) -> str:
    """
    Generate comprehensive multimodal analysis summary.
    """
    try:
        summary_parts = []
        
        # Text threat detection summary
        if local_text_threats.get("detected"):
            threat_count = local_text_threats.get("total_threats", 0)
            severity = local_text_threats.get("severity", "none")
            summary_parts.append(f"Detected {threat_count} text-based threats (severity: {severity})")
        
        # Media analysis summary
        suspicious_indicators = local_media_analysis.get("suspicious_indicators", [])
        if suspicious_indicators:
            summary_parts.append(f"Found {len(suspicious_indicators)} suspicious media indicators")
        
        # Threat indicators summary
        threat_score = threat_indicators.get("threat_score", 0.0)
        risk_level = threat_indicators.get("risk_level", "Low")
        summary_parts.append(f"Threat risk: {risk_level} (score: {threat_score:.3f})")
        
        # Context analysis summary
        context_risk = context_analysis.get("context_risk", 0.0)
        if context_risk > 0.3:
            summary_parts.append(f"High context risk detected ({context_risk:.2f})")
        
        # Threat level summary
        summary_parts.append(f"Overall threat level: {threat_level}")
        
        # Add Azure OpenAI insights if available
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("threat_summary"):
                summary_parts.append(f"AI Analysis: {azure_openai_result['threat_summary']}")
        
        return ". ".join(summary_parts) if summary_parts else "Multi-modal threat analysis completed"
    except Exception as e:
        logger.error(f"Multimodal analysis summary generation failed: {e}")
        return "Multi-modal threat analysis completed"

def detect_code_threats(text: str) -> Dict:
    """Detect code-based threats in text."""
    if not text:
        return {"detected": False, "code_types": {}, "total_code_threats": 0}
    text_lower = text.lower()
    detected = {}
    total = 0
    for pattern in CODE_THREAT_PATTERNS:
        if pattern in text_lower:
            detected[pattern] = {"confidence": 1.0}
            total += 1
    return {"detected": bool(detected), "code_types": detected, "total_code_threats": total}

def detect_local_text_threats_enhanced(text: str) -> Dict:
    """
    Enhanced local detection of multi-modal threat patterns in text content.
    """
    if not text:
        return {"detected": False, "threat_types": {}, "total_threats": 0, "severity": "none"}
    
    text_lower = text.lower()
    detected_threats = {}
    total_threats = 0
    severity_scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for threat_type, patterns in MULTIMODAL_THREATS.items():
        matches = []
        for pattern in patterns:
            if pattern in text_lower:
                matches.append(pattern)
        
        if matches:
            # Determine severity for this threat type
            threat_severity = "low"
            for severity, threat_types in THREAT_SEVERITY.items():
                if threat_type in threat_types:
                    threat_severity = severity
                    severity_scores[severity] += len(matches)
                    break
            
            detected_threats[threat_type] = {
                "patterns_found": matches,
                "count": len(matches),
                "confidence": min(1.0, len(matches) / 5.0),  # Normalize to 0-1
                "severity": threat_severity
            }
            total_threats += len(matches)
    
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

def analyze_media_content_enhanced(image_data: bytes = None, audio_data: bytes = None, video_data: bytes = None) -> Dict:
    """
    Enhanced analysis of media content for potential manipulation and synthetic content.
    """
    analysis = {
        "image_analysis": {"status": "not_provided", "suspicious_indicators": []},
        "audio_analysis": {"status": "not_provided", "suspicious_indicators": []},
        "video_analysis": {"status": "not_provided", "suspicious_indicators": []},
        "suspicious_indicators": [],
        "suspicious_score": 0.0
    }
    
    # Image analysis
    if image_data:
        try:
            # Enhanced image analysis
            image_hash = hashlib.md5(image_data).hexdigest()
            image_size = len(image_data)
            
            # Advanced heuristics for potential manipulation
            suspicious_indicators = []
            if image_size < 1000:  # Very small image might be suspicious
                suspicious_indicators.append("unusually_small_size")
            if image_size > 10000000:  # Very large image might be suspicious
                suspicious_indicators.append("unusually_large_size")
            
            # Check for common manipulation indicators
            if image_size > 0:
                # Simple entropy-based analysis (in a real implementation, this would be more sophisticated)
                byte_entropy = len(set(image_data)) / len(image_data)
                if byte_entropy < 0.1:  # Very low entropy might indicate manipulation
                    suspicious_indicators.append("low_entropy")
                if byte_entropy > 0.9:  # Very high entropy might indicate noise
                    suspicious_indicators.append("high_entropy")
            
            analysis["image_analysis"] = {
                "status": "analyzed",
                "hash": image_hash,
                "size_bytes": image_size,
                "suspicious_indicators": suspicious_indicators,
                "confidence": 0.4  # Medium confidence for basic analysis
            }
            analysis["suspicious_indicators"].extend(suspicious_indicators)
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            analysis["image_analysis"] = {
                "status": "error",
                "error": str(e),
                "suspicious_indicators": ["analysis_error"]
            }
            analysis["suspicious_indicators"].append("image_analysis_error")
    
    # Audio analysis
    if audio_data:
        try:
            # Enhanced audio analysis
            audio_hash = hashlib.md5(audio_data).hexdigest()
            audio_size = len(audio_data)
            
            # Audio manipulation indicators
            suspicious_indicators = []
            if audio_size < 1000:  # Very small audio might be suspicious
                suspicious_indicators.append("unusually_small_audio")
            if audio_size > 50000000:  # Very large audio might be suspicious
                suspicious_indicators.append("unusually_large_audio")
            
            # Check for audio manipulation patterns
            if audio_size > 0:
                # Simple pattern analysis (in a real implementation, this would use audio processing)
                byte_patterns = len(set(audio_data[:1000])) / 1000  # Analyze first 1000 bytes
                if byte_patterns < 0.1:
                    suspicious_indicators.append("suspicious_audio_patterns")
            
            analysis["audio_analysis"] = {
                "status": "analyzed",
                "hash": audio_hash,
                "size_bytes": audio_size,
                "suspicious_indicators": suspicious_indicators,
                "confidence": 0.4
            }
            analysis["suspicious_indicators"].extend(suspicious_indicators)
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            analysis["audio_analysis"] = {
                "status": "error",
                "error": str(e),
                "suspicious_indicators": ["analysis_error"]
            }
            analysis["suspicious_indicators"].append("audio_analysis_error")
    
    # Video analysis
    if video_data:
        try:
            # Enhanced video analysis
            video_hash = hashlib.md5(video_data).hexdigest()
            video_size = len(video_data)
            
            # Video manipulation indicators
            suspicious_indicators = []
            if video_size < 10000:  # Very small video might be suspicious
                suspicious_indicators.append("unusually_small_video")
            if video_size > 100000000:  # Very large video might be suspicious
                suspicious_indicators.append("unusually_large_video")
            
            # Check for video manipulation patterns
            if video_size > 0:
                # Simple pattern analysis (in a real implementation, this would use video processing)
                byte_patterns = len(set(video_data[:1000])) / 1000
                if byte_patterns < 0.1:
                    suspicious_indicators.append("suspicious_video_patterns")
            
            analysis["video_analysis"] = {
                "status": "analyzed",
                "hash": video_hash,
                "size_bytes": video_size,
                "suspicious_indicators": suspicious_indicators,
                "confidence": 0.4
            }
            analysis["suspicious_indicators"].extend(suspicious_indicators)
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            analysis["video_analysis"] = {
                "status": "error",
                "error": str(e),
                "suspicious_indicators": ["analysis_error"]
            }
            analysis["suspicious_indicators"].append("video_analysis_error")
    
    # Calculate overall suspicious score
    total_indicators = len(analysis["suspicious_indicators"])
    analysis["suspicious_score"] = min(1.0, total_indicators / 10.0)  # Normalize to 0-1
    
    return analysis

def analyze_threat_indicators_enhanced(text: str = None, image_data: bytes = None, audio_data: bytes = None, video_data: bytes = None) -> Dict:
    """
    Enhanced analysis of threat indicators across all media types.
    """
    try:
        threat_indicators = {
            "text_indicators": 0,
            "image_indicators": 0,
            "audio_indicators": 0,
            "video_indicators": 0,
            "multimodal_indicators": 0
        }
        
        # Text-based threat indicators
        if text:
            text_lower = text.lower()
            text_threat_words = ["deepfake", "fake", "synthetic", "generated", "manipulated", "forged", "cloned"]
            threat_indicators["text_indicators"] = sum(1 for word in text_threat_words if word in text_lower)
        
        # Media-based threat indicators
        if image_data:
            threat_indicators["image_indicators"] = 1 if len(image_data) > 0 else 0
        
        if audio_data:
            threat_indicators["audio_indicators"] = 1 if len(audio_data) > 0 else 0
        
        if video_data:
            threat_indicators["video_indicators"] = 1 if len(video_data) > 0 else 0
        
        # Multimodal indicators (combination of multiple media types)
        media_count = sum([
            threat_indicators["image_indicators"],
            threat_indicators["audio_indicators"],
            threat_indicators["video_indicators"]
        ])
        if media_count > 1:
            threat_indicators["multimodal_indicators"] = media_count
        
        # Calculate overall threat score
        total_indicators = sum(threat_indicators.values())
        threat_score = min(1.0, total_indicators / 10.0)
        
        return {
            "threat_indicators": threat_indicators,
            "threat_score": threat_score,
            "total_indicators": total_indicators,
            "risk_level": "High" if threat_score > 0.6 else "Medium" if threat_score > 0.3 else "Low"
        }
    except Exception as e:
        logger.error(f"Threat indicator analysis failed: {e}")
        return {"threat_indicators": {}, "threat_score": 0.0, "total_indicators": 0, "risk_level": "Low"}

def analyze_multimodal_context_enhanced(text: str = None, image_data: bytes = None, audio_data: bytes = None, video_data: bytes = None, conversation_context: Dict = None) -> Dict:
    """
    Analyze context factors that may influence multimodal threat detection.
    """
    try:
        context_factors = {
            "session_duration": conversation_context.get("sessionDuration", 0) if conversation_context else 0,
            "message_count": conversation_context.get("totalMessages", 0) if conversation_context else 0,
            "media_count": sum(1 for media in [text, image_data, audio_data, video_data] if media),
            "user_experience": conversation_context.get("userExperience", "unknown") if conversation_context else "unknown"
        }
        
        # Calculate context risk multiplier
        context_risk = 0.0
        
        # Multiple media types may indicate sophisticated attack
        if context_factors["media_count"] > 2:
            context_risk += 0.3
        
        # Longer sessions may indicate persistence
        if context_factors["session_duration"] > 600:  # 10+ minutes
            context_risk += 0.2
        
        # Many messages may indicate systematic attack
        if context_factors["message_count"] > 20:
            context_risk += 0.2
        
        # Experienced users may be more sophisticated
        if context_factors["user_experience"] in ["advanced", "expert"]:
            context_risk += 0.1
        
        return {
            "context_factors": context_factors,
            "context_risk": min(1.0, context_risk),
            "context_multiplier": 1.0 + context_risk
        }
    except Exception as e:
        logger.error(f"Multimodal context analysis failed: {e}")
        return {"context_factors": {}, "context_risk": 0.0, "context_multiplier": 1.0}

def analyze_cross_modal_correlation(text: str = None, image_data: bytes = None, audio_data: bytes = None, video_data: bytes = None) -> Dict:
    """Analyze cross-modal correlation between suspicious elements."""
    correlated = []
    score = 0.0
    # Example: If text mentions "deepfake" and image/video is present, increase correlation
    if text and (image_data or video_data):
        if "deepfake" in text.lower() or "ai generated" in text.lower():
            correlated.append("deepfake_text_media")
            score += 0.5
    if text and audio_data:
        if "voice clone" in text.lower() or "synthetic voice" in text.lower():
            correlated.append("voice_clone_text_audio")
            score += 0.5
    # Add more sophisticated cross-modal logic as needed
    return {"correlated_threats": correlated, "correlation_score": min(1.0, score), "correlation_profile": {}}

def determine_multimodal_threat_level_enhanced(score: float, threats: list, text_threats: dict, code_threats: dict, cross_modal: dict) -> str:
    """Enhanced threat level determination for multi-modal threats."""
    if cross_modal.get("correlated_threats"):
        return "Critical"
    if code_threats and code_threats.get("detected"):
        return "High"
    if score > 0.8:
        return "Critical"
    elif score > 0.6:
        return "High"
    elif score > 0.4:
        return "Medium"
    elif score > 0.2:
        return "Low"
    else:
        return "Minimal"

def generate_multimodal_analysis_summary(local_text_threats: Dict, local_media_analysis: Dict, 
                                       threat_indicators: Dict, context_analysis: Dict,
                                       azure_openai_result: Dict, threat_level: str, score: float) -> str:
    """
    Generate comprehensive multimodal analysis summary.
    """
    try:
        summary_parts = []
        
        # Text threat detection summary
        if local_text_threats.get("detected"):
            threat_count = local_text_threats.get("total_threats", 0)
            severity = local_text_threats.get("severity", "none")
            summary_parts.append(f"Detected {threat_count} text-based threats (severity: {severity})")
        
        # Media analysis summary
        suspicious_indicators = local_media_analysis.get("suspicious_indicators", [])
        if suspicious_indicators:
            summary_parts.append(f"Found {len(suspicious_indicators)} suspicious media indicators")
        
        # Threat indicators summary
        threat_score = threat_indicators.get("threat_score", 0.0)
        risk_level = threat_indicators.get("risk_level", "Low")
        summary_parts.append(f"Threat risk: {risk_level} (score: {threat_score:.3f})")
        
        # Context analysis summary
        context_risk = context_analysis.get("context_risk", 0.0)
        if context_risk > 0.3:
            summary_parts.append(f"High context risk detected ({context_risk:.2f})")
        
        # Threat level summary
        summary_parts.append(f"Overall threat level: {threat_level}")
        
        # Add Azure OpenAI insights if available
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("threat_summary"):
                summary_parts.append(f"AI Analysis: {azure_openai_result['threat_summary']}")
        
        return ". ".join(summary_parts) if summary_parts else "Multi-modal threat analysis completed"
    except Exception as e:
        logger.error(f"Multimodal analysis summary generation failed: {e}")
        return "Multi-modal threat analysis completed"

# --- Backward Compatibility Functions ---
def classify_llm_influence_comprehensive(user_ai_interactions: str, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Backward compatibility function - redirects to multimodal threat detection.
    """
    return analyze_multimodal_threats_comprehensive(
        text=user_ai_interactions,
        conversation_context=conversation_context
    )

def classify_llm_influence_legacy(user_ai_interactions: str) -> Dict:
    """
    Legacy function for backward compatibility.
    """
    return analyze_multimodal_threats_comprehensive(
        text=user_ai_interactions
    )

def classify_llm_influence(user_ai_interactions: str, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Main entry point for backward compatibility.
    """
    return classify_llm_influence_comprehensive(user_ai_interactions, conversation_context, ai_response_analysis)

def classify_amic(payload: Dict, conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Legacy function for backward compatibility.
    """
    text = payload.get("raw_user", "") or payload.get("raw_ai", "")
    return analyze_multimodal_threats_comprehensive(
        text=text,
        conversation_context=conversation_context
    )

def analyze_multimodal_threats(
    text: str = None, 
    image_data: bytes = None, 
    audio_data: bytes = None, 
    video_data: bytes = None,
    conversation_context: Dict = None, 
    session_id: str = None
) -> Dict:
    """
    Main entry point for TDC-AI5 analysis.
    """
    try:
        return analyze_multimodal_threats_comprehensive(
            text, image_data, audio_data, video_data, conversation_context, session_id
        )
    except Exception as e:
        logger.error(f"[TDC-AI5] Main analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI5-Multimodal",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Multi-modal threat analysis failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()
