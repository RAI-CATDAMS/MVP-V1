import os
import json
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError
from detection_engine import combined_detection   # NEW hybrid detection

# ─── Global extension and model ────────────────────────────────────────────────
db = SQLAlchemy()

class Telemetry(db.Model):
    __tablename__ = "telemetry"
    id          = db.Column(db.Integer, primary_key=True)
    timestamp   = db.Column(db.String,  nullable=False)
    data        = db.Column(db.JSON,    nullable=False)
    enrichments = db.Column(db.JSON,    nullable=True)  # New column

# ─── Application Factory ───────────────────────────────────────────────────────
def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")

    # --- Azure SQL Database config ---
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=(
            "mssql+pyodbc://catdamsadmin:Chloe310$$@catdamsadmin.database.windows.net:1433/"
            "catdamsadmin?driver=ODBC+Driver+18+for+SQL+Server"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Load the ingestion schema once
    schema_path = os.path.join(app.root_path, "ingest_schema.json")
    with open(schema_path) as f:
        ingest_schema = json.load(f)

    # ─── ENRICHMENT USING HYBRID DETECTION ────────────────────────────────────

    def enrich_messages(messages):   # <-- Uses new combined AI + rules detection!
        enrichments = []
        for m in messages:
            msg_text = m.get("text", "")
            detection = combined_detection(msg_text)

            # Parse OpenAI result as JSON if possible
            ai_result = detection["openai_based"]
            try:
                if ai_result:
                    ai_result_clean = ai_result.replace("```json", "").replace("```", "").strip()
                    ai_result_json = json.loads(ai_result_clean)
                else:
                    ai_result_json = {}
            except Exception:
                ai_result_json = {"error": "Failed to parse OpenAI result"}

            enrichments.append({
                "sequence": m.get("sequence"),
                "rules_based": detection["rules_based"],
                "openai_based": ai_result_json
            })
        return enrichments

    # ─── ROUTES ────────────────────────────────────────────────────────────────

    @app.route("/")
    def home():
        return "Hello, CATDAMS!"

    @app.route("/health", methods=["GET"])
    def health():
        return "OK", 200

    @app.route("/ingest", methods=["POST"])
    def ingest():
        payload = request.get_json(force=True)
        try:
            validate(instance=payload, schema=ingest_schema)
        except ValidationError as e:
            return {"error": e.message}, 400

        # Accept the full schema, extract messages for enrichment
        messages = payload.get("messages", [])
        enrichment_results = enrich_messages(messages)

        ts = datetime.utcnow().isoformat() + "Z"
        entry = Telemetry(timestamp=ts, data=payload, enrichments=enrichment_results)
        db.session.add(entry)
        db.session.commit()
        # --- UPDATED: return enrichment results for live feedback/testing ---
        return {
            "status": "accepted",
            "enrichment_results": enrichment_results
        }, 202

    @app.route("/query", methods=["GET"])
    def query():
        entries = Telemetry.query.all()
        return jsonify([
            {
                "timestamp": e.timestamp,
                "data": e.data,
                "enrichments": e.enrichments
            }
            for e in entries
        ]), 200

    return app

# ─── Entry Point ───────────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    print("Starting Flask app...")
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=8000)
