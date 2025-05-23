import os
import json
import requests
from datetime import datetime
from collections import Counter, defaultdict
from statistics import mean

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError
from detection_engine import combined_detection
from flask_cors import CORS  # <-- CORS import

db = SQLAlchemy()

class Telemetry(db.Model):
    __tablename__ = "telemetry"
    id          = db.Column(db.Integer, primary_key=True)
    timestamp   = db.Column(db.String,  nullable=False)
    data        = db.Column(db.JSON,    nullable=False)
    enrichments = db.Column(db.JSON,    nullable=True)

def get_country_from_ip(ip):
    try:
        if ip == "127.0.0.1" or ip.startswith("192.168.") or ip.startswith("10."):
            return "Local Network"
        url = f"https://ipapi.co/{ip}/country_name/"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Unknown"
    except Exception:
        return "Unknown"

def create_app(test_config=None):
    app = Flask(__name__)

    # Enable CORS for all routes and origins globally (development/testing)
    CORS(app)

    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "SQLALCHEMY_DATABASE_URI",
            "mssql+pyodbc://catdamsadmin:Chloe310$$@catdamsadmin.database.windows.net:1433/"
            "catdamsadmin?driver=ODBC+Driver+18+for+SQL+Server"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Log the actual database URI being used (safe for debugging)
    print("USING DATABASE:", app.config["SQLALCHEMY_DATABASE_URI"])

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    schema_path = os.path.join(app.root_path, "ingest_schema.json")
    with open(schema_path) as f:
        ingest_schema = json.load(f)

    def enrich_messages(messages):
        enrichments = []
        for m in messages:
            msg_text = m.get("text", "")
            detection = combined_detection(msg_text)
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

    def _flatten_rules(rules):
        flat = []
        if isinstance(rules, str):
            flat.append(rules)
        elif isinstance(rules, dict):
            flat.append(str(rules))
        elif isinstance(rules, list):
            for item in rules:
                flat.extend(_flatten_rules(item))
        elif rules is not None:
            flat.append(str(rules))
        return flat

    @app.route("/")
    def home():
        return "Hello, CATDAMS!"

    @app.route("/health", methods=["GET"])
    def health():
        return "OK", 200

    @app.route("/ingest", methods=["POST"])
    def ingest():
        payload = request.get_json(force=True)

        # Get requester IP and add to payload inside metadata
        requester_ip = request.remote_addr

        if "metadata" not in payload or not isinstance(payload["metadata"], dict):
            payload["metadata"] = {}

        payload["metadata"]["ip_address"] = requester_ip

        # Lookup country from IP and add to payload at root level
        country = get_country_from_ip(requester_ip)
        payload["country"] = country

        try:
            validate(instance=payload, schema=ingest_schema)
        except ValidationError as e:
            return {"error": e.message}, 400

        messages = payload.get("messages", [])
        enrichment_results = enrich_messages(messages)

        ts = datetime.utcnow().isoformat() + "Z"
        entry = Telemetry(timestamp=ts, data=payload, enrichments=enrichment_results)
        try:
            db.session.add(entry)
            db.session.commit()
        except Exception as db_err:
            print("DATABASE COMMIT ERROR:", db_err)
            return {"error": str(db_err)}, 500

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

    @app.route("/dashboard")
    def dashboard():
        user_id = request.args.get('user_id', '').strip()
        min_risk = request.args.get('min_risk', type=float)
        selected_vector = request.args.get('threat_vector', '').strip()
        limit = 100

        entries = Telemetry.query.order_by(Telemetry.timestamp.desc()).limit(limit).all()

        THREAT_VECTORS = [
            "Elicitation",
            "Manipulation",
            "Influence Operation",
            "PII/PHI",
            "Credential Harvesting",
            "Cognitive Intrusion",
            "Insider Threat",
            "Misinformation/Disinformation",
            "Emotion Exploitation"
        ]

        user_counts = Counter()
        agent_counts = Counter()
        alerts_by_type = Counter()
        alerts_by_day = defaultdict(int)
        threat_vector_counts = Counter()
        risk_scores = []
        severe_alerts = 0
        alert_count = 0
        table_data = []
        geo_points = []
        country_counts = Counter()

        for e in entries:
            enrichments = e.enrichments or []
            data = e.data or {}
            detected_vectors = []
            risk_level = 0
            is_alert = False

            for enrich in enrichments:
                rules = enrich.get("rules_based", "")
                openai_data = enrich.get("openai_based", {})
                score = openai_data.get("risk_score") or openai_data.get("severity") or 0
                try:
                    score = float(score)
                except Exception:
                    score = 0
                risk_level = max(risk_level, score)

                threat_vector = openai_data.get("risk_type") or openai_data.get("threat_type")
                if isinstance(threat_vector, list):
                    detected_vectors.extend(threat_vector)
                elif threat_vector:
                    detected_vectors.append(threat_vector)

                if rules:
                    flat_rules = _flatten_rules(rules)
                    for rule in flat_rules:
                        detected_vectors.append(str(rule))

                if score and score >= 7:
                    is_alert = True
                    severe_alerts += 1

            # ---- FILTERING LOGIC ----
            if user_id and user_id.lower() not in (data.get("user_id", "") or "").lower():
                continue
            if min_risk is not None and risk_level < min_risk:
                continue
            if selected_vector and selected_vector not in detected_vectors:
                continue

            for tag in detected_vectors:
                if tag in THREAT_VECTORS:
                    threat_vector_counts[tag] += 1
                    alerts_by_type[tag] += 1

            geo = None
            for enrich in enrichments:
                geo_enrich = enrich.get("geo")
                if geo_enrich and isinstance(geo_enrich, dict):
                    geo = geo_enrich
                    break
            if not geo:
                geo = data.get("geo")
            if geo and isinstance(geo, dict) and "lat" in geo and "lon" in geo:
                geo_points.append({
                    "lat": float(geo["lat"]),
                    "lon": float(geo["lon"]),
                    "label": data.get("user_id", "Entity")
                })

            # ---- COUNTRY AGGREGATION LOGIC ----
            country = data.get("country")
            if country:
                country_counts[country] += 1

            if is_alert:
                alert_count += 1
                day = e.timestamp[:10]
                alerts_by_day[day] += 1

            if risk_level:
                risk_scores.append(risk_level)
            if data.get("user_id"):
                user_counts[data["user_id"]] += 1
            if data.get("agent_id"):
                agent_counts[data["agent_id"]] += 1

            table_data.append({
                "timestamp": e.timestamp,
                "user_id": data.get("user_id"),
                "session_id": data.get("session_id"),
                "agent_id": data.get("agent_id"),
                "messages": data.get("messages"),
                "threat_vectors": detected_vectors,  # now named for UI clarity
                "risk_level": risk_level,
                "alert": is_alert,
                "enrichments": enrichments,
            })

        total_records = len(entries)
        unique_users = len(user_counts)
        top_users = user_counts.most_common(3)
        top_agent = agent_counts.most_common(1)[0][0] if agent_counts else "N/A"
        avg_risk = round(mean(risk_scores), 2) if risk_scores else 0

        chart_alerts_data = {
            "labels": list(alerts_by_day.keys()),
            "values": list(alerts_by_day.values())
        }
        chart_threat_vector_data = {tag: threat_vector_counts.get(tag, 0) for tag in THREAT_VECTORS}

        # ---- TOP THREAT COUNTRIES LOGIC ----
        top_countries = country_counts.most_common(5)
        country_labels = [item[0] for item in top_countries]
        country_values = [item[1] for item in top_countries]

        return render_template(
            "dashboard.html",
            table_data=table_data,
            total_records=total_records,
            unique_users=unique_users,
            alert_count=alert_count,
            severe_alerts=severe_alerts,
            avg_risk=avg_risk,
            top_users=top_users,
            top_agent=top_agent,
            chart_alerts_data=chart_alerts_data,
            chart_threat_vector_data=chart_threat_vector_data,
            geo_points=geo_points,
            geo_labels=country_labels,    # now for countries!
            geo_values=country_values,    # now for countries!
            threat_vectors=THREAT_VECTORS,
            selected_vector=selected_vector,
            request=request
        )

    return app

app = create_app()
