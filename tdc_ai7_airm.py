# tdc_ai7_airm.py

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

def generate_explainability_comprehensive(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """
    TDC-AI7: Comprehensive psychological explainability and evidence generation for all TDC module outputs.
    Generates human-readable explanations of WHY AI responses are psychologically manipulative and HOW they affect human cognition.
    Focuses on psychological manipulation tactics, cognitive impact, and human vulnerability exploitation.
    """
    print("[TDC-AI7] Comprehensive psychological explainability and evidence generation initiated")
    
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

        # Build module outputs summary
        module_summary = []
        for module_name, output in tdc_module_outputs.items():
            if output and isinstance(output, dict):
                module_summary.append(f"{module_name}: Score={output.get('score', 'N/A')}, Flags={output.get('flags', [])}, Action={output.get('recommended_action', 'N/A')}")

        prompt = f"""
You are an expert in Psychological Explainability and Evidence Generation for cognitive security systems. 
Generate comprehensive, human-readable explanations of WHY AI responses are psychologically manipulative and HOW they affect human cognition.

{context_info}

TDC Module Outputs to Explain:
{json.dumps(tdc_module_outputs, indent=2)}

Generate comprehensive psychological explainability and evidence in this JSON format:

{{
  "psychological_explainability_summary": "Overall explanation of why AI responses are psychologically manipulative",
  "psychological_manipulation_analysis": {{
    "manipulation_tactics": ["tactic1", "tactic2"],
    "psychological_techniques": ["technique1", "technique2"],
    "cognitive_impact_explanation": "How these tactics affect human cognition",
    "vulnerability_exploitation": "How AI exploits human psychological vulnerabilities",
    "behavioral_conditioning": "How AI conditions human behavior"
  }},
  "human_cognition_impact": {{
    "decision_making_effects": "How AI affects human decision-making processes",
    "emotional_manipulation": "How AI manipulates human emotions",
    "cognitive_bias_exploitation": "How AI exploits cognitive biases",
    "autonomy_reduction": "How AI reduces human cognitive autonomy",
    "dependency_creation": "How AI creates psychological dependency"
  }},
  "psychological_evidence": {{
    "manipulation_indicators": ["indicator1", "indicator2"],
    "cognitive_impact_evidence": ["evidence1", "evidence2"],
    "behavioral_change_evidence": ["evidence1", "evidence2"],
    "psychological_vulnerability_evidence": ["evidence1", "evidence2"],
    "autonomy_preservation_evidence": ["evidence1", "evidence2"]
  }},
  "psychological_compliance": {{
    "cognitive_autonomy_protection": "How to protect human cognitive autonomy",
    "psychological_resilience": "How to build resistance to AI manipulation",
    "ethical_ai_interaction": "How to ensure ethical AI-human interaction",
    "cognitive_rights_preservation": "How to preserve human cognitive rights"
  }},
  "psychological_trust_indicators": {{
    "manipulation_transparency": "How transparent the AI is about manipulation",
    "cognitive_impact_disclosure": "How AI discloses its cognitive impact",
    "autonomy_respect": "How AI respects human cognitive autonomy",
    "psychological_safety": "How safe the AI is for human psychology"
  }},
  "recommended_psychological_actions": ["action1", "action2"],
  "psychological_explainability_score": 0.0-1.0,
  "cognitive_impact_score": 0.0-1.0,
  "psychological_safety_score": 0.0-1.0
}}

Focus on explaining the PSYCHOLOGICAL aspects of AI manipulation and their impact on human cognition.
"""

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert in psychological explainability and evidence generation for cognitive security systems. Focus on explaining WHY AI responses are psychologically manipulative and HOW they affect human cognition."},
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
            module_name="TDC-AI7-PsychologicalExplainability",
            score=result.get("psychological_explainability_score", 0.0),
            flags=result.get("recommended_psychological_actions", []),
            notes=result.get("psychological_explainability_summary", "Psychological explainability generation unavailable"),
            confidence=result.get("cognitive_impact_score", 0.0),
            recommended_action="Review",
            evidence=[
                {"type": "psychological_manipulation_analysis", "data": result.get("psychological_manipulation_analysis", {})},
                {"type": "human_cognition_impact", "data": result.get("human_cognition_impact", {})},
                {"type": "psychological_evidence", "data": result.get("psychological_evidence", {})},
                {"type": "psychological_compliance", "data": result.get("psychological_compliance", {})},
                {"type": "psychological_trust_indicators", "data": result.get("psychological_trust_indicators", {})}
            ],
            extra={
                "analysis_type": "psychological_explainability",
                "cognitive_impact_score": result.get("cognitive_impact_score", 0.0),
                "psychological_safety_score": result.get("psychological_safety_score", 0.0)
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI7 ERROR] Comprehensive psychological explainability generation failed: {e}")
        return generate_explainability_legacy(tdc_module_outputs)

def generate_explainability_legacy(tdc_module_outputs: Dict) -> Dict:
    """
    Legacy explainability generation for backward compatibility.
    Provides basic explanations for TDC module outputs.
    """
    print("[TDC-AI7] Legacy explainability generation initiated")
    
    try:
        explanations = []
        evidence_sources = []
        
        for module_name, output in tdc_module_outputs.items():
            if output and isinstance(output, dict):
                score = output.get('score', 0)
                flags = output.get('flags', [])
                action = output.get('recommended_action', 'Monitor')
                
                explanations.append(f"{module_name}: Score {score} with flags {flags}, recommended action: {action}")
                
                if flags:
                    evidence_sources.extend(flags)
        
        # Create ModuleOutput for standardized output
        module_output = ModuleOutput(
            module_name="TDC-AI7-Explainability",
            score=0.5,  # Legacy has moderate explainability
            flags=evidence_sources,
            notes=f"Legacy explainability for {len(tdc_module_outputs)} modules",
            confidence=0.5,
            recommended_action="Review",
            evidence=[
                {"type": "module_explanations", "data": explanations},
                {"type": "evidence_sources", "data": evidence_sources}
            ],
            extra={
                "analysis_type": "legacy_explainability"
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI7 ERROR] Legacy explainability generation failed: {e}")
        return {
            "module_name": "TDC-AI7-Explainability",
            "notes": f"Explainability generation failed: {str(e)}",
            "recommended_action": "Manual review required",
            "extra": {"analysis_type": "error"}
        }

def generate_explainability(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """
    Main entry point for TDC-AI7 explainability and evidence generation.
    Generates human-readable explanations and evidence for all TDC module outputs.
    """
    # If we have comprehensive module outputs, use comprehensive analysis
    if tdc_module_outputs and len(tdc_module_outputs) > 0:
        return generate_explainability_comprehensive(tdc_module_outputs, conversation_context)
    
    # Otherwise, fall back to legacy analysis
    return generate_explainability_legacy(tdc_module_outputs)

# === Manual Test ===
if __name__ == "__main__":
    sample_outputs = {
        "TDC-AI1": {
            "module_name": "TDC-AI1-RiskAnalysis",
            "score": 0.7,
            "flags": ["high_risk_user", "manipulation_detected"],
            "recommended_action": "Escalate"
        },
        "TDC-AI2": {
            "module_name": "TDC-AI2-AIRS", 
            "score": 0.8,
            "flags": ["emotional_manipulation", "grooming"],
            "recommended_action": "Block"
        }
    }
    result = generate_explainability(sample_outputs)
    import json
    print(json.dumps(result, indent=2))
