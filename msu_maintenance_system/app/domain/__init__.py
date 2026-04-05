"""
Domain Models - Enums and Constants
Contains all business enums and validation rules.
"""

from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    
    @classmethod
    def valid_transitions(cls):
        """Define valid status transitions."""
        return {
            cls.PENDING: [cls.IN_PROGRESS, cls.CANCELLED],
            cls.IN_PROGRESS: [cls.COMPLETED, cls.CANCELLED],
            cls.COMPLETED: [],  # Terminal state
            cls.CANCELLED: []   # Terminal state
        }


class Priority(str, Enum):
    """Priority enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    STAFF = "staff"
    MAINTENANCE_ADMIN = "maintenance_admin"


class AssignmentStatus(str, Enum):
    """Assignment status enumeration."""
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SkillCategory(str, Enum):
    """Worker skill category enumeration."""
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    CARPENTRY = "carpentry"
    MECHANICAL = "mechanical"
    CIVIL = "civil"
    GENERAL = "general"


# Validation constants
MAX_DESCRIPTION_LENGTH = 2000
MAX_ITEM_NAME_LENGTH = 150
MAX_FULL_NAME_LENGTH = 150
MAX_DEPARTMENT_LENGTH = 100
MIN_PASSWORD_LENGTH = 10

# Business rules
MAX_ACTIVE_ASSIGNMENTS_PER_WORKER = 1
DEFAULT_SESSION_TIMEOUT_HOURS = 8
PAGINATION_DEFAULT_SIZE = 25
PAGINATION_MAX_SIZE = 100
