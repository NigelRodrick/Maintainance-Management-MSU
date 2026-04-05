"""
Role Constants and Permissions for MSU Maintenance System

Defines roles, capabilities, and access control rules.
"""

from enum import Enum
from typing import List, Dict, Set


class UserRole(Enum):
    """User role enumeration with strict values."""
    
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    USER = "USER"


class RoleCapabilities:
    """Defines capabilities for each role."""
    
    CAPABILITIES = {
        UserRole.ADMIN: {
            'create_users': True,
            'view_users': True,
            'view_all_jobs': True,
            'view_supervisor_activity': True,
            'system_overview': True,
            'view_analytics': True,
            'view_logs': True,
            'manage_system': True,
            'export_reports': True,
            'assign_technicians': True,
            'update_job_status': True,
            'submit_jobs': True,
            'view_own_jobs': True
        },
        UserRole.SUPERVISOR: {
            'create_users': False,
            'view_users': False,
            'view_all_jobs': True,
            'view_supervisor_activity': False,
            'system_overview': True,
            'view_analytics': True,
            'view_logs': False,
            'manage_system': False,
            'export_reports': True,
            'assign_technicians': True,
            'update_job_status': True,
            'submit_jobs': True,
            'view_own_jobs': True
        },
        UserRole.USER: {
            'create_users': False,
            'view_users': False,
            'view_all_jobs': False,
            'view_supervisor_activity': False,
            'system_overview': False,
            'view_analytics': False,
            'view_logs': False,
            'manage_system': False,
            'export_reports': False,
            'assign_technicians': False,
            'update_job_status': False,
            'submit_jobs': True,
            'view_own_jobs': True
        }
    }
    
    @classmethod
    def has_capability(cls, role: UserRole, capability: str) -> bool:
        """
        Check if a role has a specific capability.
        
        Args:
            role: User role enum
            capability: Capability name to check
            
        Returns:
            True if role has capability, False otherwise
        """
        return cls.CAPABILITIES.get(role, {}).get(capability, False)
    
    @classmethod
    def get_role_capabilities(cls, role: UserRole) -> Dict[str, bool]:
        """Get all capabilities for a role."""
        return cls.CAPABILITIES.get(role, {}).copy()
    
    @classmethod
    def get_accessible_dashboards(cls, role: UserRole) -> List[str]:
        """Get list of dashboards accessible to a role."""
        dashboard_map = {
            UserRole.ADMIN: ['admin'],
            UserRole.SUPERVISOR: ['supervisor'],
            UserRole.USER: ['user']
        }
        return dashboard_map.get(role, [])
    
    @classmethod
    def can_access_dashboard(cls, role: UserRole, dashboard: str) -> bool:
        """Check if role can access a specific dashboard."""
        return dashboard in cls.get_accessible_dashboards(role)


class RoleHierarchy:
    """Defines role hierarchy for access control."""
    
    HIERARCHY = {
        UserRole.ADMIN: 3,
        UserRole.SUPERVISOR: 2,
        UserRole.USER: 1
    }
    
    @classmethod
    def is_higher_or_equal(cls, user_role: UserRole, required_role: UserRole) -> bool:
        """
        Check if user role is higher or equal to required role.
        
        Args:
            user_role: Current user's role
            required_role: Required role for access
            
        Returns:
            True if user_role >= required_role
        """
        return cls.HIERARCHY.get(user_role, 0) >= cls.HIERARCHY.get(required_role, 0)


# Role display names for UI
ROLE_DISPLAY_NAMES = {
    UserRole.ADMIN.value: "Administrator",
    UserRole.SUPERVISOR.value: "Supervisor",
    UserRole.USER.value: "User"
}

# Role colors for UI
ROLE_COLORS = {
    UserRole.ADMIN.value: "#dc3545",      # Red
    UserRole.SUPERVISOR.value: "#fd7e14",   # Orange
    UserRole.USER.value: "#0d6efd"          # Blue
}

# Role icons for UI
ROLE_ICONS = {
    UserRole.ADMIN.value: "👑",
    UserRole.SUPERVISOR.value: "👨‍💼",
    UserRole.USER.value: "👤"
}
