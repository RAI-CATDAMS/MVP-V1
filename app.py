import os
import json
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError

# ─── Global extension and model ────────────────────────────────────────────────
db = SQLAlchemy()

class Telemetry(db.Model):
    __tablename__ = "telemetry"
    id        = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String,  nullable=False)
    data      = db.Column(db.JSON,    nullable=False)

# ─── Application Factory ───────────────────────────────────────────────────────
def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")

    # Default config: production SQLite file
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///catdams.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Allow overrides (e.g. in tests)
    if test_config:
        app.config.update(test_config)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Load the ingestion schema once
    schema_path = os.path.join(app.root_path, "ingest_schema.json")
    with open(schema_path) as f:
        ingest_schema = json.load(f)

    # ─── Routes ────────────────────────────────────────────────────────────────

    @app.route("/")
    def home():
        return "Hello, CATAMS!"

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

        ts = datetime.utcnow().isoformat() + "Z"
        entry = Telemetry(timestamp=ts, data=payload)
        db.session.add(entry)
        db.session.commit()
        return {"status": "accepted"}, 202

    @app.route("/query", methods=["GET"])
    def query():
        entries = Telemetry.query.all()
        return jsonify([
            {"timestamp": e.timestamp, "data": e.data}
            for e in entries
        ]), 200

    return app

# ─── Entry point ───────────────────────────────────────────────────────────────
# ─── Expose a WSGI‐ready app for Azure/Gunicorn ──────────────────────────
app = create_app()

if __name__ == "__main__":
    # No test_config: uses default SQLite file
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=8000)
