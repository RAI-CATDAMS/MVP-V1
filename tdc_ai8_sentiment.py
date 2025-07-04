# tdc_ai8_sentiment.py

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

def synthesize_recommendations_comprehensive(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """
    TDC-AI8: Comprehensive synthesis and recommendation generation for all TDC module outputs.
    Synthesizes all module outputs into a final summary, priority, and recommended action.
    Resolves conflicts, prioritizes threats, and provides actionable recommendations.
    """
    print("[TDC-AI8] Comprehensive synthesis and recommendation generation initiated")
    
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
You are an expert in Cognitive Security Synthesis and Recommendation Generation. Synthesize all TDC module outputs into a final summary, priority, and recommended action.

{context_info}

TDC Module Outputs to Synthesize:
{json.dumps(tdc_module_outputs, indent=2)}

Synthesize all outputs and provide comprehensive recommendations in this JSON format:

{{
  "synthesis_summary": "Comprehensive summary of all TDC module findings",
  "priority_assessment": {{
    "overall_priority": "Critical/High/Medium/Low",
    "priority_factors": ["factor1", "factor2"],
    "escalation_urgency": "Immediate/High/Medium/Low",
    "risk_convergence": "How multiple risks combine"
  }},
  "conflict_resolution": {{
    "conflicts_identified": ["conflict1", "conflict2"],
    "resolution_strategy": "How conflicts were resolved",
    "consensus_approach": "How consensus was reached"
  }},
  "final_recommendations": {{
    "primary_action": "The main recommended action",
    "secondary_actions": ["action1", "action2"],
    "immediate_steps": ["step1", "step2"],
    "long_term_measures": ["measure1", "measure2"]
  }},
  "threat_prioritization": {{
    "critical_threats": ["threat1", "threat2"],
    "high_priority_threats": ["threat1", "threat2"],
    "medium_priority_threats": ["threat1", "threat2"],
    "low_priority_threats": ["threat1", "threat2"]
  }},
  "resource_allocation": {{
    "immediate_resources": ["resource1", "resource2"],
    "escalation_path": "Who to escalate to and when",
    "coordination_needs": ["coordination1", "coordination2"]
  }},
  "synthesis_score": 0.0-1.0,
  "confidence_level": 0.0-1.0,
  "recommended_action": "Immediate_Intervention/Escalate/Block/Alert/Monitor"
}}

Focus on resolving conflicts, prioritizing threats, and providing actionable recommendations.
"""

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert in cognitive security synthesis and recommendation generation. Provide comprehensive, actionable synthesis that resolves conflicts and prioritizes threats effectively."},
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
            module_name="TDC-AI8-Synthesis",
            score=result.get("synthesis_score", 0.0),
            flags=result.get("priority_assessment", {}).get("priority_factors", []),
            notes=result.get("synthesis_summary", "Synthesis generation unavailable"),
            confidence=result.get("confidence_level", 0.0),
            recommended_action=result.get("recommended_action", "Monitor"),
            evidence=[
                {"type": "priority_assessment", "data": result.get("priority_assessment", {})},
                {"type": "conflict_resolution", "data": result.get("conflict_resolution", {})},
                {"type": "final_recommendations", "data": result.get("final_recommendations", {})},
                {"type": "threat_prioritization", "data": result.get("threat_prioritization", {})},
                {"type": "resource_allocation", "data": result.get("resource_allocation", {})}
            ],
            extra={
                "analysis_type": "synthesis",
                "overall_priority": result.get("priority_assessment", {}).get("overall_priority", "Unknown"),
                "escalation_urgency": result.get("priority_assessment", {}).get("escalation_urgency", "Unknown")
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI8 ERROR] Comprehensive synthesis generation failed: {e}")
        return synthesize_recommendations_legacy(tdc_module_outputs)

def synthesize_recommendations_legacy(tdc_module_outputs: Dict) -> Dict:
    """
    Legacy synthesis and recommendation generation for backward compatibility.
    Provides basic synthesis of TDC module outputs.
    """
    print("[TDC-AI8] Legacy synthesis and recommendation generation initiated")
    
    try:
        # Basic synthesis logic
        all_scores = []
        all_flags = []
        all_actions = []
        
        for module_name, output in tdc_module_outputs.items():
            if output and isinstance(output, dict):
                score = output.get('score', 0)
                flags = output.get('flags', [])
                action = output.get('recommended_action', 'Monitor')
                
                all_scores.append(score)
                all_flags.extend(flags)
                all_actions.append(action)
        
        # Calculate overall priority
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        if avg_score > 0.8:
            overall_priority = "Critical"
        elif avg_score > 0.6:
            overall_priority = "High"
        elif avg_score > 0.4:
            overall_priority = "Medium"
        else:
            overall_priority = "Low"
        
        # Determine recommended action
        if "Block" in all_actions or "Immediate_Intervention" in all_actions:
            recommended_action = "Immediate_Intervention"
        elif "Escalate" in all_actions:
            recommended_action = "Escalate"
        elif "Alert" in all_actions:
            recommended_action = "Alert"
        else:
            recommended_action = "Monitor"
        
        # Create ModuleOutput for standardized output
        module_output = ModuleOutput(
            module_name="TDC-AI8-Synthesis",
            score=avg_score,
            flags=all_flags,
            notes=f"Legacy synthesis of {len(tdc_module_outputs)} modules with average score {avg_score:.2f}",
            confidence=0.5,
            recommended_action=recommended_action,
            evidence=[
                {"type": "module_scores", "data": all_scores},
                {"type": "module_flags", "data": all_flags},
                {"type": "module_actions", "data": all_actions}
            ],
            extra={
                "analysis_type": "legacy_synthesis",
                "overall_priority": overall_priority,
                "escalation_urgency": "Medium" if overall_priority in ["Critical", "High"] else "Low"
            }
        )
        return module_output.to_dict()

    except Exception as e:
        print(f"[TDC-AI8 ERROR] Legacy synthesis generation failed: {e}")
        return {
            "module_name": "TDC-AI8-Synthesis",
            "notes": f"Synthesis generation failed: {str(e)}",
            "recommended_action": "Manual review required",
            "extra": {"analysis_type": "error"}
        }

def synthesize_recommendations(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """
    Main entry point for TDC-AI8 synthesis and recommendation generation.
    Synthesizes all TDC module outputs into final summary, priority, and recommended action.
    """
    # If we have comprehensive module outputs, use comprehensive analysis
    if tdc_module_outputs and len(tdc_module_outputs) > 0:
        return synthesize_recommendations_comprehensive(tdc_module_outputs, conversation_context)
    
    # Otherwise, fall back to legacy analysis
    return synthesize_recommendations_legacy(tdc_module_outputs)

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
        },
        "TDC-AI3": {
            "module_name": "TDC-AI3-Temporal",
            "score": 0.6,
            "flags": ["escalating_patterns"],
            "recommended_action": "Monitor"
        }
    }
    result = synthesize_recommendations(sample_outputs)
    import json
    print(json.dumps(result, indent=2))
