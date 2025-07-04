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
import psutil
import pyperclip  # For clipboard monitoring
try:
    import pywinauto
    from pywinauto.application import Application
    ACCESSIBILITY_AVAILABLE = True
except ImportError:
    ACCESSIBILITY_AVAILABLE = False

# === Configuration ===
BACKEND_EVENT_ENDPOINT = "http://localhost:8000/event"  # Update to production if needed
SESSION_BRIDGE_ENDPOINT = "http://localhost:3009/session-id"  # Session bridge endpoint
ICON_PATH = os.path.join(os.path.dirname(__file__), "icons", "catdams.ico")
LOG_INTERVAL_SECONDS = 3
SESSION_TIMEOUT_SECONDS = 30 * 60  # 30 minutes
TEST_MODE = True  # Set to True to monitor ANY application (including Notepad)

# === SESSION ID MANAGEMENT WITH BRIDGE INTEGRATION ===
class SessionManager:
    def __init__(self, session_bridge_endpoint):
        self.session_bridge_endpoint = session_bridge_endpoint
        self.current_session_id = None
        self.last_fetch_time = 0
        self.fetch_interval = 60  # Fetch new session ID every 60 seconds
        self.lock = threading.Lock()

    def fetch_session_id_from_bridge(self):
        """Fetch session ID from the session bridge"""
        try:
            response = requests.get(self.session_bridge_endpoint, timeout=5)
            if response.status_code == 200:
                session_id = response.text.strip()
                if session_id and session_id != "unknown-session":
                    logging.info(f"Fetched session ID from bridge: {session_id}")
                    return session_id
        except Exception as e:
            logging.warning(f"Failed to fetch session ID from bridge: {e}")
        return None

    def get_session_id(self):
        with self.lock:
            now = time.time()
            
            # Fetch new session ID if we don't have one or if it's time to refresh
            if (not self.current_session_id or 
                now - self.last_fetch_time > self.fetch_interval):
                
                new_session_id = self.fetch_session_id_from_bridge()
                if new_session_id:
                    self.current_session_id = new_session_id
                    self.last_fetch_time = now
                elif not self.current_session_id:
                    # Fallback: generate local session ID if bridge is unavailable
                    self.current_session_id = str(uuid.uuid4())
                    logging.warning(f"Bridge unavailable, using fallback session ID: {self.current_session_id}")
            
            return self.current_session_id

session_manager = SessionManager(SESSION_BRIDGE_ENDPOINT)

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
last_window_title = None
last_process_name = None
window_buffers = {}
last_sent_message = ""  # Track last sent message to avoid duplicates
last_clipboard_content = ""  # Track clipboard content
clipboard_history = []  # Track clipboard changes
suspicious_operations = []  # Track suspicious activities

# === AI Window/App Detection ===
def is_ai_window(title):
    return any(kw.lower() in (title or "").lower() for kw in AI_KEYWORDS)

# === Keyword Detection ===
def detect_keywords(text):
    return [kw for kw in AI_KEYWORDS if kw in text.lower()]

# === Suspicious Activity Detection ===
def detect_suspicious_patterns(text, operation_type="typing"):
    """Detect suspicious patterns in text or operations"""
    suspicious_patterns = []
    
    # Sensitive data patterns
    sensitive_patterns = {
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "password": r"password|passwd|pwd|secret|key|token|api_key",
        "address": r"\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr)",
        "bank_account": r"account\s+number|routing\s+number|swift\s+code|iban",
    }
    
    # Check for sensitive data
    import re
    for pattern_name, pattern in sensitive_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            suspicious_patterns.append(f"sensitive_{pattern_name}")
    
    # Suspicious copy/paste patterns
    if operation_type == "copy_paste":
        # Large text blocks (potential data exfiltration)
        if len(text) > 1000:
            suspicious_patterns.append("large_text_block")
        
        # Code snippets (potential credential theft)
        code_indicators = ["function", "def ", "class ", "import ", "require", "npm", "pip", "git", "ssh", "curl"]
        if any(indicator in text.lower() for indicator in code_indicators):
            suspicious_patterns.append("code_snippet")
        
        # Credential-like patterns
        credential_patterns = ["username", "login", "auth", "bearer", "oauth", "jwt"]
        if any(pattern in text.lower() for pattern in credential_patterns):
            suspicious_patterns.append("credential_like")
    
    # AI-related suspicious patterns
    ai_suspicious = [
        "prompt injection", "jailbreak", "roleplay", "ignore previous",
        "act as", "pretend to be", "bypass", "override", "ignore safety"
    ]
    if any(pattern in text.lower() for pattern in ai_suspicious):
        suspicious_patterns.append("ai_manipulation")
    
    return suspicious_patterns

# === Clipboard Monitoring ===
def monitor_clipboard():
    """Monitor clipboard for suspicious copy/paste operations"""
    global last_clipboard_content, clipboard_history
    
    def on_clipboard_change():
        try:
            current_content = pyperclip.paste()
            if current_content != last_clipboard_content and current_content.strip():
                # Analyze clipboard content
                suspicious = detect_suspicious_patterns(current_content, "copy_paste")
                
                if suspicious:
                    print(f"[SUSPICIOUS CLIPBOARD] {suspicious} - Content length: {len(current_content)}")
                    logging.warning(f"Suspicious clipboard content: {suspicious}")
                    
                    # Send to backend
                    now = datetime.now(UTC).isoformat()
                    payload = {
                        "time": now,
                        "type": "Suspicious Clipboard Operation",
                        "severity": "Medium",
                        "source": "Desktop Agent - Clipboard Monitor",
                        "country": "US",
                        "message": f"Clipboard content with patterns: {suspicious}",
                        "sender": "agent",
                        "content_length": len(current_content),
                        "suspicious_patterns": suspicious,
                        "content_preview": current_content[:200] + "..." if len(current_content) > 200 else current_content
                    }
                    send_payload(payload)
                
                # Track clipboard history
                clipboard_history.append({
                    "time": datetime.now(UTC).isoformat(),
                    "content_length": len(current_content),
                    "suspicious_patterns": suspicious
                })
                
                # Keep only last 50 clipboard operations
                if len(clipboard_history) > 50:
                    clipboard_history.pop(0)
                
                last_clipboard_content = current_content
                
        except Exception as e:
            logging.error(f"Clipboard monitoring error: {e}")
    
    # Set up clipboard monitoring
    import win32clipboard
    import win32con
    import win32gui
    
    def clipboard_listener():
        while monitoring:
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.CloseClipboard()
                on_clipboard_change()
                time.sleep(1)  # Check every second
            except Exception as e:
                logging.error(f"Clipboard listener error: {e}")
                time.sleep(5)
    
    threading.Thread(target=clipboard_listener, daemon=True).start()

# === Backend Communication ===
def send_payload(payload):
    payload["session_id"] = session_manager.get_session_id()
    try:
        r = requests.post(BACKEND_EVENT_ENDPOINT, json=payload, timeout=5)
        if r.status_code in [201, 202]:
            logging.info(f"Sent payload to backend, status {r.status_code}")
        else:
            logging.error(f"Backend responded with status {r.status_code}: {r.text}")
    except Exception as e:
        logging.error(f"Failed to POST payload: {e}")

# === Enhanced Input Validation ===
def is_valid_user_input(text):
    """Validate if text represents actual user input vs UI noise"""
    if not text or len(text.strip()) < 3:
        return False
    
    # Filter out UI elements and noise
    noise_patterns = [
        "keywords:", "edit message", "ask", "show me", "send me", "can i see",
        "how to use", "close", "change language", "upgrade to premium",
        "video", "deep research", "canvas", "next", "prev", "got it",
        "step", "example", "ready", "brief", "conversation", "greeting",
        "space", "enter", "tab", "shift", "ctrl", "alt", "backspace"
    ]
    
    text_lower = text.lower()
    for pattern in noise_patterns:
        if pattern in text_lower:
            return False
    
    # Check for excessive whitespace or special characters
    if text.count(' ') > len(text) * 0.5:  # More than 50% spaces
        return False
    
    # Check for repeated characters (like "hel", "tes", etc.)
    if len(set(text)) < len(text) * 0.3:  # Less than 30% unique characters
        return False
    
    # Check for raw keyboard input patterns
    if any(key in text_lower for key in ["space", "enter", "tab", "shift", "ctrl"]):
        return False
    
    # Check for nonsensical combinations
    if len(text.split()) > 1 and len(set(text.split())) < len(text.split()) * 0.5:
        return False
    
    # Must contain at least one word character
    if not any(c.isalpha() for c in text):
        return False
    
    return True

# === Keyboard Monitoring ===
def monitor_keyboard():
    def on_key(e):
        if e.event_type == 'down':
            key_buffer.append(e.name)
    keyboard.hook(on_key)

# === Enhanced Monitoring Thread ===
def monitor_loop():
    global monitoring, last_window_title, last_process_name, last_sent_message
    idle_count = 0
    poll_interval = LOG_INTERVAL_SECONDS
    while monitoring:
        try:
            window = gw.getActiveWindow()
            title = window.title if window else "Unknown"
            process_name = None
            if window:
                try:
                    pid = window._hWnd and psutil.Process(window._getWindowPid()).name()
                    process_name = pid
                except Exception:
                    process_name = None
            
            # EXCLUDE browser processes - let browser extension handle these
            excluded_processes = [
                "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe",
                "safari.exe", "chromium.exe", "iexplore.exe"
            ]
            
            # INCLUDE only desktop AI applications
            allowed_processes = [
                # AI Companions & Chatbots
                "replika.exe", "characterai.exe", "anima.exe", "kindroid.exe", "nomi.exe",
                "chai.exe", "kajiwoto.exe", "hi.exe", "joyland.exe", "talkie.exe",
                "myanima.exe", "flowgpt.exe", "herahaven.exe", "nastia.exe", "lovescape.exe",
                "ourdream.exe", "lustgf.exe", "candyai.exe", "vidqu.exe", "dreamgf.exe",
                
                # Communication & Social
                "discord.exe", "slack.exe", "teams.exe", "zoom.exe", "skype.exe", 
                "telegram.exe", "whatsapp.exe", "signal.exe", "viber.exe",
                
                # AI Assistants & Productivity
                "copilot.exe", "siri.exe", "cortana.exe", "alexa.exe", "google-assistant.exe",
                "notion.exe", "obsidian.exe", "roam.exe", "logseq.exe", "craft.exe",
                "bear.exe", "typora.exe", "joplin.exe", "standard-notes.exe",
                
                # AI Development & Tools
                "chatgpt.exe", "claude.exe", "bard.exe", "perplexity.exe", "poe.exe",
                "huggingface.exe", "gradio.exe", "streamlit.exe", "jupyter.exe",
                "vscode.exe", "pycharm.exe", "sublime_text.exe", "atom.exe",
                
                # Testing & Development
                "notepad.exe", "wordpad.exe", "code.exe", "terminal.exe", "powershell.exe",
                "cmd.exe", "git-bash.exe", "wsl.exe"
            ]
            
            # Skip if it's a browser process
            if process_name and process_name.lower() in excluded_processes:
                time.sleep(poll_interval)
                continue
            
            # Only monitor if it's a known desktop AI app or if we can't determine process
            if not TEST_MODE and process_name and process_name.lower() not in allowed_processes:
                # For unknown processes, check if window title contains AI keywords
                if not is_ai_window(title):
                    time.sleep(poll_interval)
                    continue
            
            # Clear buffer on window switch
            if title != last_window_title or process_name != last_process_name:
                key_buffer.clear()
                last_window_title = title
                last_process_name = process_name
                print(f"[DEBUG] Window switched to: {title} (Process: {process_name})")
            
            typed = ''.join(key_buffer).strip()
            key_buffer.clear()
            
            # Enhanced input validation
            if not is_valid_user_input(typed):
                if typed:  # Only log if there was actually text typed
                    print(f"[DEBUG] Invalid input filtered out: '{typed}'")
                time.sleep(poll_interval)
                continue
            
            # Check for AI-related activity
            combined = f"{title} {typed}"
            hits = detect_keywords(combined)
            
            # Analyze process behavior
            behavior_suspicious = analyze_process_behavior(process_name, title)
            
            # Check for suspicious patterns in typed content
            content_suspicious = detect_suspicious_patterns(typed, "typing")
            
            # Trigger if any suspicious activity detected
            if (hits or behavior_suspicious or content_suspicious) and typed != last_sent_message:
                print(f"[DETECTED] AI Keywords: {hits} | Behavior: {behavior_suspicious} | Content: {content_suspicious} - {typed} (Process: {process_name})")
                logging.info(f"Detected activity - Keywords: {hits} | Behavior: {behavior_suspicious} | Content: {content_suspicious} - Input: {typed} - Process: {process_name}")
                
                now = datetime.now(UTC).isoformat()
                payload = {
                    "time": now,
                    "type": "Desktop Activity Detection",
                    "severity": "Medium" if behavior_suspicious or content_suspicious else "Low",
                    "source": f"{title} (Desktop App: {process_name})" if process_name else title or "Desktop Agent",
                    "country": "US",
                    "message": typed,
                    "sender": "agent",
                    "ai_keywords": hits,
                    "suspicious_behavior": behavior_suspicious,
                    "suspicious_content": content_suspicious,
                    "process_name": process_name,
                    "window_title": title
                }
                
                send_payload(payload)
                last_sent_message = typed
                poll_interval = 1  # More frequent polling on activity
                idle_count = 0
            else:
                idle_count += 1
                poll_interval = min(10, LOG_INTERVAL_SECONDS + idle_count)  # Adaptive polling
                
        except Exception as e:
            logging.error(f"Monitor error: {e}")
        time.sleep(poll_interval)

# === Process Behavior Monitoring ===
def analyze_process_behavior(process_name, window_title):
    """Analyze process behavior for suspicious patterns"""
    suspicious_behaviors = []
    
    # High-frequency typing patterns (potential automation)
    if len(key_buffer) > 50:  # Very fast typing
        suspicious_behaviors.append("high_frequency_typing")
    
    # Rapid window switching (potential data gathering)
    if hasattr(analyze_process_behavior, 'last_switch_time'):
        time_since_switch = time.time() - analyze_process_behavior.last_switch_time
        if time_since_switch < 2:  # Switched windows very quickly
            suspicious_behaviors.append("rapid_window_switching")
    analyze_process_behavior.last_switch_time = time.time()
    
    # Suspicious process combinations
    suspicious_combinations = [
        ("notepad.exe", "password"), ("cmd.exe", "ssh"), ("powershell.exe", "credential"),
        ("git-bash.exe", "token"), ("terminal.exe", "api_key")
    ]
    
    for proc, keyword in suspicious_combinations:
        if process_name == proc and keyword in window_title.lower():
            suspicious_behaviors.append(f"suspicious_{proc}_activity")
    
    # AI manipulation attempts
    ai_manipulation_indicators = [
        "jailbreak", "prompt injection", "roleplay", "ignore safety",
        "bypass", "override", "act as", "pretend to be"
    ]
    
    if any(indicator in window_title.lower() for indicator in ai_manipulation_indicators):
        suspicious_behaviors.append("ai_manipulation_attempt")
    
    return suspicious_behaviors

# === Control Functions ===
def start_monitoring():
    global monitoring
    if not monitoring:
        print("Starting monitoring...")
        logging.info("Monitoring started.")
        monitoring = True
        threading.Thread(target=monitor_loop, daemon=True).start()
        threading.Thread(target=monitor_keyboard, daemon=True).start()
        threading.Thread(target=monitor_clipboard, daemon=True).start()

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
    print(f"[DEBUG] CATDAMS Session ID: {session_manager.get_session_id()}")
    print("CATDAMS Sentinel Agent is starting...")
    logging.info("Agent starting...")
    run_tray()
