"""
Centralized Access Control System for MSU Maintenance System

Provides unified access control with admin bypass functionality and comprehensive audit logging.
This is the single source of truth for all permission checks throughout the application.
"""

from functools import wraps
from flask import request, abort, jsonify
from flask_login import current_user
from typing import Callable, Any, Dict, List, Optional, Union
from datetime import datetime
import json
import logging

from ..constants.roles import UserRole, RoleCapabilities, RoleHierarchy
from ..models import User, JobRequest, Assignment, Material
from ..extensions import db

# Configure audit logging
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)
# Use console logging instead of file logging to avoid directory dependencies
audit_handler = logging.StreamHandler()
audit_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)


class AccessControl:
    """Centralized access control with admin bypass."""
    
    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin."""
        return (
            hasattr(current_user, 'role') and 
            current_user.role == UserRole.ADMIN.value
        )
    
    @staticmethod
    def get_current_user_info() -> Dict[str, Any]:
        """Get current user information for logging."""
        return {
            'user_id': getattr(current_user, 'id', None),
            'user_email': getattr(current_user, 'email', None),
            'user_role': getattr(current_user, 'role', None),
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
    
    @staticmethod
    def log_admin_action(action: str, resource_type: str, resource_id: Any = None, 
                        details: Dict[str, Any] = None):
        """Log admin action for audit trail."""
        if not AccessControl.is_admin():
            return
        
        user_info = AccessControl.get_current_user_info()
        log_entry = {
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {},
            **user_info
        }
        
        audit_logger.info(f"ADMIN_ACTION: {json.dumps(log_entry)}")
    
    @staticmethod
    def check_permission(capability: str, resource_type: str = None) -> bool:
        """
        Check if current user has permission, with admin bypass.
        
        Args:
            capability: Required capability
            resource_type: Type of resource being accessed
            
        Returns:
            True if user has permission or is admin
        """
        # Admin bypass - ALLOW ALL OPERATIONS
        if AccessControl.is_admin():
            AccessControl.log_admin_action(
                action='ACCESS_BYPASS',
                resource_type=resource_type,
                details={'capability': capability}
            )
            return True
        
        # Regular permission check
        if not hasattr(current_user, 'role'):
            return False
        
        user_role = UserRole(current_user.role)
        return RoleCapabilities.has_capability(user_role, capability)
    
    @staticmethod
    def check_model_access(model_class: type, operation: str = 'read') -> bool:
        """
        Check access to specific model with admin bypass.
        
        Args:
            model_class: SQLAlchemy model class
            operation: Operation type (read, create, update, delete)
            
        Returns:
            True if user has access or is admin
        """
        if AccessControl.is_admin():
            AccessControl.log_admin_action(
                action=f'MODEL_{operation.upper()}',
                resource_type=model_class.__name__,
                details={'operation': operation}
            )
            return True
        
        # Map models to capabilities
        model_capability_map = {
            User: 'view_users',
            JobRequest: 'view_all_jobs',
            Assignment: 'assign_technicians',
            Material: 'view_all_jobs'
        }
        
        capability = model_capability_map.get(model_class, 'view_own_jobs')
        return AccessControl.check_permission(capability, model_class.__name__)
    
    @staticmethod
    def filter_queryset_for_user(query, model_class: type):
        """
        Filter queryset based on user permissions, with admin bypass.
        
        Args:
            query: SQLAlchemy query object
            model_class: Model class being queried
            
        Returns:
            Filtered query (unfiltered for admin)
        """
        if AccessControl.is_admin():
            AccessControl.log_admin_action(
                action='QUERY_ALL',
                resource_type=model_class.__name__,
                details={'query_unfiltered': True}
            )
            return query  # Admin sees all
        
        # Apply user-specific filters
        user_id = getattr(current_user, 'id', None)
        if not user_id:
            return query.filter(False)  # No access
        
        if model_class == JobRequest:
            return query.filter(JobRequest.submitted_by == user_id)
        elif model_class == Assignment:
            return query.join(JobRequest).filter(JobRequest.submitted_by == user_id)
        elif model_class == Material:
            return query.join(JobRequest).filter(JobRequest.submitted_by == user_id)
        
        return query


class AdminBypassDecorator:
    """Decorators with admin bypass functionality."""
    
    @staticmethod
    def require_capability(capability: str, resource_type: str = None):
        """
        Decorator requiring specific capability with admin bypass.
        
        Args:
            capability: Required capability
            resource_type: Type of resource being accessed
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if not AccessControl.check_permission(capability, resource_type):
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'message': f'{capability} capability required',
                            'admin_bypass_available': AccessControl.is_admin()
                        }), 403
                    abort(403)
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_model_access(model_class: type, operation: str = 'read'):
        """
        Decorator requiring model access with admin bypass.
        
        Args:
            model_class: SQLAlchemy model class
            operation: Operation type
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if not AccessControl.check_model_access(model_class, operation):
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'message': f'Access to {model_class.__name__} {operation} required',
                            'admin_bypass_available': AccessControl.is_admin()
                        }), 403
                    abort(403)
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def admin_only():
        """Decorator requiring admin role only."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if not AccessControl.is_admin():
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'message': 'Admin access required'
                        }), 403
                    abort(403)
                return func(*args, **kwargs)
            return wrapper
        return decorator


class SystemWideAccess:
    """System-wide access control for all operations."""
    
    @staticmethod
    def can_create_user() -> bool:
        return AccessControl.check_permission('create_users', 'User')
    
    @staticmethod
    def can_view_users() -> bool:
        return AccessControl.check_permission('view_users', 'User')
    
    @staticmethod
    def can_view_all_jobs() -> bool:
        return AccessControl.check_permission('view_all_jobs', 'JobRequest')
    
    @staticmethod
    def can_assign_technicians() -> bool:
        return AccessControl.check_permission('assign_technicians', 'Assignment')
    
    @staticmethod
    def can_update_job_status() -> bool:
        return AccessControl.check_permission('update_job_status', 'JobRequest')
    
    @staticmethod
    def can_view_analytics() -> bool:
        return AccessControl.check_permission('view_analytics', 'Analytics')
    
    @staticmethod
    def can_manage_system() -> bool:
        return AccessControl.check_permission('manage_system', 'System')
    
    @staticmethod
    def can_export_reports() -> bool:
        return AccessControl.check_permission('export_reports', 'Reports')


# Convenience decorators for backward compatibility
def require_capability(capability: str, resource_type: str = None):
    """Require specific capability with admin bypass."""
    return AdminBypassDecorator.require_capability(capability, resource_type)

def require_model_access(model_class: type, operation: str = 'read'):
    """Require model access with admin bypass."""
    return AdminBypassDecorator.require_model_access(model_class, operation)

def admin_only():
    """Require admin role only."""
    return AdminBypassDecorator.admin_only()

# Enhanced decorators with logging
def log_admin_action(action: str, resource_type: str = None):
    """Decorator to log admin actions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if AccessControl.is_admin():
                AccessControl.log_admin_action(
                    action=action,
                    resource_type=resource_type,
                    details={'function': func.__name__, 'args': str(args)[:200]}
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global access control instance
access_control = AccessControl()
system_access = SystemWideAccess()
