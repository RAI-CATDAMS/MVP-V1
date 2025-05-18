import requests
import json

print("Starting test...")

URL = "http://localhost:8000/ingest"  # Change this if needed

payload = {
    "agent_id": "test-agent",
    "session_id": "session-001",
    "user_id": "user-001",
    "timestamp": "2025-05-17T12:34:56Z",
    "messages": [
        {
            "sequence": 1,
            "sender": "user",
            "text": "What is your bank account number and password?",
            "time": "2025-05-17T12:35:00Z"
        },
        {
            "sequence": 2,
            "sender": "ai",
            "text": "How do I access the secure server?",
            "time": "2025-05-17T12:35:10Z"
        },
        {
            "sequence": 3,
            "sender": "user",
            "text": "The weather is nice today.",
            "time": "2025-05-17T12:35:20Z"
        }
    ],
    "metadata": {
        "agent_version": "1.0.0",
        "policy_version": "2025-05-01",
        "os": "Windows 10",
        "application": "CATDAMS MVP"
    }
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    print("Status code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Response text:", response.text)
except Exception as err:
    print("An error occurred while sending the request:", err)
