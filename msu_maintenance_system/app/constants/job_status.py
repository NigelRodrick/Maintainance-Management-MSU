"""
Job Status Constants and Enums for MSU Maintenance System

Defines valid job statuses and business rules for status transitions.
"""

from enum import Enum
from typing import List, Dict, Set


class JobStatus(Enum):
    """Job status enumeration with valid values."""
    
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class JobStatusTransition:
    """Defines valid job status transitions."""
    
    # Define valid transitions: from_status -> [to_statuses]
    VALID_TRANSITIONS: Dict[JobStatus, List[JobStatus]] = {
        JobStatus.PENDING: [JobStatus.IN_PROGRESS],
        JobStatus.IN_PROGRESS: [JobStatus.COMPLETED],
        JobStatus.COMPLETED: []  # Terminal state - no further transitions
    }
    
    # Allow override transitions for supervisors/admins
    OVERRIDE_TRANSITIONS: Dict[JobStatus, List[JobStatus]] = {
        JobStatus.PENDING: [JobStatus.IN_PROGRESS, JobStatus.COMPLETED],
        JobStatus.IN_PROGRESS: [JobStatus.PENDING, JobStatus.COMPLETED],
        JobStatus.COMPLETED: [JobStatus.PENDING, JobStatus.IN_PROGRESS]  # Allow reopening
    }
    
    @classmethod
    def is_valid_transition(cls, from_status: str, to_status: str, 
                          is_override: bool = False) -> bool:
        """
        Check if a status transition is valid.
        
        Args:
            from_status: Current status string
            to_status: New status string
            is_override: Whether to allow override transitions (for supervisors/admins)
            
        Returns:
            True if transition is valid, False otherwise
        """
        try:
            from_enum = JobStatus(from_status.upper())
            to_enum = JobStatus(to_status.upper())
            
            transitions = cls.OVERRIDE_TRANSITIONS if is_override else cls.VALID_TRANSITIONS
            
            return to_enum in transitions.get(from_enum, [])
        except (ValueError, AttributeError):
            return False
    
    @classmethod
    def get_valid_next_statuses(cls, current_status: str, 
                               is_override: bool = False) -> List[str]:
        """
        Get list of valid next statuses for current status.
        
        Args:
            current_status: Current status string
            is_override: Whether to include override transitions
            
        Returns:
            List of valid next status strings
        """
        try:
            current_enum = JobStatus(current_status.upper())
            transitions = cls.OVERRIDE_TRANSITIONS if is_override else cls.VALID_TRANSITIONS
            valid_statuses = transitions.get(current_enum, [])
            return [status.value for status in valid_statuses]
        except (ValueError, AttributeError):
            return []
    
    @classmethod
    def get_all_statuses(cls) -> List[str]:
        """Get all valid status values."""
        return [status.value for status in JobStatus]
    
    @classmethod
    def is_terminal_status(cls, status: str) -> bool:
        """Check if status is terminal (no further transitions)."""
        try:
            status_enum = JobStatus(status.upper())
            return len(cls.VALID_TRANSITIONS.get(status_enum, [])) == 0
        except (ValueError, AttributeError):
            return False
    
    @classmethod
    def get_default_status(cls) -> str:
        """Get the default status for new jobs."""
        return JobStatus.PENDING.value


# Status display names for frontend
STATUS_DISPLAY_NAMES = {
    JobStatus.PENDING.value: "Pending",
    JobStatus.IN_PROGRESS.value: "In Progress",
    JobStatus.COMPLETED.value: "Completed"
}

# Status colors for UI
STATUS_COLORS = {
    JobStatus.PENDING.value: "#ffc107",  # Yellow
    JobStatus.IN_PROGRESS.value: "#17a2b8",  # Blue
    JobStatus.COMPLETED.value: "#28a745"  # Green
}

# Status icons for UI
STATUS_ICONS = {
    JobStatus.PENDING.value: "⏳",
    JobStatus.IN_PROGRESS.value: "🔧",
    JobStatus.COMPLETED.value: "✅"
}
