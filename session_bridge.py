from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import getpass
import uuid
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

user = getpass.getuser()
SESSION_FILE = f"C:/Users/{user}/Documents/catdams_session_id.txt"

# Session management with conversation boundaries
class SessionManager:
    def __init__(self, session_file):
        self.session_file = session_file
        self.current_session_id = None
        self.last_activity = 0
        self.session_timeout = 5 * 60  # 5 minutes timeout for new sessions
    
    def get_session_id(self):
        now = time.time()
        
        # If no session exists or session has timed out, create new one
        if (not self.current_session_id or 
            now - self.last_activity > self.session_timeout):
            self.current_session_id = str(uuid.uuid4())
            self.last_activity = now
            
            # Update the session file
            try:
                with open(self.session_file, "w") as f:
                    f.write(self.current_session_id)
                logger.info(f"Generated new session ID: {self.current_session_id}")
            except Exception as e:
                logger.error(f"Failed to write session file: {e}")
        else:
            # Update activity time for existing session
            self.last_activity = now
        
        return self.current_session_id
    
    def load_existing_session(self):
        """Load existing session from file if it exists and is recent"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r") as f:
                    session_id = f.read().strip()
                    if session_id:
                        # Check if session is recent (within 5 minutes)
                        file_time = os.path.getmtime(self.session_file)
                        if time.time() - file_time < self.session_timeout:
                            self.current_session_id = session_id
                            self.last_activity = file_time
                            logger.info(f"Loaded existing session: {session_id}")
                            return True
            except Exception as e:
                logger.error(f"Failed to load session file: {e}")
        return False

# Global session manager
session_manager = SessionManager(SESSION_FILE)

def ensure_session_file_exists():
    """Ensure the session file exists with a valid session ID"""
    if not os.path.exists(SESSION_FILE):
        session_id = session_manager.get_session_id()
        logger.info(f"Created new session file with ID: {session_id}")
    return True

class SessionRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        if self.path == "/session-id":
            try:
                # Get current session ID (creates new one if needed)
                session_id = session_manager.get_session_id()
                
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.end_headers()
                self.wfile.write(session_id.encode())
                logger.info(f"Served session ID: {session_id}")
                
            except Exception as e:
                logger.error(f"Error serving session ID: {e}")
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(f"Error reading session ID: {e}".encode())
        else:
            self.send_response(404)
            self.end_headers()
            logger.warning(f"404 for path: {self.path}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

if __name__ == "__main__":
    # Try to load existing session on startup
    session_manager.load_existing_session()
    
    server_address = ("localhost", 3009)
    httpd = HTTPServer(server_address, SessionRequestHandler)
    logger.info("CATDAMS Session Bridge running at http://localhost:3009/session-id")
    print("CATDAMS Session Bridge running at http://localhost:3009/session-id")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Session bridge stopped by user")
        print("\nSession bridge stopped")
