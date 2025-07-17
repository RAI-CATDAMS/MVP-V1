# db_check.py

from app import db, Telemetry, app
import json

def check_serialization():
    with app.app_context():
        any_problem = False
        for e in Telemetry.query.all():
            try:
                json.dumps(e.data)
                json.dumps(e.enrichments)
            except Exception as ex:
                any_problem = True
                print(f"Problematic entry ID {e.id}: {ex}")
        if not any_problem:
            print("All Telemetry entries are JSON serializable.")

if __name__ == "__main__":
    check_serialization()
