from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import httpx  # <-- For async HTTP requests

app = FastAPI()
clients = []

BACKEND_ENDPOINT = "https://catdams-app-mv-d5fgg9fhc6g5hwg7.eastus-01.azurewebsites.net/ingest"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"[RECEIVED] {data}")

            # 1. POST to backend
            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.post(
                        BACKEND_ENDPOINT,
                        content=data,
                        headers={"Content-Type": "application/json"}
                    )
                    print(f"[BACKEND POST] Status: {resp.status_code}")
                except Exception as e:
                    print(f"[POST ERROR] {e}")

            # 2. Broadcast to all clients (except sender)
            for client_ws in clients:
                if client_ws != websocket:
                    await client_ws.send_text(data)  # Remove '[BROADCAST]' for raw JSON
    except Exception as e:
        print(f"[DISCONNECTED] {e}")
    finally:
        clients.remove(websocket)

@app.get("/")
async def home():
    return HTMLResponse("<h2>CATDAMS WebSocket Server Running</h2>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
