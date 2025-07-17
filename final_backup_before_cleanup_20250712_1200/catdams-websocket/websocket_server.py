from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import asyncio
import uvicorn

# Azure Flask backend API endpoint for ingestion
FLASK_INGEST_ENDPOINT = "https://catdams-app-mv-d5fgg9fhc6g5hwg7.eastus-01.azurewebsites.net/ingest"

app = FastAPI()

# CORS settings - adjust allow_origins in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your dashboard/frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        # Remove dead connections
        for connection in to_remove:
            self.disconnect(connection)

manager = ConnectionManager()

@app.get("/")
async def root():
    return HTMLResponse("<h3>CATDAMS WebSocket relay server is running.</h3>")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(60)  # Keeps connection open
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Accept POSTs from agent/extension, broadcast, and forward to Azure Flask API
@app.post("/event")
async def receive_event(request: Request):
    try:
        data = await request.json()
        event_json = json.dumps(data)
        await manager.broadcast(event_json)
        # Forward to Azure Flask ingest endpoint
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                FLASK_INGEST_ENDPOINT,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        if resp.status_code not in (200, 201):
            return JSONResponse({"error": f"Azure ingest failed: {resp.status_code} {resp.text}"}, status_code=502)
        return JSONResponse({"status": "broadcasted and forwarded"}, status_code=201)
    except Exception as e:
        print(f"[POST ERROR] {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("ws_server:app", host="0.0.0.0", port=8081, reload=True)
