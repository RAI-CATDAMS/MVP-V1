
import logging
import requests
import json
from datetime import datetime, UTC

# Updated endpoint for local development
CATDAMS_ENDPOINT = "http://localhost:8000/event"

logging.basicConfig(level=logging.INFO, filename="catdams_agent.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def send_to_backend(payload):
    """Send payload to CATDAMS backend with TDC module integration"""
    try:
        # Ensure payload has required fields for TDC analysis
        if "session_id" not in payload:
            payload["session_id"] = "desktop-agent-" + datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        
        if "timestamp" not in payload:
            payload["timestamp"] = datetime.now(UTC).isoformat()
        
        if "sender" not in payload:
            payload["sender"] = "USER"
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(CATDAMS_ENDPOINT, headers=headers, json=payload, timeout=10)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"Backend accepted payload: {response.status_code}")
            
            # Log TDC analysis if present
            if "tdc_analysis" in payload and payload["tdc_analysis"]:
                tdc_count = len(payload["tdc_analysis"])
                logger.info(f"TDC Analysis sent: {tdc_count} modules analyzed")
                
        else:
            logger.warning(f"Backend returned unexpected status: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Failed to send to backend: {e}")

def format_tdc_analysis(tdc_analysis):
    """Format TDC analysis for logging and display"""
    if not tdc_analysis:
        return "No TDC analysis"
    
    formatted = []
    for module_name, analysis in tdc_analysis.items():
        if isinstance(analysis, dict):
            confidence = analysis.get('confidence', 0)
            indicators = []
            for key, value in analysis.items():
                if key != 'confidence' and isinstance(value, list):
                    indicators.extend(value[:2])  # Show first 2 indicators
            
            if indicators:
                module_short = module_name.replace('tdc_ai', 'TDC-AI').replace('_', ' ').title()
                formatted.append(f"{module_short} ({confidence:.1f}): {', '.join(indicators)}")
    
    return " | ".join(formatted) if formatted else "No significant indicators"

def self_test():
    """Self-test for desktop agent with TDC integration"""
    logger.info("CATDAMS Desktop Agent starting self-test...")
    try:
        import pystray, keyboard, pygetwindow, plyer
        logger.info("All required packages loaded successfully.")
        
        # Test backend connectivity
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code in [200, 202]:
            logger.info("Backend connectivity check passed.")
        else:
            logger.warning("Backend connectivity returned unexpected code.")
        
        # Test TDC module awareness
        test_tdc_analysis = {
            "tdc_ai1_user_susceptibility": {
                "risk_indicators": ["emotional_vulnerability"],
                "confidence": 0.7
            },
            "tdc_ai2_ai_manipulation_tactics": {
                "manipulation_indicators": ["prompt_manipulation"],
                "confidence": 0.8
            }
        }
        
        formatted = format_tdc_analysis(test_tdc_analysis)
        logger.info(f"TDC Analysis formatting test: {formatted}")
        
    except Exception as e:
        logger.error(f"Self-test failed: {e}")
