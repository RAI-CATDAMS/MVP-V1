# get_session_history.py

import pyodbc
import json
from dotenv import load_dotenv
import os

load_dotenv()

def get_session_history(session_id, lookback_limit=50):
    """
    Pulls recent records from Azure SQL and filters those that match session_id inside the 'data' JSON.
    """
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DATABASE")
    username = os.getenv("AZURE_SQL_USERNAME")
    password = os.getenv("AZURE_SQL_PASSWORD")

    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT TOP {lookback_limit} timestamp, data
                FROM dbo.telemetry
                ORDER BY timestamp DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            history = []
            for row in rows:
                try:
                    parsed = json.loads(row.data)
                    if parsed.get("session_id") == session_id:
                        history.append({
                            "session_id": parsed["session_id"],
                            "timestamp": row.timestamp,
                            "indicators": parsed.get("indicators", [])
                        })
                except Exception as e:
                    print(f"⚠️ Skipping row due to parse error: {e}")

            return history

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return []
