import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from datetime import datetime
import random

app = FastAPI()

# Allow JS access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# Serve dashboard and JS
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_alias(request: Request):
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# === WebSocket endpoint for dashboard ===
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # === Randomized fake threat payload ===
        threat = {
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "type": random.choice(["AI_Manipulation", "Insider_Threat", "Elicitation", "Data_Exfiltration"]),
            "severity": random.choice(["Low", "Medium", "High", "Critical"]),
            "source": random.choice(["Desktop Agent", "Browser Extension", "Mobile App", "AI Chatbot"]),
            "country": random.choice(["US", "RU", "CN", "IR", "DE", "IN"]),
            "message": random.choice([
                "User appears to trust AI over humans.",
                "Sensitive keywords detected.",
                "Unusual time-of-day activity.",
                "High-risk behavioral indicator observed.",
                "Multiple AI sessions initiated.",
                "System command issued to AI model."
            ]),
            "lat": random.uniform(30.0, 50.0),
            "lon": random.uniform(-120.0, -70.0),
            "synthesis": random.choice([
                "Cognitive manipulation likely occurring.",
                "User demonstrates emotional attachment to AI.",
                "Potential insider exfiltration behavior.",
                "Repeated AI dependency detected.",
                "Behavior suggests elicitation by AI agent."
            ])
        }
        await websocket.send_json(threat)
        await asyncio.sleep(3)
