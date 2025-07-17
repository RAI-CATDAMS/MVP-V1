"""
CATDAMS False Positive Reduction Module
========================================

This module implements advanced false positive reduction techniques including:
- Context-aware filtering
- Confidence scoring
- User behavior baselines
- Historical pattern recognition
- Machine learning-based adjustments
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import sqlite3
import threading

@dataclass
class UserBaseline:
    """User behavior baseline for false positive reduction"""
    user_id: str
    avg_message_length: float
    common_platforms: List[str]
    typical_session_duration: float
    risk_score_distribution: Dict[str, float]
    last_updated: datetime
    confidence: float

@dataclass
class ContextFilter:
    """Context-based filtering rules"""
    rule_id: str
    name: str
    conditions: Dict[str, Any]
    action: str  # 'allow', 'block', 'review'
    confidence_threshold: float
    enabled: bool
    created_at: datetime
    performance_metrics: Dict[str, float]

class FalsePositiveReducer:
    """
    Advanced false positive reduction system for CATDAMS
    """
    
    def __init__(self, db_path: str = "catdams.db"):
        self.db_path = db_path
        self.user_baselines: Dict[str, UserBaseline] = {}
        self.context_filters: List[ContextFilter] = []
        self.false_positive_db: Dict[str, Dict] = {}
        self.confidence_adjustments: Dict[str, float] = {}
        self.lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Load existing data
        self._load_user_baselines()
        self._load_context_filters()
        self._load_false_positive_db()
        
        # Performance tracking
        self.performance_metrics = {
            'total_events': 0,
            'false_positives_reduced': 0,
            'confidence_adjustments': 0,
            'baseline_updates': 0
        }
    
    def _init_database(self):
        """Initialize database tables for false positive reduction"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_baselines (
                    user_id TEXT PRIMARY KEY,
                    avg_message_length REAL,
                    common_platforms TEXT,
                    typical_session_duration REAL,
                    risk_score_distribution TEXT,
                    last_updated TEXT,
                    confidence REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_filters (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT,
                    conditions TEXT,
                    action TEXT,
                    confidence_threshold REAL,
                    enabled INTEGER,
                    created_at TEXT,
                    performance_metrics TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS false_positive_patterns (
                    pattern_hash TEXT PRIMARY KEY,
                    pattern_data TEXT,
                    confidence REAL,
                    created_at TEXT,
                    usage_count INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS confidence_adjustments (
                    adjustment_id TEXT PRIMARY KEY,
                    module_name TEXT,
                    adjustment_factor REAL,
                    reason TEXT,
                    created_at TEXT
                )
            """)
    
    def _load_user_baselines(self):
        """Load user behavior baselines from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM user_baselines")
            for row in cursor.fetchall():
                baseline = UserBaseline(
                    user_id=row[0],
                    avg_message_length=row[1],
                    common_platforms=json.loads(row[2]) if row[2] else [],
                    typical_session_duration=row[3],
                    risk_score_distribution=json.loads(row[4]) if row[4] else {},
                    last_updated=datetime.fromisoformat(row[5]),
                    confidence=row[6]
                )
                self.user_baselines[baseline.user_id] = baseline
    
    def _load_context_filters(self):
        """Load context-based filtering rules"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM context_filters WHERE enabled = 1")
            for row in cursor.fetchall():
                filter_rule = ContextFilter(
                    rule_id=row[0],
                    name=row[1],
                    conditions=json.loads(row[2]),
                    action=row[3],
                    confidence_threshold=row[4],
                    enabled=bool(row[5]),
                    created_at=datetime.fromisoformat(row[6]),
                    performance_metrics=json.loads(row[7]) if row[7] else {}
                )
                self.context_filters.append(filter_rule)
    
    def _load_false_positive_db(self):
        """Load false positive patterns database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM false_positive_patterns")
            for row in cursor.fetchall():
                self.false_positive_db[row[0]] = {
                    'pattern_data': json.loads(row[1]),
                    'confidence': row[2],
                    'created_at': datetime.fromisoformat(row[3]),
                    'usage_count': row[4]
                }
    
    def analyze_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an event for false positive reduction
        
        Args:
            event_data: The event data to analyze
            
        Returns:
            Enhanced event data with false positive reduction applied
        """
        with self.lock:
            self.performance_metrics['total_events'] += 1
            
            # Extract key information
            user_id = event_data.get('user_id', 'unknown')
            session_id = event_data.get('session_id', 'unknown')
            threat_level = event_data.get('threat_level', 'Low')
            threat_vector = event_data.get('threat_vector', 'Unknown')
            source = event_data.get('source', 'Unknown')
            
            # Step 1: Context-aware filtering
            context_score = self._apply_context_filters(event_data)
            
            # Step 2: User behavior baseline analysis
            baseline_score = self._analyze_user_baseline(user_id, event_data)
            
            # Step 3: Historical pattern recognition
            pattern_score = self._check_historical_patterns(event_data)
            
            # Step 4: Confidence adjustment
            confidence_adjustment = self._calculate_confidence_adjustment(event_data)
            
            # Step 5: Multi-factor confidence calculation
            final_confidence = self._calculate_final_confidence(
                context_score, baseline_score, pattern_score, confidence_adjustment
            )
            
            # Step 6: Apply confidence-based filtering
            filtered_event = self._apply_confidence_filtering(event_data, final_confidence)
            
            # Step 7: Update baselines and patterns
            self._update_user_baseline(user_id, event_data)
            self._update_false_positive_patterns(event_data)
            
            return filtered_event
    
    def _apply_context_filters(self, event_data: Dict[str, Any]) -> float:
        """Apply context-based filtering rules"""
        context_score = 1.0
        
        for filter_rule in self.context_filters:
            if self._evaluate_filter_conditions(filter_rule.conditions, event_data):
                if filter_rule.action == 'allow':
                    context_score *= 0.5  # Reduce confidence
                elif filter_rule.action == 'block':
                    context_score *= 0.1  # Significantly reduce confidence
                elif filter_rule.action == 'review':
                    context_score *= 0.8  # Moderate reduction
                
                # Update performance metrics
                self._update_filter_performance(filter_rule.rule_id, True)
        
        return context_score
    
    def _evaluate_filter_conditions(self, conditions: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Evaluate if event matches filter conditions"""
        for key, expected_value in conditions.items():
            actual_value = event_data.get(key)
            
            if isinstance(expected_value, dict):
                # Complex condition (e.g., range, regex)
                if 'min' in expected_value and actual_value < expected_value['min']:
                    return False
                if 'max' in expected_value and actual_value > expected_value['max']:
                    return False
                if 'regex' in expected_value:
                    import re
                    if not re.search(expected_value['regex'], str(actual_value)):
                        return False
            else:
                # Simple equality check
                if actual_value != expected_value:
                    return False
        
        return True
    
    def _analyze_user_baseline(self, user_id: str, event_data: Dict[str, Any]) -> float:
        """Analyze event against user behavior baseline"""
        baseline = self.user_baselines.get(user_id)
        if not baseline:
            return 1.0  # No baseline, no adjustment
        
        baseline_score = 1.0
        
        # Check message length
        message_length = len(str(event_data.get('message', '')))
        if abs(message_length - baseline.avg_message_length) > baseline.avg_message_length * 0.5:
            baseline_score *= 0.9
        
        # Check platform usage
        source = event_data.get('source', '')
        if source not in baseline.common_platforms:
            baseline_score *= 0.8
        
        # Check risk score distribution
        threat_level = event_data.get('threat_level', 'Low')
        expected_frequency = baseline.risk_score_distribution.get(threat_level, 0.1)
        if expected_frequency < 0.05:  # Very rare for this user
            baseline_score *= 0.7
        
        return baseline_score
    
    def _check_historical_patterns(self, event_data: Dict[str, Any]) -> float:
        """Check for known false positive patterns"""
        pattern_hash = self._generate_pattern_hash(event_data)
        
        if pattern_hash in self.false_positive_db:
            pattern_info = self.false_positive_db[pattern_hash]
            return pattern_info['confidence']
        
        return 1.0
    
    def _generate_pattern_hash(self, event_data: Dict[str, Any]) -> str:
        """Generate hash for pattern matching"""
        pattern_key = f"{event_data.get('threat_vector', '')}_{event_data.get('source', '')}_{event_data.get('threat_level', '')}"
        return hashlib.md5(pattern_key.encode()).hexdigest()
    
    def _calculate_confidence_adjustment(self, event_data: Dict[str, Any]) -> float:
        """Calculate confidence adjustment based on historical data"""
        adjustment = 1.0
        
        # Check for module-specific adjustments
        for module_name, adjustment_factor in self.confidence_adjustments.items():
            if module_name in str(event_data):
                adjustment *= adjustment_factor
        
        return adjustment
    
    def _calculate_final_confidence(self, context_score: float, baseline_score: float, 
                                  pattern_score: float, confidence_adjustment: float) -> float:
        """Calculate final confidence score using weighted average"""
        weights = {
            'context': 0.3,
            'baseline': 0.25,
            'pattern': 0.25,
            'adjustment': 0.2
        }
        
        final_confidence = (
            context_score * weights['context'] +
            baseline_score * weights['baseline'] +
            pattern_score * weights['pattern'] +
            confidence_adjustment * weights['adjustment']
        )
        
        return max(0.0, min(1.0, final_confidence))
    
    def _apply_confidence_filtering(self, event_data: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Apply confidence-based filtering to event"""
        # Apply confidence threshold
        if confidence < 0.3:  # Very low confidence
            event_data['filtered_out'] = True
            event_data['filter_reason'] = 'Low confidence score'
            self.performance_metrics['false_positives_reduced'] += 1
        elif confidence < 0.6:  # Moderate confidence
            event_data['requires_review'] = True
            event_data['confidence_score'] = confidence
        else:  # High confidence
            event_data['confidence_score'] = confidence
        
        # Adjust threat level based on confidence
        if confidence < 0.5:
            original_level = event_data.get('threat_level', 'Low')
            if original_level in ['Critical', 'High']:
                event_data['threat_level'] = 'Medium'
                event_data['level_adjusted'] = True
        
        return event_data
    
    def _update_user_baseline(self, user_id: str, event_data: Dict[str, Any]):
        """Update user behavior baseline"""
        baseline = self.user_baselines.get(user_id)
        
        if not baseline:
            # Create new baseline
            baseline = UserBaseline(
                user_id=user_id,
                avg_message_length=len(str(event_data.get('message', ''))),
                common_platforms=[event_data.get('source', '')],
                typical_session_duration=0.0,
                risk_score_distribution={event_data.get('threat_level', 'Low'): 1.0},
                last_updated=datetime.now(),
                confidence=0.5
            )
            self.user_baselines[user_id] = baseline
        else:
            # Update existing baseline
            message_length = len(str(event_data.get('message', '')))
            baseline.avg_message_length = (baseline.avg_message_length + message_length) / 2
            
            source = event_data.get('source', '')
            if source not in baseline.common_platforms:
                baseline.common_platforms.append(source)
            
            threat_level = event_data.get('threat_level', 'Low')
            baseline.risk_score_distribution[threat_level] = \
                baseline.risk_score_distribution.get(threat_level, 0) + 1
            
            baseline.last_updated = datetime.now()
            baseline.confidence = min(1.0, baseline.confidence + 0.01)
        
        # Save to database
        self._save_user_baseline(baseline)
        self.performance_metrics['baseline_updates'] += 1
    
    def _update_false_positive_patterns(self, event_data: Dict[str, Any]):
        """Update false positive patterns database"""
        pattern_hash = self._generate_pattern_hash(event_data)
        
        if pattern_hash in self.false_positive_db:
            # Update existing pattern
            pattern_info = self.false_positive_db[pattern_hash]
            pattern_info['usage_count'] += 1
            pattern_info['confidence'] = min(1.0, pattern_info['confidence'] + 0.05)
        else:
            # Create new pattern
            self.false_positive_db[pattern_hash] = {
                'pattern_data': {
                    'threat_vector': event_data.get('threat_vector'),
                    'source': event_data.get('source'),
                    'threat_level': event_data.get('threat_level')
                },
                'confidence': 0.5,
                'created_at': datetime.now(),
                'usage_count': 1
            }
    
    def _save_user_baseline(self, baseline: UserBaseline):
        """Save user baseline to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_baselines 
                (user_id, avg_message_length, common_platforms, typical_session_duration, 
                 risk_score_distribution, last_updated, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                baseline.user_id,
                baseline.avg_message_length,
                json.dumps(baseline.common_platforms),
                baseline.typical_session_duration,
                json.dumps(baseline.risk_score_distribution),
                baseline.last_updated.isoformat(),
                baseline.confidence
            ))
    
    def _update_filter_performance(self, rule_id: str, matched: bool):
        """Update filter performance metrics"""
        for filter_rule in self.context_filters:
            if filter_rule.rule_id == rule_id:
                metrics = filter_rule.performance_metrics
                metrics['total_matches'] = metrics.get('total_matches', 0) + 1
                if matched:
                    metrics['successful_matches'] = metrics.get('successful_matches', 0) + 1
                metrics['success_rate'] = metrics['successful_matches'] / metrics['total_matches']
                break
    
    def add_context_filter(self, name: str, conditions: Dict[str, Any], 
                          action: str, confidence_threshold: float = 0.5) -> str:
        """Add a new context-based filter"""
        rule_id = f"filter_{int(time.time())}"
        
        filter_rule = ContextFilter(
            rule_id=rule_id,
            name=name,
            conditions=conditions,
            action=action,
            confidence_threshold=confidence_threshold,
            enabled=True,
            created_at=datetime.now(),
            performance_metrics={}
        )
        
        self.context_filters.append(filter_rule)
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO context_filters 
                (rule_id, name, conditions, action, confidence_threshold, enabled, created_at, performance_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule_id, name, json.dumps(conditions), action, confidence_threshold, 
                1, datetime.now().isoformat(), '{}'
            ))
        
        return rule_id
    
    def set_confidence_adjustment(self, module_name: str, adjustment_factor: float, reason: str = ""):
        """Set confidence adjustment for a specific module"""
        self.confidence_adjustments[module_name] = adjustment_factor
        
        # Save to database
        adjustment_id = f"adj_{int(time.time())}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO confidence_adjustments 
                (adjustment_id, module_name, adjustment_factor, reason, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (adjustment_id, module_name, adjustment_factor, reason, datetime.now().isoformat()))
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            **self.performance_metrics,
            'user_baselines_count': len(self.user_baselines),
            'context_filters_count': len(self.context_filters),
            'false_positive_patterns_count': len(self.false_positive_db),
            'confidence_adjustments_count': len(self.confidence_adjustments)
        }
    
    def export_false_positive_data(self) -> Dict[str, Any]:
        """Export false positive reduction data for analysis"""
        return {
            'user_baselines': {
                user_id: {
                    'avg_message_length': baseline.avg_message_length,
                    'common_platforms': baseline.common_platforms,
                    'risk_score_distribution': baseline.risk_score_distribution,
                    'confidence': baseline.confidence
                }
                for user_id, baseline in self.user_baselines.items()
            },
            'context_filters': [
                {
                    'name': filter_rule.name,
                    'conditions': filter_rule.conditions,
                    'action': filter_rule.action,
                    'performance_metrics': filter_rule.performance_metrics
                }
                for filter_rule in self.context_filters
            ],
            'false_positive_patterns': self.false_positive_db,
            'confidence_adjustments': self.confidence_adjustments,
            'performance_metrics': self.performance_metrics
        }

# Global instance
false_positive_reducer = FalsePositiveReducer()

def reduce_false_positives(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to reduce false positives in an event
    
    Args:
        event_data: The event data to process
        
    Returns:
        Processed event data with false positive reduction applied
    """
    return false_positive_reducer.analyze_event(event_data)

def get_false_positive_metrics() -> Dict[str, Any]:
    """Get false positive reduction performance metrics"""
    return false_positive_reducer.get_performance_metrics()

def export_false_positive_data() -> Dict[str, Any]:
    """Export false positive reduction data"""
    return false_positive_reducer.export_false_positive_data() 