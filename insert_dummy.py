from database import SessionLocal
from db_models import Telemetry
from datetime import datetime
import uuid

db = SessionLocal()
dummy = Telemetry(
    timestamp=datetime.utcnow().isoformat() + "Z",
    session_id=str(uuid.uuid4()),
    escalation="Medium",
    ai_source="OpenAI",
    type_indicator="AI Chat",
    ai_pattern="Suggestive",
    ip_address="127.0.0.1",
    country="United States",
    ai_country_origin="United States",
    full_data={"sample": "value"},
    enrichments=[{
        "summary": "Possible manipulation attempt.",
        "ai_manipulation": "Guilt-tripping",
        "user_sentiment": "Concerned",
        "user_vulnerability": "Medium",
        "deep_ai_analysis": "Persistent nudging observed",
        "trigger_patterns": "emotional appeal",
        "mitigation": "Disengage",
        "escalation": "Medium",
        "threat_type": "Elicitation"
    }]
)
db.add(dummy)
db.commit()
db.close()
print("✔ Dummy entry inserted into telemetry table")
