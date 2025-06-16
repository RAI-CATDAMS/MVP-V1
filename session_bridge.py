from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import getpass

user = getpass.getuser()
SESSION_FILE = f"C:/Users/{user}/Documents/catdams_session_id.txt"

class SessionRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/session-id":
            try:
                with open(SESSION_FILE, "r") as f:
                    session_id = f.read().strip()
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(session_id.encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error reading session ID: {e}".encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server_address = ("localhost", 3009)
    httpd = HTTPServer(server_address, SessionRequestHandler)
    print("CATDAMS Session Bridge running at http://localhost:3009/session-id")
    httpd.serve_forever()
