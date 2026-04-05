"""
Utilities package for shared application utilities.
"""

from .auth_utils import get_redirect_dashboard, validate_role, can_access_dashboard

__all__ = [
    'get_redirect_dashboard',
    'validate_role', 
    'can_access_dashboard'
]
