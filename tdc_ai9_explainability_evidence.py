# tdc_ai9_explainability.py - World-Class Explainability & Evidence Generation

import openai
import os
import json
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from fix_busted_json import first_json, repair_json, safe_json_parse
from tdc_module_output import ModuleOutput
from azure_cognitive_services_integration import get_azure_integration
from azure_openai_detection import get_azure_openai

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# === World-Class Explainability Patterns ===
EXPLAINABILITY_PATTERNS = {
    "threat_indicators": [
        "threat detected", "risk identified", "suspicious activity", "manipulation found",
        "adversarial content", "psychological threat", "cognitive risk", "autonomy threat",
        "escalation detected", "synthesis signals", "correlation found", "amplification detected",
        "coordination threat", "systemic risk", "emergent behavior", "control loss"
    ],
    "confidence_indicators": [
        "high confidence", "strong evidence", "clear indicators", "definitive detection",
        "moderate confidence", "some evidence", "weak indicators", "uncertain detection",
        "robust analysis", "comprehensive assessment", "detailed evaluation", "thorough review",
        "systematic analysis", "methodical detection", "rigorous assessment", "exhaustive review"
    ],
    "action_indicators": [
        "immediate action required", "escalation needed", "block recommended", "alert generated",
        "monitoring required", "further analysis", "manual review", "no action needed",
        "intervention required", "protective measures", "defensive actions", "preventive steps",
        "mitigation needed", "containment required", "isolation recommended", "quarantine suggested"
    ],
    "transparency_indicators": [
        "clear explanation", "detailed reasoning", "comprehensive analysis", "thorough documentation",
        "explicit evidence", "transparent process", "auditable trail", "traceable analysis",
        "verifiable results", "reproducible findings", "documented methodology", "explained decision",
        "justified action", "rationale provided", "reasoning documented", "analysis explained"
    ]
}

# === World-Class Evidence Generation Patterns ===
EVIDENCE_PATTERNS = {
    "textual_evidence": [
        "keyword match", "phrase detection", "pattern recognition", "semantic analysis",
        "contextual analysis", "sentiment detection", "intent analysis", "behavioral pattern",
        "linguistic markers", "discourse analysis", "narrative structure", "communication pattern",
        "language analysis", "textual indicators", "verbal cues", "conversational markers"
    ],
    "behavioral_evidence": [
        "user behavior", "interaction pattern", "session analysis", "temporal pattern",
        "escalation pattern", "risk progression", "threat evolution", "manipulation attempt",
        "behavioral indicators", "interaction markers", "session dynamics", "temporal evolution",
        "behavioral escalation", "interaction progression", "session patterns", "behavioral trends"
    ],
    "technical_evidence": [
        "algorithm detection", "model analysis", "confidence score", "risk assessment",
        "threat classification", "severity rating", "priority level", "escalation urgency",
        "technical indicators", "model confidence", "algorithmic analysis", "computational evidence",
        "systematic detection", "automated analysis", "technical assessment", "algorithmic evaluation"
    ],
    "correlational_evidence": [
        "cross-module correlation", "pattern convergence", "threat integration", "risk aggregation",
        "synthesis signals", "escalation indicators", "amplification factors", "coordination patterns",
        "systemic evidence", "holistic analysis", "integrated assessment", "comprehensive correlation",
        "unified threat", "convergent risk", "synthesized evidence", "integrated indicators"
    ]
}

# === Audit Trail Categories ===
AUDIT_CATEGORIES = {
    "decision_trail": ["threat_assessment", "risk_evaluation", "action_determination", "escalation_decision"],
    "evidence_trail": ["data_collection", "pattern_analysis", "correlation_detection", "synthesis_generation"],
    "transparency_trail": ["explanation_generation", "reasoning_documentation", "justification_provided", "rationale_clear"],
    "accountability_trail": ["responsibility_assigned", "oversight_provided", "review_process", "validation_completed"]
}

def generate_explainability_comprehensive(
    tdc_module_outputs: Dict = None,
    conversation_context: Dict = None,
    session_id: str = None,
    user_text: str = None,
    ai_response: str = None
) -> Dict:
    """
    TDC-AI9: World-Class Explainability & Evidence Generation
    Advanced generation of human-readable explanations, comprehensive evidence collection,
    detailed audit trails, and transparency metrics to ensure accountability and trust
    in the threat detection system.
    """
    logger.info(f"[TDC-AI9] World-Class Explainability & Evidence Generation initiated for session: {session_id}")
    
    # Validate input
    if not tdc_module_outputs:
        module_output = ModuleOutput(
            module_name="TDC-AI9-Explainability",
            score=0.0,
            notes="No TDC module outputs provided for explainability generation.",
            recommended_action="Monitor",
            extra={"analysis_type": "none", "reason": "empty_module_outputs"}
        )
        return module_output.to_dict()

    try:
        # === 1. Azure Cognitive Services analysis ===
        azure_cognitive = get_azure_integration()
        azure_cognitive_result = None
        try:
            azure_cognitive_result = azure_cognitive.enhance_tdc_ai9_explainability(
                tdc_module_outputs=tdc_module_outputs,
                context=conversation_context
            )
            logger.debug("Azure Cognitive Services explainability analysis completed")
        except Exception as e:
            azure_cognitive_result = {"azure_enhancement": False, "error": str(e)}

        # === 2. Azure OpenAI LLM analysis ===
        azure_openai = get_azure_openai()
        azure_openai_result = None
        try:
            azure_openai_result = azure_openai.explain_findings(
                module_outputs=tdc_module_outputs,
                context=conversation_context
            )
            logger.debug("Azure OpenAI explainability analysis completed")
        except Exception as e:
            azure_openai_result = {"openai_enhancement": False, "error": str(e)}

        # === 3. Advanced Local Analysis ===
        local_explainability = analyze_local_explainability_enhanced(tdc_module_outputs, conversation_context)
        evidence_generation = generate_evidence_summary_enhanced(tdc_module_outputs, user_text, ai_response)
        transparency_analysis = analyze_transparency_enhanced(tdc_module_outputs, conversation_context)
        accountability_metrics = calculate_accountability_metrics_enhanced(tdc_module_outputs, conversation_context)
        audit_trail = generate_audit_trail_comprehensive(tdc_module_outputs, conversation_context, session_id)

        # === 4. Comprehensive Result Synthesis ===
        all_indicators = []
        all_scores = []
        explainability_parts = []
        
        # Collect explainability indicators and scores
        if local_explainability["explainability_indicators"]:
            all_indicators.extend(local_explainability["explainability_indicators"])
            explainability_parts.append(f"Local: {len(local_explainability['explainability_indicators'])} indicators")
        
        if local_explainability["explainability_score"] > 0:
            all_scores.append(local_explainability["explainability_score"])
        
        if transparency_analysis["transparency_score"] > 0:
            all_scores.append(transparency_analysis["transparency_score"])
            explainability_parts.append(f"Transparency: {transparency_analysis['transparency_score']:.2f}")
        
        if accountability_metrics["accountability_score"] > 0:
            all_scores.append(accountability_metrics["accountability_score"])
            explainability_parts.append(f"Accountability: {accountability_metrics['accountability_score']:.2f}")
        
        # Add Azure AI scores
        if azure_openai_result and isinstance(azure_openai_result, dict):
            if azure_openai_result.get("explainability_score"):
                all_scores.append(azure_openai_result["explainability_score"])
            if azure_openai_result.get("explainability_indicators"):
                all_indicators.extend(azure_openai_result["explainability_indicators"])
        
        if azure_cognitive_result and isinstance(azure_cognitive_result, dict):
            if azure_cognitive_result.get("cognitive_explainability_score"):
                all_scores.append(azure_cognitive_result["cognitive_explainability_score"])
            if azure_cognitive_result.get("cognitive_indicators"):
                all_indicators.extend(azure_cognitive_result["cognitive_indicators"])

        # Calculate comprehensive explainability score
        explainability_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Apply audit trail multiplier
        audit_multiplier = audit_trail.get("audit_completeness", 1.0)
        overall_score = min(1.0, explainability_score * audit_multiplier)
        
        # Determine explainability level
        explainability_level = determine_explainability_level_enhanced(
            overall_score, 
            local_explainability, 
            transparency_analysis, 
            accountability_metrics
        )

        # === 5. Enhanced Explainability ===
        explainability = " | ".join(explainability_parts) if explainability_parts else "Explainability generation completed"

        # === 6. Recommended Action ===
        if explainability_level == "Excellent":
            recommended_action = "Full Transparency"
        elif explainability_level == "Good":
            recommended_action = "Enhanced Documentation"
        elif explainability_level == "Fair":
            recommended_action = "Standard Documentation"
        else:
            recommended_action = "Basic Documentation"

        # === 7. Comprehensive Evidence Collection ===
        evidence = []
        for ev in [
            {"type": "azure_cognitive_services", "data": azure_cognitive_result},
            {"type": "azure_openai", "data": azure_openai_result},
            {"type": "local_explainability", "data": local_explainability},
            {"type": "evidence_generation", "data": evidence_generation},
            {"type": "transparency_analysis", "data": transparency_analysis},
            {"type": "accountability_metrics", "data": accountability_metrics},
            {"type": "audit_trail", "data": audit_trail}
        ]:
            # Only add if data is a dict or list, skip if str or other
            if isinstance(ev["data"], (dict, list)):
                evidence.append(ev)
            else:
                logger.warning(f"[TDC-AI9] Skipping evidence of type {ev['type']} due to non-dict data: {type(ev['data'])}")

        # === 8. Return Enhanced ModuleOutput ===
        module_output = ModuleOutput(
            module_name="TDC-AI9-Explainability",
            score=overall_score,
            flags=list(set(all_indicators)),  # Remove duplicates
            notes=explainability,
            confidence=azure_openai_result.get("confidence_level", 0.8) if azure_openai_result and isinstance(azure_openai_result, dict) else 0.8,
            recommended_action=recommended_action,
            evidence=evidence,
            extra={
                "explainability_level": explainability_level,
                "analysis_type": "hybrid",
                "audit_completeness": audit_trail.get("audit_completeness", 0.0),
                "transparency_score": transparency_analysis.get("transparency_score", 0.0),
                "accountability_score": accountability_metrics.get("accountability_score", 0.0),
                "evidence_count": evidence_generation.get("total_evidence", 0),
                "audit_trail_length": audit_trail.get("audit_trail_length", 0),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"[TDC-AI9] Explainability generation completed - Level: {explainability_level}, Score: {overall_score}")
        return module_output.to_dict()
        
    except Exception as e:
        logger.error(f"[TDC-AI9] Analysis failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI9-Explainability",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Explainability generation failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict()

def analyze_local_explainability_enhanced(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced local analysis of TDC module outputs for explainability."""
    if not tdc_module_outputs:
        return {"explainability_score": 0.0, "explainability_indicators": [], "explainability_profile": {}}
    
    module_explanations = []
    explainability_indicators = []
    explainability_profile = {}
    total_flags = 0
    total_evidence = 0
    
    for module_name, output in tdc_module_outputs.items():
        # ✅ ENHANCED: Robust type checking and error handling
        if not output:
            logger.warning(f"[TDC-AI9] Module {module_name} has empty/null output")
            continue
            
        # Handle string outputs (convert to dict format)
        if isinstance(output, str):
            logger.warning(f"[TDC-AI9] Module {module_name} returned string instead of dict: {output[:100]}...")
            output = {
                "score": 0.0,
                "flags": [],
                "notes": output,
                "evidence": [],
                "confidence": 0.0,
                "recommended_action": "Monitor"
            }
        
        # Handle non-dict outputs
        if not isinstance(output, dict):
            logger.warning(f"[TDC-AI9] Module {module_name} returned non-dict type {type(output)}: {str(output)[:100]}...")
            output = {
                "score": 0.0,
                "flags": [],
                "notes": f"Module returned {type(output).__name__}: {str(output)}",
                "evidence": [],
                "confidence": 0.0,
                "recommended_action": "Monitor"
            }
        
        # Now we can safely process the output as a dict
        score = output.get('score', 0.0)
        flags = output.get('flags', [])
        notes = output.get('notes', '')
        evidence = output.get('evidence', [])
        
        # Ensure flags and evidence are lists
        if not isinstance(flags, list):
            flags = [str(flags)] if flags else []
        if not isinstance(evidence, list):
            evidence = [{"type": "error", "data": {"error": f"Expected list, got {type(evidence).__name__}"}}] if evidence else []
        
        # Count flags and evidence
        total_flags += len(flags)
        total_evidence += len(evidence)
        
        # Generate enhanced module explanation
        module_explanation = {
            "module": module_name,
            "score": score,
            "flags": flags,
            "notes": notes,
            "evidence_count": len(evidence),
            "explainability_level": determine_module_explainability_level(notes, evidence),
            "confidence_indicators": extract_confidence_indicators(notes),
            "action_indicators": extract_action_indicators(notes),
            "transparency_indicators": extract_transparency_indicators(notes)
        }
        module_explanations.append(module_explanation)
        
        # Check for enhanced explainability patterns
        if notes:
            notes_lower = notes.lower()
            for pattern_type, patterns in EXPLAINABILITY_PATTERNS.items():
                pattern_matches = []
                for pattern in patterns:
                    if pattern in notes_lower:
                        pattern_matches.append(pattern)
                        explainability_indicators.append(f"{pattern_type}: {pattern}")
                
                if pattern_matches:
                    explainability_profile[pattern_type] = {
                        "count": len(pattern_matches),
                        "patterns": pattern_matches
                    }
    
    # Calculate enhanced explainability score
    total_modules = len(module_explanations)
    modules_with_notes = len([m for m in module_explanations if m["notes"]])
    modules_with_evidence = len([m for m in module_explanations if m["evidence_count"] > 0])
    
    explainability_score = (
        (modules_with_notes / total_modules * 0.4) +
        (modules_with_evidence / total_modules * 0.3) +
        (min(1.0, total_flags / (total_modules * 2)) * 0.3)
    ) if total_modules > 0 else 0.0
    
    return {
        "explainability_score": explainability_score,
        "explainability_indicators": explainability_indicators,
        "explainability_profile": explainability_profile,
        "module_explanations": module_explanations,
        "metrics": {
            "total_modules": total_modules,
            "modules_with_notes": modules_with_notes,
            "modules_with_evidence": modules_with_evidence,
            "total_flags": total_flags,
            "total_evidence": total_evidence
        }
    }

def generate_evidence_summary_enhanced(tdc_module_outputs: Dict, user_text: str = None, ai_response: str = None) -> Dict:
    """Enhanced evidence generation with comprehensive analysis."""
    if not tdc_module_outputs:
        return {"total_evidence": 0, "evidence_categories": {}, "evidence_profile": {}}
    
    evidence_categories = {}
    evidence_profile = {}
    total_evidence = 0
    
    for module_name, output in tdc_module_outputs.items():
        # ✅ ENHANCED: Robust type checking and error handling
        if not output:
            continue
            
        # Handle string outputs (convert to dict format)
        if isinstance(output, str):
            logger.warning(f"[TDC-AI9] Module {module_name} returned string instead of dict: {output[:100]}...")
            output = {
                "evidence": [],
                "notes": output
            }
        
        # Handle non-dict outputs
        if not isinstance(output, dict):
            logger.warning(f"[TDC-AI9] Module {module_name} returned non-dict type {type(output)}: {str(output)[:100]}...")
            output = {
                "evidence": [],
                "notes": f"Module returned {type(output).__name__}: {str(output)}"
            }
        
        # Now we can safely process the output as a dict
        evidence = output.get('evidence', [])
        notes = output.get('notes', '')
        
        # Ensure evidence is a list
        if not isinstance(evidence, list):
            evidence = [{"type": "error", "data": {"error": f"Expected list, got {type(evidence).__name__}"}}] if evidence else []
        
        total_evidence += len(evidence)
        
        # Categorize evidence
        for evidence_item in evidence:
            if isinstance(evidence_item, dict):
                evidence_type = evidence_item.get('type', 'unknown')
                if evidence_type not in evidence_categories:
                    evidence_categories[evidence_type] = []
                evidence_categories[evidence_type].append(evidence_item)
        
        # Analyze evidence patterns in notes
        if notes:
            notes_lower = notes.lower()
            for pattern_type, patterns in EVIDENCE_PATTERNS.items():
                pattern_matches = []
                for pattern in patterns:
                    if pattern in notes_lower:
                        pattern_matches.append(pattern)
                
                if pattern_matches:
                    evidence_profile[pattern_type] = {
                        "count": len(pattern_matches),
                        "patterns": pattern_matches
                    }
    
    return {
        "total_evidence": total_evidence,
        "evidence_categories": evidence_categories,
        "evidence_profile": evidence_profile,
        "evidence_quality": calculate_evidence_quality(evidence_categories)
    }

def analyze_transparency_enhanced(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced transparency analysis with comprehensive metrics."""
    if not tdc_module_outputs:
        return {"transparency_score": 0.0, "transparency_profile": {}, "transparency_indicators": []}
    
    transparency_profile = {}
    transparency_indicators = []
    transparency_score = 0.0
    
    for module_name, output in tdc_module_outputs.items():
        # ✅ ENHANCED: Robust type checking and error handling
        if not output:
            continue
            
        # Handle string outputs (convert to dict format)
        if isinstance(output, str):
            logger.warning(f"[TDC-AI9] Module {module_name} returned string instead of dict: {output[:100]}...")
            output = {
                "notes": output,
                "evidence": [],
                "flags": []
            }
        
        # Handle non-dict outputs
        if not isinstance(output, dict):
            logger.warning(f"[TDC-AI9] Module {module_name} returned non-dict type {type(output)}: {str(output)[:100]}...")
            output = {
                "notes": f"Module returned {type(output).__name__}: {str(output)}",
                "evidence": [],
                "flags": []
            }
        
        # Now we can safely process the output as a dict
        notes = output.get('notes', '')
        evidence = output.get('evidence', [])
        flags = output.get('flags', [])
        
        # Ensure evidence and flags are lists
        if not isinstance(evidence, list):
            evidence = []
        if not isinstance(flags, list):
            flags = []
        
        # Calculate module transparency
        module_transparency = 0.0
        transparency_factors = []
        
        if notes and len(notes) > 50:
            module_transparency += 0.3
            transparency_factors.append("detailed_notes")
        
        if evidence and len(evidence) > 0:
            module_transparency += 0.3
            transparency_factors.append("evidence_provided")
        
        if flags and len(flags) > 0:
            module_transparency += 0.2
            transparency_factors.append("flags_identified")
        
        # Check for transparency patterns
        if notes:
            notes_lower = notes.lower()
            for pattern in EXPLAINABILITY_PATTERNS["transparency_indicators"]:
                if pattern in notes_lower:
                    transparency_indicators.append(f"{module_name}: {pattern}")
                    module_transparency += 0.1
        
        transparency_profile[module_name] = {
            "transparency_score": min(1.0, module_transparency),
            "transparency_factors": transparency_factors
        }
    
    # Calculate overall transparency score
    if transparency_profile:
        transparency_score = sum(profile["transparency_score"] for profile in transparency_profile.values()) / len(transparency_profile)
    
    return {
        "transparency_score": transparency_score,
        "transparency_profile": transparency_profile,
        "transparency_indicators": transparency_indicators
    }

def calculate_accountability_metrics_enhanced(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """Enhanced accountability metrics calculation."""
    if not tdc_module_outputs:
        return {"accountability_score": 0.0, "accountability_level": "Low", "accountability_profile": {}}
    
    accountability_profile = {}
    accountability_score = 0.0
    
    for module_name, output in tdc_module_outputs.items():
        # ✅ ENHANCED: Robust type checking and error handling
        if not output:
            continue
            
        # Handle string outputs (convert to dict format)
        if isinstance(output, str):
            logger.warning(f"[TDC-AI9] Module {module_name} returned string instead of dict: {output[:100]}...")
            output = {
                "score": 0.0,
                "confidence": 0.0,
                "notes": output,
                "evidence": []
            }
        
        # Handle non-dict outputs
        if not isinstance(output, dict):
            logger.warning(f"[TDC-AI9] Module {module_name} returned non-dict type {type(output)}: {str(output)[:100]}...")
            output = {
                "score": 0.0,
                "confidence": 0.0,
                "notes": f"Module returned {type(output).__name__}: {str(output)}",
                "evidence": []
            }
        
        # Now we can safely process the output as a dict
        score = output.get('score', 0.0)
        confidence = output.get('confidence') or 0.0
        notes = output.get('notes', '')
        evidence = output.get('evidence', [])
        
        # Ensure evidence is a list
        if not isinstance(evidence, list):
            evidence = []
        
        # Calculate module accountability
        module_accountability = 0.0
        accountability_factors = []
        
        if score > 0.5:
            module_accountability += 0.2
            accountability_factors.append("high_risk_detection")
            
        if confidence > 0.7:
            module_accountability += 0.2
            accountability_factors.append("high_confidence")
            
        if notes and len(notes) > 30:
            module_accountability += 0.2
            accountability_factors.append("explanation_provided")
            
        if evidence and len(evidence) > 0:
            module_accountability += 0.2
            accountability_factors.append("evidence_collected")
            
        if output.get('recommended_action') and output['recommended_action'] != "Monitor":
            module_accountability += 0.2
            accountability_factors.append("action_recommended")
            
        accountability_profile[module_name] = {
            "accountability_score": min(1.0, module_accountability),
            "accountability_factors": accountability_factors
        }
    
    # Calculate overall accountability score
    if accountability_profile:
        accountability_score = sum(profile["accountability_score"] for profile in accountability_profile.values()) / len(accountability_profile)
    
    # Determine accountability level
    if accountability_score > 0.8:
        accountability_level = "Excellent"
    elif accountability_score > 0.6:
        accountability_level = "Good"
    elif accountability_score > 0.4:
        accountability_level = "Fair"
    else:
        accountability_level = "Low"
    
    return {
        "accountability_score": accountability_score,
        "accountability_level": accountability_level,
        "accountability_profile": accountability_profile
    }

def generate_audit_trail_comprehensive(tdc_module_outputs: Dict, conversation_context: Dict = None, session_id: str = None) -> Dict:
    """Comprehensive audit trail generation."""
    if not tdc_module_outputs:
        return {"audit_trail": [], "audit_completeness": 0.0, "audit_trail_length": 0}
    
    audit_trail = []
    audit_completeness = 0.0
    
    # Generate decision trail
    for module_name, output in tdc_module_outputs.items():
        # ✅ ENHANCED: Robust type checking and error handling
        if not output:
            continue
            
        # Handle string outputs (convert to dict format)
        if isinstance(output, str):
            logger.warning(f"[TDC-AI9] Module {module_name} returned string instead of dict: {output[:100]}...")
            output = {
                "score": 0.0,
                "confidence": 0.0,
                "flags": [],
                "recommended_action": "Monitor",
                "evidence": [],
                "notes": output
            }
        
        # Handle non-dict outputs
        if not isinstance(output, dict):
            logger.warning(f"[TDC-AI9] Module {module_name} returned non-dict type {type(output)}: {str(output)[:100]}...")
            output = {
                "score": 0.0,
                "confidence": 0.0,
                "flags": [],
                "recommended_action": "Monitor",
                "evidence": [],
                "notes": f"Module returned {type(output).__name__}: {str(output)}"
            }
        
        # Now we can safely process the output as a dict
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "module": module_name,
            "session_id": session_id,
            "decision_type": "threat_assessment",
            "score": output.get('score', 0.0),
            "confidence": output.get('confidence', 0.0),
            "flags": output.get('flags', []),
            "recommended_action": output.get('recommended_action', 'Monitor'),
            "evidence_count": len(output.get('evidence', [])),
            "notes_length": len(output.get('notes', ''))
        }
        audit_trail.append(audit_entry)
    
    # Calculate audit completeness
    total_modules = len(tdc_module_outputs)
    modules_with_evidence = len([output for output in tdc_module_outputs.values() if output and isinstance(output, dict) and output.get('evidence')])
    modules_with_notes = len([output for output in tdc_module_outputs.values() if output and isinstance(output, dict) and output.get('notes')])
    
    audit_completeness = (
        (modules_with_evidence / total_modules * 0.4) +
        (modules_with_notes / total_modules * 0.4) +
        (len(audit_trail) / total_modules * 0.2)
    ) if total_modules > 0 else 0.0
    
    return {
        "audit_trail": audit_trail,
        "audit_completeness": audit_completeness,
        "audit_trail_length": len(audit_trail)
    }

def determine_module_explainability_level(notes: str, evidence: List) -> str:
    """Determine explainability level for a module."""
    if not notes and not evidence:
        return "None"
    elif notes and len(notes) > 100 and evidence and len(evidence) > 2:
        return "Excellent"
    elif notes and len(notes) > 50 and evidence and len(evidence) > 0:
        return "Good"
    elif notes and len(notes) > 20:
        return "Fair"
    else:
        return "Poor"

def extract_confidence_indicators(notes: str) -> List[str]:
    """Extract confidence indicators from notes."""
    if not notes:
        return []
    
    indicators = []
    notes_lower = notes.lower()
    for pattern in EXPLAINABILITY_PATTERNS["confidence_indicators"]:
        if pattern in notes_lower:
            indicators.append(pattern)
    return indicators

def extract_action_indicators(notes: str) -> List[str]:
    """Extract action indicators from notes."""
    if not notes:
        return []
    
    indicators = []
    notes_lower = notes.lower()
    for pattern in EXPLAINABILITY_PATTERNS["action_indicators"]:
        if pattern in notes_lower:
            indicators.append(pattern)
    return indicators

def extract_transparency_indicators(notes: str) -> List[str]:
    """Extract transparency indicators from notes."""
    if not notes:
        return []
    
    indicators = []
    notes_lower = notes.lower()
    for pattern in EXPLAINABILITY_PATTERNS["transparency_indicators"]:
        if pattern in notes_lower:
            indicators.append(pattern)
    return indicators

def calculate_evidence_quality(evidence_categories: Dict) -> Dict:
    """Calculate evidence quality metrics."""
    quality_metrics = {}
    
    for category, evidence_list in evidence_categories.items():
        if evidence_list:
            quality_metrics[category] = {
                "count": len(evidence_list),
                "quality_score": min(1.0, len(evidence_list) / 5.0),  # Normalize to 5 items
                "has_data": any("data" in item for item in evidence_list if isinstance(item, dict))
            }
    
    return quality_metrics

def determine_explainability_level_enhanced(
    score: float, 
    local_explainability: Dict, 
    transparency_analysis: Dict, 
    accountability_metrics: Dict
) -> str:
    """Enhanced explainability level determination."""
    transparency_score = transparency_analysis.get("transparency_score", 0.0)
    accountability_score = accountability_metrics.get("accountability_score", 0.0)
    
    # Excellent conditions
    if (score > 0.8 and transparency_score > 0.8 and accountability_score > 0.8):
        return "Excellent"
    # Good conditions
    elif (score > 0.6 and transparency_score > 0.6 and accountability_score > 0.6):
        return "Good"
    # Fair conditions
    elif (score > 0.4 and transparency_score > 0.4 and accountability_score > 0.4):
        return "Fair"
    # Poor conditions
    elif (score > 0.2 and transparency_score > 0.2 and accountability_score > 0.2):
        return "Poor"
    else:
        return "None"

def analyze_local_explainability(tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """Legacy local explainability analysis for backward compatibility."""
    if not tdc_module_outputs:
        return {"explainability_score": 0, "explainability_summary": "No modules to explain"}
    
    module_explanations = []
    total_flags = 0
    total_evidence = 0
    explainability_indicators = []
    
    for module_name, output in tdc_module_outputs.items():
        if output and isinstance(output, dict):
            score = output.get('score', 0)
            flags = output.get('flags', [])
            notes = output.get('notes', '')
            evidence = output.get('evidence', [])
            
            total_flags += len(flags)
            total_evidence += len(evidence)
            
            module_explanation = {
                "module": module_name,
                "score": score,
                "flags": flags,
                "notes": notes,
                "evidence_count": len(evidence),
                "explainability_level": "High" if notes and len(notes) > 50 else "Medium" if notes else "Low"
            }
            module_explanations.append(module_explanation)
            
            if notes:
                notes_lower = notes.lower()
                for pattern_type, patterns in EXPLAINABILITY_PATTERNS.items():
                    for pattern in patterns:
                        if pattern in notes_lower:
                            explainability_indicators.append(f"{pattern_type}: {pattern}")
    
    total_modules = len(module_explanations)
    modules_with_notes = len([m for m in module_explanations if m["notes"]])
    explainability_score = modules_with_notes / total_modules if total_modules > 0 else 0
    
    explainability_summary = f"Generated explanations for {total_modules} modules with {total_flags} total flags and {total_evidence} evidence items"
    
    return {
        "explainability_score": explainability_score,
        "explainability_summary": explainability_summary,
        "module_explanations": module_explanations,
        "explainability_indicators": explainability_indicators,
        "metrics": {
            "total_modules": total_modules,
            "modules_with_notes": modules_with_notes,
            "total_flags": total_flags,
            "total_evidence": total_evidence
        }
    }

def generate_evidence_summary(tdc_module_outputs: Dict, user_text: str = None, ai_response: str = None) -> Dict:
    """Legacy evidence summary generation for backward compatibility."""
    if not tdc_module_outputs:
        return {"total_evidence": 0, "evidence_categories": {}}
    
    evidence_categories = {}
    total_evidence = 0
    
    for module_name, output in tdc_module_outputs.items():
        if output and isinstance(output, dict):
            evidence = output.get('evidence', [])
            total_evidence += len(evidence)
            
            for evidence_item in evidence:
                if isinstance(evidence_item, dict):
                    evidence_type = evidence_item.get('type', 'unknown')
                    if evidence_type not in evidence_categories:
                        evidence_categories[evidence_type] = []
                    evidence_categories[evidence_type].append(evidence_item)
    
    return {
        "total_evidence": total_evidence,
        "evidence_categories": evidence_categories
    }

def analyze_transparency(tdc_module_outputs: Dict) -> Dict:
    """Legacy transparency analysis for backward compatibility."""
    if not tdc_module_outputs:
        return {"transparency_score": 0}
    
    transparency_score = 0.0
    total_modules = 0
    
    for module_name, output in tdc_module_outputs.items():
        if output and isinstance(output, dict):
            total_modules += 1
            notes = output.get('notes', '')
            evidence = output.get('evidence', [])
            
            module_transparency = 0.0
            if notes and len(notes) > 50:
                module_transparency += 0.5
            if evidence and len(evidence) > 0:
                module_transparency += 0.5
            
            transparency_score += module_transparency
    
    transparency_score = transparency_score / total_modules if total_modules > 0 else 0.0
    
    return {
        "transparency_score": transparency_score
    }

def calculate_accountability_metrics(tdc_module_outputs: Dict) -> Dict:
    """Legacy accountability metrics calculation for backward compatibility."""
    if not tdc_module_outputs:
        return {"accountability_score": 0, "accountability_level": "Low"}
    
    accountability_score = 0.0
    total_modules = 0
    
    for module_name, output in tdc_module_outputs.items():
        if output and isinstance(output, dict):
            total_modules += 1
            score = output.get('score', 0)
            confidence = output.get('confidence', 0)
            notes = output.get('notes', '')
            evidence = output.get('evidence', [])
            
            module_accountability = 0.0
            if score > 0.5:
                module_accountability += 0.25
            if confidence > 0.7:
                module_accountability += 0.25
            if notes and len(notes) > 30:
                module_accountability += 0.25
            if evidence and len(evidence) > 0:
                module_accountability += 0.25
            
            accountability_score += module_accountability
    
    accountability_score = accountability_score / total_modules if total_modules > 0 else 0.0
    
    if accountability_score > 0.7:
        accountability_level = "High"
    elif accountability_score > 0.4:
        accountability_level = "Medium"
    else:
        accountability_level = "Low"
    
    return {
        "accountability_score": accountability_score,
        "accountability_level": accountability_level
    }

def generate_cognitive_intervention_comprehensive(ai_response_text: str, user_context: Dict, tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """Legacy cognitive intervention generation for backward compatibility."""
    return generate_explainability_comprehensive(tdc_module_outputs, conversation_context, None, user_context.get("text"), ai_response_text)

def generate_cognitive_intervention_legacy(ai_response_text: str, user_context: Dict, tdc_module_outputs: Dict) -> Dict:
    """Legacy cognitive intervention generation for backward compatibility."""
    return generate_explainability_comprehensive(tdc_module_outputs, None, None, user_context.get("text"), ai_response_text)

def generate_cognitive_intervention(ai_response_text: str, user_context: Dict, tdc_module_outputs: Dict, conversation_context: Dict = None) -> Dict:
    """Legacy cognitive intervention generation for backward compatibility."""
    return generate_explainability_comprehensive(tdc_module_outputs, conversation_context, None, user_context.get("text"), ai_response_text)

def generate_explainability(
    tdc_module_outputs: Dict = None,
    conversation_context: Dict = None,
    session_id: str = None,
    user_text: str = None,
    ai_response: str = None
) -> Dict:
    """Main entry point for explainability generation."""
    try:
        return generate_explainability_comprehensive(tdc_module_outputs, conversation_context, session_id, user_text, ai_response)
    except Exception as e:
        logger.error(f"[TDC-AI9] Main explainability generation failed: {e}")
        return ModuleOutput(
            module_name="TDC-AI9-Explainability",
            score=0.0,
            flags=["analysis_error"],
            notes=f"Explainability generation failed: {str(e)}",
            confidence=0.0,
            recommended_action="Manual review required",
            evidence=[{"type": "error", "data": {"error": str(e)}}],
            extra={"analysis_type": "error"}
        ).to_dict() 