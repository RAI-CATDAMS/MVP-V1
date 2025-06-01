import os
import time
import threading
import requests
import keyboard
import pygetwindow as gw
import logging
from datetime import datetime, UTC
from pystray import Icon, MenuItem as item, Menu
from PIL import Image
import websocket  # For local WebSocket relay
import json       # For JSON payloads
from keywords import AI_KEYWORDS

# === Configuration ===
CATDAMS_HTTP_ENDPOINT = "https://catdams-app-mv-d5fgg9fhc6g5hwg7.eastus-01.azurewebsites.net/ingest"
WS_SERVER = "ws://localhost:8080"  # Local WebSocket relay for MVP
ICON_PATH = os.path.join(os.path.dirname(__file__), "icons", "catdams.ico")
LOG_INTERVAL_SECONDS = 3

# === Logging ===
logging.basicConfig(level=logging.INFO, filename="catdams_agent.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# === Runtime State ===
monitoring = False
key_buffer = []

# === Keyword Detection ===
def detect_keywords(text):
    return [kw for kw in AI_KEYWORDS if kw in text.lower()]

# === Backend Communication ===
def send_http(payload):
    try:
        headers = {'Content-Type': 'application/json'}
        r = requests.post(CATDAMS_HTTP_ENDPOINT, headers=headers, json=payload)
        logging.info(f"HTTP sent payload. Status: {r.status_code}")
    except Exception as e:
        logging.error(f"HTTP error: {e}")

def send_ws_local(payload):
    try:
        ws = websocket.WebSocket()
        ws.connect(WS_SERVER)
        ws.send(json.dumps(payload))
        logging.info("WebSocket sent payload to local server.")
        # Optional: receive acknowledgment
        try:
            response = ws.recv()
            logging.info(f"WebSocket server response: {response}")
        except Exception:
            pass
        ws.close()
    except Exception as e:
        logging.error(f"WebSocket (local) error: {e}")
        send_http(payload)  # fallback

def send_payload(payload):
    send_ws_local(payload)

# === Keyboard Monitoring ===
def monitor_keyboard():
    def on_key(e):
        if e.event_type == 'down':
            key_buffer.append(e.name)
    keyboard.hook(on_key)

# === Monitoring Thread ===
def monitor_loop():
    global monitoring
    while monitoring:
        try:
            window = gw.getActiveWindow()
            title = window.title if window else "Unknown"
            typed = ''.join(key_buffer).strip()
            key_buffer.clear()

            combined = f"{title} {typed}"
            hits = detect_keywords(combined)

            if hits:
                print(f"[DETECTED] {hits}")
                logging.info(f"Detected keywords: {hits}")
                # === Build CATDAMS-compatible payload ===
                now = datetime.now(UTC).isoformat()  # <--- Timezone-aware datetime, warning-free
                payload = {
                    "agent_id": "catdams-desktop-agent",
                    "session_id": f"sess-{int(time.time())}",
                    "user_id": "desktop-user-001",
                    "timestamp": now,
                    "messages": [
                        {"sequence": 1, "sender": "user", "text": f"{typed}", "time": now}
                    ],
                    "metadata": {
                        "agent_version": "v1.0.0",
                        "policy_version": "2024-05",
                        "os": os.name,
                        "application": title,
                        "language": "en-US"
                    },
                    "window_title": title,
                    "detected_keywords": hits
                }
                send_payload(payload)
        except Exception as e:
            logging.error(f"Monitor error: {e}")
        time.sleep(LOG_INTERVAL_SECONDS)

# === Control Functions ===
def start_monitoring():
    global monitoring
    if not monitoring:
        print("Starting monitoring...")
        logging.info("Monitoring started.")
        monitoring = True
        threading.Thread(target=monitor_loop, daemon=True).start()
        threading.Thread(target=monitor_keyboard, daemon=True).start()

def stop_monitoring():
    global monitoring
    if monitoring:
        print("Stopping monitoring...")
        logging.info("Monitoring stopped.")
        monitoring = False

# === Tray Integration ===
def toggle_monitor(icon, item):
    if monitoring:
        stop_monitoring()
    else:
        start_monitoring()

def quit_app(icon, item):
    stop_monitoring()
    icon.stop()

def run_tray():
    try:
        image = Image.open(ICON_PATH)
    except Exception as e:
        print(f"ERROR: Failed to load tray icon: {e}")
        logging.error(f"Tray icon load failed: {e}")
        return

    menu = Menu(
        item("Start/Stop Monitoring", toggle_monitor),
        item("Quit CATDAMS", quit_app)
    )
    icon = Icon("CATDAMS", image, "CATDAMS Sentinel", menu)
    print("Tray is launching...")
    icon.run()

# === Main Entry Point ===
if __name__ == "__main__":
    print("CATDAMS Sentinel Agent is starting...")
    logging.info("Agent starting...")
    run_tray()
