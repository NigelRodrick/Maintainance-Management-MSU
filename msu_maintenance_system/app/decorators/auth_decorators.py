"""
Authentication and Authorization Decorators for MSU Maintenance System

Provides role-based access control using Flask-Login with centralized admin bypass.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, abort, jsonify, request
from flask_login import login_required, current_user
from typing import Callable, Any

from ..constants.roles import UserRole, RoleCapabilities, RoleHierarchy
from ..utils.access_control import AccessControl, AdminBypassDecorator, require_capability, require_model_access, admin_only, log_admin_action


def role_required(required_role: str):
    """
    Decorator to require specific role for route access with admin bypass.
    
    Args:
        required_role: Required role string (ADMIN, SUPERVISOR, USER)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs) -> Any:
            # Admin bypass - ALLOW ALL OPERATIONS
            if AccessControl.is_admin():
                AccessControl.log_admin_action(
                    action='ROLE_BYPASS',
                    resource_type='Route',
                    details={'required_role': required_role, 'function': func.__name__}
                )
                return func(*args, **kwargs)
            
            # Check if user has required role
            if not hasattr(current_user, 'role') or current_user.role != required_role:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'message': f'{required_role} access required',
                        'admin_bypass_available': AccessControl.is_admin(),
                        'redirect': url_for('auth.login')
                    }), 403
                
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def capability_required(capability: str):
    """
    Decorator to require specific capability for route access with admin bypass.
    
    Args:
        capability: Required capability string
        
    Returns:
        Decorator function
    """
    return require_capability(capability)


# Specific role decorators for convenience
def admin_required(func: Callable) -> Callable:
    """Require admin role."""
    return admin_only()(func)


def supervisor_required_decorator(func: Callable) -> Callable:
    """Require supervisor role or higher with admin bypass."""
    def decorator(f: Callable) -> Callable:
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs) -> Any:
            # Admin bypass
            if AccessControl.is_admin():
                AccessControl.log_admin_action(
                    action='SUPERVISOR_BYPASS',
                    resource_type='Route',
                    details={'function': func.__name__}
                )
                return f(*args, **kwargs)
            
            if not hasattr(current_user, 'role'):
                abort(403)
                
            user_role = UserRole(current_user.role)
            if not RoleHierarchy.is_higher_or_equal(user_role, UserRole.SUPERVISOR):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def supervisor_required(func: Callable) -> Callable:
    """Require supervisor role or higher."""
    return supervisor_required_decorator(func)


def any_authenticated_user(func: Callable) -> Callable:
    """Require any authenticated user."""
    return login_required(func)


def log_access(action: str, resource_type: str = None):
    """
    Decorator to log access to protected resources with admin logging.
    
    Args:
        action: Action being performed
        resource_type: Type of resource being accessed
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs) -> Any:
            # Enhanced logging with admin tracking
            if AccessControl.is_admin():
                AccessControl.log_admin_action(
                    action=action,
                    resource_type=resource_type,
                    details={'function': func.__name__, 'access_granted': True}
                )
            else:
                # Regular user access logging
                try:
                    user_id = getattr(current_user, 'id', 'anonymous')
                    user_role = getattr(current_user, 'role', 'unknown')
                    
                    # TODO: Implement proper logging for non-admin users
                    print(f"ACCESS_LOG: User {user_id} ({user_role}) attempting {action}")
                    
                except Exception as e:
                    # Don't let logging errors break the main function
                    print(f"LOGGING_ERROR: {str(e)}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Enhanced decorators for model-level access
def require_job_access(operation: str = 'read'):
    """Require job access with admin bypass."""
    from ..models import JobRequest
    return require_model_access(JobRequest, operation)


def require_user_access(operation: str = 'read'):
    """Require user access with admin bypass."""
    from ..models import User
    return require_model_access(User, operation)


def require_assignment_access(operation: str = 'read'):
    """Require assignment access with admin bypass."""
    from ..models import Assignment
    return require_model_access(Assignment, operation)


# System-wide access decorators
def require_system_access():
    """Require system management access with admin bypass."""
    return require_capability('manage_system', 'System')


def require_analytics_access():
    """Require analytics access with admin bypass."""
    return require_capability('view_analytics', 'Analytics')


def require_report_access():
    """Require report export access with admin bypass."""
    return require_capability('export_reports', 'Reports')
