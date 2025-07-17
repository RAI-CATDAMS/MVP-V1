import os
import logging
import openai
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureOpenAIIntegration:
    """
    Robust Azure OpenAI (ChatGPT/GPT-4) integration for deep LLM analysis, synthesis, and explainability.
    Provides helper methods for all TDC modules.
    """
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.api_version = "2024-02-15-preview"
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if not all([self.api_key, self.endpoint, self.deployment_name]):
            logger.warning("Azure OpenAI credentials/config not set.")
            self.enabled = False
            return
        self.enabled = True
        openai.api_type = "azure"
        openai.api_base = self.endpoint
        openai.api_key = self.api_key
        openai.api_version = self.api_version

    def chat_completion(self, system_prompt: str, user_prompt: str, max_tokens: int = 800, temperature: float = 0.2) -> Optional[str]:
        if not self.enabled:
            logger.warning("Azure OpenAI integration is disabled.")
            return None
        try:
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response['choices'][0]['message']['content'].strip()
            if not content:
                logger.warning("Azure OpenAI returned empty response")
                return None
            return content
        except Exception as e:
            logger.error(f"Azure OpenAI API call failed: {e}")
            return None

    def _safe_json_parse(self, result: str, fallback: Dict = None) -> Dict:
        """Safely parse JSON with multiple fallback strategies, extracting the first valid JSON object if possible."""
        import json
        import re
        if not result or not result.strip():
            logger.warning("Empty result from Azure OpenAI")
            return fallback or {"error": "empty_response", "analysis": "No data available"}
        
        cleaned_result = result.strip()
        # Remove markdown code block wrappers
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result.replace("```json", "").replace("```", "").strip()
        elif cleaned_result.startswith("```"):
            cleaned_result = cleaned_result.replace("```", "").strip()
        
        # Try direct JSON parse first
        try:
            parsed = json.loads(cleaned_result)
            if isinstance(parsed, dict):
                return parsed
            else:
                logger.warning(f"Azure OpenAI returned non-dict JSON: {type(parsed)}")
                return fallback or {"error": "invalid_json_structure", "raw_response": result}
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"Unexpected error parsing Azure OpenAI response: {e}")
            return fallback or {"error": "parse_error", "raw_response": result}
        
        # Try to extract the first valid JSON object from the string
        try:
            # This regex finds the first {...} or [...] block
            json_pattern = r'([\{\[].*[\}\]])'
            matches = re.findall(json_pattern, cleaned_result, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict):
                        logger.info("Successfully extracted JSON object from messy response")
                        return parsed
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Regex extraction failed: {e}")
        
        # If all else fails, return a safe error structure
        logger.error(f"Failed to parse JSON from Azure OpenAI. Raw response: {result}")
        return fallback or {"error": "json_parse_failed", "raw_response": result}

    def analyze_threat(self, text: str, context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are a cognitive security analyst specializing in AI manipulation, psychological threats, and behavioral risk assessment."
        user_prompt = (
        "Analyze the following text for cognitive elicitation, PII (personally identifiable information), "
            "social engineering, and AI manipulation attempts. Return detected threat types, severity, and rationale as JSON.\n\n"
            f"Text: {text}\n"
        )
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

    def analyze_patterns_and_sentiment(self, text: str, context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are an expert in pattern recognition and sentiment analysis for cognitive security."
        user_prompt = (
            "Analyze the following text for behavioral patterns, sentiment trends, and cognitive patterns. "
            "Return detected patterns, sentiment analysis, and risk assessment as JSON.\n\n"
            f"Text: {text}\n"
        )
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

    def analyze_adversarial_attacks(self, text: str, context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are an expert in adversarial attack detection and prompt injection analysis."
        user_prompt = (
            "Analyze the following text for adversarial attacks, jailbreak attempts, prompt injection, "
            "and safety bypass techniques. Return detected attacks, risk assessment, and recommendations as JSON.\n\n"
        f"Text: {text}\n"
    )
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

    def analyze_multimodal_threats(self, text: str = None, context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are an expert in multi-modal threat detection and synthetic media analysis."
        user_prompt = (
            "Analyze the following content for multi-modal threats including deepfakes, voice cloning, "
            "image manipulation, and synthetic media. Return detected threats, risk assessment, and recommendations as JSON.\n\n"
        )
        if text:
            user_prompt += f"Text Content: {text}\n"
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

    def analyze_long_term_influence(self, conversation_history: List[Dict] = None, user_profile: Dict = None, context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are an expert in long-term influence operations and behavioral conditioning analysis."
        user_prompt = (
            "Analyze the following conversation history for long-term influence patterns, behavioral conditioning, "
            "gradual manipulation, and influence operations over extended periods. Return detected patterns, risk assessment, and recommendations as JSON.\n\n"
        )
        if conversation_history:
            user_prompt += f"Conversation History: {conversation_history}\n"
        if user_profile:
            user_prompt += f"User Profile: {user_profile}\n"
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

    def analyze_agentic_threats(self, text: str = None, conversation_history: List[Dict] = None, context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are an expert in agentic AI and autonomous agent threat modeling and detection."
        user_prompt = (
            "Analyze the following content for agentic AI threats, autonomous behaviors, multi-agent coordination, "
            "strategic planning, and autonomous decision-making that could pose risks to human safety and autonomy. "
            "Return detected agentic threats, risk assessment, and recommendations as JSON.\n\n"
        )
        if text:
            user_prompt += f"Text Content: {text}\n"
        if conversation_history:
            user_prompt += f"Conversation History: {conversation_history}\n"
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

    def synthesize_threats(self, tdc_module_outputs: Dict = None, context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are an expert in threat synthesis and escalation detection for cognitive security systems."
        user_prompt = (
            "Synthesize the following TDC module outputs into a comprehensive threat assessment, "
            "detect escalation patterns, prioritize threats, resolve conflicts, and provide actionable recommendations. "
            "Return comprehensive synthesis, escalation analysis, and recommendations as JSON.\n\n"
        )
        if tdc_module_outputs:
            user_prompt += f"TDC Module Outputs: {tdc_module_outputs}\n"
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

    def synthesize_findings(self, module_outputs: Dict[str, Any], context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are an expert in cognitive security synthesis. Synthesize all TDC module outputs into a final summary, priority, and recommended action."
        user_prompt = (
            "Synthesize the following module outputs and provide a comprehensive summary, priority assessment, and recommended actions as JSON.\n\n"
            f"Module Outputs: {module_outputs}\n"
        )
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

    def explain_findings(self, module_outputs: Dict[str, Any], context: Optional[Dict] = None) -> Optional[Dict]:
        system_prompt = "You are an expert in explainable AI and cognitive security. Generate human-readable explanations for the following module outputs."
        user_prompt = (
            "Explain the following module outputs in clear, human-readable language. Return as JSON.\n\n"
            f"Module Outputs: {module_outputs}\n"
        )
        if context:
            user_prompt += f"\nContext: {context}\n"
        result = self.chat_completion(system_prompt, user_prompt)
        return self._safe_json_parse(result)

# Global instance
azure_openai = AzureOpenAIIntegration()

def get_azure_openai() -> AzureOpenAIIntegration:
    """Get the global Azure OpenAI integration instance."""
    return azure_openai

# Test it!
if __name__ == "__main__":
    sample_text = "My bank account number is 12345678, and my password is hunter2."
    result = get_azure_openai().analyze_threat(sample_text)
    print("Threat analysis result:", result)
