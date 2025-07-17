# airm_controller.py

from get_session_history import get_session_history
from tdc_ai4_prompt_attack_detection import analyze_adversarial_attacks
import json

def run_airm_for_session(session_id, lookback_limit=10):
    """
    Runs AIRM (TDC-AI7) for a given session by pulling history and computing susceptibility.
    Returns a dict with susceptibility_score, grade, and summary.
    """
    history = get_session_history(session_id, lookback_limit=lookback_limit)

    if not history:
        print(f"\n⚠️ No session history found for session_id: {session_id}")
        return {
            "susceptibility_score": 0,
            "risk_grade": "Unknown",
            "trending_factors": [],
            "summary": f"No session data found for session_id: {session_id}. Unable to evaluate AI susceptibility."
        }

    print(f"\n✅ Retrieved {len(history)} session entries for session_id: {session_id}")
    result = analyze_adversarial_attacks(history)
    return result

# === Manual Test ===
if __name__ == "__main__":
    test_id = "a5d39560-a938-4323-bf40-b4298832ad7e"  # ✅ Confirmed valid session ID
    output = run_airm_for_session(test_id)
    print("\n🧠 AIRM Susceptibility Assessment:")
    print(json.dumps(output, indent=2))
