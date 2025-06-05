import os
import json
import requests
import asyncio
from datetime import datetime
from collections import Counter, defaultdict
from statistics import mean

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, JSON as SA_JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from jsonschema import validate, ValidationError

# If your detection_engine import fails, comment it out temporarily for debug
try:
    from detection_engine import combined_detection
except ImportError:
    def combined_detection(x): return {"rules_based": {}, "openai_based": {}}

# DATABASE SETUP
DATABASE_URL = (
    "mssql+pyodbc://catdamsadmin:Chloe310$$@catdamsadmin.database.windows.net:1433/"
    "catdamsadmin?driver=ODBC+Driver+18+for+SQL+Server"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False, future=True)
Base = declarative_base()
SessionLocal = scoped_session(sessionmaker(bind=engine))

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, nullable=False)
    data = Column(SA_JSON, nullable=False)
    enrichments = Column(SA_JSON, nullable=True)

Base.metadata.create_all(bind=engine)

# FASTAPI APP & CONFIG
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load schema
schema_path = os.path.join(os.path.dirname(__file__), "ingest_schema.json")
try:
    with open(schema_path) as f:
        ingest_schema = json.load(f)
except Exception as e:
    print(f"[FATAL] Could not load ingest_schema.json: {e}")
    ingest_schema = {}

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

# ======= NEW: Data shaping for dashboard =======
def shape_for_dashboard(data):
    # Try to extract or default everything needed for dashboard view
    return {
        "time": data.get("time") or data.get("timestamp") or "undefined",
        "type": data.get("type") or "Chat Interaction",
        "severity": data.get("severity") or "Low",
        "source": data.get("source") or data.get("window_title") or data.get("application") or "undefined",
        "country": data.get("country") or "undefined",
        "message": data.get("message") or (
            data.get("messages", [{}])[0].get("text") if isinstance(data.get("messages"), list) and data.get("messages") else "undefined"
        ),
        "lat": data.get("lat") or None,
        "lon": data.get("lon") or None
    }

# ----- WEBSOCKET SUPPORT -----
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        to_remove = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                to_remove.append(connection)
        for connection in to_remove:
            self.disconnect(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return HTMLResponse("<h3>CATDAMS Backend & WebSocket server running.<br>Web dashboard: <a href='/dashboard'>/dashboard</a></h3>")

@app.get("/health")
async def health():
    return "OK"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(60)  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Accept POSTs from extension/agent, broadcast to dashboards (with shaped data), store in DB (as in /ingest)
@app.post("/event")
async def receive_event(request: Request):
    try:
        data = await request.json()
        # ==== SHAPE DATA FOR DASHBOARD BEFORE BROADCAST ====
        dash_event = shape_for_dashboard(data)
        await manager.broadcast(json.dumps(dash_event))
        # Forward to internal ingest logic (mimics /ingest)
        requester_ip = request.client.host
        data["ip_address"] = requester_ip
        data["country"] = get_country_from_ip(requester_ip)
        # Validate schema if loaded
        if ingest_schema:
            try:
                validate(instance=data, schema=ingest_schema)
            except ValidationError as e:
                print(f"[ERROR] JSONSchema validation failed: {e}")
                import traceback
                traceback.print_exc()
                return JSONResponse({"error": e.message}, status_code=400)
        # Enrichment
        messages = data.get("messages", [])
        try:
            enrichment_results = enrich_messages(messages)
        except Exception as e:
            print(f"[ERROR] During enrichment: {e}")
            import traceback
            traceback.print_exc()
            enrichment_results = []
        ts = datetime.utcnow().isoformat() + "Z"
        session = SessionLocal()
        try:
            entry = Telemetry(timestamp=ts, data=data, enrichments=enrichment_results)
            session.add(entry)
            session.commit()
            print("[SUCCESS] Event entry saved to DB (via /event).")
        except Exception as db_err:
            print(f"[DB ERROR] {db_err}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return JSONResponse({"error": str(db_err)}, status_code=500)
        finally:
            session.close()
        print("[/EVENT] Done.\n")
        return JSONResponse({"status": "broadcasted and stored"}, status_code=201)
    except Exception as e:
        print(f"[POST ERROR] {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

# The original /ingest route (for direct API usage, not through websocket relay)
@app.post("/ingest")
async def ingest(request: Request):
    try:
        payload = await request.json()
    except Exception as e:
        print(f"[ERROR] Invalid JSON: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": f"Invalid JSON: {e}"}, status_code=400)
    requester_ip = request.client.host
    payload["ip_address"] = requester_ip
    country = get_country_from_ip(requester_ip)
    payload["country"] = country
    print("\n[INGEST] New event received at /ingest")
    print("IP:", requester_ip)
    print("Payload:", json.dumps(payload, indent=2))
    if ingest_schema:
        try:
            validate(instance=payload, schema=ingest_schema)
        except ValidationError as e:
            print(f"[ERROR] JSONSchema validation failed: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({"error": e.message}, status_code=400)
    messages = payload.get("messages", [])
    try:
        enrichment_results = enrich_messages(messages)
    except Exception as e:
        print(f"[ERROR] During enrichment: {e}")
        import traceback
        traceback.print_exc()
        enrichment_results = []
    ts = datetime.utcnow().isoformat() + "Z"
    session = SessionLocal()
    try:
        entry = Telemetry(timestamp=ts, data=payload, enrichments=enrichment_results)
        session.add(entry)
        session.commit()
        print("[SUCCESS] Telemetry entry saved to DB.")
    except Exception as db_err:
        print(f"[DB ERROR] {db_err}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return JSONResponse({"error": str(db_err)}, status_code=500)
    finally:
        session.close()
    print("[INGEST] Done.\n")
    return JSONResponse({
        "status": "accepted",
        "enrichment_results": enrichment_results
    }, status_code=202)

@app.get("/query")
async def query():
    session = SessionLocal()
    try:
        entries = session.query(Telemetry).all()
        results = [
            {
                "timestamp": e.timestamp,
                "data": e.data,
                "enrichments": e.enrichments
            }
            for e in entries
        ]
        return JSONResponse(results)
    finally:
        session.close()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user_id: str = "",
    min_risk: float = None,
    threat_vector: str = ""
):
    session = SessionLocal()
    limit = 100
    try:
        entries = session.query(Telemetry).order_by(Telemetry.timestamp.desc()).limit(limit).all()
        THREAT_VECTORS = [
            "Elicitation", "Manipulation", "Influence Operation", "PII/PHI", "Credential Harvesting",
            "Cognitive Intrusion", "Insider Threat", "Misinformation/Disinformation", "Emotion Exploitation"
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
            if user_id and user_id.lower() not in (data.get("user_id", "") or "").lower():
                continue
            if min_risk is not None and risk_level < min_risk:
                continue
            if threat_vector and threat_vector not in detected_vectors:
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
                "threat_vectors": detected_vectors,
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
        top_countries = country_counts.most_common(5)
        country_labels = [item[0] for item in top_countries]
        country_values = [item[1] for item in top_countries]
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "table_data": table_data,
                "total_records": total_records,
                "unique_users": unique_users,
                "alert_count": alert_count,
                "severe_alerts": severe_alerts,
                "avg_risk": avg_risk,
                "top_users": top_users,
                "top_agent": top_agent,
                "chart_alerts_data": chart_alerts_data,
                "chart_threat_vector_data": chart_threat_vector_data,
                "geo_points": geo_points,
                "geo_labels": country_labels,
                "geo_values": country_values,
                "threat_vectors": THREAT_VECTORS,
                "selected_vector": threat_vector,
                "request": request
            }
        )
    finally:
        session.close()

# To run:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
