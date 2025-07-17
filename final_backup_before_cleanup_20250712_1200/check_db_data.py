#!/usr/bin/env python3
"""
Database Data Checker for CATDAMS Dashboard
Checks what data is available and why the dashboard might not be displaying it.
"""

import sqlite3
import json
from datetime import datetime, timedelta

def check_database_data():
    """Check all database tables and their data"""
    conn = sqlite3.connect('catdams.db')
    cursor = conn.cursor()
    
    print("🔍 CATDAMS Database Data Analysis")
    print("=" * 50)
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"📋 Available tables: {[table[0] for table in tables]}")
    print()
    
    # Check table schemas
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"📋 {table_name} columns: {[col[1] for col in columns]}")
    print()
    
    # Check telemetry data
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    telemetry_count = cursor.fetchone()[0]
    print(f"📊 Telemetry records: {telemetry_count}")
    
    if telemetry_count > 0:
        cursor.execute("SELECT timestamp, session_id FROM telemetry ORDER BY timestamp DESC LIMIT 5")
        recent_telemetry = cursor.fetchall()
        print("📅 Recent telemetry entries:")
        for entry in recent_telemetry:
            print(f"   - {entry[0]} | Session: {entry[1]}")
    
    print()
    
    # Check threat logs
    cursor.execute("SELECT COUNT(*) FROM threat_logs")
    threat_count = cursor.fetchone()[0]
    print(f"⚠️  Threat log records: {threat_count}")
    
    if threat_count > 0:
        cursor.execute("SELECT created_at, session_id, threat_score, escalation_level FROM threat_logs ORDER BY created_at DESC LIMIT 5")
        recent_threats = cursor.fetchall()
        print("🚨 Recent threat entries:")
        for entry in recent_threats:
            print(f"   - {entry[0]} | Session: {entry[1]} | Score: {entry[2]} | Level: {entry[3]}")
    
    print()
    
    # Check AIPC data
    cursor.execute("SELECT COUNT(*) FROM aipc_evaluations")
    aipc_count = cursor.fetchone()[0]
    print(f"🤖 AIPC evaluation records: {aipc_count}")
    
    if aipc_count > 0:
        cursor.execute("SELECT timestamp, session_id, escalation_score, escalation_level FROM aipc_evaluations ORDER BY timestamp DESC LIMIT 5")
        recent_aipc = cursor.fetchall()
        print("🧠 Recent AIPC entries:")
        for entry in recent_aipc:
            print(f"   - {entry[0]} | Session: {entry[1]} | Score: {entry[2]} | Level: {entry[3]}")
    
    print()
    
    # Check for recent data (last 24 hours)
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    cursor.execute("SELECT COUNT(*) FROM telemetry WHERE timestamp > ?", (yesterday,))
    recent_telemetry_count = cursor.fetchone()[0]
    print(f"🕐 Telemetry records in last 24h: {recent_telemetry_count}")
    
    cursor.execute("SELECT COUNT(*) FROM threat_logs WHERE created_at > ?", (yesterday,))
    recent_threat_count = cursor.fetchone()[0]
    print(f"🕐 Threat records in last 24h: {recent_threat_count}")
    
    print()
    
    # Check session data
    cursor.execute("SELECT COUNT(DISTINCT session_id) FROM telemetry")
    unique_sessions = cursor.fetchone()[0]
    print(f"🆔 Unique sessions: {unique_sessions}")
    
    if unique_sessions > 0:
        cursor.execute("SELECT session_id, COUNT(*) as event_count FROM telemetry GROUP BY session_id ORDER BY event_count DESC LIMIT 5")
        session_stats = cursor.fetchall()
        print("📈 Top sessions by event count:")
        for session in session_stats:
            print(f"   - {session[0]}: {session[1]} events")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("🔧 Dashboard Data Issues Analysis:")
    
    if telemetry_count == 0:
        print("❌ NO TELEMETRY DATA - Dashboard will be empty")
        print("   Solution: Need to generate test data or ensure data ingestion is working")
    elif recent_telemetry_count == 0:
        print("⚠️  NO RECENT TELEMETRY DATA - Dashboard may appear stale")
        print("   Solution: Check if data ingestion is currently working")
    else:
        print("✅ Telemetry data available")
    
    if threat_count == 0:
        print("❌ NO THREAT DATA - Threat analysis will be empty")
        print("   Solution: Need threat detection to be working")
    else:
        print("✅ Threat data available")
    
    if aipc_count == 0:
        print("❌ NO AIPC DATA - AI analysis will be empty")
        print("   Solution: Need AIPC module to be processing data")
    else:
        print("✅ AIPC data available")

if __name__ == "__main__":
    check_database_data() 