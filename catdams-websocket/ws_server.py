import json  # <-- This import is essential!
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

# Configure your Flask backend API endpoint for ingestion
FLASK_INGEST_ENDPOINT = "http://localhost:5000/ingest"

app = FastAPI()

# Allow all CORS origins for dev; restrict in prod!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected websocket clients
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
        # Clean up closed connections
        for connection in to_remove:
            self.disconnect(connection)

manager = ConnectionManager()

@app.get("/")
async def root():
    return HTMLResponse("<h3>CATDAMS WebSocket server is running on /ws</h3>")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(60)  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Accept POSTs from extension/agent and broadcast to dashboards, plus forward to Flask API
@app.post("/event")
async def receive_event(request: Request):
    try:
        data = await request.json()
        # Convert to string for WebSocket broadcast
        event_json = json.dumps(data)
        await manager.broadcast(event_json)
        # Forward to Flask ingest endpoint for database storage
        async with httpx.AsyncClient() as client:
            await client.post(FLASK_INGEST_ENDPOINT, json=data)
        return JSONResponse({"status": "broadcasted and forwarded"}, status_code=201)
    except Exception as e:
        print(f"[POST ERROR] {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("ws_server:app", host="0.0.0.0", port=8081, reload=True)
