"""
Authentication Utilities

Shared authentication logic that doesn't cause circular imports.
"""

from flask import url_for
from typing import Optional


def get_redirect_dashboard(user_role: str) -> str:
    """
    Get the appropriate dashboard URL based on user role.
    
    Args:
        user_role: User role string (ADMIN, SUPERVISOR, USER)
        
    Returns:
        URL for role-appropriate dashboard
    """
    dashboard_map = {
        'ADMIN': 'admin.admin_dashboard',
        'SUPERVISOR': 'supervisor.supervisor_dashboard',
        'USER': 'user.user_dashboard'
    }
    
    dashboard_name = dashboard_map.get(user_role, 'user.user_dashboard')
    return url_for(dashboard_name)


def validate_role(role_str: str) -> Optional[str]:
    """
    Validate role string and return normalized role.
    
    Args:
        role_str: Role string to validate
        
    Returns:
        Normalized role string or None if invalid
    """
    valid_roles = ['ADMIN', 'SUPERVISOR', 'USER']
    
    if not role_str:
        return 'USER'  # Default role
    
    # Normalize to uppercase
    normalized_role = role_str.upper().strip()
    
    return normalized_role if normalized_role in valid_roles else None


def can_access_dashboard(user_role: str, dashboard: str) -> bool:
    """
    Check if user role can access specific dashboard.
    
    Args:
        user_role: User's role
        dashboard: Dashboard name to access
        
    Returns:
        True if access allowed, False otherwise
    """
    access_rules = {
        'ADMIN': ['admin', 'supervisor', 'user'],
        'SUPERVISOR': ['supervisor', 'user'],
        'USER': ['user']
    }
    
    allowed_dashboards = access_rules.get(user_role, [])
    return dashboard in allowed_dashboards
