"""
CATDAMS Analytics API
Provides endpoints for the analytics engine to access real data from the database and TDC modules.
Updated for 11-Module TDC Structure with comprehensive analytics capabilities.
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
from db_models import Telemetry, ThreatLog

# Create analytics router
analytics_router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Safety: Version tracking for rollback
API_VERSION = "2.0.0"  # Updated for 11-module structure

# Safety: Configuration for data limits and timeouts
MAX_RECORDS_PER_REQUEST = 1000
DEFAULT_TIME_RANGE_DAYS = 30

# ML Prediction Configuration
PREDICTION_DAYS = 7
TREND_ANALYSIS_DAYS = 30

# TDC Module Configuration
TDC_MODULES = {
    "tdc_ai1_user_susceptibility": "User Risk & Susceptibility Analysis",
    "tdc_ai2_ai_manipulation_tactics": "AI Tactics & Manipulation Detection", 
    "tdc_ai3_sentiment_analysis": "Pattern & Sentiment Analysis",
    "tdc_ai4_prompt_attack_detection": "Adversarial Prompt & Attack Detection",
    "tdc_ai5_multimodal_threat": "Multi-Modal Threat Detection",
    "tdc_ai6_longterm_influence_conditioning": "Long-Term Influence & Conditioning Analysis",
    "tdc_ai7_agentic_threats": "Agentic AI & Autonomous Agent Threat Modeling",
    "tdc_ai8_synthesis_integration": "Threat Synthesis & Escalation Detection",
    "tdc_ai9_explainability_evidence": "Explainability & Evidence Generation",
    "tdc_ai10_psychological_manipulation": "Cognitive Bias & Psychological Manipulation",
    "tdc_ai11_intervention_response": "Cognitive Intervention & Response"
}

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

def extract_module_metrics(module_data: Dict) -> Dict:
    """Extract standardized metrics from TDC module output"""
    if not module_data:
        return {
            "confidence": 0.0,
            "threat_level": "NONE",
            "processing_time": 0.0,
            "evidence_count": 0,
            "categories": [],
            "summary": "No data available"
        }
    
    return {
        "confidence": module_data.get("confidence", 0.0),
        "threat_level": module_data.get("threat_level", "NONE"),
        "processing_time": module_data.get("processing_time", 0.0),
        "evidence_count": len(module_data.get("evidence", [])),
        "categories": module_data.get("categories", []),
        "summary": module_data.get("summary", "No summary available")
    }

# === SESSION ANALYSIS ENDPOINTS ===

@analytics_router.get("/sessions/summary")
async def get_session_summary(
    days: int = Query(DEFAULT_TIME_RANGE_DAYS, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """
    Get comprehensive session analysis summary with 11-module integration
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
        
        # Get threat statistics with 11-module data
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
        
        # Get module activation statistics
        module_stats = {}
        for module_field in TDC_MODULES.keys():
            # Count records where this module has data
            module_count = db.query(func.count(ThreatLog.id)).filter(
                ThreatLog.created_at >= cutoff_date,
                getattr(ThreatLog, module_field).isnot(None)
            ).scalar() or 0
            module_stats[module_field] = module_count
        
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
            },
            "module_activation": module_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session analysis error: {str(e)}")

@analytics_router.get("/sessions/active")
async def get_active_sessions(
    limit: int = Query(10, description="Number of recent sessions to return"),
    db: Session = Depends(get_db_session)
):
    """
    Get recent active sessions with 11-module threat analysis
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
            # Get threat data for this session with 11-module analysis
            threat_data = db.query(ThreatLog).filter(
                ThreatLog.session_id == session.session_id
            ).order_by(desc(ThreatLog.created_at)).first()
            
            # Extract module metrics
            module_analysis = {}
            if threat_data:
                for module_field in TDC_MODULES.keys():
                    module_data = getattr(threat_data, module_field)
                    module_analysis[module_field] = extract_module_metrics(safe_json_parse(module_data))
            
            sessions_data.append({
                "session_id": session.session_id,
                "last_activity": session.last_activity,
                "event_count": session.event_count,
                "threat_score": threat_data.threat_score if threat_data else 0,
                "escalation_level": threat_data.escalation_level if threat_data else "NONE",
                "module_analysis": module_analysis
            })
        
        return {
            "api_version": API_VERSION,
            "active_sessions": sessions_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active sessions error: {str(e)}")

# === 11-MODULE TDC PERFORMANCE ENDPOINTS ===

@analytics_router.get("/tdc/performance")
async def get_tdc_performance(
    days: int = Query(DEFAULT_TIME_RANGE_DAYS, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """
    Get comprehensive 11-module TDC performance metrics
    """
    try:
        days = validate_time_range(days)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Overall threat detection performance
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
        
        # Individual module performance analysis with error handling
        module_performance = {}
        for module_field, module_name in TDC_MODULES.items():
            try:
                # Check if the column exists in the database
                if not hasattr(ThreatLog, module_field):
                    module_performance[module_field] = {
                        "module_name": module_name,
                        "total_analyses": 0,
                        "avg_confidence": 0.0,
                        "threat_level_distribution": {},
                        "avg_processing_time": 0.0,
                        "avg_evidence_count": 0,
                        "activation_rate": 0.0,
                        "status": "column_not_found"
                    }
                    continue
                
                # Get records with this module data
                module_records = db.query(ThreatLog).filter(
                    ThreatLog.created_at >= cutoff_date,
                    getattr(ThreatLog, module_field).isnot(None)
                ).all()
                
                if module_records:
                    # Extract metrics from module data
                    confidences = []
                    threat_levels = Counter()
                    processing_times = []
                    evidence_counts = []
                    
                    for record in module_records:
                        try:
                            module_data = safe_json_parse(getattr(record, module_field))
                            if module_data:
                                confidences.append(module_data.get("confidence", 0.0))
                                threat_levels[module_data.get("threat_level", "NONE")] += 1
                                processing_times.append(module_data.get("processing_time", 0.0))
                                evidence_counts.append(len(module_data.get("evidence", [])))
                        except Exception as e:
                            # Skip records with malformed data
                            continue
                    
                    module_performance[module_field] = {
                        "module_name": module_name,
                        "total_analyses": len(module_records),
                        "avg_confidence": round(mean(confidences), 2) if confidences and len(confidences) > 0 else 0.0,
                        "threat_level_distribution": dict(threat_levels),
                        "avg_processing_time": round(mean(processing_times), 3) if processing_times and len(processing_times) > 0 else 0.0,
                        "avg_evidence_count": round(mean(evidence_counts), 1) if evidence_counts and len(evidence_counts) > 0 else 0,
                        "activation_rate": round(len(module_records) / total_detections * 100, 1) if total_detections and total_detections > 0 else 0.0,
                        "status": "active"
                    }
                else:
                    module_performance[module_field] = {
                        "module_name": module_name,
                        "total_analyses": 0,
                        "avg_confidence": 0.0,
                        "threat_level_distribution": {},
                        "avg_processing_time": 0.0,
                        "avg_evidence_count": 0,
                        "activation_rate": 0.0,
                        "status": "no_data"
                    }
            except Exception as e:
                # Handle any module-specific errors gracefully
                module_performance[module_field] = {
                    "module_name": module_name,
                    "total_analyses": 0,
                    "avg_confidence": 0.0,
                    "threat_level_distribution": {},
                    "avg_processing_time": 0.0,
                    "avg_evidence_count": 0,
                    "activation_rate": 0.0,
                    "status": f"error: {str(e)[:50]}"
                }
        
        return {
            "api_version": API_VERSION,
            "time_range_days": days,
            "overall_performance": {
                "total_detections": total_detections,
                "avg_threat_score": round(avg_threat_score, 2),
                "high_critical_detections": high_critical_detections
            },
            "module_performance": module_performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TDC performance error: {str(e)}")

@analytics_router.get("/tdc/module/{module_name}")
async def get_module_analysis(
    module_name: str,
    days: int = Query(DEFAULT_TIME_RANGE_DAYS, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """
    Get detailed analysis for a specific TDC module
    """
    try:
        if module_name not in TDC_MODULES:
            raise HTTPException(status_code=400, detail=f"Invalid module name. Valid modules: {list(TDC_MODULES.keys())}")
        
        days = validate_time_range(days)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all records with this module data
        module_records = db.query(ThreatLog).filter(
            ThreatLog.created_at >= cutoff_date,
            getattr(ThreatLog, module_name).isnot(None)
        ).order_by(desc(ThreatLog.created_at)).all()
        
        if not module_records:
            return {
                "api_version": API_VERSION,
                "module_name": module_name,
                "module_display_name": TDC_MODULES[module_name],
                "message": "No data available for this module in the specified time range"
            }
        
        # Analyze module data
        confidences = []
        threat_levels = Counter()
        processing_times = []
        evidence_counts = []
        categories = Counter()
        summaries = []
        
        for record in module_records:
            module_data = safe_json_parse(getattr(record, module_name))
            if module_data:
                confidences.append(module_data.get("confidence", 0.0))
                threat_levels[module_data.get("threat_level", "NONE")] += 1
                processing_times.append(module_data.get("processing_time", 0.0))
                evidence_counts.append(len(module_data.get("evidence", [])))
                
                # Collect categories
                for category in module_data.get("categories", []):
                    categories[category] += 1
                
                # Collect summaries
                summary = module_data.get("summary", "")
                if summary and summary != "No summary available":
                    summaries.append(summary)
        
        # Recent activity (last 10 records)
        recent_activity = []
        for record in module_records[:10]:
            module_data = safe_json_parse(getattr(record, module_name))
            recent_activity.append({
                "timestamp": record.created_at.isoformat(),
                "session_id": record.session_id,
                "confidence": module_data.get("confidence", 0.0) if module_data else 0.0,
                "threat_level": module_data.get("threat_level", "NONE") if module_data else "NONE",
                "summary": module_data.get("summary", "No summary") if module_data else "No summary"
            })
        
        return {
            "api_version": API_VERSION,
            "module_name": module_name,
            "module_display_name": TDC_MODULES[module_name],
            "time_range_days": days,
            "total_analyses": len(module_records),
            "performance_metrics": {
                "avg_confidence": round(mean(confidences), 2) if confidences else 0.0,
                "confidence_range": {
                    "min": min(confidences) if confidences else 0.0,
                    "max": max(confidences) if confidences else 0.0
                },
                "avg_processing_time": round(mean(processing_times), 3) if processing_times else 0.0,
                "avg_evidence_count": round(mean(evidence_counts), 1) if evidence_counts else 0
            },
            "threat_analysis": {
                "threat_level_distribution": dict(threat_levels),
                "top_categories": dict(categories.most_common(10)),
                "total_categories": len(categories)
            },
            "recent_activity": recent_activity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Module analysis error: {str(e)}")

# === ML PREDICTIONS AND TREND ANALYSIS ===

@analytics_router.get("/predictions/trends")
async def get_trend_predictions(
    days: int = Query(PREDICTION_DAYS, description="Number of days to predict"),
    db: Session = Depends(get_db_session)
):
    """
    Get ML-based trend predictions and analysis with 11-module integration
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
    Get anomaly detection results with 11-module integration
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

# === 11-MODULE PATTERN ANALYSIS ===

@analytics_router.get("/tdc/patterns")
async def get_tdc_patterns(
    limit: int = Query(20, description="Number of patterns to return"),
    db: Session = Depends(get_db_session)
):
    """
    Get comprehensive 11-module pattern analysis
    """
    try:
        limit = min(limit, MAX_RECORDS_PER_REQUEST)
        
        # Get recent threat logs with module data
        recent_threats = db.query(ThreatLog).order_by(
            desc(ThreatLog.created_at)
        ).limit(limit).all()
        
        patterns = {
            "module_activation_patterns": {},
            "threat_level_patterns": {},
            "confidence_patterns": {},
            "category_patterns": Counter(),
            "cross_module_correlations": {}
        }
        
        for threat in recent_threats:
            # Analyze each module's patterns
            for module_field in TDC_MODULES.keys():
                module_data = safe_json_parse(getattr(threat, module_field))
                if module_data:
                    # Module activation patterns
                    if module_field not in patterns["module_activation_patterns"]:
                        patterns["module_activation_patterns"][module_field] = 0
                    patterns["module_activation_patterns"][module_field] += 1
                    
                    # Threat level patterns
                    threat_level = module_data.get("threat_level", "NONE")
                    if module_field not in patterns["threat_level_patterns"]:
                        patterns["threat_level_patterns"][module_field] = Counter()
                    patterns["threat_level_patterns"][module_field][threat_level] += 1
                    
                    # Confidence patterns
                    confidence = module_data.get("confidence", 0.0)
                    if module_field not in patterns["confidence_patterns"]:
                        patterns["confidence_patterns"][module_field] = []
                    patterns["confidence_patterns"][module_field].append(confidence)
                    
                    # Category patterns
                    for category in module_data.get("categories", []):
                        patterns["category_patterns"][category] += 1
        
        # Calculate average confidences
        for module_field in patterns["confidence_patterns"]:
            confidences = patterns["confidence_patterns"][module_field]
            if confidences:
                patterns["confidence_patterns"][module_field] = {
                    "avg": round(mean(confidences), 2),
                    "min": min(confidences),
                    "max": max(confidences),
                    "count": len(confidences)
                }
        
        return {
            "api_version": API_VERSION,
            "patterns": patterns,
            "top_categories": dict(patterns["category_patterns"].most_common(10))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis error: {str(e)}")

@analytics_router.get("/threats/patterns")
async def get_threat_patterns(
    days: int = Query(DEFAULT_TIME_RANGE_DAYS, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """
    Get threat patterns with 11-module integration
    """
    try:
        days = validate_time_range(days)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get threat data with module analysis
        threats = db.query(ThreatLog).filter(
            ThreatLog.created_at >= cutoff_date
        ).order_by(desc(ThreatLog.created_at)).all()
        
        patterns = {
            "escalation_levels": Counter(),
            "threat_scores": [],
            "module_contributions": {},
            "session_patterns": Counter(),
            "time_patterns": Counter()
        }
        
        for threat in threats:
            # Basic threat patterns
            patterns["escalation_levels"][threat.escalation_level] += 1
            patterns["threat_scores"].append(threat.threat_score)
            patterns["session_patterns"][threat.session_id] += 1
            
            # Time patterns
            hour = threat.created_at.hour
            patterns["time_patterns"][f"{hour:02d}:00"] += 1
            
            # Module contribution analysis
            for module_field in TDC_MODULES.keys():
                module_data = safe_json_parse(getattr(threat, module_field))
                if module_data and module_data.get("confidence", 0.0) > 0.5:
                    if module_field not in patterns["module_contributions"]:
                        patterns["module_contributions"][module_field] = 0
                    patterns["module_contributions"][module_field] += 1
        
        # Calculate threat score statistics
        if patterns["threat_scores"]:
            patterns["threat_score_stats"] = {
                "avg": round(mean(patterns["threat_scores"]), 2),
                "min": min(patterns["threat_scores"]),
                "max": max(patterns["threat_scores"]),
                "total": len(patterns["threat_scores"])
            }
        
        return {
            "api_version": API_VERSION,
            "time_range_days": days,
            "patterns": {
                "escalation_levels": dict(patterns["escalation_levels"]),
                "threat_score_stats": patterns.get("threat_score_stats", {}),
                "module_contributions": patterns["module_contributions"],
                "top_sessions": dict(patterns["session_patterns"].most_common(10)),
                "time_distribution": dict(patterns["time_patterns"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat patterns error: {str(e)}")

@analytics_router.get("/threats/timeline")
async def get_threat_timeline(
    days: int = Query(7, description="Number of days for timeline"),
    db: Session = Depends(get_db_session)
):
    """
    Get threat timeline with 11-module integration
    """
    try:
        days = validate_time_range(days)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily threat data
        from sqlalchemy import text
        daily_query = text("""
            SELECT CAST(created_at AS DATE) as date,
                   COUNT(id) as threat_count,
                   AVG(threat_score) as avg_score,
                   COUNT(CASE WHEN escalation_level = 'CRITICAL' THEN 1 END) as critical_count
            FROM threat_logs
            WHERE created_at >= :cutoff_date
            GROUP BY CAST(created_at AS DATE)
            ORDER BY CAST(created_at AS DATE)
        """)
        
        daily_data = db.execute(daily_query, {"cutoff_date": cutoff_date}).fetchall()
        
        timeline = []
        for day in daily_data:
            timeline.append({
                "date": day.date.isoformat(),
                "threat_count": day.threat_count,
                "avg_threat_score": round(day.avg_score, 2) if day.avg_score else 0,
                "critical_threats": day.critical_count
            })
        
        return {
            "api_version": API_VERSION,
            "timeline_days": days,
            "timeline": timeline
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline error: {str(e)}")

@analytics_router.get("/realtime/current")
async def get_current_activity(
    db: Session = Depends(get_db_session)
):
    """
    Get current real-time activity with 11-module status
    """
    try:
        # Get recent activity (last hour)
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        
        # Recent threats
        recent_threats = db.query(ThreatLog).filter(
            ThreatLog.created_at >= recent_cutoff
        ).order_by(desc(ThreatLog.created_at)).limit(10).all()
        
        # Recent sessions
        recent_sessions = db.query(Telemetry).filter(
            Telemetry.timestamp >= recent_cutoff
        ).order_by(desc(Telemetry.timestamp)).limit(10).all()
        
        # Module activity in last hour
        module_activity = {}
        for module_field in TDC_MODULES.keys():
            module_count = db.query(func.count(ThreatLog.id)).filter(
                ThreatLog.created_at >= recent_cutoff,
                getattr(ThreatLog, module_field).isnot(None)
            ).scalar() or 0
            module_activity[module_field] = module_count
        
        return {
            "api_version": API_VERSION,
            "current_time": datetime.utcnow().isoformat(),
            "activity_window": "1 hour",
            "recent_threats": [
                {
                    "timestamp": threat.created_at.isoformat(),
                    "session_id": threat.session_id,
                    "threat_score": threat.threat_score,
                    "escalation_level": threat.escalation_level
                } for threat in recent_threats
            ],
            "recent_sessions": [
                {
                    "timestamp": session.timestamp,
                    "session_id": session.session_id,
                    "sender": session.sender,
                    "type_indicator": session.type_indicator
                } for session in recent_sessions
            ],
            "module_activity": module_activity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time activity error: {str(e)}")

# === HEALTH AND STATUS ENDPOINTS ===

@analytics_router.get("/health")
async def analytics_health():
    """
    Analytics API health check
    """
    return {
        "api_version": API_VERSION,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "modules_supported": len(TDC_MODULES)
    }

@analytics_router.get("/status")
async def analytics_status(db: Session = Depends(get_db_session)):
    """
    Analytics API detailed status
    """
    try:
        # Get basic statistics
        total_threats = db.query(func.count(ThreatLog.id)).scalar() or 0
        total_sessions = db.query(func.count(Telemetry.session_id.distinct())).scalar() or 0
        
        # Check module data availability
        module_status = {}
        for module_field in TDC_MODULES.keys():
            module_count = db.query(func.count(ThreatLog.id)).filter(
                getattr(ThreatLog, module_field).isnot(None)
            ).scalar() or 0
            module_status[module_field] = {
                "available_records": module_count,
                "status": "active" if module_count > 0 else "no_data"
            }
        
        return {
            "api_version": API_VERSION,
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "database_stats": {
                "total_threats": total_threats,
                "total_sessions": total_sessions
            },
            "module_status": module_status,
            "supported_modules": TDC_MODULES
        }
    except Exception as e:
        return {
            "api_version": API_VERSION,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }