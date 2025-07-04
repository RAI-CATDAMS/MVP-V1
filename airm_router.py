# airm_router.py

from fastapi import APIRouter
from airm_controller import run_airm_for_session

router = APIRouter()

@router.get("/airm/{session_id}")
def get_airm_susceptibility(session_id: str):
    """
    API endpoint to run AIRM susceptibility analysis for a given session_id.
    """
    result = run_airm_for_session(session_id)
    return result
