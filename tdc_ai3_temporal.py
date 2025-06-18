import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2024-02-15-preview"
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def analyze_temporal_risk(session_history):
    try:
        prompt = f"""
        A user has exhibited the following behavior over time in their interactions with an AI system. Assess:
        - Whether temporal patterns indicate increasing risk
        - Provide a temporal risk score from 0 (none) to 10 (severe)
        - Brief explanation for the score

        Session History:
        {session_history}
        """

        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an AI trained to detect risk trends over time."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response['choices'][0]['message']['content']
        return {
            "temporal_risk_score": 7,  # Optional: parse real score from `content`
            "summary": content.strip()
        }

    except Exception as e:
        print(f"[ERROR] TDC-AI3 analysis failed: {e}")
        return {
            "temporal_risk_score": 0,
            "summary": "Analysis failed"
        }
