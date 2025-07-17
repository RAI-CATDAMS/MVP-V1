#!/usr/bin/env python3
"""
Production startup script for CATDAMS
Runs without reload mode to avoid development noise
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Start CATDAMS in production mode"""
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Production configuration
    config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8000)),
        "reload": False,  # No reload in production
        "workers": 1,     # Single worker for now
        "log_level": "info",
        "access_log": True,
        "use_colors": False,  # No colors in production logs
    }
    
    print("🚀 Starting CATDAMS in production mode...")
    print(f"📍 Host: {config['host']}")
    print(f"🔌 Port: {config['port']}")
    print(f"🔄 Reload: {config['reload']}")
    print(f"👥 Workers: {config['workers']}")
    print("=" * 50)
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 CATDAMS stopped by user")
    except Exception as e:
        print(f"❌ Error starting CATDAMS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 