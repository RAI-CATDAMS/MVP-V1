import json
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")

# ─── Database setup ─────────────────────────────────────────────────────────
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///catdams.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Telemetry(db.Model):
    __tablename__ = "telemetry"
    id        = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    data      = db.Column(db.JSON,   nullable=False)

# Create the SQLite file and tables if they don’t exist
with app.app_context():
    db.create_all()

# ─── Load ingestion schema ─────────────────────────────────────────────────
with open("ingest_schema.json") as f:
    ingest_schema = json.load(f)

# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return "Welcome to the Future Home of CATDAMS!"

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

    # Store in SQLite
    ts = datetime.utcnow().isoformat() + "Z"
    entry = Telemetry(timestamp=ts, data=payload)
    db.session.add(entry)
    db.session.commit()
    return {"status": "accepted"}, 202

@app.route("/query", methods=["GET"])
def query():
    entries = Telemetry.query.all()
    result = [{"timestamp": e.timestamp, "data": e.data} for e in entries]
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)
