import json

from jsonschema import validate, ValidationError

import os
from flask import Flask, request
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")

# Load ingestion schema
with open("ingest_schema.json") as f:
    ingest_schema = json.load(f)

@app.route("/")
def home():
    return "Hello, CATAMS!"

@app.route("/health")

def health():

        return {"status": "ok"}, 200


@app.route("/ingest", methods=["POST"])
def ingest():
    payload = request.get_json(force=True)
    try:
        validate(instance=payload, schema=ingest_schema)
    except ValidationError as e:
        return {"error": e.message}, 400

        return {"status": "accepted"}, 202


if __name__ == "__main__":
    app.run(debug=True)

