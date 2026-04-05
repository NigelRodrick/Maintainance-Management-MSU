"""
Migration Tracker

Tracks usage of deprecated components and provides migration guidance.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from functools import wraps
from flask import request, current_app

from ..utils.logging_config import get_logger

# Setup logger
logger = get_logger('migration_tracker')


class MigrationTracker:
    """Tracks usage of deprecated components for migration planning."""
    
    def __init__(self):
        self.deprecated_components = {
            'routes.py': {
                'status': 'deprecated',
                'replacement': 'routes/ directory with proper blueprints',
                'migration_guide': 'Use routes/auth.py, routes/main.py, etc.',
                'removal_target': 'v2.1.0',
                'usage_count': 0,
                'last_used': None
            },
            'auth.py (legacy decorators)': {
                'status': 'deprecated',
                'replacement': 'services/unified_auth_service.py',
                'migration_guide': 'Use unified_auth_service for all authentication',
                'removal_target': 'v2.1.0',
                'usage_count': 0,
                'last_used': None
            },
            'raw pyodbc connections': {
                'status': 'deprecated',
                'replacement': 'services/unified_db_service.py',
                'migration_guide': 'Use unified_db_service for all database operations',
                'removal_target': 'v2.2.0',
                'usage_count': 0,
                'last_used': None
            },
            'session-based auth only': {
                'status': 'deprecated',
                'replacement': 'Flask-Login with unified service',
                'migration_guide': 'Use unified_auth_service for consistent authentication',
                'removal_target': 'v2.1.0',
                'usage_count': 0,
                'last_used': None
            }
        }
    
    def track_usage(self, component: str, context: str = None):
        """
        Track usage of a deprecated component.
        
        Args:
            component: Name of deprecated component
            context: Context where it was used
        """
        if component in self.deprecated_components:
            self.deprecated_components[component]['usage_count'] += 1
            self.deprecated_components[component]['last_used'] = datetime.now()
            
            # Log the usage
            logger.warning(f"DEPRECATED COMPONENT USED: {component}")
            if context:
                logger.warning(f"Context: {context}")
            if request and request.endpoint:
                logger.warning(f"Route: {request.endpoint}")
        else:
            logger.warning(f"Unknown deprecated component tracked: {component}")
    
    def get_migration_report(self) -> Dict:
        """
        Get comprehensive migration report.
        
        Returns:
            Dict with migration status and recommendations
        """
        total_deprecated = len(self.deprecated_components)
        actively_used = sum(1 for comp in self.deprecated_components.values() 
                          if comp['usage_count'] > 0)
        
        return {
            'summary': {
                'total_deprecated_components': total_deprecated,
                'actively_used_components': actively_used,
                'unused_components': total_deprecated - actively_used,
                'report_generated': datetime.now().isoformat()
            },
            'components': self.deprecated_components,
            'recommendations': self._get_recommendations(),
            'priority_actions': self._get_priority_actions()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get migration recommendations based on usage."""
        recommendations = []
        
        for component, info in self.deprecated_components.items():
            if info['usage_count'] > 0:
                recommendations.append(
                    f"URGENT: Migrate {component} (used {info['usage_count']} times) "
                    f"before {info['removal_target']}"
                )
            else:
                recommendations.append(
                    f"SAFE: Remove {component} (no usage detected) "
                    f"target {info['removal_target']}"
                )
        
        return sorted(recommendations, key=lambda x: 'URGENT' in x, reverse=True)
    
    def _get_priority_actions(self) -> List[Dict]:
        """Get prioritized action items."""
        actions = []
        
        for component, info in self.deprecated_components.items():
            priority = 'high' if info['usage_count'] > 10 else 'medium' if info['usage_count'] > 0 else 'low'
            
            actions.append({
                'component': component,
                'priority': priority,
                'action': 'migrate' if info['usage_count'] > 0 else 'remove',
                'target_version': info['removal_target'],
                'replacement': info['replacement'],
                'usage_count': info['usage_count'],
                'last_used': info['last_used']
            })
        
        return sorted(actions, key=lambda x: (x['priority'] != 'high', x['usage_count']), reverse=True)
    
    def is_deprecated(self, component: str) -> bool:
        """Check if a component is deprecated."""
        return component in self.deprecated_components
    
    def get_replacement(self, component: str) -> Optional[str]:
        """Get replacement for deprecated component."""
        return self.deprecated_components.get(component, {}).get('replacement')
    
    def can_remove_safely(self, component: str) -> bool:
        """Check if component can be removed safely (no usage)."""
        return self.deprecated_components.get(component, {}).get('usage_count', 0) == 0


# Global migration tracker instance
migration_tracker = MigrationTracker()


# Decorators for tracking deprecated usage
def deprecated(component: str, replacement: str = None, removal_target: str = None):
    """
    Decorator to mark deprecated functions and track usage.
    
    Args:
        component: Name of deprecated component
        replacement: Replacement component name
        removal_target: Target version for removal
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Track usage
            context = f"Function: {func.__name__}"
            if request and request.endpoint:
                context += f" in route: {request.endpoint}"
            
            migration_tracker.track_usage(component, context)
            
            # Log deprecation warning
            logger.warning(f"DEPRECATED FUNCTION CALLED: {func.__name__}")
            if replacement:
                logger.warning(f"REPLACEMENT: {replacement}")
            if removal_target:
                logger.warning(f"REMOVAL_TARGET: {removal_target}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def deprecated_class(component: str, replacement: str = None, removal_target: str = None):
    """
    Class decorator to mark deprecated classes and track usage.
    
    Args:
        component: Name of deprecated component
        replacement: Replacement component name
        removal_target: Target version for removal
    """
    def decorator(cls):
        # Wrap __init__ to track instantiation
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            # Track usage
            context = f"Class: {cls.__name__}"
            if request and request.endpoint:
                context += f" in route: {request.endpoint}"
            
            migration_tracker.track_usage(component, context)
            
            # Log deprecation warning
            logger.warning(f"DEPRECATED CLASS INSTANTIATED: {cls.__name__}")
            if replacement:
                logger.warning(f"REPLACEMENT: {replacement}")
            if removal_target:
                logger.warning(f"REMOVAL_TARGET: {removal_target}")
            
            return original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        return cls
    return decorator


# Utility functions for migration guidance
def get_migration_status() -> Dict:
    """Get current migration status."""
    return migration_tracker.get_migration_report()


def check_component_status(component: str) -> Dict:
    """Check status of specific component."""
    if component in migration_tracker.deprecated_components:
        return migration_tracker.deprecated_components[component]
    else:
        return {'status': 'unknown', 'message': 'Component not found in deprecated list'}


def log_deprecation_warning(component: str, context: str = None):
    """Log a deprecation warning without tracking."""
    logger.warning(f"DEPRECATED: {component}")
    if context:
        logger.warning(f"Context: {context}")


# Migration helper functions
def suggest_migration_path(component: str) -> Optional[str]:
    """Suggest migration path for deprecated component."""
    return migration_tracker.get_replacement(component)


def is_safe_to_remove(component: str) -> bool:
    """Check if it's safe to remove a component."""
    return migration_tracker.can_remove_safely(component)
