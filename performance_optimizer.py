"""
CATDAMS Performance Optimization Module
=======================================

This module provides comprehensive performance optimization for CATDAMS including:
- Database query optimization
- Caching strategies
- Connection pooling
- Performance monitoring
- Resource management
"""

import time
import json
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from dataclasses import dataclass
import logging
import psutil
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: datetime
    ttl: int  # Time to live in seconds
    access_count: int = 0
    last_accessed: datetime = None

@dataclass
class PerformanceMetric:
    """Performance metric tracking"""
    operation: str
    duration: float
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any]

class DatabaseOptimizer:
    """Database optimization and connection management"""
    
    def __init__(self, db_path: str = "catdams.db"):
        self.db_path = db_path
        self.connection_pool = []
        self.max_connections = 10
        self.connection_timeout = 30
        self.query_cache = {}
        self.query_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'avg_time': 0})
        
        # Initialize connection pool
        self._init_connection_pool()
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _init_connection_pool(self):
        """Initialize database connection pool"""
        for _ in range(self.max_connections):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            self.connection_pool.append(conn)
    
    def _create_indexes(self):
        """Create database indexes for better query performance"""
        with self._get_connection() as conn:
            # Indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_user_id ON telemetry(full_data->>'user_id')")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_session_id ON telemetry(full_data->>'session_id')")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_threat_log_timestamp ON threat_log(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_threat_log_threat_level ON threat_log(threat_level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_threat_log_user_id ON threat_log(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_threat_log_session_id ON threat_log(session_id)")
    
    def _get_connection(self):
        """Get a database connection from the pool"""
        if self.connection_pool:
            return self.connection_pool.pop()
        else:
            # Create new connection if pool is empty
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            return conn
    
    def _return_connection(self, conn):
        """Return a connection to the pool"""
        if len(self.connection_pool) < self.max_connections:
            self.connection_pool.append(conn)
        else:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a database query with performance tracking"""
        start_time = time.time()
        conn = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch results
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Update query statistics
            duration = time.time() - start_time
            self._update_query_stats(query, duration, True)
            
            return results
            
        except Exception as e:
            duration = time.time() - start_time
            self._update_query_stats(query, duration, False)
            logger.error(f"Database query error: {e}")
            raise
        finally:
            if conn:
                self._return_connection(conn)
    
    def _update_query_stats(self, query: str, duration: float, success: bool):
        """Update query performance statistics"""
        stats = self.query_stats[query]
        stats['count'] += 1
        if success:
            stats['total_time'] += duration
            stats['avg_time'] = stats['total_time'] / stats['count']
    
    def get_query_performance(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return {
            'total_queries': sum(stats['count'] for stats in self.query_stats.values()),
            'avg_query_time': sum(stats['avg_time'] for stats in self.query_stats.values()) / len(self.query_stats) if self.query_stats else 0,
            'slowest_queries': sorted(
                [(query, stats['avg_time']) for query, stats in self.query_stats.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

class CacheManager:
    """Advanced caching system with multiple strategies"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = deque()
        self.lock = threading.RLock()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if entry has expired
                if datetime.now() - entry.timestamp > timedelta(seconds=entry.ttl):
                    del self.cache[key]
                    self.access_order.remove(key)
                    self.stats['size'] -= 1
                    self.stats['misses'] += 1
                    return None
                
                # Update access statistics
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                self.access_order.remove(key)
                self.access_order.appendleft(key)
                
                self.stats['hits'] += 1
                return entry.data
            else:
                self.stats['misses'] += 1
                return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache"""
        with self.lock:
            # Evict if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # Create cache entry
            entry = CacheEntry(
                data=value,
                timestamp=datetime.now(),
                ttl=ttl,
                access_count=1,
                last_accessed=datetime.now()
            )
            
            self.cache[key] = entry
            self.access_order.appendleft(key)
            self.stats['size'] = len(self.cache)
    
    def _evict_oldest(self):
        """Evict oldest cache entry"""
        if self.access_order:
            oldest_key = self.access_order.pop()
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries matching pattern"""
        with self.lock:
            if pattern:
                keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            else:
                keys_to_remove = list(self.cache.keys())
            
            for key in keys_to_remove:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
            
            self.stats['size'] = len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) if (self.stats['hits'] + self.stats['misses']) > 0 else 0
        
        return {
            **self.stats,
            'hit_rate': hit_rate,
            'max_size': self.max_size,
            'utilization': self.stats['size'] / self.max_size
        }

class PerformanceMonitor:
    """System performance monitoring and alerting"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.max_metrics = 10000
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 2.0,
            'error_rate': 5.0
        }
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()
    
    def track_operation(self, operation: str, func: Callable, *args, **kwargs) -> Any:
        """Track performance of an operation"""
        start_time = time.time()
        success = False
        
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            logger.error(f"Operation {operation} failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            self._record_metric(operation, duration, success)
    
    def _record_metric(self, operation: str, duration: float, success: bool, metadata: Dict[str, Any] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=datetime.now(),
            success=success,
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        
        # Keep only recent metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        # Check for performance alerts
        self._check_alerts(metric)
    
    def _check_alerts(self, metric: PerformanceMetric):
        """Check for performance alerts"""
        if metric.duration > self.thresholds['response_time']:
            self._create_alert('high_response_time', f"Operation {metric.operation} took {metric.duration:.2f}s")
        
        if not metric.success:
            # Calculate error rate
            recent_metrics = [m for m in self.metrics if m.operation == metric.operation and 
                            (datetime.now() - m.timestamp).seconds < 300]  # Last 5 minutes
            error_rate = (sum(1 for m in recent_metrics if not m.success) / len(recent_metrics)) * 100
            
            if error_rate > self.thresholds['error_rate']:
                self._create_alert('high_error_rate', f"Error rate for {metric.operation}: {error_rate:.1f}%")
    
    def _create_alert(self, alert_type: str, message: str):
        """Create a performance alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now(),
            'severity': 'warning'
        }
        self.alerts.append(alert)
        logger.warning(f"Performance alert: {message}")
    
    def _monitor_system(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > self.thresholds['cpu_usage']:
                    self._create_alert('high_cpu', f"CPU usage: {cpu_percent:.1f}%")
                
                # Memory usage
                memory = psutil.virtual_memory()
                if memory.percent > self.thresholds['memory_usage']:
                    self._create_alert('high_memory', f"Memory usage: {memory.percent:.1f}%")
                
                # Disk usage
                disk = psutil.disk_usage('/')
                if disk.percent > self.thresholds['disk_usage']:
                    self._create_alert('high_disk', f"Disk usage: {disk.percent:.1f}%")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                time.sleep(60)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        # Calculate statistics
        recent_metrics = [m for m in self.metrics if (datetime.now() - m.timestamp).seconds < 3600]  # Last hour
        
        if not recent_metrics:
            return {'error': 'No recent metrics available'}
        
        operations = defaultdict(list)
        for metric in recent_metrics:
            operations[metric.operation].append(metric)
        
        operation_stats = {}
        for operation, metrics in operations.items():
            durations = [m.duration for m in metrics]
            success_count = sum(1 for m in metrics if m.success)
            
            operation_stats[operation] = {
                'count': len(metrics),
                'avg_duration': sum(durations) / len(durations),
                'max_duration': max(durations),
                'min_duration': min(durations),
                'success_rate': (success_count / len(metrics)) * 100
            }
        
        return {
            'system_resources': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            },
            'operation_stats': operation_stats,
            'recent_alerts': self.alerts[-10:],  # Last 10 alerts
            'cache_stats': cache_manager.get_stats(),
            'database_stats': db_optimizer.get_query_performance()
        }

class AsyncTaskManager:
    """Asynchronous task management for performance optimization"""
    
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, Any] = {}
        self.lock = asyncio.Lock()
    
    async def execute_async(self, task_id: str, coro):
        """Execute an asynchronous task"""
        async with self.lock:
            if task_id in self.tasks:
                # Cancel existing task
                self.tasks[task_id].cancel()
            
            # Create new task
            task = asyncio.create_task(coro)
            self.tasks[task_id] = task
        
        try:
            result = await task
            self.task_results[task_id] = result
            return result
        except asyncio.CancelledError:
            logger.info(f"Task {task_id} was cancelled")
            raise
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            raise
        finally:
            async with self.lock:
                if task_id in self.tasks:
                    del self.tasks[task_id]
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                'status': 'running',
                'done': task.done(),
                'cancelled': task.cancelled()
            }
        elif task_id in self.task_results:
            return {
                'status': 'completed',
                'result': self.task_results[task_id]
            }
        else:
            return {'status': 'not_found'}

# Global instances
db_optimizer = DatabaseOptimizer()
cache_manager = CacheManager()
performance_monitor = PerformanceMonitor()
async_task_manager = AsyncTaskManager()

def optimize_query(query: str, params: tuple = None) -> List[Dict]:
    """Optimized database query execution"""
    return performance_monitor.track_operation('database_query', db_optimizer.execute_query, query, params)

def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    return cache_manager.get(key)

def cache_set(key: str, value: Any, ttl: int = 3600):
    """Set value in cache"""
    cache_manager.set(key, value, ttl)

def cache_invalidate(pattern: str = None):
    """Invalidate cache entries"""
    cache_manager.invalidate(pattern)

def get_performance_report() -> Dict[str, Any]:
    """Get comprehensive performance report"""
    return performance_monitor.get_performance_report()

async def execute_async_task(task_id: str, coro):
    """Execute an asynchronous task"""
    return await async_task_manager.execute_async(task_id, coro)

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status"""
    return async_task_manager.get_task_status(task_id)

# Performance decorators
def track_performance(operation_name: str = None):
    """Decorator to track function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            return performance_monitor.track_operation(name, func, *args, **kwargs)
        return wrapper
    return decorator

def cache_result(ttl: int = 3600, key_func: Callable = None):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator 