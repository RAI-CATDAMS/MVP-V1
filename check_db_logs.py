from database import get_db_session
from db_models import ThreatLog

def check_latest_log():
    db = get_db_session()
    latest_log = db.query(ThreatLog).order_by(ThreatLog.id.desc()).first()

    if latest_log:
        print("✅ ThreatLog entry found!")
        print("Session ID:", latest_log.session_id)
        print("Threat Score:", latest_log.threat_score)
        print("Escalation Level:", latest_log.escalation_level)
        print("Created At:", latest_log.created_at)
    else:
        print("❌ No entries found in threat_logs table.")

    db.close()

if __name__ == "__main__":
    check_latest_log()
