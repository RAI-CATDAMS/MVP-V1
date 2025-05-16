import json
from jsonschema import validate, ValidationError
import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")

# Load ingestion schema
with open("ingest_schema.json") as f:
    ingest_schema = json.load(f)

# In-memory store for ingested records
_ingests = []

@app.route("/")
def home():
    return "Hello, CATAMS!"

@app.route("/ingest", methods=["POST"])
def ingest():
    payload = request.get_json(force=True)
    try:
        validate(instance=payload, schema=ingest_schema)
    except ValidationError as e:
        return {"error": e.message}, 400

    # If we get here, validation passed
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": payload
    }
    _ingests.append(record)
    return {"status": "accepted"}, 202

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

@app.route("/query", methods=["GET"])
def query():
    return jsonify(_ingests), 200

if __name__ == "__main__":
    app.run(debug=True)
