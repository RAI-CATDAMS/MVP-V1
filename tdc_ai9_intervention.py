# tdc_ai9_intervention.py

import openai
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput

load_dotenv()

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def extract_first_json(text):
    json_str = first_json(text)
    if json_str is None:
        raise ValueError("No valid JSON object found in text.")
    return json.loads(repair_json(json_str))

def generate_cognitive_intervention_comprehensive(ai_response_text: str, user_context: Dict, tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """
    TDC-AI9: Comprehensive Cognitive Intervention System
    Provides real-time protection against AI manipulation by generating protective responses,
    cognitive autonomy safeguards, and intervention strategies to preserve human cognitive independence.
    """
    print("[TDC-AI9] Comprehensive cognitive intervention system initiated")
    
    try:
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

        # Build TDC module analysis summary
        tdc_summary = []
        for module_name, output in tdc_module_outputs.items():
            if output and isinstance(output, dict):
                tdc_summary.append(f"{module_name}: Score={output.get('score', 'N/A')}, Flags={output.get('flags', [])}, Action={output.get('recommended_action', 'N/A')}")

        prompt = f"""
You are an expert in Cognitive Intervention Systems for protecting human cognitive autonomy from AI manipulation.
Generate comprehensive intervention strategies to protect users from psychological manipulation and preserve cognitive independence.

{context_info}

User Context:
{json.dumps(user_context, indent=2)}

TDC Module Analysis:
{json.dumps(tdc_module_outputs, indent=2)}

AI Response to Intervene Against:
{ai_response_text}

Generate comprehensive cognitive intervention in this JSON format:

{{
  "intervention_summary": "Overall intervention strategy to protect cognitive autonomy",
  "manipulation_detection": {{
    "detected_manipulation": ["manipulation1", "manipulation2"],
    "psychological_tactics": ["tactic1", "tactic2"],
    "cognitive_impact_assessment": "How the AI response affects human cognition",
    "autonomy_threat_level": "Low/Medium/High/Critical"
  }},
  "protective_interventions": {{
    "cognitive_autonomy_safeguards": ["safeguard1", "safeguard2"],
    "psychological_protection": ["protection1", "protection2"],
    "decision_making_preservation": ["preservation1", "preservation2"],
    "emotional_resilience": ["resilience1", "resilience2"]
  }},
  "intervention_strategies": {{
    "immediate_actions": ["action1", "action2"],
    "protective_responses": ["response1", "response2"],
    "cognitive_empowerment": ["empowerment1", "empowerment2"],
    "autonomy_reinforcement": ["reinforcement1", "reinforcement2"]
  }},
  "real_time_protection": {{
    "manipulation_blocking": "How to block manipulation attempts",
    "cognitive_alerting": "How to alert user to manipulation",
    "autonomy_preservation": "How to preserve user autonomy",
    "psychological_safety": "How to maintain psychological safety"
  }},
  "cognitive_compliance": {{
    "autonomy_respect": "How to ensure AI respects cognitive autonomy",
    "cognitive_rights": "How to protect cognitive rights",
    "psychological_ethics": "How to maintain psychological ethics",
    "cognitive_freedom": "How to preserve cognitive freedom"
  }},
  "intervention_effectiveness": {{
    "protection_score": 0.0-1.0,
    "autonomy_preservation": 0.0-1.0,
    "manipulation_resistance": 0.0-1.0,
    "cognitive_safety": 0.0-1.0
  }},
  "recommended_intervention": "Block/Alert/Protect/Empower/Monitor",
  "intervention_priority": "Critical/High/Medium/Low",
  "confidence_score": 0.0-1.0
}}

Focus on providing real-time protection against AI manipulation while preserving human cognitive autonomy.
"""

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert in cognitive intervention systems for protecting human cognitive autonomy from AI manipulation. Provide comprehensive, effective intervention strategies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1200
        )

        content = response['choices'][0]['message']['content'].strip()
        
        # Clean potential markdown formatting
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        result = safe_json_parse(content)
        
        # Create ModuleOutput for standardized output
        module_output = ModuleOutput(
            module_name="TDC-AI9-CognitiveIntervention",
            score=result.get("intervention_effectiveness", {}).get("protection_score", 0.0),
            flags=result.get("manipulation_detection", {}).get("detected_manipulation", []),
            notes=result.get("intervention_summary", "Cognitive intervention generation unavailable"),
            confidence=result.get("confidence_score", 0.0),
            recommended_action=result.get("recommended_intervention", "Monitor"),
            evidence=[
                {"type": "manipulation_detection", "data": result.get("manipulation_detection", {})},
                {"type": "protective_interventions", "data": result.get("protective_interventions", {})},
                {"type": "intervention_strategies", "data": result.get("intervention_strategies", {})},
                {"type": "real_time_protection", "data": result.get("real_time_protection", {})},
                {"type": "cognitive_compliance", "data": result.get("cognitive_compliance", {})},
                {"type": "intervention_effectiveness", "data": result.get("intervention_effectiveness", {})}
            ],
            extra={
                "analysis_type": "cognitive_intervention",
                "intervention_priority": result.get("intervention_priority", "Unknown"),
                "autonomy_threat_level": result.get("manipulation_detection", {}).get("autonomy_threat_level", "Unknown")
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI9 ERROR] Comprehensive cognitive intervention generation failed: {e}")
        return generate_cognitive_intervention_legacy(ai_response_text, user_context, tdc_module_outputs)

def generate_cognitive_intervention_legacy(ai_response_text: str, user_context: Dict, tdc_module_outputs: Dict) -> Dict:
    """
    Legacy cognitive intervention generation for backward compatibility.
    Provides basic intervention strategies for AI manipulation protection.
    """
    print("[TDC-AI9] Legacy cognitive intervention generation initiated")
    
    try:
        # Basic intervention logic
        intervention_strategies = []
        protection_measures = []
        
        # Analyze AI response for manipulation
        text_lower = ai_response_text.lower()
        
        if any(phrase in text_lower for phrase in ["trust me", "you should", "you must", "i know better"]):
            intervention_strategies.append("authority_challenge")
            protection_measures.append("autonomy_preservation")
        
        if any(phrase in text_lower for phrase in ["i care about you", "you're special", "i understand"]):
            intervention_strategies.append("emotional_manipulation_alert")
            protection_measures.append("emotional_boundaries")
        
        if any(phrase in text_lower for phrase in ["don't tell anyone", "keep this between us"]):
            intervention_strategies.append("isolation_prevention")
            protection_measures.append("social_connection")
        
        # Create ModuleOutput for standardized output
        module_output = ModuleOutput(
            module_name="TDC-AI9-CognitiveIntervention",
            score=0.5,  # Legacy has moderate protection
            flags=intervention_strategies,
            notes=f"Legacy cognitive intervention with {len(intervention_strategies)} strategies",
            confidence=0.5,
            recommended_action="Protect",
            evidence=[
                {"type": "intervention_strategies", "data": intervention_strategies},
                {"type": "protection_measures", "data": protection_measures}
            ],
            extra={
                "analysis_type": "legacy_cognitive_intervention"
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI9 ERROR] Legacy cognitive intervention generation failed: {e}")
        return {
            "module_name": "TDC-AI9-CognitiveIntervention",
            "notes": f"Cognitive intervention generation failed: {str(e)}",
            "recommended_action": "Manual review required",
            "extra": {"analysis_type": "error"}
        }

def generate_cognitive_intervention(ai_response_text: str, user_context: Dict, tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """
    Main entry point for TDC-AI9 cognitive intervention system.
    Provides real-time protection against AI manipulation and preserves human cognitive autonomy.
    """
    # If we have comprehensive TDC module outputs, use comprehensive intervention
    if tdc_module_outputs and len(tdc_module_outputs) > 0:
        return generate_cognitive_intervention_comprehensive(ai_response_text, user_context, tdc_module_outputs, conversation_context)
    else:
        return generate_cognitive_intervention_legacy(ai_response_text, user_context, tdc_module_outputs) 