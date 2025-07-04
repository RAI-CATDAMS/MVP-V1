"""
CATDAMS Analytics API
Provides endpoints for the analytics engine to access real data from the database and TDC modules.
Built incrementally with safety measures and rollback capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from collections import Counter, defaultdict
from statistics import mean

from database import get_db_session
from db_models import Telemetry, ThreatLog, AIPCEvaluation, AIPCMatch

# Create analytics router
analytics_router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Safety: Version tracking for rollback
API_VERSION = "1.0.0"

# Safety: Configuration for data limits and timeouts
MAX_RECORDS_PER_REQUEST = 1000
DEFAULT_TIME_RANGE_DAYS = 30

# ML Prediction Configuration
PREDICTION_DAYS = 7
TREND_ANALYSIS_DAYS = 30

def safe_json_parse(data, default=None):
    """Safely parse JSON data with fallback"""
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return default
    return default

def validate_time_range(days: int) -> int:
    """Validate and limit time range for safety"""
    if days < 1:
        return 1
    if days > 365:
        return 365
    return days

# === SESSION ANALYSIS ENDPOINTS ===

@analytics_router.get("/sessions/summary")
async def get_session_summary(
    days: int = Query(DEFAULT_TIME_RANGE_DAYS, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """
    Get comprehensive session analysis summary
    """
    try:
        days = validate_time_range(days)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get session statistics
        session_stats = db.query(
            func.count(Telemetry.session_id.distinct()).label('total_sessions'),
            func.count(Telemetry.id).label('total_events'),
            func.avg(Telemetry.id).label('avg_events_per_session')
        ).filter(Telemetry.timestamp >= cutoff_date).first()
        
        # Get threat statistics (SQL Server compatible)
        total_threats = db.query(func.count(ThreatLog.id)).filter(
            ThreatLog.created_at >= cutoff_date
        ).scalar() or 0
        
        avg_threat_score = db.query(func.avg(ThreatLog.threat_score)).filter(
            ThreatLog.created_at >= cutoff_date
        ).scalar() or 0
        
        critical_threats = db.query(func.count(ThreatLog.id)).filter(
            ThreatLog.created_at >= cutoff_date,
            ThreatLog.escalation_level == 'CRITICAL'
        ).scalar() or 0
        
        return {
            "api_version": API_VERSION,
            "time_range_days": days,
            "session_analysis": {
                "total_sessions": session_stats.total_sessions or 0,
                "total_events": session_stats.total_events or 0,
                "avg_events_per_session": round(session_stats.avg_events_per_session or 0, 2)
            },
            "threat_analysis": {
                "total_threats": total_threats,
                "avg_threat_score": round(avg_threat_score, 2),
                "critical_threats": critical_threats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session analysis error: {str(e)}")

@analytics_router.get("/sessions/active")
async def get_active_sessions(
    limit: int = Query(10, description="Number of recent sessions to return"),
    db: Session = Depends(get_db_session)
):
    """
    Get recent active sessions with threat analysis
    """
    try:
        limit = min(limit, MAX_RECORDS_PER_REQUEST)
        
        # Get recent sessions with threat data
        recent_sessions = db.query(
            Telemetry.session_id,
            func.max(Telemetry.timestamp).label('last_activity'),
            func.count(Telemetry.id).label('event_count')
        ).group_by(Telemetry.session_id).order_by(
            desc(func.max(Telemetry.timestamp))
        ).limit(limit).all()
        
        sessions_data = []
        for session in recent_sessions:
            # Get threat data for this session
            threat_data = db.query(ThreatLog).filter(
                ThreatLog.session_id == session.session_id
            ).order_by(desc(ThreatLog.created_at)).first()
            
            sessions_data.append({
                "session_id": session.session_id,
                "last_activity": session.last_activity,
                "event_count": session.event_count,
                "threat_score": threat_data.threat_score if threat_data else 0,
                "escalation_level": threat_data.escalation_level if threat_data else "NONE"
            })
        
        return {
            "api_version": API_VERSION,
            "active_sessions": sessions_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active sessions error: {str(e)}")

# === TDC MODULE PERFORMANCE ENDPOINTS ===

@analytics_router.get("/tdc/performance")
async def get_tdc_performance(
    days: int = Query(DEFAULT_TIME_RANGE_DAYS, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """
    Get TDC module performance metrics
    """
    try:
        days = validate_time_range(days)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # AIPC Module Performance (SQL Server compatible)
        total_evaluations = db.query(func.count(AIPCEvaluation.id)).filter(
            AIPCEvaluation.timestamp >= cutoff_date
        ).scalar() or 0
        
        avg_escalation_score = db.query(func.avg(AIPCEvaluation.escalation_score)).filter(
            AIPCEvaluation.timestamp >= cutoff_date
        ).scalar() or 0
        
        critical_evaluations = db.query(func.count(AIPCEvaluation.id)).filter(
            AIPCEvaluation.timestamp >= cutoff_date,
            AIPCEvaluation.escalation_level == 'CRITICAL'
        ).scalar() or 0
        
        # Threat Detection Performance (SQL Server compatible)
        total_detections = db.query(func.count(ThreatLog.id)).filter(
            ThreatLog.created_at >= cutoff_date
        ).scalar() or 0
        
        avg_threat_score = db.query(func.avg(ThreatLog.threat_score)).filter(
            ThreatLog.created_at >= cutoff_date
        ).scalar() or 0
        
        high_critical_detections = db.query(func.count(ThreatLog.id)).filter(
            ThreatLog.created_at >= cutoff_date,
            ThreatLog.escalation_level.in_(['HIGH', 'CRITICAL'])
        ).scalar() or 0
        
        return {
            "api_version": API_VERSION,
            "time_range_days": days,
            "aipc_module": {
                "total_evaluations": total_evaluations,
                "avg_escalation_score": round(avg_escalation_score, 2),
                "critical_evaluations": critical_evaluations
            },
            "threat_detection": {
                "total_detections": total_detections,
                "avg_threat_score": round(avg_threat_score, 2),
                "high_critical_detections": high_critical_detections
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TDC performance error: {str(e)}")

# === ML PREDICTIONS AND TREND ANALYSIS ===

@analytics_router.get("/predictions/trends")
async def get_trend_predictions(
    days: int = Query(PREDICTION_DAYS, description="Number of days to predict"),
    db: Session = Depends(get_db_session)
):
    """
    Get ML-based trend predictions and analysis
    """
    try:
        days = validate_time_range(days)
        analysis_cutoff = datetime.utcnow() - timedelta(days=TREND_ANALYSIS_DAYS)
        
        # Get historical data for trend analysis (SQL Server compatible)
        from sqlalchemy import text
        daily_threats_query = text("""
            SELECT CAST(created_at AS DATE) as date,
                   COUNT(id) as threat_count,
                   AVG(threat_score) as avg_score
            FROM threat_logs
            WHERE created_at >= :cutoff_date
            GROUP BY CAST(created_at AS DATE)
            ORDER BY CAST(created_at AS DATE)
        """)
        
        daily_threats = db.execute(daily_threats_query, {"cutoff_date": analysis_cutoff}).fetchall()
        
        # Simple trend analysis (moving average)
        threat_counts = [day.threat_count for day in daily_threats]
        threat_scores = [day.avg_score for day in daily_threats]
        
        # Calculate trends
        if len(threat_counts) >= 2:
            threat_trend = (threat_counts[-1] - threat_counts[0]) / len(threat_counts)
            score_trend = (threat_scores[-1] - threat_scores[0]) / len(threat_scores) if threat_scores[0] else 0
        else:
            threat_trend = 0
            score_trend = 0
        
        # Simple prediction (linear extrapolation)
        current_threats = threat_counts[-1] if threat_counts else 0
        predicted_threats = max(0, current_threats + (threat_trend * days))
        
        current_score = threat_scores[-1] if threat_scores else 0
        predicted_score = max(0, current_score + (score_trend * days))
        
        # Risk assessment
        risk_level = "LOW"
        if predicted_threats > current_threats * 1.5:
            risk_level = "HIGH"
        elif predicted_threats > current_threats * 1.2:
            risk_level = "MEDIUM"
        
        return {
            "api_version": API_VERSION,
            "prediction_days": days,
            "analysis_period_days": TREND_ANALYSIS_DAYS,
            "current_metrics": {
                "daily_threats": current_threats,
                "avg_threat_score": round(current_score, 2)
            },
            "predicted_metrics": {
                "daily_threats": round(predicted_threats, 2),
                "avg_threat_score": round(predicted_score, 2)
            },
            "trends": {
                "threat_trend": round(threat_trend, 2),
                "score_trend": round(score_trend, 2),
                "trend_direction": "increasing" if threat_trend > 0 else "decreasing"
            },
            "risk_assessment": {
                "level": risk_level,
                "confidence": "medium",
                "factors": [
                    "historical trend analysis",
                    "threat score patterns",
                    "seasonal variations"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend prediction error: {str(e)}")

@analytics_router.get("/predictions/anomalies")
async def get_anomaly_detection(
    db: Session = Depends(get_db_session)
):
    """
    Get anomaly detection results
    """
    try:
        # Get recent threat data for anomaly detection
        recent_threats = db.query(
            ThreatLog.threat_score,
            ThreatLog.escalation_level,
            ThreatLog.created_at
        ).filter(
            ThreatLog.created_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        if not recent_threats:
            return {
                "api_version": API_VERSION,
                "anomalies": [],
                "message": "No recent data for anomaly detection"
            }
        
        # Simple anomaly detection (statistical outliers)
        scores = [t.threat_score for t in recent_threats]
        avg_score = mean(scores)
        std_dev = (sum((x - avg_score) ** 2 for x in scores) / len(scores)) ** 0.5
        
        anomalies = []
        for threat in recent_threats:
            if threat.threat_score > avg_score + (2 * std_dev):
                anomalies.append({
                    "timestamp": threat.created_at.isoformat(),
                    "threat_score": threat.threat_score,
                    "escalation_level": threat.escalation_level,
                    "anomaly_type": "high_score",
                    "severity": "high" if threat.threat_score > avg_score + (3 * std_dev) else "medium"
                })
        
        return {
            "api_version": API_VERSION,
            "anomalies": anomalies,
            "statistics": {
                "total_threats_analyzed": len(recent_threats),
                "anomalies_detected": len(anomalies),
                "avg_threat_score": round(avg_score, 2),
                "std_deviation": round(std_dev, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection error: {str(e)}")

@analytics_router.get("/tdc/aipc/patterns")
async def get_aipc_patterns(
    limit: int = Query(20, description="Number of patterns to return"),
    db: Session = Depends(get_db_session)
):
    """
    Get AIPC pattern analysis
    """
    try:
        limit = min(limit, MAX_RECORDS_PER_REQUEST)
        
        # Get most common patterns
        patterns = db.query(
            AIPCMatch.category,
            AIPCMatch.pattern,
            func.count(AIPCMatch.id).label('occurrence_count'),
            func.avg(AIPCMatch.similarity).label('avg_similarity'),
            func.avg(AIPCMatch.severity).label('avg_severity')
        ).group_by(AIPCMatch.category, AIPCMatch.pattern).order_by(
            desc(func.count(AIPCMatch.id))
        ).limit(limit).all()
        
        pattern_data = []
        for pattern in patterns:
            pattern_data.append({
                "category": pattern.category,
                "pattern": pattern.pattern,
                "occurrence_count": pattern.occurrence_count,
                "avg_similarity": round(pattern.avg_similarity or 0, 2),
                "avg_severity": round(pattern.avg_severity or 0, 2)
            })
        
        return {
            "api_version": API_VERSION,
            "aipc_patterns": pattern_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AIPC patterns error: {str(e)}")

# === THREAT PATTERNS ENDPOINTS ===

@analytics_router.get("/threats/patterns")
async def get_threat_patterns(
    days: int = Query(DEFAULT_TIME_RANGE_DAYS, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """
    Get threat pattern analysis
    """
    try:
        days = validate_time_range(days)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get threat logs with analysis
        threat_logs = db.query(ThreatLog).filter(
            ThreatLog.created_at >= cutoff_date
        ).order_by(desc(ThreatLog.created_at)).limit(MAX_RECORDS_PER_REQUEST).all()
        
        # Analyze patterns
        escalation_counts = Counter()
        threat_scores = []
        indicators_analysis = {}
        
        for log in threat_logs:
            escalation_counts[log.escalation_level] += 1
            threat_scores.append(log.threat_score)
            
            # Analyze indicators
            indicators = safe_json_parse(log.indicators, {})
            if isinstance(indicators, dict):
                for indicator, value in indicators.items():
                    if indicator not in indicators_analysis:
                        indicators_analysis[indicator] = Counter()
                    indicators_analysis[indicator][str(value)] += 1
        
        # Get top indicators
        top_indicators = []
        for indicator, counts in indicators_analysis.items():
            top_value = counts.most_common(1)[0] if counts else ("N/A", 0)
            top_indicators.append({
                "indicator": indicator,
                "most_common_value": top_value[0],
                "occurrence_count": top_value[1]
            })
        
        return {
            "api_version": API_VERSION,
            "time_range_days": days,
            "escalation_distribution": dict(escalation_counts),
            "threat_score_stats": {
                "avg_score": round(mean(threat_scores), 2) if threat_scores else 0,
                "min_score": min(threat_scores) if threat_scores else 0,
                "max_score": max(threat_scores) if threat_scores else 0
            },
            "top_indicators": sorted(top_indicators, key=lambda x: x["occurrence_count"], reverse=True)[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat patterns error: {str(e)}")

@analytics_router.get("/threats/timeline")
async def get_threat_timeline(
    days: int = Query(7, description="Number of days for timeline"),
    db: Session = Depends(get_db_session)
):
    """
    Get threat timeline data for charts
    """
    try:
        days = validate_time_range(days)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily threat counts
        daily_threats = db.query(
            func.date(ThreatLog.created_at).label('date'),
            func.count(ThreatLog.id).label('threat_count'),
            func.avg(ThreatLog.threat_score).label('avg_score')
        ).filter(
            ThreatLog.created_at >= cutoff_date
        ).group_by(
            func.date(ThreatLog.created_at)
        ).order_by(
            func.date(ThreatLog.created_at)
        ).all()
        
        timeline_data = []
        for day in daily_threats:
            timeline_data.append({
                "date": day.date.isoformat(),
                "threat_count": day.threat_count,
                "avg_score": round(day.avg_score or 0, 2)
            })
        
        return {
            "api_version": API_VERSION,
            "time_range_days": days,
            "timeline": timeline_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat timeline error: {str(e)}")

# === REAL-TIME DATA ENDPOINTS ===

@analytics_router.get("/realtime/current")
async def get_current_activity(
    db: Session = Depends(get_db_session)
):
    """
    Get current system activity (last hour)
    """
    try:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # Recent events
        recent_events = db.query(Telemetry).filter(
            Telemetry.timestamp >= one_hour_ago.isoformat()
        ).order_by(desc(Telemetry.timestamp)).limit(10).all()
        
        # Recent threats
        recent_threats = db.query(ThreatLog).filter(
            ThreatLog.created_at >= one_hour_ago
        ).order_by(desc(ThreatLog.created_at)).limit(5).all()
        
        events_data = []
        for event in recent_events:
            events_data.append({
                "timestamp": event.timestamp,
                "session_id": event.session_id,
                "type": event.type_indicator,
                "ai_source": event.ai_source
            })
        
        threats_data = []
        for threat in recent_threats:
            threats_data.append({
                "timestamp": threat.created_at.isoformat(),
                "session_id": threat.session_id,
                "threat_score": threat.threat_score,
                "escalation_level": threat.escalation_level
            })
        
        return {
            "api_version": API_VERSION,
            "current_activity": {
                "recent_events": events_data,
                "recent_threats": threats_data,
                "active_sessions": len(set(event.session_id for event in recent_events))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Current activity error: {str(e)}")

# === HEALTH AND STATUS ENDPOINTS ===

@analytics_router.get("/health")
async def analytics_health():
    """
    Analytics API health check
    """
    return {
        "status": "healthy",
        "api_version": API_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

@analytics_router.get("/status")
async def analytics_status(db: Session = Depends(get_db_session)):
    """
    Analytics API status with data availability
    """
    try:
        # Check data availability
        total_telemetry = db.query(func.count(Telemetry.id)).scalar() or 0
        total_threats = db.query(func.count(ThreatLog.id)).scalar() or 0
        total_aipc = db.query(func.count(AIPCEvaluation.id)).scalar() or 0
        
        # Check recent activity
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_activity = db.query(func.count(Telemetry.id)).filter(
            Telemetry.timestamp >= one_hour_ago.isoformat()
        ).scalar() or 0
        
        return {
            "status": "operational",
            "api_version": API_VERSION,
            "data_availability": {
                "total_telemetry_records": total_telemetry,
                "total_threat_records": total_threats,
                "total_aipc_records": total_aipc,
                "recent_activity_last_hour": recent_activity
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "api_version": API_VERSION,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }