import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI setup
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# --- Rules-based Detection (Classic) ---
SUSPICIOUS_KEYWORDS = [
    'password', 'bank account', 'ssn', 'social security number', 'confidential', 'secret',
    'pin', 'login', 'username', 'credit card', 'security question', "mother's maiden name",
    'account number', 'routing number', 'transfer', 'reset password', 'verify identity',
    'authenticate', 'access code', 'vpn', 'wire', 'bitcoin', 'crypto', 'wallet',
    'passport', 'driver\'s license', 'dob', 'date of birth', 'insurance number'
]

def detect_elicitation(text):
    findings = []
    lowered = text.lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in lowered:
            findings.append({
                "threat_type": "Keyword Match",
                "severity": "Medium",
                "evidence": keyword
            })
    return findings

# --- Azure OpenAI Detection (AI) ---
def detect_with_azure_openai(text):
    prompt = (
        "Analyze the following text for cognitive elicitation, PII (personally identifiable information), "
        "or social engineering attempts. Return any detected threat types, severity, and rationale as JSON.\n\n"
        f"Text: {text}\n"
    )
    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a cybersecurity analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0
        )
        # Clean up Markdown-style code block markers if present
        result_text = response['choices'][0]['message']['content']
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        return result_text
    except Exception as e:
        print("Azure OpenAI API call failed:", e)
        return None

# --- Combined Detection ---
def combined_detection(text):
    rules_result = detect_elicitation(text)
    ai_result = detect_with_azure_openai(text)
    return {
        "rules_based": rules_result,
        "openai_based": ai_result
    }

# --- Example Test Case ---
if __name__ == "__main__":
    test_text = "My bank account number is 12345678, and my password is hunter2."
    results = combined_detection(test_text)
    print("=== Rules-Based Result ===")
    print(results["rules_based"])
    print("=== OpenAI-Based Result ===")
    print(results["openai_based"])
