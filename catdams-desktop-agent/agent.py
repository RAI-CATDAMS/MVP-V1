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
import json
from keywords import AI_KEYWORDS
import uuid
import getpass

# === Configuration ===
BACKEND_EVENT_ENDPOINT = "http://localhost:8000/event"  # Update to production if needed
ICON_PATH = os.path.join(os.path.dirname(__file__), "icons", "catdams.ico")
LOG_INTERVAL_SECONDS = 3

# === SESSION ID MANAGEMENT (with forced path) ===
user = getpass.getuser()
SESSION_FILE = f"C:/Users/{user}/Documents/catdams_session_id.txt"

def get_or_create_session_id():
    print(f"[DEBUG] Looking for session file at: {SESSION_FILE}")
    
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                session_id = f.read().strip()
                if session_id:
                    print(f"[DEBUG] Reusing existing session ID: {session_id}")
                    return session_id
        except Exception as read_err:
            print(f"[ERROR] Failed to read session ID file: {read_err}")
    
    # If not found or unreadable, create new session ID
    session_id = str(uuid.uuid4())
    try:
        with open(SESSION_FILE, "w") as f:
            f.write(session_id)
        print(f"[DEBUG] New session ID written: {session_id}")
    except Exception as write_err:
        print(f"[ERROR] Failed to write session ID file: {write_err}")
    
    return session_id

SESSION_ID = get_or_create_session_id()

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    filename="catdams_agent.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Runtime State ===
monitoring = False
key_buffer = []

# === AI Window/App Detection ===
def is_ai_window(title):
    return any(kw.lower() in (title or "").lower() for kw in AI_KEYWORDS)

# === Keyword Detection ===
def detect_keywords(text):
    return [kw for kw in AI_KEYWORDS if kw in text.lower()]

# === Backend Communication ===
def send_payload(payload):
    payload["session_id"] = SESSION_ID
    try:
        r = requests.post(BACKEND_EVENT_ENDPOINT, json=payload, timeout=5)
        if r.status_code in [201, 202]:
            logging.info(f"Sent payload to backend, status {r.status_code}")
        else:
            logging.error(f"Backend responded with status {r.status_code}: {r.text}")
    except Exception as e:
        logging.error(f"Failed to POST payload: {e}")

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

            if not is_ai_window(title):
                time.sleep(LOG_INTERVAL_SECONDS)
                continue

            combined = f"{title} {typed}"
            hits = detect_keywords(combined)

            if hits:
                print(f"[DETECTED] {hits}")
                logging.info(f"Detected keywords: {hits}")
                now = datetime.now(UTC).isoformat()
                payload = {
                    "time": now,
                    "type": "Chat Interaction",
                    "severity": "Low",
                    "source": title or "Desktop Agent",
                    "country": "US",
                    "message": f"{typed} | Keywords: {', '.join(hits)}",
                    "sender": "desktop"
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
    print(f"[DEBUG] CATDAMS Session ID: {SESSION_ID}")
    print("CATDAMS Sentinel Agent is starting...")
    logging.info("Agent starting...")
    run_tray()
