"""
Performance Monitoring Service
Metrics collection and performance tracking.
"""

import time
import psutil
import functools
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import request, g
from app.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self):
        self.metrics = {}
        self.request_times = []
        self.query_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        
    def record_request_time(self, duration: float, endpoint: str):
        """Record request duration."""
        timestamp = datetime.utcnow()
        
        if 'requests' not in self.metrics:
            self.metrics['requests'] = []
        
        self.metrics['requests'].append({
            'timestamp': timestamp,
            'duration': duration,
            'endpoint': endpoint,
            'method': request.method if request else 'UNKNOWN'
        })
        
        # Keep only last 1000 requests
        if len(self.metrics['requests']) > 1000:
            self.metrics['requests'] = self.metrics['requests'][-1000:]
    
    def record_query_time(self, duration: float, query_type: str):
        """Record database query duration."""
        timestamp = datetime.utcnow()
        
        if 'queries' not in self.metrics:
            self.metrics['queries'] = []
        
        self.metrics['queries'].append({
            'timestamp': timestamp,
            'duration': duration,
            'type': query_type
        })
        
        # Keep only last 500 queries
        if len(self.metrics['queries']) > 500:
            self.metrics['queries'] = self.metrics['queries'][-500:]
    
    def record_cache_hit(self):
        """Record cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        self.cache_misses += 1
    
    def get_system_metrics(self) -> Dict:
        """Get system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def get_request_metrics(self, minutes: int = 5) -> Dict:
        """Get request performance metrics."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            # Filter recent requests
            recent_requests = [
                r for r in self.metrics.get('requests', [])
                if r['timestamp'] > cutoff_time
            ]
            
            if not recent_requests:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'max_response_time': 0,
                    'min_response_time': 0,
                    'requests_per_minute': 0,
                    'slow_requests': 0,
                    'endpoint_breakdown': {}
                }
            
            # Calculate metrics
            response_times = [r['duration'] for r in recent_requests]
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            slow_requests = len([r for r in recent_requests if r['duration'] > 2.0])  # > 2 seconds
            
            # Endpoint breakdown
            endpoint_breakdown = {}
            for req in recent_requests:
                endpoint = req['endpoint']
                if endpoint not in endpoint_breakdown:
                    endpoint_breakdown[endpoint] = {
                        'count': 0,
                        'total_time': 0,
                        'avg_time': 0
                    }
                endpoint_breakdown[endpoint]['count'] += 1
                endpoint_breakdown[endpoint]['total_time'] += req['duration']
            
            # Calculate averages for each endpoint
            for endpoint, data in endpoint_breakdown.items():
                data['avg_time'] = data['total_time'] / data['count']
            
            return {
                'total_requests': len(recent_requests),
                'avg_response_time': round(avg_response_time, 3),
                'max_response_time': round(max_response_time, 3),
                'min_response_time': round(min_response_time, 3),
                'requests_per_minute': round(len(recent_requests) / minutes, 2),
                'slow_requests': slow_requests,
                'endpoint_breakdown': endpoint_breakdown,
                'period_minutes': minutes
            }
            
        except Exception as e:
            logger.error(f"Error getting request metrics: {e}")
            return {}
    
    def get_database_metrics(self, minutes: int = 5) -> Dict:
        """Get database performance metrics."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            # Filter recent queries
            recent_queries = [
                q for q in self.metrics.get('queries', [])
                if q['timestamp'] > cutoff_time
            ]
            
            if not recent_queries:
                return {
                    'total_queries': 0,
                    'avg_query_time': 0,
                    'max_query_time': 0,
                    'slow_queries': 0,
                    'query_type_breakdown': {}
                }
            
            # Calculate metrics
            query_times = [q['duration'] for q in recent_queries]
            avg_query_time = sum(query_times) / len(query_times)
            max_query_time = max(query_times)
            slow_queries = len([q for q in recent_queries if q['duration'] > 1.0])  # > 1 second
            
            # Query type breakdown
            query_type_breakdown = {}
            for query in recent_queries:
                qtype = query['type']
                if qtype not in query_type_breakdown:
                    query_type_breakdown[qtype] = {
                        'count': 0,
                        'total_time': 0,
                        'avg_time': 0
                    }
                query_type_breakdown[qtype]['count'] += 1
                query_type_breakdown[qtype]['total_time'] += query['duration']
            
            # Calculate averages for each query type
            for qtype, data in query_type_breakdown.items():
                data['avg_time'] = data['total_time'] / data['count']
            
            return {
                'total_queries': len(recent_queries),
                'avg_query_time': round(avg_query_time, 3),
                'max_query_time': round(max_query_time, 3),
                'slow_queries': slow_queries,
                'query_type_breakdown': query_type_breakdown,
                'period_minutes': minutes
            }
            
        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {}
    
    def get_cache_metrics(self) -> Dict:
        """Get cache performance metrics."""
        try:
            cache_info = cache_service.get_cache_info()
            
            total_requests = self.cache_hits + self.cache_misses
            hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'total_requests': total_requests,
                'hit_rate_percent': round(hit_rate, 2),
                'redis_info': cache_info
            }
            
        except Exception as e:
            logger.error(f"Error getting cache metrics: {e}")
            return {}
    
    def get_health_status(self) -> Dict:
        """Get overall application health status."""
        try:
            system_metrics = self.get_system_metrics()
            request_metrics = self.get_request_metrics()
            cache_metrics = self.get_cache_metrics()
            
            # Determine health status
            health_status = 'HEALTHY'
            issues = []
            
            # Check CPU usage
            if system_metrics.get('cpu_percent', 0) > 80:
                health_status = 'WARNING'
                issues.append('High CPU usage')
            
            # Check memory usage
            if system_metrics.get('memory_percent', 0) > 85:
                health_status = 'WARNING'
                issues.append('High memory usage')
            
            # Check response times
            if request_metrics.get('avg_response_time', 0) > 2.0:
                health_status = 'WARNING'
                issues.append('Slow response times')
            
            # Check cache hit rate
            if cache_metrics.get('hit_rate_percent', 0) < 50:
                health_status = 'WARNING'
                issues.append('Low cache hit rate')
            
            # Critical issues
            if system_metrics.get('cpu_percent', 0) > 95 or system_metrics.get('memory_percent', 0) > 95:
                health_status = 'CRITICAL'
                issues.append('Critical resource usage')
            
            return {
                'status': health_status,
                'issues': issues,
                'system_metrics': system_metrics,
                'request_metrics': request_metrics,
                'cache_metrics': cache_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'UNKNOWN',
                'issues': ['Unable to collect metrics'],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary."""
        try:
            return {
                'health': self.get_health_status(),
                'system': self.get_system_metrics(),
                'requests': self.get_request_metrics(),
                'database': self.get_database_metrics(),
                'cache': self.get_cache_metrics()
            }
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(func):
    """Decorator to monitor function performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record performance metrics
            if hasattr(request, 'endpoint'):
                performance_monitor.record_request_time(duration, request.endpoint)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper


def monitor_database_query(query_type: str = 'unknown'):
    """Decorator to monitor database query performance."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                performance_monitor.record_query_time(duration, query_type)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"DB query {query_type} failed after {duration:.3f}s: {e}")
                raise
        return wrapper
    return decorator


class RequestTimer:
    """Context manager for timing requests."""
    
    def __init__(self, endpoint: str = 'unknown'):
        self.endpoint = endpoint
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            performance_monitor.record_request_time(duration, self.endpoint)


class QueryTimer:
    """Context manager for timing database queries."""
    
    def __init__(self, query_type: str = 'unknown'):
        self.query_type = query_type
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            performance_monitor.record_query_time(duration, self.query_type)


# Flask before/after request handlers
def setup_request_monitoring(app):
    """Setup Flask request monitoring."""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            endpoint = request.endpoint or 'unknown'
            performance_monitor.record_request_time(duration, endpoint)
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response


# Cache monitoring wrapper
def cached_function(ttl: int = 3600, cache_key: str = None):
    """Decorator to cache function results with monitoring."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key:
                key = cache_key
            else:
                key = f"func:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try cache
            cached_result = cache_service.get(key)
            if cached_result is not None:
                performance_monitor.record_cache_hit()
                return cached_result
            
            # Cache miss - execute function
            performance_monitor.record_cache_miss()
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Cache result
            cache_service.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator
