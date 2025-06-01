import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_cors import CORS

# Azure SQL connection string - make sure your secrets are secure!
DATABASE_URI = (
    "mssql+pyodbc://catdamsadmin:Chloe310$$@catdamsadmin.database.windows.net:1433/"
    "catdamsadmin?driver=ODBC+Driver+18+for+SQL+Server"
)

app = Flask(__name__)
CORS(app)  # Enable CORS for API & dashboard

# SQLAlchemy config
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

### =======================
###   DATABASE MODELS
### =======================

class ThreatEvent(db.Model):
    __tablename__ = 'threat_events'
    id        = db.Column(db.Integer, primary_key=True)
    time      = db.Column(db.String, nullable=False)
    type      = db.Column(db.String, nullable=False)
    severity  = db.Column(db.String, nullable=False)
    source    = db.Column(db.String, nullable=False)
    country   = db.Column(db.String, nullable=False)
    message   = db.Column(db.String, nullable=False)
    lat       = db.Column(db.Float, nullable=True)
    lon       = db.Column(db.Float, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "type": self.type,
            "severity": self.severity,
            "source": self.source,
            "country": self.country,
            "message": self.message,
            "lat": self.lat,
            "lon": self.lon
        }

### =======================
###   ROUTES & API ENDPOINTS
### =======================

@app.route("/")
def index():
    return "<h2>CATDAMS API is running. Go to /dashboard for the dashboard.</h2>"

@app.route("/dashboard")
def dashboard():
    # Only pass simple context; all live data is loaded by JS over WebSocket/API.
    return render_template("dashboard.html")

@app.route("/api/threats/recent", methods=["GET"])
def get_recent_threats():
    # Return the most recent 50 threats for dashboard initialization
    events = ThreatEvent.query.order_by(desc(ThreatEvent.id)).limit(50).all()
    return jsonify([e.as_dict() for e in reversed(events)])  # oldest first

@app.route("/api/threats/summary", methods=["GET"])
def get_threat_summary():
    # Compute stats: total, prevalent, top country, type/severity/country counts
    all_events = ThreatEvent.query.all()
    total = len(all_events)
    type_counts = {}
    severity_counts = {}
    country_counts = {}
    for e in all_events:
        type_counts[e.type] = type_counts.get(e.type, 0) + 1
        severity_counts[e.severity] = severity_counts.get(e.severity, 0) + 1
        country_counts[e.country] = country_counts.get(e.country, 0) + 1
    prevalent = max(type_counts, key=type_counts.get) if type_counts else None
    top_country = max(country_counts, key=country_counts.get) if country_counts else None
    return jsonify({
        "total": total,
        "prevalent": prevalent,
        "top_country": top_country,
        "type_counts": type_counts,
        "severity_counts": severity_counts,
        "country_counts": country_counts
    })

@app.route("/ingest", methods=["POST"])
def ingest_threat():
    # Endpoint for Sentinel agent or WebSocket server to POST new events
    try:
        data = request.get_json(force=True)
        required_fields = ["time", "type", "severity", "source", "country", "message"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        event = ThreatEvent(
            time = data.get("time", datetime.utcnow().isoformat()),
            type = data["type"],
            severity = data["severity"],
            source = data["source"],
            country = data["country"],
            message = data["message"],
            lat = float(data.get("lat", 0)) if data.get("lat") else None,
            lon = float(data.get("lon", 0)) if data.get("lon") else None
        )
        db.session.add(event)
        db.session.commit()
        # Optionally, broadcast to WebSocket (see companion ws_server)
        return jsonify({"status": "ok"}), 201
    except Exception as ex:
        print(f"[ERROR] /ingest: {ex}")
        return jsonify({"error": str(ex)}), 500

### =======================
###   INITIALIZATION
### =======================

def setup_database():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    setup_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
