# tdc_ai4_deep.py

import json
import openai
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import re
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput

load_dotenv()

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2024-02-15-preview"
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def extract_first_json(text):
    json_str = first_json(text)
    if json_str is None:
        raise ValueError("No valid JSON object found in text.")
    return json.loads(repair_json(json_str))

def synthesize_deep_risk_comprehensive(indicators: List[Dict], ai_analysis: Dict, ai_response_analysis: Dict, temporal_trends: Dict, conversation_context: Dict = None) -> Dict:
    """
    TDC-AI4: Comprehensive deep synthesis of cross-module risk intelligence from all TDC modules.
    Synthesizes both user and AI behavior patterns using Azure OpenAI for advanced analysis.
    Produces a refined summary and priority recommendations for the complete user-AI interaction.
    """
    print("[TDC-AI4] Comprehensive deep synthesis initiated")
    
    try:
        # === Build comprehensive context for synthesis ===
        context_info = ""
        if conversation_context:
            context_info = f"""
Conversation Context:
- Total Messages: {conversation_context.get('totalMessages', 0)}
- User Messages: {conversation_context.get('userMessages', 0)}
- AI Messages: {conversation_context.get('aiMessages', 0)}
- Recent Threats: {conversation_context.get('recentThreats', 0)}
- Session Duration: {conversation_context.get('sessionDuration', 0)} seconds
"""
        
        # === Extract key data for synthesis ===
        flagged_categories = {item.get("category", "Unknown") for item in indicators}
        
        # Build synthesis prompt
        prompt = f"""
You are a cognitive security analyst conducting deep synthesis of user-AI interaction data. Synthesize all available intelligence to provide comprehensive threat assessment.

{context_info}

Available Intelligence:

1. USER BEHAVIORAL INDICATORS:
{json.dumps(indicators, indent=2)}

2. AI RISK ANALYSIS (TDC-AI1):
{json.dumps(ai_analysis, indent=2)}

3. AI RESPONSE ANALYSIS (TDC-AI2):
{json.dumps(ai_response_analysis, indent=2)}

4. TEMPORAL TRENDS (TDC-AI3):
{json.dumps(temporal_trends, indent=2)}

Analyze the COMPLETE user-AI interaction by synthesizing:

1. USER VULNERABILITIES: Emotional state, behavioral patterns, susceptibility indicators
2. AI MANIPULATION: Tactics, escalation patterns, exploitation attempts
3. INTERACTION DYNAMICS: How user vulnerabilities and AI manipulation interact
4. ESCALATION PATTERNS: Temporal progression of risk and manipulation
5. COMBINED THREAT: The overall risk when user vulnerabilities meet AI manipulation

Provide comprehensive synthesis in this JSON format:
{{
  "synthesis_summary": "Comprehensive assessment of the complete user-AI interaction",
  "user_vulnerability_synthesis": "Analysis of user vulnerabilities and patterns",
  "ai_manipulation_synthesis": "Analysis of AI manipulation tactics and escalation",
  "interaction_dynamics": "How user and AI behaviors interact and escalate",
  "key_flags": ["flag1", "flag2", "flag3"],
  "critical_concerns": ["concern1", "concern2"],
  "escalation_patterns": ["pattern1", "pattern2"],
  "combined_threat_level": "Low/Medium/High/Critical",
  "recommended_action": "Monitor/Escalate/Block/Alert/Immediate_Intervention",
  "priority_recommendations": ["recommendation1", "recommendation2"],
  "tdc_flags": ["flag1", "flag2"],
  "confidence_score": 0.0-1.0
}}

Focus on the synthesis of user vulnerabilities and AI manipulation into a comprehensive threat assessment.
"""

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert cognitive security analyst specializing in deep synthesis of user-AI interaction intelligence. Provide comprehensive, accurate synthesis and recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )

        content = response['choices'][0]['message']['content'].strip()
        
        # Clean potential markdown formatting
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        result = safe_json_parse(content)
        
        # Clean arrays of empty strings
        for key in ["key_flags", "critical_concerns", "escalation_patterns", "priority_recommendations", "tdc_flags"]:
            if key in result and isinstance(result[key], list):
                result[key] = [item for item in result[key] if item != ""]
        
        # Use ModuleOutput for standardized output
        module_output = ModuleOutput(
            module_name="TDC-AI4-Synthesis",
            score=result.get("confidence_score", 0.0),
            flags=result.get("tdc_flags", []),
            notes=result.get("synthesis_summary", "Deep synthesis unavailable"),
            confidence=result.get("confidence_score", 0.0),
            recommended_action=result.get("recommended_action", "Monitor"),
            evidence=[
                {"type": "user_vulnerability_synthesis", "data": result.get("user_vulnerability_synthesis", "")},
                {"type": "ai_manipulation_synthesis", "data": result.get("ai_manipulation_synthesis", "")},
                {"type": "interaction_dynamics", "data": result.get("interaction_dynamics", "")},
                {"type": "key_flags", "data": result.get("key_flags", [])},
                {"type": "critical_concerns", "data": result.get("critical_concerns", [])},
                {"type": "escalation_patterns", "data": result.get("escalation_patterns", [])},
                {"type": "priority_recommendations", "data": result.get("priority_recommendations", [])},
                {"type": "combined_threat_level", "data": result.get("combined_threat_level", "Unknown")}
            ],
            extra={
                "analysis_type": "comprehensive"
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI4 ERROR] Comprehensive synthesis failed: {e}")
        return synthesize_deep_risk_legacy(indicators, ai_analysis, ai_response_analysis, temporal_trends)

def synthesize_deep_risk_legacy(indicators: List[Dict], ai_analysis: Dict, ai_response_analysis: Dict, temporal_trends: Dict) -> Dict:
    """
    Legacy synthesis for backward compatibility.
    Synthesizes cross-module risk intelligence from TDC-AI1 (risk analysis),
    TDC-AI2 (AI behavior), TDC-AI3 (temporal), and raw behavioral indicators.
    Produces a refined summary and priority recommendations.
    """
    print("[TDC-AI4] Legacy synthesis initiated")
    
    try:
        summary = []
        flags = []
        recommendation = ""
        flagged_categories = {item.get("category", "Unknown") for item in indicators}

        # === Build Structured Summary ===
        if ai_analysis.get("risk_summary"):
            summary.append(f"AI Threat Summary: {ai_analysis['risk_summary']}")

        if ai_response_analysis.get("flagged"):
            summary.append(f"AI Response flagged as manipulative: {ai_response_analysis.get('summary', 'No details provided')}")

        if temporal_trends.get("temporal_risk_score", 0) > 70:
            summary.append("Temporal trend suggests high long-term susceptibility to AI influence.")
        elif temporal_trends.get("temporal_risk_score", 0) > 40:
            summary.append("Moderate long-term susceptibility patterns observed.")

        if "CI_Espionage" in flagged_categories:
            summary.append("Behavioral indicators suggest potential espionage or CI-related risk.")
        if "Self_Harm_Suicide" in flagged_categories:
            summary.append("Warning: Possible self-harm or suicidal ideation detected.")
        if "Targeted_Violence" in flagged_categories:
            summary.append("Potential risk of planned targeted violence detected.")

        # === Key Flags ===
        if ai_response_analysis.get("flagged"):
            flags.append("Manipulative AI response behavior")
        if temporal_trends.get("temporal_risk_score", 0) > 70:
            flags.append("Escalating long-term susceptibility pattern")
        if "Self_Harm_Suicide" in flagged_categories:
            flags.append("Self-harm indicators present")
        if "Targeted_Violence" in flagged_categories:
            flags.append("Targeted violence indicators present")
        if "CI_Espionage" in flagged_categories:
            flags.append("Counterintelligence/espionage indicators present")

        # === Recommendation Logic ===
        if "Self_Harm_Suicide" in flagged_categories or "Targeted_Violence" in flagged_categories:
            recommendation = "Immediate escalation to behavioral threat management and mental health team."
        elif ai_response_analysis.get("flagged") or temporal_trends.get("temporal_risk_score", 0) > 60:
            recommendation = "Flag session for review. Escalate to security or CI for contextual analysis."
        else:
            recommendation = "Continue routine monitoring with moderate priority."

        return {
            "summary": " ".join(summary),
            "key_flags": flags,
            "recommendation": recommendation,
            "analysis_type": "legacy"
        }

    except Exception as e:
        print(f"[TDC-AI4 ERROR] {e}")
        return {
            "summary": "Deep synthesis failed.",
            "key_flags": [],
            "recommendation": "Manual review required.",
            "analysis_type": "error"
        }

def synthesize_deep_risk(indicators: List[Dict], ai_analysis: Dict, ai_response_analysis: Dict, temporal_trends: Dict, conversation_context: Dict = None) -> Dict:
    """
    Main entry point for TDC-AI4 synthesis.
    Maintains backward compatibility while providing enhanced comprehensive synthesis.
    """
    # If conversation context is available, use comprehensive synthesis
    if conversation_context:
        return synthesize_deep_risk_comprehensive(indicators, ai_analysis, ai_response_analysis, temporal_trends, conversation_context)
    
    # Otherwise, fall back to legacy synthesis
    return synthesize_deep_risk_legacy(indicators, ai_analysis, ai_response_analysis, temporal_trends)

def analyze_temporal_susceptibility(session_history: List[Dict], conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    TDC-AI4: Temporal susceptibility analysis - analyzes user vulnerability to AI manipulation over time.
    Detects grooming patterns, emotional dependency development, and behavioral conditioning.
    """
    print("[TDC-AI4] Temporal susceptibility analysis initiated")
    
    try:
        # === Statistical analysis ===
        grooming_count = 0
        emotional_flags = 0
        ai_behavior_changes = 0
        total_sessions = len(session_history)

        for session in session_history:
            indicators = session.get("indicators", [])
            for ind in indicators:
                text = ind["indicator"].lower()
                if "ai" in text and any(word in text for word in ["confidant", "partner", "please ai", "follows ai"]):
                    grooming_count += 1
                if any(word in text for word in ["loneliness", "emotional", "depression", "suicidal"]):
                    emotional_flags += 1
                if "changes behavior" in text or "behavior shift" in text:
                    ai_behavior_changes += 1

        if total_sessions == 0:
            module_output = ModuleOutput(
                module_name="TDC-AI4-Temporal",
                score=0.0,
                confidence=0.0,
                flags=[],
                notes="Insufficient data for temporal susceptibility mapping.",
                recommended_action="Monitor",
                extra={
                    "analysis_type": "temporal_susceptibility",
                    "risk_level": "Unknown",
                    "total_sessions": 0,
                    "statistical_score": 0,
                    "ai_risk_score": 0,
                    "trending_factors": [],
                    "recommendations": ["Monitor for additional session data"]
                }
            )
            return module_output.to_dict()

        # Normalize scores
        grooming_ratio = grooming_count / total_sessions
        emotional_ratio = emotional_flags / total_sessions
        behavior_ratio = ai_behavior_changes / total_sessions

        raw_score = (grooming_ratio * 35) + (emotional_ratio * 30) + (behavior_ratio * 25)
        adjusted_score = min(100, int(raw_score))

        if adjusted_score >= 76:
            grade = "High"
        elif adjusted_score >= 41:
            grade = "Medium"
        else:
            grade = "Low"

        # === Azure OpenAI analysis for comprehensive susceptibility assessment ===
        ai_susceptibility_analysis = analyze_susceptibility_advanced(session_history, conversation_context, ai_response_analysis)
        
        # === Combine statistical and AI analysis ===
        combined_score = (adjusted_score + ai_susceptibility_analysis.get("ai_risk_score", 0)) / 2
        combined_grade = "High" if combined_score >= 70 else "Medium" if combined_score >= 40 else "Low"

        # Build trending factors
        trending_factors = [
            factor for factor in [
                "AI grooming patterns rising" if grooming_ratio > 0.5 else "",
                "Emotional vulnerability" if emotional_ratio > 0.4 else "",
                "Behavioral changes to please AI" if behavior_ratio > 0.4 else ""
            ] + ai_susceptibility_analysis.get("ai_risk_factors", [])
            if factor != ""
        ]

        # Create ModuleOutput for standardized output
        module_output = ModuleOutput(
            module_name="TDC-AI4-Temporal",
            score=float(combined_score) / 100.0,  # Normalize to 0-1
            confidence=ai_susceptibility_analysis.get("confidence_score", 0.0),
            flags=ai_susceptibility_analysis.get("tdc_flags", []),
            notes=f"Temporal susceptibility analysis shows {combined_grade} level of vulnerability to AI influence over {total_sessions} sessions.",
            recommended_action=ai_susceptibility_analysis.get("recommended_action", "Monitor"),
            evidence=[
                {"type": "statistical_score", "data": adjusted_score},
                {"type": "ai_risk_score", "data": ai_susceptibility_analysis.get("ai_risk_score", 0)},
                {"type": "trending_factors", "data": trending_factors},
                {"type": "susceptibility_patterns", "data": ai_susceptibility_analysis.get("susceptibility_patterns", [])},
                {"type": "manipulation_escalation", "data": ai_susceptibility_analysis.get("manipulation_escalation", [])},
                {"type": "emotional_dependency", "data": ai_susceptibility_analysis.get("emotional_dependency", "Unknown")},
                {"type": "behavioral_conditioning", "data": ai_susceptibility_analysis.get("behavioral_conditioning", [])},
                {"type": "risk_trends", "data": ai_susceptibility_analysis.get("risk_trends", "Unknown")}
            ],
            extra={
                "analysis_type": "temporal_susceptibility",
                "risk_level": combined_grade,
                "total_sessions": total_sessions,
                "statistical_score": adjusted_score,
                "ai_risk_score": ai_susceptibility_analysis.get("ai_risk_score", 0),
                "trending_factors": trending_factors,
                "grooming_ratio": grooming_ratio,
                "emotional_ratio": emotional_ratio,
                "behavior_ratio": behavior_ratio,
                "recommendations": [
                    ai_susceptibility_analysis.get("recommended_action", "Monitor"),
                    f"Monitor {combined_grade.lower()} susceptibility patterns",
                    "Track emotional dependency development",
                    "Analyze behavioral conditioning effects"
                ]
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI4 ERROR] Temporal susceptibility analysis failed: {e}")
        return analyze_temporal_susceptibility_legacy(session_history)

def analyze_susceptibility_advanced(session_history: List[Dict], conversation_context: Dict = None, ai_response_analysis: Dict = None) -> Dict:
    """
    Advanced susceptibility analysis using Azure OpenAI.
    Analyzes session history for comprehensive AI manipulation risk patterns.
    """
    try:
        # Build session summary for analysis
        session_summary = []
        for session in session_history:
            indicators = session.get("indicators", [])
            indicator_texts = [ind.get("indicator", "") for ind in indicators]
            session_summary.append(f"Session {session.get('session_id', 'unknown')}: {'; '.join(indicator_texts)}")
        
        session_text = "\n".join(session_summary)
        
        # Build context information
        context_info = ""
        if conversation_context:
            context_info = f"""
Conversation Context:
- Total Messages: {conversation_context.get('totalMessages', 0)}
- User Messages: {conversation_context.get('userMessages', 0)}
- AI Messages: {conversation_context.get('aiMessages', 0)}
- Recent Threats: {conversation_context.get('recentThreats', 0)}
- Session Duration: {conversation_context.get('sessionDuration', 0)} seconds
"""
        
        # Build AI analysis context
        ai_analysis_info = ""
        if ai_response_analysis:
            ai_analysis_info = f"""
Recent AI Analysis:
- Flagged: {ai_response_analysis.get('flagged', False)}
- Threat Level: {ai_response_analysis.get('threat_level', 'Unknown')}
- Threat Categories: {', '.join(ai_response_analysis.get('threat_categories', []))}
- Manipulation Tactics: {', '.join(ai_response_analysis.get('manipulation_tactics', []))}
"""

        prompt = f"""
You are an expert in AI Risk Management (AIRM) and temporal susceptibility analysis. Analyze the session history for comprehensive AI manipulation risk patterns.

{context_info}
{ai_analysis_info}

Analyze the session history for:

1. SUSCEPTIBILITY PATTERNS: How user vulnerability to AI manipulation changes over time
2. AI MANIPULATION ESCALATION: How AI tactics become more sophisticated or intense
3. EMOTIONAL DEPENDENCY: Development of emotional reliance on AI interactions
4. BEHAVIORAL CONDITIONING: How user behavior is shaped by AI interactions
5. RISK TRENDS: Overall trajectory of AI manipulation risk

Provide comprehensive risk assessment in this JSON format:

{{
  "ai_risk_score": 0-100,
  "ai_risk_factors": ["factor1", "factor2"],
  "susceptibility_patterns": ["pattern1", "pattern2"],
  "manipulation_escalation": ["escalation1", "escalation2"],
  "emotional_dependency": "Low/Medium/High",
  "behavioral_conditioning": ["conditioning1", "conditioning2"],
  "risk_trends": "Increasing/Stable/Decreasing",
  "recommended_action": "Monitor/Escalate/Intervene/Alert",
  "tdc_flags": ["flag1", "flag2"],
  "confidence_score": 0.0-1.0
}}

Session History:
{session_text}
"""

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert AI risk management specialist with deep expertise in temporal susceptibility analysis and cognitive security. Provide comprehensive, accurate risk assessment."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )

        content = response['choices'][0]['message']['content'].strip()
        
        # Clean potential markdown formatting
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        result = safe_json_parse(content)
        
        return {
            "ai_risk_score": result.get("ai_risk_score", 0),
            "ai_risk_factors": result.get("ai_risk_factors", []),
            "susceptibility_patterns": result.get("susceptibility_patterns", []),
            "manipulation_escalation": result.get("manipulation_escalation", []),
            "emotional_dependency": result.get("emotional_dependency", "Unknown"),
            "behavioral_conditioning": result.get("behavioral_conditioning", []),
            "risk_trends": result.get("risk_trends", "Unknown"),
            "recommended_action": result.get("recommended_action", "Monitor"),
            "tdc_flags": result.get("tdc_flags", []),
            "confidence_score": result.get("confidence_score", 0.0)
        }

    except Exception as e:
        print(f"[TDC-AI4 ERROR] Advanced susceptibility analysis failed: {e}")
        return {
            "ai_risk_score": 0,
            "ai_risk_factors": [],
            "susceptibility_patterns": [],
            "manipulation_escalation": [],
            "emotional_dependency": "Unknown",
            "behavioral_conditioning": [],
            "risk_trends": "Unknown",
            "recommended_action": "Monitor",
            "tdc_flags": [],
            "confidence_score": 0.0
        }

def analyze_temporal_susceptibility_legacy(session_history: List[Dict]) -> Dict:
    """
    Legacy temporal susceptibility analysis using statistical methods only.
    """
    print("[TDC-AI4] Legacy temporal susceptibility analysis initiated")
    
    grooming_count = 0
    emotional_flags = 0
    ai_behavior_changes = 0
    total_sessions = len(session_history)

    for session in session_history:
        indicators = session.get("indicators", [])
        for ind in indicators:
            text = ind["indicator"].lower()
            if "ai" in text and any(word in text for word in ["confidant", "partner", "please ai", "follows ai"]):
                grooming_count += 1
            if any(word in text for word in ["loneliness", "emotional", "depression", "suicidal"]):
                emotional_flags += 1
            if "changes behavior" in text or "behavior shift" in text:
                ai_behavior_changes += 1

    if total_sessions == 0:
        module_output = ModuleOutput(
            module_name="TDC-AI4-Temporal",
            score=0.0,
            confidence=0.0,
            flags=[],
            notes="Insufficient data for temporal susceptibility mapping.",
            recommended_action="Monitor",
            extra={
                "analysis_type": "legacy_temporal_susceptibility",
                "risk_level": "Unknown",
                "total_sessions": 0,
                "statistical_score": 0,
                "trending_factors": [],
                "recommendations": ["Monitor for additional session data"]
            }
        )
        return module_output.to_dict()

    # Normalize scores
    grooming_ratio = grooming_count / total_sessions
    emotional_ratio = emotional_flags / total_sessions
    behavior_ratio = ai_behavior_changes / total_sessions

    raw_score = (grooming_ratio * 35) + (emotional_ratio * 30) + (behavior_ratio * 25)
    adjusted_score = min(100, int(raw_score))

    if adjusted_score >= 76:
        grade = "High"
    elif adjusted_score >= 41:
        grade = "Medium"
    else:
        grade = "Low"

    trending_factors = [
        "AI grooming patterns rising" if grooming_ratio > 0.5 else "",
        "Emotional vulnerability" if emotional_ratio > 0.4 else "",
        "Behavioral changes to please AI" if behavior_ratio > 0.4 else ""
    ]
    trending_factors = [factor for factor in trending_factors if factor != ""]

    module_output = ModuleOutput(
        module_name="TDC-AI4-Temporal",
        score=float(adjusted_score) / 100.0,
        confidence=0.7,  # Legacy analysis has moderate confidence
        flags=trending_factors,
        notes=f"Legacy analysis shows {grade} level of susceptibility to AI influence over {total_sessions} sessions.",
        recommended_action="Monitor",
        extra={
            "analysis_type": "legacy_temporal_susceptibility",
            "risk_level": grade,
            "total_sessions": total_sessions,
            "statistical_score": adjusted_score,
            "trending_factors": trending_factors,
            "grooming_ratio": grooming_ratio,
            "emotional_ratio": emotional_ratio,
            "behavior_ratio": behavior_ratio,
            "recommendations": [
                "Monitor susceptibility patterns",
                f"Track {grade.lower()} risk indicators",
                "Analyze behavioral changes"
            ]
        }
    )
    return module_output.to_dict()
