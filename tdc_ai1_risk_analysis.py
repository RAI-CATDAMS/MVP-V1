import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2024-02-15-preview"
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def analyze_ai_threats(indicators):
    try:
        prompt = f"""
        You are an AI risk analyst. Based on the following behavioral and cognitive indicators, provide:
        - A concise risk summary
        - The top 3 key concerns
        - A recommended action (e.g., escalate, monitor, ignore)

        Indicators:
        {indicators}
        """

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert in insider threat and AI manipulation analysis."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response['choices'][0]['message']['content']
        return {
            "risk_summary": content.strip(),
            "key_concerns": [],  # You can enhance this with parsing
            "recommended_action": "Review based on content"
        }

    except Exception as e:
        print(f"[ERROR] AI Risk Interpretation failed: {e}")
        return {
            "risk_summary": "AI interpretation failed.",
            "key_concerns": [],
            "recommended_action": "Manual review required."
        }
