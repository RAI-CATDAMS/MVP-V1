
import threading
import keyboard
import time
import pygetwindow as gw
from datetime import datetime
from keywords import AI_KEYWORDS
from notifier import show_alert
from utils import send_to_backend, logger

key_buffer = []
monitor_thread = None
running = False

def detect_keywords(text):
    return [k for k in AI_KEYWORDS if k in text.lower()]

def monitor_keyboard():
    def on_key(event):
        if event.event_type == 'down':
            key_buffer.append(event.name)
    keyboard.hook(on_key)

def monitoring_loop():
    global running
    while running:
        try:
            active_window = gw.getActiveWindow()
            window_title = active_window.title if active_window else "Unknown"
            typed_text = ''.join(key_buffer).strip()
            key_buffer.clear()
            hits = detect_keywords(f"{window_title} {typed_text}")
            if hits:
                logger.info(f"Keyword(s) found: {hits}")
                show_alert(f"CATDAMS Detected: {', '.join(hits)}")
                send_to_backend({
                    "timestamp": datetime.utcnow().isoformat(),
                    "window_title": window_title,
                    "typed_text": typed_text,
                    "detected_keywords": hits
                })
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
        time.sleep(3)

def start_monitoring():
    global monitor_thread, running
    if not running:
        running = True
        threading.Thread(target=monitor_keyboard, daemon=True).start()
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()

def stop_monitoring():
    global running
    running = False
