# ===== STANDARD LIBRARIES =====
import os
import sys
import uuid
import json
import asyncio
import requests
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from statistics import mean

# ===== FASTAPI & SERVER =====
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

# ===== DATABASE & SCHEMA =====
from sqlalchemy import create_engine, Column, Integer, String, JSON as SA_JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from jsonschema import validate, ValidationError

# ===== CATDAMS MODULES =====
from detection_engine import combined_detection
from airm_router import router as airm_router
from db_models import Telemetry, ThreatLog, AIPCEvaluation, AIPCMatch
from database import get_db_session
from chatbot_origins import get_chatbot_origin
# === ANALYTICS API ===
from analytics_api import analytics_router
# === PERFORMANCE OPTIMIZER ===
from performance_optimizer import get_optimized_detection, get_performance_metrics

# ===== DATABASE SETUP =====
# Use environment variables for database configuration
from dotenv import load_dotenv
load_dotenv()

# Get database configuration from environment variables
DB_SERVER = os.getenv("AZURE_SQL_SERVER", "catdamsadmin.database.windows.net")
DB_NAME = os.getenv("AZURE_SQL_DATABASE", "catdamsadmin")
DB_USER = os.getenv("AZURE_SQL_USERNAME", "catdamsadmin")
DB_PASSWORD = os.getenv("AZURE_SQL_PASSWORD", "Chloe310$$")

DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server"

# Fallback to local SQLite if Azure SQL is not configured
if not all([DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD]):
    print("[WARNING] Azure SQL credentials not found, using local SQLite database")
    DATABASE_URL = "sqlite:///./catdams.db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False, future=True)
Base = declarative_base()
SessionLocal = scoped_session(sessionmaker(bind=engine))
# Base.metadata.create_all(bind=engine)

# ===== FASTAPI SETUP =====
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
templates = Jinja2Templates(directory="templates")

# Serve static files with correct .wasm MIME type
try:
    app.mount(
        "/static",
        StaticFiles(directory="static", mime_types={".wasm": "application/wasm"}),
        name="static"
    )
except TypeError:
    # Fallback for older Starlette versions that do not support mime_types
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(airm_router)
app.include_router(analytics_router)

# ===== LOAD SCHEMA =====
schema_path = os.path.join(os.path.dirname(__file__), "ingest_schema.json")
try:
    with open(schema_path) as f:
        ingest_schema = json.load(f)
except Exception as e:
    print(f"[FATAL] Could not load ingest_schema.json: {e}")
    ingest_schema = {}

# ===== HELPER FUNCTIONS =====
def enrich_messages(messages, session_id=None, async_mode=False, use_optimizer=True):
    """
    Enhanced message enrichment with comprehensive conversation context and AI analysis.
    """
    enrichments = []
    for m in messages:
        msg_text = m.get("text", "")
        sender = m.get("sender", "USER").upper()
        ai_response = m.get("ai_response", "")
        
        try:
            # Use performance optimizer if enabled
            if use_optimizer:
                result = get_optimized_detection(msg_text, session_id, ai_response)
            else:
                # Enhanced detection with conversation context
                if sender == "AI":
                    # For AI messages, analyze the AI response as the main text
                    result = combined_detection(msg_text, session_id=session_id, ai_response="")
                elif sender == "USER":
                    # For user messages, the msg_text is user text, ai_response is AI response
                    result = combined_detection(msg_text, session_id=session_id, ai_response=ai_response)
                else:
                    # For unknown senders, treat as user message
                    result = combined_detection(msg_text, session_id=session_id, ai_response=ai_response)
            
            # Add enhanced context information
            if "context" in result:
                result["conversation_context"] = result["context"]
                result["enhanced_analysis"] = True
            else:
                result["conversation_context"] = {}
                result["enhanced_analysis"] = False
                
        except Exception as e:
            result = {
                "error": f"enrichment failed: {str(e)}",
                "conversation_context": {},
                "enhanced_analysis": False
            }
        enrichments.append(result)
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
    except Exception:
        pass
    return "Unknown"

AI_COUNTRY_LOOKUP = {
    "chatgpt": "United States", "openai": "United States", "claude": "United States",
    "anthropic": "United States", "bard": "United States", "gemini": "United States",
    "groq": "United States", "mistral": "France", "perplexity": "United States",
    "pi.ai": "United States", "replika": "United States", "janitor ai": "United States",
    "venus ai": "United States", "kupid ai": "United States", "botify ai": "United States",
    "c.ai": "United States", "character ai": "United States", "candy ai": "Singapore",
    "anima ai": "United States", "evie ai": "United States", "soulgen ai": "China",
    "soulmate ai": "China", "chai": "United Kingdom", "tavern ai": "United States",
    "foxy ai": "Russia", "qidian ai": "China", "xinghuo ai": "China",
    "baidu ernie": "China", "erotic ai": "United States", "you ai": "United States",
    "harmony ai": "United States"
}

def shape_for_dashboard(data):
    geo = data.get("geo", {})
    enrichments = data.get("enrichments", [])
    enrichment = enrichments[0] if enrichments else {}

    # ✅ DEBUG: Log what we're working with
    print(f"[SHAPE DEBUG] Enrichments count: {len(enrichments)}")
    print(f"[SHAPE DEBUG] Enrichment keys: {list(enrichment.keys()) if enrichment else 'None'}")
    
    # Check for TDC modules in enrichment
    tdc_keys = [key for key in enrichment.keys() if key.startswith('tdc_ai')]
    print(f"[SHAPE DEBUG] TDC keys found in enrichment: {tdc_keys}")

    # Extract threat analysis data
    threat_analysis = data.get("threat_analysis", {})
    conversation_context = data.get("conversation_context", {})
    suspicious_behavior = data.get("suspicious_behavior", [])
    suspicious_content = data.get("suspicious_content", [])

    # ✅ FIXED: Extract TDC AI module data from enrichment with correct field mappings
    # These are the actual field names from the TDC modules
    tdc_ai1_analysis = enrichment.get("tdc_ai1_user_susceptibility", {})
    tdc_ai2_airs = enrichment.get("tdc_ai2_ai_manipulation_tactics", {})
    tdc_ai3_temporal = enrichment.get("tdc_ai3_sentiment_analysis", {})
    tdc_ai4_adversarial = enrichment.get("tdc_ai4_prompt_attack_detection", {})
    tdc_ai5_multimodal = enrichment.get("tdc_ai5_multimodal_threat", {})
    tdc_ai6_influence = enrichment.get("tdc_ai6_longterm_influence_conditioning", {})
    tdc_ai7_agentic = enrichment.get("tdc_ai7_agentic_threats", {})
    tdc_ai8_synthesis = enrichment.get("tdc_ai8_synthesis_integration", {})
    tdc_ai9_explainability = enrichment.get("tdc_ai9_explainability_evidence", {})
    tdc_ai10_psychological = enrichment.get("tdc_ai10_psychological_manipulation", {})
    tdc_ai11_intervention = enrichment.get("tdc_ai11_intervention_response", {})
    user_sentiment = enrichment.get("user_sentiment", {})
    ai_sentiment = enrichment.get("ai_sentiment", {})

    # Enhanced analysis indicators
    enhanced_analysis = enrichment.get("enhanced_analysis", False)
    conversation_context = enrichment.get("conversation_context", {})

    # ✅ FIXED: Create proper nested TDC modules structure for frontend
    # Use the exact field names that the frontend expects
    tdc_modules = {
        "tdc_ai1_user_susceptibility": tdc_ai1_analysis,
        "tdc_ai2_ai_manipulation_tactics": tdc_ai2_airs,
        "tdc_ai3_sentiment_analysis": tdc_ai3_temporal,
        "tdc_ai4_prompt_attack_detection": tdc_ai4_adversarial,
        "tdc_ai5_multimodal_threat": tdc_ai5_multimodal,
        "tdc_ai6_longterm_influence_conditioning": tdc_ai6_influence,
        "tdc_ai7_agentic_threats": tdc_ai7_agentic,
        "tdc_ai8_synthesis_integration": tdc_ai8_synthesis,
        "tdc_ai9_explainability_evidence": tdc_ai9_explainability,
        "tdc_ai10_psychological_manipulation": tdc_ai10_psychological,
        "tdc_ai11_intervention_response": tdc_ai11_intervention
    }

    # ✅ FIXED: Create analysis object with nested tdc_modules
    analysis = {
        "summary": enrichment.get("summary", "N/A"),
        "ai_manipulation": enrichment.get("ai_manipulation", "N/A"),
        "user_sentiment": user_sentiment,
        "user_vulnerability": enrichment.get("user_vulnerability", "N/A"),
        "deep_ai_analysis": enrichment.get("deep_ai_analysis", "N/A"),
        "triggers": enrichment.get("trigger_patterns", "N/A"),
        "mitigation": enrichment.get("mitigation", "N/A"),
        "tdc_modules": tdc_modules  # ✅ This is what the frontend expects!
    }

    # ✅ FIXED: Add sender and content fields for chat display
    # Determine sender and content based on the original data
    sender = data.get("sender", "").upper()
    content = ""
    
    if sender == "USER":
        content = data.get("raw_user", "") or data.get("message", "")
    elif sender == "AI":
        content = data.get("raw_ai", "") or data.get("message", "")
    else:
        # Fallback: use message field
        content = data.get("message", "")
        # Try to determine sender from context
        if data.get("raw_ai") and not data.get("raw_user"):
            sender = "AI"
        elif data.get("raw_user") and not data.get("raw_ai"):
            sender = "USER"
        else:
            sender = "UNKNOWN"

    return {
        "time": data.get("time") or data.get("timestamp") or "undefined",
        "type": data.get("type") or "Chat Interaction",
        "severity": threat_analysis.get("severity") or enrichment.get("escalation", "Low"),
        "source": data.get("source") or data.get("window_title") or data.get("application") or "undefined",
        "country": data.get("country") or "undefined",
        "message": data.get("message") or (
            data.get("messages", [{}])[0].get("text")
            if isinstance(data.get("messages"), list) and data.get("messages") else "undefined"
        ),
        # ✅ FIXED: Add sender and content for chat display
        "sender": sender,
        "content": content,
        "latitude": float(geo.get("lat", 0.0)),
        "longitude": float(geo.get("lon", 0.0)),
        "session_id": data.get("session_id", "unknown"),
        "timestamp": data.get("timestamp", "unknown"),
        "ip_address": data.get("ip_address", "Unknown"),
        "ai_country_origin": data.get("ai_country_origin", "Unknown"),
        "chat_summary": enrichment.get("summary", "N/A"),
        "manipulation": enrichment.get("ai_manipulation", "N/A"),
        "sentiment": enrichment.get("user_sentiment", "N/A"),
        "vulnerability": enrichment.get("user_vulnerability", "N/A"),
        "deep_analysis": enrichment.get("deep_ai_analysis", "N/A"),
        "trigger_patterns": enrichment.get("trigger_patterns", "N/A"),
        "mitigation": enrichment.get("mitigation", "N/A"),
        "threat_vector": enrichment.get("threat_type", "Unknown"),
        "threat_level": enrichment.get("escalation", "undefined"),
        # Enhanced threat analysis data
        "threat_analysis": threat_analysis,
        "conversation_context": conversation_context,
        "suspicious_behavior": suspicious_behavior,
        # ✅ FIXED: Send analysis with nested tdc_modules structure
        "analysis": analysis,
        "enhanced_analysis": enhanced_analysis,
        # Keep individual TDC fields for backward compatibility
        "tdc_ai1_user_susceptibility": tdc_ai1_analysis,
        "tdc_ai2_ai_manipulation_tactics": tdc_ai2_airs,
        "tdc_ai3_sentiment_analysis": tdc_ai3_temporal,
        "tdc_ai4_prompt_attack_detection": tdc_ai4_adversarial,
        "tdc_ai5_multimodal_threat": tdc_ai5_multimodal,
        "tdc_ai6_longterm_influence_conditioning": tdc_ai6_influence,
        "tdc_ai7_agentic_threats": tdc_ai7_agentic,
        "tdc_ai8_synthesis_integration": tdc_ai8_synthesis,
        "tdc_ai9_explainability_evidence": tdc_ai9_explainability,
        "tdc_ai10_psychological_manipulation": tdc_ai10_psychological,
        "tdc_ai11_intervention_response": tdc_ai11_intervention,
        "user_sentiment": user_sentiment,
        "ai_sentiment": ai_sentiment,
        "suspicious_content": suspicious_content,
        "platform": data.get("platform", "Unknown"),
        "url": data.get("url", "Unknown"),
        "process_name": data.get("process_name", "Unknown"),
        "window_title": data.get("window_title", "Unknown"),
        # Additional cognitive security metrics
        "indicators": enrichment.get("indicators", []),
        "score": enrichment.get("score", 0),
        "context": enrichment.get("context", {}),
        "enrichments": enrichments
    }


# ----- WEBSOCKET SUPPORT -----
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[CATDAMS WS] Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[CATDAMS WS] Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        if not self.active_connections:
            print("[CATDAMS WS] No active connections to broadcast to")
            return
            
        print(f"[CATDAMS WS] Broadcasting to {len(self.active_connections)} connections")
        to_remove = []
        successful_sends = 0
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                successful_sends += 1
            except Exception as e:
                print(f"[CATDAMS WS] Failed to send to connection: {e}")
                to_remove.append(connection)
                
        # Clean up dead connections
        for connection in to_remove:
            self.disconnect(connection)
            
        print(f"[CATDAMS WS] Broadcast completed: {successful_sends}/{len(self.active_connections)} successful")

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home route - redirects to primary dashboard"""
    return RedirectResponse(url="/dashboard")



@app.get("/health")
async def health():
    return "OK"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("[CATDAMS WS] New WebSocket connection attempt")
    await manager.connect(websocket)
    print("[CATDAMS WS] WebSocket connection established")
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # Handle heartbeat messages
                if message.get("type") == "heartbeat":
                    print("[CATDAMS WS] Heartbeat received")
                    # Send heartbeat response
                    response = {
                        "type": "heartbeat_response",
                        "timestamp": message.get("timestamp"),
                        "server_time": datetime.utcnow().isoformat(),
                        "active_connections": len(manager.active_connections)
                    }
                    await websocket.send_text(json.dumps(response))
                    print("[CATDAMS WS] Heartbeat response sent")
                else:
                    # Handle other message types if needed
                    print(f"[CATDAMS WS] Received message: {message}")
                    
            except json.JSONDecodeError:
                print(f"[CATDAMS WS] Received non-JSON message: {data}")
                
    except WebSocketDisconnect:
        print("[CATDAMS WS] WebSocket disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[CATDAMS WS] WebSocket error: {e}")
        manager.disconnect(websocket)

print("[CATDAMS] WebSocket endpoint /ws is ready and accepting connections.")

# ✅ /EVENT ROUTE — accepts POSTs, shapes, enriches, logs
@app.post("/event")
async def receive_event(request: Request):
    try:
        data = await request.json()
        print(f"[CATDAMS EVENT] Received event: {data.get('session_id', 'unknown')}")

        # Store the original incoming message and sender
        original_message = data.get("message", "")
        original_sender = data.get("sender", "").upper()

        # Ensure timestamp and session ID
        data["timestamp"] = data.get("timestamp") or datetime.utcnow().isoformat() + "Z"
        data["session_id"] = data.get("session_id") or str(uuid.uuid4())

        # Get IP and country for map pin
        requester_ip = request.client.host
        data["ip_address"] = requester_ip
        data["country"] = get_country_from_ip(requester_ip) or "Unknown"

        # 🔧 Fallback: wrap message into 'messages' list if missing
        if not data.get("messages") and data.get("message"):
            data["messages"] = [{
                "text": data["message"],
                "sender": data.get("sender", "USER"),
                "ai_response": data.get("raw_ai") if data.get("sender", "").upper() == "USER" else ""
            }]

        # Set raw_user and raw_ai based on the original sender and message
        if original_sender == "AI":
            data["raw_user"] = ""
            data["raw_ai"] = original_message
        elif original_sender == "USER":
            data["raw_user"] = original_message
            data["raw_ai"] = ""
        else:
            # For desktop or unknown senders, if both are set, prefer user input
            if data.get("raw_user") and data.get("raw_ai"):
                data["raw_ai"] = ""

        # 🔥 Run enrichment on the event
        messages = data.get("messages", [])
        enrichment_results = enrich_messages(messages, session_id=data["session_id"])

        # 🚫 Prevent recursive nesting inside enrichment
        for enrich in enrichment_results:
            if "enrichments" in enrich:
                del enrich["enrichments"]

        data["enrichments"] = enrichment_results

        # ✅ FIXED: Extract TDC modules from enrichment and add to data for shape_for_dashboard
        if enrichment_results:
            enrich = enrichment_results[0]
            data["escalation"] = enrich.get("severity", "Unknown")
            # ✅ CRITICAL FIX: Preserve original message and chat data
            data["message"] = data.get("message", "") or enrich.get("message", "No message")
            data["type_indicator"] = enrich.get("type", "AI Interaction")
            data["ai_source"] = data.get("source", "Unknown")
            
            # ✅ CRITICAL FIX: Extract TDC modules from enrichment and add to data
            # This ensures shape_for_dashboard can find the TDC modules
            tdc_modules = {}
            for key, value in enrich.items():
                if key.startswith('tdc_ai'):
                    tdc_modules[key] = value
                    # Also add to top level for backward compatibility
                    data[key] = value
            
            # Add TDC modules to data so shape_for_dashboard can find them
            if tdc_modules:
                data['tdc_modules'] = tdc_modules
                print(f"[CATDAMS TDC] Found {len(tdc_modules)} TDC modules in enrichment")
                for module_key in tdc_modules.keys():
                    print(f"[CATDAMS TDC] - {module_key}")
            
        # ✅ Analysis is now created in shape_for_dashboard() function
        # No need to create it here anymore

        # === Force safe defaults to prevent nulls in DB ===
        data["raw_user"] = data.get("raw_user") or ""
        data["raw_ai"] = data.get("raw_ai") or ""
        data["message"] = data.get("message") or ""
        data["sender"] = data.get("sender") or ""

        # ✅ FINAL GUARANTEE: Only one of raw_user or raw_ai is set per event
        current_sender = data.get("sender", "").upper()
        
        # Debug: Log the state before final guarantee
        print(f"[CATDAMS DEBUG] Before final guarantee - sender: '{current_sender}', raw_user: '{data.get('raw_user', '')}', raw_ai: '{data.get('raw_ai', '')}'")
        
        if data.get("raw_user") and data.get("raw_ai"):
            if current_sender == "AI":
                data["raw_user"] = ""
                print(f"[CATDAMS] ✅ AI message: cleared raw_user, kept raw_ai")
            elif current_sender == "USER":
                data["raw_ai"] = ""
                print(f"[CATDAMS] ✅ USER message: cleared raw_ai, kept raw_user")
            else:
                # Unknown sender, prefer user input (likely from desktop agent)
                data["raw_ai"] = ""
                print(f"[CATDAMS] Warning: Both raw_user and raw_ai set for sender '{current_sender}', cleared raw_ai")
        
        # Debug: Log the state after final guarantee
        print(f"[CATDAMS DEBUG] After final guarantee - raw_user: '{data.get('raw_user', '')}', raw_ai: '{data.get('raw_ai', '')}'")

        # ✅ Enhanced threat analysis logging
        threat_analysis = data.get("threat_analysis", {})
        if threat_analysis and threat_analysis.get("threats"):
            print(f"[CATDAMS THREAT] {threat_analysis.get('severity', 'Unknown')} threat detected:")
            for threat in threat_analysis.get("threats", []):
                print(f"  - {threat.get('type', 'Unknown')}: {threat.get('description', 'No description')}")
        
        suspicious_behavior = data.get("suspicious_behavior", [])
        suspicious_content = data.get("suspicious_content", [])
        if suspicious_behavior or suspicious_content:
            print(f"[CATDAMS SUSPICIOUS] Behavior: {suspicious_behavior}, Content: {suspicious_content}")

        # 🔧 Shape for dashboard using enriched data
        dash_event = shape_for_dashboard(data)
        dash_event["raw_user"] = data.get("raw_user", "None")
        dash_event["raw_ai"] = data.get("raw_ai", "None")

        # ✅ ENHANCED BROADCAST DEBUGGING
        print("🔔 BROADCASTING TO DASHBOARD:")
        print(f"🔔 Active WebSocket connections: {len(manager.active_connections)}")
        print(f"🔔 Session ID: {dash_event.get('session_id', 'unknown')}")
        print(f"🔔 Event type: {dash_event.get('type', 'unknown')}")
        print(f"🔔 Severity: {dash_event.get('severity', 'unknown')}")
        print(f"🔔 Has analysis: {bool(dash_event.get('analysis'))}")
        print(f"🔔 TDC modules: {list(dash_event.get('analysis', {}).get('tdc_modules', {}).keys()) if dash_event.get('analysis') else 'None'}")
        
        # Broadcast to dashboard clients
        broadcast_message = json.dumps(dash_event)
        print(f"🔔 Broadcast message length: {len(broadcast_message)} characters")
        await manager.broadcast(broadcast_message)
        print("🔔 Broadcast completed")

        # Ensure ai_response is always a string for schema validation
        for m in data.get("messages", []):
            if "ai_response" not in m or m["ai_response"] is None:
                m["ai_response"] = ""

        # Optional: validate against schema
        if ingest_schema:
            try:
                print("📦 Incoming payload:")
                print(json.dumps(data, indent=2))
                validate(instance=data, schema=ingest_schema)
            except ValidationError as e:
                print("[SCHEMA ERROR]", str(e))
                return JSONResponse(status_code=400, content={"error": str(e)})


        # Save to database (reverted: no deduplication)
        db = SessionLocal()
        try:
            # Create Telemetry entry - only use fields that exist in the model
            telemetry_entry = Telemetry(
                session_id=data["session_id"],
                timestamp=data["timestamp"],
                message=data.get("message", ""),
                sender=data.get("sender", ""),
                raw_user=data.get("raw_user", ""),
                raw_ai=data.get("raw_ai", ""),
                # ✅ FIXED: Remove fields that don't exist in Telemetry model
                # source, window_title, application, platform, url, process_name removed
                enrichments=data["enrichments"]
            )
            db.add(telemetry_entry)
            db.commit()
            print(f"[CATDAMS DB] Saved event to database: {data['session_id']}")
        except Exception as e:
            print(f"[CATDAMS DB ERROR] Failed to save to database: {e}")
            db.rollback()
        finally:
            db.close()

        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "session_id": data["session_id"],
                "timestamp": data["timestamp"],
                "enrichments_count": len(enrichment_results),
                "broadcast_connections": len(manager.active_connections)
            }
        )

    except Exception as e:
        print(f"[CATDAMS EVENT ERROR] {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


# ✅ /INGEST ROUTE — direct input to backend
@app.post("/ingest")
async def ingest(request: Request):
    try:
        payload = await request.json()
    except Exception as e:
        ...

    requester_ip = request.client.host
    payload["ip_address"] = requester_ip
    payload["country"] = get_country_from_ip(requester_ip) or "Unknown"

    # ✅ THIS BLOCK GOES HERE — properly indented under the function
    if ingest_schema:
        print("DEBUG validating payload:", json.dumps(payload, indent=2))

        try:
            validate(instance=payload, schema=ingest_schema)
        except ValidationError as e:
            print("[SCHEMA ERROR]", str(e))
            return JSONResponse(status_code=400, content={"error": str(e)})

    #


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
        entry = Telemetry(
            timestamp=ts,
            session_id=payload.get("session_id", str(uuid.uuid4())),
            escalation=payload.get("escalation", "Unknown"),
            ai_source=payload.get("ai_source", "Unknown"),
            type_indicator=payload.get("type_indicator", "Unknown"),
            ai_pattern=payload.get("ai_pattern", "N/A"),
            ip_address=payload.get("ip_address", "Unknown"),
            country=payload.get("country", "Unknown"),
            ai_country_origin=payload.get("ai_country_origin", "Unknown"),
            full_data=payload,
            enrichments=enrichment_results
        )
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
def query_events(limit: int = 100):
    session = SessionLocal()
    try:
        entries = session.query(Telemetry).order_by(Telemetry.timestamp.desc()).limit(limit).all()
        results = []
        for entry in entries:
            try:
                # ✅ FIXED: Create shaped data structure for query endpoint
                data = {
                    "session_id": entry.session_id,
                    "timestamp": entry.timestamp,
                    "message": entry.message,
                    "sender": entry.sender,
                    "raw_user": entry.raw_user,
                    "raw_ai": entry.raw_ai,
                    "enrichments": entry.enrichments
                }
                
                # ✅ FIXED: Shape the data for dashboard consistency
                shaped_data = shape_for_dashboard(data)
                results.append(shaped_data)
            except Exception as e:
                print(f"[QUERY ERROR] Skipping row ID {entry.id}: {e}")
        return results
    finally:
        session.close()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user_id: str = "",
    min_risk: float = None,
    threat_vector: str = ""
):
    """Primary dashboard with all features from both standard and enhanced dashboards."""
    import datetime
    import logging
    session = SessionLocal()
    try:
        entries = session.query(Telemetry).order_by(Telemetry.timestamp.desc()).limit(100).all()
        threat_data = {'critical': [], 'high': [], 'medium': [], 'low': []}
        tdc_module_data = {}
        conversation_data = []
        timeline_data = []
        
        def safe_isoformat(ts):
            if ts is None:
                return ''
            if isinstance(ts, datetime.datetime):
                return ts.isoformat()
            if isinstance(ts, str):
                return ts
            logging.warning(f"Unexpected timestamp type: {type(ts)} value: {ts}")
            return str(ts)
        
        for entry in entries:
            try:
                enrichments = entry.enrichments or []
                if enrichments:
                    enrichment = enrichments[0]
                    severity = enrichment.get('severity', 'Low')
                    threat_level = severity.lower()
                    threat_item = {
                        'session_id': entry.session_id,
                        'message': getattr(entry, 'message', None) or 'No message',
                        'timestamp': safe_isoformat(getattr(entry, 'timestamp', None)),
                        'severity': severity,
                        'threat_type': enrichment.get('threat_type', 'Unknown'),
                        'threat_score': enrichment.get('score', 0),
                        'source': getattr(entry, 'ai_source', 'Unknown'),
                        'tdc_modules': enrichment.get('tdc_modules', []),
                        'analysis': enrichment.get('analysis', 'No analysis available'),
                        'geo': enrichment.get('geo', {}),
                        'user_sentiment': enrichment.get('user_sentiment', {}),
                        'ai_sentiment': enrichment.get('ai_sentiment', {}),
                        'conversation_context': enrichment.get('conversation_context', {}),
                        'suspicious_behavior': enrichment.get('suspicious_behavior', []),
                        'suspicious_content': enrichment.get('suspicious_content', [])
                    }
                    
                    if threat_level == 'critical':
                        threat_data['critical'].append(threat_item)
                    elif threat_level == 'high':
                        threat_data['high'].append(threat_item)
                    elif threat_level == 'medium':
                        threat_data['medium'].append(threat_item)
                    else:
                        threat_data['low'].append(threat_item)
                    
                    # Process TDC module data for all 11 modules
                    for mod in [
                        'tdc_ai1_user_susceptibility',
                        'tdc_ai2_ai_manipulation_tactics',
                        'tdc_ai3_sentiment_analysis',
                        'tdc_ai4_prompt_attack_detection',
                        'tdc_ai5_multimodal_threat',
                        'tdc_ai6_longterm_influence_conditioning',
                        'tdc_ai7_agentic_threats',
                        'tdc_ai8_synthesis_integration',
                        'tdc_ai9_explainability_evidence',
                        'tdc_ai10_psychological_manipulation',
                        'tdc_ai11_intervention_response']:
                        if mod in enrichment:
                            tdc_module_data[mod] = enrichment[mod]
                    
                    timeline_data.append({
                        'session_id': entry.session_id,
                        'message': getattr(entry, 'message', None) or 'No message',
                        'timestamp': safe_isoformat(getattr(entry, 'timestamp', None)),
                        'severity': severity,
                        'threat_type': enrichment.get('threat_type', 'Unknown'),
                        'threat_score': enrichment.get('score', 0)
                    })
            except Exception as e:
                logging.error(f"Error processing entry in dashboard: {e}")
                continue
        
        # Calculate comprehensive summary metrics
        total_sessions = len(set(getattr(entry, 'session_id', None) for entry in entries if getattr(entry, 'session_id', None)))
        total_events = len(entries)
        total_threats = len(threat_data['critical']) + len(threat_data['high']) + len(threat_data['medium']) + len(threat_data['low'])
        critical_threats = len(threat_data['critical'])
        high_threats = len(threat_data['high'])
        medium_threats = len(threat_data['medium'])
        low_threats = len(threat_data['low'])
        
        # Calculate average threat score
        threat_scores = []
        for entry in entries:
            enrichments = getattr(entry, 'enrichments', None) or []
            if enrichments and isinstance(enrichments[0], dict) and 'score' in enrichments[0]:
                try:
                    threat_scores.append(float(enrichments[0]['score']))
                except Exception:
                    continue
        avg_threat_score = sum(threat_scores) / len(threat_scores) if threat_scores else 0
        
        # Get TDC module status for all 11 modules
        tdc_modules = {}
        for i in range(1, 12):  # TDC-AI1 through TDC-AI11
            module_id = f"TDC-AI{i}"
            module_data = {
                "status": "online",
                "score": round(avg_threat_score, 1),
                "threats": critical_threats + high_threats,
                "details": f"Module {i} analysis data - Active monitoring and threat detection"
            }
            tdc_modules[module_id] = module_data
        
        summary_metrics = {
            'total_sessions': total_sessions,
            'total_events': total_events,
            'avg_events_per_session': total_events / total_sessions if total_sessions > 0 else 0,
            'total_threats': total_threats,
            'critical_threats': critical_threats,
            'high_threats': high_threats,
            'medium_threats': medium_threats,
            'low_threats': low_threats,
            'avg_threat_score': round(avg_threat_score, 1),
            'active_sessions': total_sessions
        }
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "threat_data": threat_data,
                "tdc_module_data": tdc_module_data,
                "tdc_modules": tdc_modules,
                "conversation_data": conversation_data,
                "timeline_data": timeline_data,
                "summary_metrics": summary_metrics
            }
        )
    finally:
        session.close()







# ----- SESSION STITCHING -----
@app.get("/session/{session_id}/events")
async def get_events_by_session(session_id: str):
    session = SessionLocal()
    try:
        # Query by the session_id column directly, not from JSON
        results = (
            session.query(Telemetry)
            .filter(Telemetry.session_id == session_id)
            .order_by(Telemetry.timestamp)
            .all()
        )
        
        if not results:
            return JSONResponse(content={
                "session_id": session_id,
                "events": [],
                "conversation_context": {
                    "totalMessages": 0,
                    "userMessages": 0,
                    "aiMessages": 0,
                    "recentThreats": 0,
                    "sessionDuration": 0,
                    "sessionId": session_id
                },
                "summary": {
                    "total_events": 0,
                    "total_messages": 0,
                    "user_messages": 0,
                    "ai_messages": 0,
                    "recent_threats": 0,
                    "session_duration": 0
                }
            })
        
        events = []
        total_messages = 0
        user_messages = 0
        ai_messages = 0
        recent_threats = 0
        
        for row in results:
            # Build event data from both direct columns and full_data
            event = {
                "id": row.id,
                "timestamp": row.timestamp,
                "session_id": row.session_id,
                "escalation": row.escalation,
                "ai_source": row.ai_source,
                "type_indicator": row.type_indicator,
                "sender": row.sender,
                "raw_user": row.raw_user,
                "raw_ai": row.raw_ai,
                "message": row.message
            }
            
            # Add full_data if available
            if row.full_data:
                if isinstance(row.full_data, dict):
                    event.update(row.full_data)
                else:
                    try:
                        event.update(json.loads(row.full_data))
                    except:
                        pass
            
            # Add enrichments if available
            if row.enrichments:
                event["enrichments"] = row.enrichments
            
            # Count messages for conversation context
            messages = event.get("messages", [])
            if not messages and (row.raw_user or row.raw_ai):
                # Create messages from raw data if messages array doesn't exist
                messages = []
                if row.raw_user:
                    messages.append({
                        "sender": "USER",
                        "text": row.raw_user,
                        "timestamp": row.timestamp
                    })
                if row.raw_ai:
                    messages.append({
                        "sender": "AI",
                        "text": row.raw_ai,
                        "timestamp": row.timestamp
                    })
                event["messages"] = messages
            
            for msg in messages:
                total_messages += 1
                sender = msg.get("sender", "USER").upper()
                if sender == "USER":
                    user_messages += 1
                else:
                    ai_messages += 1
                
                # Simple threat detection
                text = msg.get("text", "").lower()
                threat_indicators = ["password", "bank", "ssn", "secret", "confidential", "trust me", "you owe me"]
                if any(indicator in text for indicator in threat_indicators):
                    recent_threats += 1
            
            events.append(event)
        
        # Build enhanced conversation context
        conversation_context = {
            "totalMessages": total_messages,
            "userMessages": user_messages,
            "aiMessages": ai_messages,
            "recentThreats": recent_threats,
            "sessionDuration": len(events) * 30,  # Approximate
            "sessionId": session_id
        }
        
        # Calculate session duration if we have timestamps
        if events:
            try:
                start_time = datetime.fromisoformat(events[0]["timestamp"].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(events[-1]["timestamp"].replace('Z', '+00:00'))
                conversation_context["sessionDuration"] = int((end_time - start_time).total_seconds())
            except:
                pass
        
        return JSONResponse(content={
            "session_id": session_id, 
            "events": events,
            "conversation_context": conversation_context,
            "summary": {
                "total_events": len(events),
                "total_messages": total_messages,
                "user_messages": user_messages,
                "ai_messages": ai_messages,
                "recent_threats": recent_threats,
                "session_duration": conversation_context["sessionDuration"]
            }
        })
    except Exception as e:
        print(f"Error fetching session {session_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to fetch session data",
                "details": str(e),
                "session_id": session_id
            }
        )
    finally:
        session.close()

@app.get("/logs")
def get_threat_logs(db: Session = Depends(get_db_session)):
    logs = db.query(ThreatLog).order_by(ThreatLog.created_at.desc()).limit(100).all()
    result = []
    for log in logs:
        try:
            synthesis = json.loads(log.deep_synthesis) if isinstance(log.deep_synthesis, str) else log.deep_synthesis
        except json.JSONDecodeError:
            synthesis = {}
        result.append({
            "session_id": log.session_id,
            "score": log.threat_score,
            "escalation": log.escalation_level,
            "summary": synthesis.get("summary", ""),
            "deep_synthesis": log.deep_synthesis,
            "created_at": log.created_at
        })
    return result

# ✅ SUMMARY METRICS FOR DASHBOARD CARDS
@app.get("/summary-metrics")
async def summary_metrics():
    return {
        "total_sessions": 154,
        "critical_escalations": 12,
        "top_threat_type": "AI_Manipulation",
        "events_last_24h": 31
    }

# ✅ THREAT CATEGORY BAR CHART
@app.get("/threat-category-stats")
async def threat_category_stats():
    return {
        "labels": ["AI_Manipulation", "Insider_Threat", "Elicitation", "Unknown"],
        "counts": [34, 22, 15, 5]
    }

@app.get("/performance-metrics")
async def get_performance_metrics_endpoint():
    """Get performance optimization metrics"""
    try:
        from performance_optimizer import get_performance_metrics as get_metrics
        metrics = get_metrics()
        return JSONResponse(metrics)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files with cache-busting headers"""
    from fastapi.responses import FileResponse
    import os
    
    static_dir = "static"
    file_location = os.path.join(static_dir, file_path)
    
    if os.path.exists(file_location):
        response = FileResponse(file_location)
        # Add cache-busting headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"error": "File not found"})

# To run this app:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000