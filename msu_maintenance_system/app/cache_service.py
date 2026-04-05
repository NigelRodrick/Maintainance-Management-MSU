"""
Caching Service
Redis-based caching for frequently accessed data.
"""

import json
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import timedelta
import redis
from app.extensions import cache


class CacheService:
    """Redis caching service with serialization and TTL management."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or cache
        self.default_ttl = 3600  # 1 hour default TTL
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return default
            
            # Try to deserialize as JSON only (removed pickle for security)
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # For non-JSON data, try to decode as string
                try:
                    return value.decode('utf-8')
                except (AttributeError, UnicodeDecodeError):
                    return value
        except Exception as e:
            # Log error but don't break application
            print(f"Cache get error for key {key}: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        try:
            # Serialize value
            if isinstance(value, (dict, list, tuple, bool)) or value is None:
                serialized = json.dumps(value, default=str)
            elif hasattr(value, '__dict__'):
                # For objects, try JSON first, then pickle
                try:
                    serialized = json.dumps(value.__dict__, default=str)
                except (TypeError, ValueError):
                    serialized = pickle.dumps(value)
            else:
                serialized = str(value)
            
            # Set with TTL
            expire_time = ttl or self.default_ttl
            return self.redis_client.setex(key, expire_time, serialized)
        except Exception as e:
            # Log error but don't break application
            print(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error for key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for existing key."""
        try:
            return bool(self.redis_client.expire(key, ttl))
        except Exception as e:
            print(f"Cache expire error for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            print(f"Cache TTL error for key {key}: {e}")
            return -1
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value."""
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Cache increment error for key {key}: {e}")
            return 0
    
    def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement numeric value."""
        try:
            return self.redis_client.decrby(key, amount)
        except Exception as e:
            print(f"Cache decrement error for key {key}: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """Clear all cache data (use with caution)."""
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False


class CacheKeys:
    """Cache key constants."""
    
    # User-related cache keys
    USER_PROFILE = "user:profile:{user_id}"
    USER_PERMISSIONS = "user:permissions:{user_id}"
    USER_STATS = "user:stats:{user_id}"
    
    # Job-related cache keys
    JOB_LIST = "jobs:list:{page}:{filters}"
    JOB_STATS = "jobs:stats"
    JOB_DETAIL = "job:detail:{job_id}"
    JOB_BY_STATUS = "jobs:status:{status}"
    JOB_BY_DEPARTMENT = "jobs:department:{department}"
    
    # Worker-related cache keys
    WORKER_LIST = "workers:list:{page}:{filters}"
    WORKER_STATS = "worker:stats"
    WORKER_AVAILABLE = "workers:available:{skill_category}"
    WORKER_PERFORMANCE = "worker:performance:{worker_id}"
    
    # Assignment-related cache keys
    ASSIGNMENT_LIST = "assignments:list:{page}:{filters}"
    ASSIGNMENT_STATS = "assignments:stats"
    ASSIGNMENT_ACTIVE = "assignments:active"
    
    # Material-related cache keys
    MATERIAL_LIST = "materials:list:{page}:{filters}"
    MATERIAL_STATS = "materials:stats"
    MATERIAL_SUMMARY = "materials:summary:{job_id}"
    
    # Dashboard cache keys
    DASHBOARD_STATS = "dashboard:stats"
    DASHBOARD_RECENT = "dashboard:recent:{days}"
    
    # Search cache keys
    SEARCH_RESULTS = "search:{query_hash}"
    
    # Session cache keys
    SESSION_DATA = "session:{session_id}"
    RATE_LIMIT = "rate_limit:{identifier}:{window}"


class CacheService:
    """Enhanced cache service with domain-specific methods."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or cache
        self.default_ttl = 3600  # 1 hour default TTL
        self.keys = CacheKeys()
    
    def cache_user_profile(self, user_id: int, profile_data: Dict, ttl: int = 1800) -> bool:
        """Cache user profile data."""
        key = self.keys.USER_PROFILE.format(user_id=user_id)
        return self.set(key, profile_data, ttl)
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get cached user profile."""
        key = self.keys.USER_PROFILE.format(user_id=user_id)
        return self.get(key)
    
    def cache_job_stats(self, stats_data: Dict, ttl: int = 300) -> bool:
        """Cache job statistics."""
        key = self.keys.JOB_STATS
        return self.set(key, stats_data, ttl)
    
    def get_job_stats(self) -> Optional[Dict]:
        """Get cached job statistics."""
        key = self.keys.JOB_STATS
        return self.get(key)
    
    def cache_job_list(self, page: int, filters: str, jobs_data: List, ttl: int = 600) -> bool:
        """Cache job list with pagination."""
        key = self.keys.JOB_LIST.format(page=page, filters=filters)
        return self.set(key, jobs_data, ttl)
    
    def get_job_list(self, page: int, filters: str) -> Optional[List]:
        """Get cached job list."""
        key = self.keys.JOB_LIST.format(page=page, filters=filters)
        return self.get(key)
    
    def cache_worker_stats(self, stats_data: Dict, ttl: int = 300) -> bool:
        """Cache worker statistics."""
        key = self.keys.WORKER_STATS
        return self.set(key, stats_data, ttl)
    
    def get_worker_stats(self) -> Optional[Dict]:
        """Get cached worker statistics."""
        key = self.keys.WORKER_STATS
        return self.get(key)
    
    def cache_available_workers(self, skill_category: str, workers_data: List, ttl: int = 300) -> bool:
        """Cache available workers by skill category."""
        key = self.keys.WORKER_AVAILABLE.format(skill_category=skill_category)
        return self.set(key, workers_data, ttl)
    
    def get_available_workers(self, skill_category: str) -> Optional[List]:
        """Get cached available workers."""
        key = self.keys.WORKER_AVAILABLE.format(skill_category=skill_category)
        return self.get(key)
    
    def cache_dashboard_stats(self, stats_data: Dict, ttl: int = 180) -> bool:
        """Cache dashboard statistics."""
        key = self.keys.DASHBOARD_STATS
        return self.set(key, stats_data, ttl)
    
    def get_dashboard_stats(self) -> Optional[Dict]:
        """Get cached dashboard statistics."""
        key = self.keys.DASHBOARD_STATS
        return self.get(key)
    
    def cache_search_results(self, query_hash: str, results_data: List, ttl: int = 900) -> bool:
        """Cache search results."""
        key = self.keys.SEARCH_RESULTS.format(query_hash=query_hash)
        return self.set(key, results_data, ttl)
    
    def get_search_results(self, query_hash: str) -> Optional[List]:
        """Get cached search results."""
        key = self.keys.SEARCH_RESULTS.format(query_hash=query_hash)
        return self.get(key)
    
    def invalidate_user_cache(self, user_id: int) -> bool:
        """Invalidate all user-related cache entries."""
        patterns = [
            f"user:profile:{user_id}",
            f"user:permissions:{user_id}",
            f"user:stats:{user_id}"
        ]
        
        success = True
        for pattern in patterns:
            if not self.delete(pattern):
                success = False
        
        return success
    
    def invalidate_job_cache(self) -> int:
        """Invalidate all job-related cache entries."""
        patterns = [
            "jobs:*",
            "job:*"
        ]
        
        deleted_count = 0
        for pattern in patterns:
            deleted_count += self.delete_pattern(pattern)
        
        return deleted_count
    
    def invalidate_worker_cache(self) -> int:
        """Invalidate all worker-related cache entries."""
        patterns = [
            "workers:*",
            "worker:*"
        ]
        
        deleted_count = 0
        for pattern in patterns:
            deleted_count += self.delete_pattern(pattern)
        
        return deleted_count
    
    def invalidate_dashboard_cache(self) -> bool:
        """Invalidate dashboard cache entries."""
        patterns = [
            "dashboard:*"
        ]
        
        deleted_count = 0
        for pattern in patterns:
            deleted_count += self.delete_pattern(pattern)
        
        return deleted_count > 0
    
    def get_cache_info(self) -> Dict:
        """Get cache information and statistics."""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            print(f"Cache info error: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate."""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)


# Global cache service instance
cache_service = CacheService()
