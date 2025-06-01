
import logging
import requests

CATDAMS_ENDPOINT = "https://catdams-app-mv-d5fgg9fhc6g5hwg7.eastus-01.azurewebsites.net/ingest"

logging.basicConfig(level=logging.INFO, filename="catdams-desktop-agent/catdams_agent.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def send_to_backend(payload):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(CATDAMS_ENDPOINT, headers=headers, json=payload)
        if response.status_code not in [200, 202]:
            logger.warning(f"Backend returned unexpected status: {response.status_code}")
        else:
            logger.info(f"Backend accepted payload: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send to backend: {e}")

def self_test():
    logger.info("CATDAMS Sentinel Agent starting self-test...")
    try:
        import pystray, keyboard, pygetwindow, plyer
        logger.info("All required packages loaded successfully.")
        response = requests.get("https://catdams-app-mv-d5fgg9fhc6g5hwg7.eastus-01.azurewebsites.net/health", timeout=5)
        if response.status_code in [200, 202]:
            logger.info("Backend connectivity check passed.")
        else:
            logger.warning("Backend connectivity returned unexpected code.")
    except Exception as e:
        logger.error(f"Self-test failed: {e}")
