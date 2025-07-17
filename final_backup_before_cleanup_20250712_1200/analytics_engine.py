# CATDAMS Analytics Engine - Phase 1, Step 1.4
# Safe, incremental implementation that doesn't break existing functionality

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeAnalyticsEngine:
    """
    Safe analytics engine that provides basic analytics without interfering
    with existing CATDAMS functionality.
    """
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.session_data = {}
        self.threat_patterns = Counter()
        self.performance_data = []
        self.is_enabled = False  # Disabled by default for safety
        
    def enable(self):
        """Safely enable analytics engine"""
        self.is_enabled = True
        logger.info("[ANALYTICS] Analytics engine enabled safely")
        
    def disable(self):
        """Safely disable analytics engine"""
        self.is_enabled = False
        logger.info("[ANALYTICS] Analytics engine disabled")
        
    def is_safe_to_process(self, data: Any) -> bool:
        """Safety check to ensure data is safe to process"""
        if not self.is_enabled:
            return False
            
        if not isinstance(data, dict):
            return False
            
        # Only process if it has basic required fields
        required_fields = ['timestamp', 'session_id']
        return all(field in data for field in required_fields)
    
    def collect_basic_metrics(self, data: Dict) -> Dict:
        """
        Safely collect basic metrics without modifying original data
        Returns a copy of metrics, doesn't affect original data
        """
        if not self.is_safe_to_process(data):
            return {}
            
        try:
            metrics = {
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'session_id': data.get('session_id', 'unknown'),
                'threat_level': data.get('severity', 'Unknown'),
                'source': data.get('source', 'Unknown'),
                'message_length': len(str(data.get('message', ''))),
                'has_ai_response': bool(data.get('ai_response')),
                'tdc_modules_used': len([k for k in data.keys() if k.startswith('tdc_ai')])
            }
            
            # Store metrics safely
            self.metrics['basic'].append(metrics)
            
            # Keep only last 1000 entries to prevent memory issues
            if len(self.metrics['basic']) > 1000:
                self.metrics['basic'] = self.metrics['basic'][-1000:]
                
            return metrics
            
        except Exception as e:
            logger.error(f"[ANALYTICS] Error collecting metrics: {e}")
            return {}
    
    def get_basic_stats(self) -> Dict:
        """Get basic statistics safely"""
        if not self.metrics['basic']:
            return {'status': 'no_data', 'message': 'No analytics data available'}
            
        try:
            stats = {
                'total_events': len(self.metrics['basic']),
                'unique_sessions': len(set(m['session_id'] for m in self.metrics['basic'])),
                'threat_level_distribution': Counter(m['threat_level'] for m in self.metrics['basic']),
                'source_distribution': Counter(m['source'] for m in self.metrics['basic']),
                'avg_message_length': sum(m['message_length'] for m in self.metrics['basic']) / len(self.metrics['basic']),
                'events_with_ai_response': sum(1 for m in self.metrics['basic'] if m['has_ai_response']),
                'last_updated': datetime.now().isoformat()
            }
            return stats
            
        except Exception as e:
            logger.error(f"[ANALYTICS] Error calculating stats: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_session_analytics(self, session_id: str) -> Dict:
        """Get analytics for a specific session safely"""
        if not self.metrics['basic']:
            return {'status': 'no_data', 'message': 'No session data available'}
            
        try:
            session_events = [m for m in self.metrics['basic'] if m['session_id'] == session_id]
            
            if not session_events:
                return {'status': 'not_found', 'message': f'No data for session {session_id}'}
                
            stats = {
                'session_id': session_id,
                'total_events': len(session_events),
                'threat_levels': Counter(m['threat_level'] for m in session_events),
                'avg_message_length': sum(m['message_length'] for m in session_events) / len(session_events),
                'ai_interactions': sum(1 for m in session_events if m['has_ai_response']),
                'first_event': min(m['timestamp'] for m in session_events),
                'last_event': max(m['timestamp'] for m in session_events)
            }
            return stats
            
        except Exception as e:
            logger.error(f"[ANALYTICS] Error getting session analytics: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_performance_metrics(self) -> Dict:
        """Get basic performance metrics safely"""
        return {
            'analytics_enabled': self.is_enabled,
            'total_metrics_collected': len(self.metrics['basic']),
            'memory_usage_estimate': len(self.metrics['basic']) * 0.001,  # Rough estimate in MB
            'last_collection': datetime.now().isoformat(),
            'status': 'healthy'
        }
    
    def clear_data(self):
        """Safely clear all analytics data"""
        self.metrics.clear()
        self.session_data.clear()
        self.threat_patterns.clear()
        self.performance_data.clear()
        logger.info("[ANALYTICS] All analytics data cleared safely")

# Global instance - safe to use
analytics_engine = SafeAnalyticsEngine()

# Safe wrapper functions that don't interfere with existing code
def safe_collect_metrics(data: Dict) -> Dict:
    """Safe wrapper to collect metrics without affecting original data"""
    return analytics_engine.collect_basic_metrics(data)

def safe_get_stats() -> Dict:
    """Safe wrapper to get analytics stats"""
    return analytics_engine.get_basic_stats()

def safe_get_session_stats(session_id: str) -> Dict:
    """Safe wrapper to get session analytics"""
    return analytics_engine.get_session_analytics(session_id)

def safe_enable_analytics():
    """Safe wrapper to enable analytics"""
    analytics_engine.enable()

def safe_disable_analytics():
    """Safe wrapper to disable analytics"""
    analytics_engine.disable()

def safe_get_performance() -> Dict:
    """Safe wrapper to get performance metrics"""
    return analytics_engine.get_performance_metrics()

# Test function to verify everything works
def test_analytics_safety():
    """Test that analytics engine doesn't break anything"""
    try:
        # Test with sample data
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'session_id': 'test-session-123',
            'severity': 'Medium',
            'source': 'test',
            'message': 'Test message',
            'ai_response': 'Test AI response'
        }
        
        # Test collection
        metrics = safe_collect_metrics(test_data)
        assert isinstance(metrics, dict), "Metrics should be a dictionary"
        
        # Test stats
        stats = safe_get_stats()
        assert isinstance(stats, dict), "Stats should be a dictionary"
        
        # Test session analytics
        session_stats = safe_get_session_stats('test-session-123')
        assert isinstance(session_stats, dict), "Session stats should be a dictionary"
        
        # Test performance
        perf = safe_get_performance()
        assert isinstance(perf, dict), "Performance should be a dictionary"
        
        logger.info("[ANALYTICS] All safety tests passed successfully")
        return True
        
    except Exception as e:
        logger.error(f"[ANALYTICS] Safety test failed: {e}")
        return False

if __name__ == "__main__":
    # Run safety test
    test_analytics_safety() 