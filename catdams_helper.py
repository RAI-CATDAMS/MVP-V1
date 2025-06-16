import sys
import struct
import json

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = struct.unpack('=I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return message

def write_session_id(session_id):
    with open("C:/Users/micha/Documents/catdams_session_id.txt", "w") as f:
        f.write(session_id.strip())

if __name__ == "__main__":
    while True:
        try:
            message = read_message()
            data = json.loads(message)
            session_id = data.get("session_id")
            if session_id:
                write_session_id(session_id)
        except Exception:
            continue
