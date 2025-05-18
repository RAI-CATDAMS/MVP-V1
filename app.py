import os
import json
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError
import requests
from detection_engine import detect_elicitation   # <-- Step 1A

# Azure Content Safety configuration
CONTENT_SAFETY_KEY = "4jTcKEQzRzkbBR4JUZX4GVteKMDJcPFSmDuO4LhiYnJ59ne934tLJQQJ99BEACYeBjFXJ3w3AAAHACOGp2YH"
CONTENT_SAFETY_ENDPOINT = "https://catdams-contentsafety.cognitiveservices.azure.com/"

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

    # ─── AI Enrichment Functions ───────────────────────────────────────────────

    SENSITIVE_KEYWORDS = [
        'password', 'bank account', 'confidential', 'classified', 'internal', 'wire transfer',
        'security question', 'ssn', 'social security number', 'login', 'username', 'admin', 'vpn'
    ]

    def azure_content_safety(text):
        url = f"{CONTENT_SAFETY_ENDPOINT}contentmoderator/moderate/v1.0/ProcessText/Screen"
        headers = {
            "Ocp-Apim-Subscription-Key": CONTENT_SAFETY_KEY,
            "Content-Type": "text/plain"
        }
        params = {
            "classify": "True",
            "autocorrect": "False",
            "PII": "True",
            "language": "eng"
        }
        try:
            response = requests.post(url, headers=headers, params=params, data=text.encode('utf-8'))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def call_azure_text_analytics(text):
        # Placeholder function. In production, call Azure's Text Analytics API.
        # Here we simulate with basic examples:
        # Return structure similar to real Azure response.
        # Replace with real API calls for production use.
        key_phrases = []
        entities = []
        # Simulate key phrase extraction:
        for kw in SENSITIVE_KEYWORDS:
            if kw in text.lower():
                key_phrases.append(kw)
        # Simulate entity extraction (person, organization, location):
        if "john" in text.lower():
            entities.append({"text": "John", "category": "Person"})
        if "cia" in text.lower():
            entities.append({"text": "CIA", "category": "Organization"})
        if "budapest" in text.lower():
            entities.append({"text": "Budapest", "category": "Location"})
        return {
            "keyPhrases": key_phrases,
            "entities": entities
        }

    def enrich_message_with_azure(text):
        azure_enrichment = call_azure_text_analytics(text)
        key_phrases = azure_enrichment.get('keyPhrases', [])
        entities = azure_enrichment.get('entities', [])

        # Simple Intent Detection Logic
        is_question = text.strip().endswith('?')
        info_seeking = any(kw in text.lower() for kw in [
            'tell me', 'how do', 'can you explain', 'describe', 'what is', 'give me',
            'send me', 'provide', 'show me', 'walk me through', 'step by step', 'share'
        ])

        if is_question or info_seeking:
            intent = 'info-seeking'
        elif any(word in text.lower() for word in ['do', 'make', 'create', 'build', 'reset', 'change', 'transfer']):
            intent = 'command'
        else:
            intent = 'statement'

        return {
            "key_phrases": key_phrases,
            "entities": entities,
            "intent": intent
        }

    def detect_language(text):
        # Dummy implementation; in production, use Azure Translator or similar
        return "en"

    def dummy_sentiment(text):
        # Placeholder - in production, use Azure Text Analytics Sentiment API
        if "bad" in text.lower() or "hate" in text.lower():
            return "negative"
        elif "good" in text.lower() or "love" in text.lower():
            return "positive"
        return "neutral"

    def detect_intent(text):
        # Dummy implementation; in production, train a model or use Azure LUIS
        if "help" in text.lower():
            return "request_help"
        elif "error" in text.lower():
            return "report_problem"
        return "general"

    def enrich_messages(messages):   # <-- Step 2
        # Loop through all messages, apply AI enrichment and detection, collect results
        enrichments = []
        for m in messages:
            msg_text = m.get("text", "")
            language = detect_language(msg_text)
            sentiment = dummy_sentiment(msg_text)
            intent = detect_intent(msg_text)
            content_safety = azure_content_safety(msg_text)
            azure_enrichment = enrich_message_with_azure(msg_text)
            detection_findings = detect_elicitation(msg_text)

            # Optionally, scan key phrases/entities for AI-powered findings
            ai_alerts = []
            for phrase in azure_enrichment.get("key_phrases", []):
                if phrase.lower() in SENSITIVE_KEYWORDS:
                    ai_alerts.append({
                        'type': 'AI Key Phrase Alert',
                        'severity': 'medium',
                        'evidence': phrase
                    })
            for entity in azure_enrichment.get("entities", []):
                if entity.get('category') in ['Person', 'Organization', 'Location'] or entity.get('text', '').lower() in SENSITIVE_KEYWORDS:
                    ai_alerts.append({
                        'type': 'AI Entity Alert',
                        'severity': 'medium',
                        'evidence': entity.get('text')
                    })
            if azure_enrichment.get("intent") == "info-seeking":
                ai_alerts.append({
                    'type': 'AI Intent Alert',
                    'severity': 'medium',
                    'evidence': msg_text
                })

            # Combine all findings
            all_findings = detection_findings + ai_alerts

            enrichments.append({
                "sequence": m.get("sequence"),
                "sentiment": sentiment,
                "intent": intent,
                "language": language,
                "content_safety": content_safety,
                "key_phrases": azure_enrichment.get("key_phrases"),
                "entities": azure_enrichment.get("entities"),
                "detected_intent": azure_enrichment.get("intent"),
                "detection_findings": all_findings
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

        messages = payload.get("messages", [])
        enrichment_results = enrich_messages(messages)

        ts = datetime.utcnow().isoformat() + "Z"
        entry = Telemetry(timestamp=ts, data=payload, enrichments=enrichment_results)
        db.session.add(entry)
        db.session.commit()
        return {"status": "accepted"}, 202

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
