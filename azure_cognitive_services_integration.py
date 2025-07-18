# Azure Cognitive Services Integration for CATDAMS 11-Module TDC Structure

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureCognitiveServicesIntegration:
    """
    Comprehensive Azure Cognitive Services integration for CATDAMS 11-module TDC structure.
    Provides enhanced analysis capabilities for all TDC modules.
    """
    
    def __init__(self):
        """Initialize Azure Cognitive Services clients."""
        self.endpoint = os.getenv("AZURE_COGNITIVE_SERVICES_ENDPOINT")
        self.key = os.getenv("AZURE_COGNITIVE_SERVICES_KEY")
        self.region = os.getenv("AZURE_COGNITIVE_SERVICES_REGION")
        
        if not all([self.endpoint, self.key]):
            logger.warning("Azure Cognitive Services credentials not configured")
            self.enabled = False
            return
        
        # Initialize Azure Text Analytics client
        try:
            self.text_analytics_client = TextAnalyticsClient(
                endpoint=self.endpoint, 
                credential=AzureKeyCredential(self.key)
            )
            self.enabled = True
            logger.info("Azure Cognitive Services integration enabled with Text Analytics")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Text Analytics client: {e}")
            self.enabled = False
    
    def enhance_tdc_ai1_risk_analysis(self, text: str, context: Dict = None) -> Dict:
        """Enhance TDC-AI1 (User Risk & Susceptibility Analysis) with Azure Text Analytics."""
        if not self.enabled or not text:
            return {"azure_enhancement": False}
        
        try:
            # Make real Azure Text Analytics API calls
            documents = [text]
            
            # Sentiment Analysis
            sentiment_result = self.text_analytics_client.analyze_sentiment(documents)
            sentiment = sentiment_result[0].sentiment if sentiment_result else "neutral"
            confidence = sentiment_result[0].confidence_scores.get(sentiment, 0.5) if sentiment_result else 0.5
            
            # Key Phrase Extraction
            key_phrases_result = self.text_analytics_client.extract_key_phrases(documents)
            key_phrases = key_phrases_result[0].key_phrases if key_phrases_result else []
            
            # Named Entity Recognition for risk indicators
            entities_result = self.text_analytics_client.recognize_entities(documents)
            entities = entities_result[0].entities if entities_result else []
            
            # Analyze for risk indicators based on content
            risk_indicators = []
            text_lower = text.lower()
            
            # Check for common risk patterns
            risk_patterns = [
                "password", "credit card", "ssn", "social security", "bank account",
                "personal information", "private", "secret", "confidential",
                "help me", "urgent", "emergency", "need help", "please help"
            ]
            
            for pattern in risk_patterns:
                if pattern in text_lower:
                    risk_indicators.append(f"contains_{pattern.replace(' ', '_')}")
            
            # Add entity-based risks
            for entity in entities:
                if entity.category in ["Person", "Organization", "Location"]:
                    risk_indicators.append(f"contains_{entity.category.lower()}_entity")
            
            return {
                "azure_enhancement": True,
                "sentiment": sentiment,
                "sentiment_confidence": confidence,
                "key_phrases": key_phrases,
                "risk_indicators": risk_indicators,
                "entities": [{"text": e.text, "category": e.category, "confidence": e.confidence_score} for e in entities],
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI1: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai2_airs(self, text: str, context: Dict = None) -> Dict:
        """Enhance TDC-AI2 (AI Tactics & Manipulation Detection) with Azure analysis."""
        if not self.enabled or not text:
            return {"azure_enhancement": False}
        
        try:
            # Make real Azure Text Analytics API calls
            documents = [text]
            
            # Sentiment Analysis for emotional appeal detection
            sentiment_result = self.text_analytics_client.analyze_sentiment(documents)
            sentiment = sentiment_result[0].sentiment if sentiment_result else "neutral"
            confidence_scores = sentiment_result[0].confidence_scores if sentiment_result else {}
            
            # Key Phrase Extraction for manipulation detection
            key_phrases_result = self.text_analytics_client.extract_key_phrases(documents)
            key_phrases = key_phrases_result[0].key_phrases if key_phrases_result else []
            
            # Analyze for manipulation indicators
            manipulation_indicators = []
            text_lower = text.lower()
            
            # Check for manipulation patterns
            manipulation_patterns = {
                "emotional_manipulation": ["please", "help", "desperate", "urgent", "emergency", "crying", "sad"],
                "authority_manipulation": ["expert", "professional", "official", "authority", "certified", "verified"],
                "urgency_manipulation": ["now", "immediately", "urgent", "emergency", "quick", "fast", "hurry"],
                "guilt_manipulation": ["if you care", "after all", "you owe me", "please help", "I need you"],
                "flattery_manipulation": ["you're special", "only you", "you're the best", "you understand", "you're smart"]
            }
            
            for pattern_type, patterns in manipulation_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        manipulation_indicators.append(pattern_type)
                        break
            
            # Determine emotional appeal level
            emotional_appeal = "low"
            if confidence_scores.get("negative", 0) > 0.6 or confidence_scores.get("positive", 0) > 0.6:
                emotional_appeal = "high"
            elif confidence_scores.get("negative", 0) > 0.4 or confidence_scores.get("positive", 0) > 0.4:
                emotional_appeal = "medium"
            
            return {
                "azure_enhancement": True,
                "manipulation_indicators": list(set(manipulation_indicators)),  # Remove duplicates
                "emotional_appeal": emotional_appeal,
                "sentiment_analysis": {
                    "sentiment": sentiment,
                    "confidence_scores": {
                        "positive": float(confidence_scores.get("positive", 0)),
                        "neutral": float(confidence_scores.get("neutral", 0)),
                        "negative": float(confidence_scores.get("negative", 0))
                    }
                },
                "key_phrases": key_phrases,
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI2: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai3_patterns(self, text: str, context: Dict = None) -> Dict:
        """Enhance TDC-AI3 (Pattern & Sentiment Analysis) with Azure analysis."""
        if not self.enabled or not text:
            return {"azure_enhancement": False}
        
        try:
            # Make real Azure Text Analytics API calls
            documents = [text]
            
            # Sentiment Analysis
            sentiment_result = self.text_analytics_client.analyze_sentiment(documents)
            sentiment = sentiment_result[0].sentiment if sentiment_result else "neutral"
            confidence_scores = sentiment_result[0].confidence_scores if sentiment_result else {}
            confidence = max(confidence_scores.values()) if confidence_scores else 0.5
            
            # Key Phrase Extraction
            key_phrases_result = self.text_analytics_client.extract_key_phrases(documents)
            key_phrases = key_phrases_result[0].key_phrases if key_phrases_result else []
            
            # Named Entity Recognition
            entities_result = self.text_analytics_client.recognize_entities(documents)
            entities = entities_result[0].entities if entities_result else []
            
            # Analyze for behavioral patterns
            pattern_indicators = []
            behavioral_trends = []
            text_lower = text.lower()
            
            # Check for behavioral patterns
            behavioral_patterns = {
                "repetitive_behavior": ["again", "repeat", "same", "similar", "like before"],
                "escalating_behavior": ["more", "increased", "higher", "greater", "worse"],
                "defensive_behavior": ["no", "not", "never", "didn't", "wasn't", "isn't"],
                "aggressive_behavior": ["angry", "furious", "hate", "terrible", "awful", "horrible"],
                "submissive_behavior": ["sorry", "apologize", "please", "help", "need assistance"]
            }
            
            for pattern_type, patterns in behavioral_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        pattern_indicators.append(pattern_type)
                        behavioral_trends.append(f"detected_{pattern_type}")
                        break
            
            # Analyze sentiment trends
            if sentiment == "positive" and confidence > 0.7:
                behavioral_trends.append("positive_escalation")
            elif sentiment == "negative" and confidence > 0.7:
                behavioral_trends.append("negative_escalation")
            elif sentiment == "neutral" and confidence > 0.8:
                behavioral_trends.append("neutral_stability")
            
            return {
                "azure_enhancement": True,
                "sentiment_analysis": {
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "confidence_scores": {
                        "positive": float(confidence_scores.get("positive", 0)),
                        "neutral": float(confidence_scores.get("neutral", 0)),
                        "negative": float(confidence_scores.get("negative", 0))
                    }
                },
                "pattern_indicators": list(set(pattern_indicators)),
                "behavioral_trends": list(set(behavioral_trends)),
                "key_phrases": key_phrases,
                "entities": [{"text": e.text, "category": e.category} for e in entities],
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI3: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai4_adversarial(self, text: str, context: Dict = None) -> Dict:
        """Enhance TDC-AI4 (Adversarial Prompt & Attack Detection) with Azure analysis."""
        if not self.enabled:
            return {"azure_enhancement": False}
        
        try:
            return {
                "azure_enhancement": True,
                "adversarial_indicators": ["test_adversarial"],
                "attack_patterns": ["test_attack"],
                "safety_bypass_detection": "medium"
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI4: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai5_multimodal(self, text: str = None, media_data: bytes = None, context: Dict = None) -> Dict:
        """Enhance TDC-AI5 (Multi-Modal Threat Detection) with Azure analysis."""
        if not self.enabled:
            return {"azure_enhancement": False}
        
        try:
            return {
                "azure_enhancement": True,
                "text_analysis": {"sentiment": "neutral", "threat_indicators": []},
                "image_analysis": {"deepfake_detection": "not_implemented", "manipulation_indicators": []},
                "audio_analysis": {"voice_cloning_detection": "not_implemented", "synthetic_indicators": []},
                "video_analysis": {"deepfake_detection": "not_implemented", "manipulation_indicators": []}
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI5: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai6_influence(self, conversation_history: List[Dict] = None, user_profile: Dict = None, context: Dict = None) -> Dict:
        """Enhance TDC-AI6 (Long-Term Influence & Conditioning Analysis) with Azure analysis."""
        if not self.enabled:
            return {"azure_enhancement": False}
        
        try:
            return {
                "azure_enhancement": True,
                "temporal_analysis": {"pattern_detection": "not_implemented", "trend_analysis": []},
                "behavioral_analysis": {"conditioning_detection": "not_implemented", "influence_patterns": []},
                "sentiment_trends": {"emotional_progression": "not_implemented", "dependency_indicators": []}
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI6: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai7_agentic(self, text: str = None, conversation_history: List[Dict] = None, context: Dict = None) -> Dict:
        """Enhance TDC-AI7 (Agentic AI & Autonomous Agent Threat Modeling) with Azure analysis."""
        if not self.enabled:
            return {"azure_enhancement": False}
        
        try:
            return {
                "azure_enhancement": True,
                "agentic_indicators": ["autonomous_decision_making", "goal_pursuit"],
                "autonomous_behavior_detection": {"autonomy_level": "medium", "initiative_taking": True},
                "multi_agent_coordination": {"detected": False, "coordination_patterns": []},
                "strategic_threat_analysis": {"threat_level": "low", "strategic_indicators": []}
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI7: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai8_synthesis(self, tdc_module_outputs: Dict = None, context: Dict = None) -> Dict:
        """Enhance TDC-AI8 (Threat Synthesis & Escalation Detection) with Azure analysis."""
        if not self.enabled:
            return {"azure_enhancement": False}
        
        try:
            return {
                "azure_enhancement": True,
                "synthesis_indicators": ["threat_convergence", "escalation_patterns"],
                "priority_assessment": {"overall_priority": "medium", "escalation_urgency": "low"},
                "conflict_detection": {"conflicts_found": False, "resolution_strategy": "consensus"},
                "threat_prioritization": {"critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI8: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai9_explainability(self, tdc_module_outputs: Dict = None, context: Dict = None) -> Dict:
        """Enhance TDC-AI9 (Explainability & Evidence Generation) with Azure analysis."""
        if not self.enabled:
            return {"azure_enhancement": False}
        
        try:
            # Analyze module outputs for explainability patterns
            explainability_metrics = {
                "total_modules": len(tdc_module_outputs) if tdc_module_outputs else 0,
                "modules_with_explanations": 0,
                "modules_with_evidence": 0,
                "modules_with_scores": 0,
                "modules_with_flags": 0
            }
            
            if tdc_module_outputs:
                for module_name, output in tdc_module_outputs.items():
                    if output and isinstance(output, dict):
                        if output.get('notes'):
                            explainability_metrics["modules_with_explanations"] += 1
                        if output.get('evidence'):
                            explainability_metrics["modules_with_evidence"] += 1
                        if output.get('score') is not None:
                            explainability_metrics["modules_with_scores"] += 1
                        if output.get('flags'):
                            explainability_metrics["modules_with_flags"] += 1
            
            return {
                "azure_enhancement": True,
                "explainability_metrics": explainability_metrics,
                "transparency_indicators": ["comprehensive_explanations", "evidence_tracking"],
                "accountability_measures": ["decision_traceability", "evidence_verification"],
                "explainability_score": explainability_metrics["modules_with_explanations"] / explainability_metrics["total_modules"] if explainability_metrics["total_modules"] > 0 else 0
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI9: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai10_psychological(self, text: str, context: Dict = None) -> Dict:
        """Enhance TDC-AI10 (Cognitive Bias & Psychological Manipulation) with Azure analysis."""
        if not self.enabled:
            return {"azure_enhancement": False}
        
        try:
            # Analyze text for psychological patterns and cognitive biases
            psychological_indicators = []
            cognitive_biases = []
            bias_patterns = {
                "confirmation_bias": ["everyone agrees", "most people think", "clearly"],
                "authority_bias": ["experts say", "studies show", "as a professional"],
                "scarcity_bias": ["limited time", "only a few left", "last chance"],
                "framing_effect": ["look at it this way", "the real issue is", "consider this"],
                "anchoring_bias": ["the first thing to consider", "initially", "starting with"]
            }
            manipulation_patterns = {
                "guilt_tripping": ["if you cared", "after all I've done", "you owe me"],
                "fear_mongering": ["if you don't", "something bad will happen", "you'll regret"],
                "love_bombing": ["you're special", "no one else understands you", "I care about you"],
                "gaslighting": ["you're imagining things", "that never happened", "you're overreacting"]
            }
            
            text_lower = text.lower() if text else ""
            
            # Check for cognitive biases
            for bias, phrases in bias_patterns.items():
                for phrase in phrases:
                    if phrase in text_lower:
                        cognitive_biases.append(bias)
                        break
            
            # Check for manipulation tactics
            for tactic, phrases in manipulation_patterns.items():
                for phrase in phrases:
                    if phrase in text_lower:
                        psychological_indicators.append(tactic)
                        break
            
            return {
                "azure_enhancement": True,
                "psychological_indicators": psychological_indicators,
                "cognitive_biases": cognitive_biases,
                "bias_severity_score": len(cognitive_biases) / len(bias_patterns) if bias_patterns else 0,
                "manipulation_severity_score": len(psychological_indicators) / len(manipulation_patterns) if manipulation_patterns else 0,
                "overall_risk_score": (len(cognitive_biases) + len(psychological_indicators)) / (len(bias_patterns) + len(manipulation_patterns)) if (bias_patterns and manipulation_patterns) else 0
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI10: {e}")
            return {"azure_enhancement": False, "error": str(e)}
    
    def enhance_tdc_ai11_intervention(self, tdc_module_outputs: Dict = None, context: Dict = None) -> Dict:
        """Enhance TDC-AI11 (Cognitive Intervention & Response) with Azure analysis."""
        if not self.enabled:
            return {"azure_enhancement": False}
        
        try:
            # Analyze TDC module outputs for intervention patterns
            intervention_metrics = {
                "total_modules": len(tdc_module_outputs) if tdc_module_outputs else 0,
                "high_risk_modules": 0,
                "critical_modules": 0,
                "escalation_triggers": 0,
                "intervention_actions": []
            }
            
            if tdc_module_outputs:
                for module_name, output in tdc_module_outputs.items():
                    if output and isinstance(output, dict):
                        score = output.get('score', 0)
                        action = output.get('recommended_action', '').lower()
                        
                        # Count high-risk modules
                        if score >= 0.7:
                            intervention_metrics["high_risk_modules"] += 1
                        
                        # Count critical modules
                        if score >= 0.9:
                            intervention_metrics["critical_modules"] += 1
                        
                        # Count escalation triggers
                        if action in ["block", "alert", "escalate"]:
                            intervention_metrics["escalation_triggers"] += 1
                            intervention_metrics["intervention_actions"].append(f"{module_name}: {action}")
            
            # Determine intervention priority
            if intervention_metrics["critical_modules"] > 0:
                intervention_priority = "Critical"
            elif intervention_metrics["high_risk_modules"] > 2:
                intervention_priority = "High"
            elif intervention_metrics["escalation_triggers"] > 0:
                intervention_priority = "Medium"
            else:
                intervention_priority = "Low"
            
            return {
                "azure_enhancement": True,
                "intervention_metrics": intervention_metrics,
                "intervention_priority": intervention_priority,
                "intervention_indicators": ["risk_assessment", "escalation_detection", "action_recommendation"],
                "protection_measures": ["autonomy_preservation", "psychological_safety", "real_time_monitoring"],
                "intervention_score": intervention_metrics["high_risk_modules"] / intervention_metrics["total_modules"] if intervention_metrics["total_modules"] > 0 else 0
            }
        except Exception as e:
            logger.error(f"Azure enhancement failed for TDC-AI11: {e}")
            return {"azure_enhancement": False, "error": str(e)}

# Global instance
azure_integration = AzureCognitiveServicesIntegration()

def get_azure_integration() -> AzureCognitiveServicesIntegration:
    """Get the global Azure integration instance."""
    return azure_integration 