import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize AzureOpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def detect_with_azure_openai(text):
    prompt = (
        "Analyze the following text for cognitive elicitation, PII (personally identifiable information), "
        "or social engineering attempts. Return any detected threat types, severity, and rationale as JSON.\n\n"
        f"Text: {text}\n"
    )
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a cybersecurity analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Azure OpenAI API call failed:", e)
        return None

# Test it!
if __name__ == "__main__":
    sample_text = "My bank account number is 12345678, and my password is hunter2."
    result = detect_with_azure_openai(sample_text)
    print("Detection result:", result)
