"""
Job Status Service for MSU Maintenance System

Handles job status updates with validation, logging, and business rules.
"""

from datetime import datetime
from typing import Dict, Optional, Tuple, Any
import logging

from .database import db_service
from ..constants.job_status import JobStatus, JobStatusTransition, STATUS_DISPLAY_NAMES

logger = logging.getLogger(__name__)


class JobStatusService:
    """Service layer for job status management."""
    
    def __init__(self):
        self.db_service = db_service
    
    def update_job_status(self, job_id: int, new_status: str, updated_by: int, 
                         is_override: bool = False) -> Dict[str, Any]:
        """
        Update job status with validation and logging.
        
        Args:
            job_id: ID of the job to update
            new_status: New status value
            updated_by: ID of the user making the update
            is_override: Whether to allow override transitions (for supervisors/admins)
            
        Returns:
            Dictionary with update result
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Validate inputs
        self._validate_update_inputs(job_id, new_status, updated_by)
        
        # Get current job details
        current_job = self._get_job_by_id(job_id)
        if not current_job:
            raise ValueError(f"Job with ID {job_id} not found")
        
        current_status = current_job['status']
        
        # Validate status transition
        if not JobStatusTransition.is_valid_transition(current_status, new_status, is_override):
            valid_statuses = JobStatusTransition.get_valid_next_statuses(current_status, is_override)
            raise ValueError(
                f"Invalid status transition from {current_status} to {new_status}. "
                f"Valid next statuses: {valid_statuses}"
            )
        
        # If status is already the same, no update needed
        if current_status == new_status:
            return {
                'success': True,
                'message': f'Job {job_id} already has status {new_status}',
                'job_id': job_id,
                'old_status': current_status,
                'new_status': new_status,
                'updated_at': current_job.get('updated_at', datetime.now())
            }
        
        # Perform atomic update
        try:
            update_result = self._perform_status_update(job_id, new_status, updated_by)
            
            # Log the status change
            self._log_status_change(job_id, current_status, new_status, updated_by)
            
            logger.info(f"Job {job_id} status updated from {current_status} to {new_status} by user {updated_by}")
            
            return {
                'success': True,
                'message': 'Job status updated successfully',
                'job_id': job_id,
                'old_status': current_status,
                'new_status': new_status,
                'updated_at': update_result['updated_at']
            }
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {str(e)}")
            raise RuntimeError(f"Database error: {str(e)}")
    
    def _validate_update_inputs(self, job_id: int, new_status: str, updated_by: int) -> None:
        """Validate input parameters for status update."""
        if not isinstance(job_id, int) or job_id <= 0:
            raise ValueError("Invalid job ID: must be a positive integer")
        
        if not isinstance(updated_by, int) or updated_by <= 0:
            raise ValueError("Invalid user ID: must be a positive integer")
        
        if not isinstance(new_status, str) or not new_status.strip():
            raise ValueError("Invalid status: must be a non-empty string")
        
        # Validate status value
        valid_statuses = JobStatusTransition.get_all_statuses()
        if new_status.upper() not in valid_statuses:
            raise ValueError(f"Invalid status value: {new_status}. Valid values: {valid_statuses}")
    
    def _get_job_by_id(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get job details by ID."""
        query = """
            SELECT id, department, description, category, priority, status, date_created, updated_at
            FROM JobRequests
            WHERE id = ?
        """
        try:
            jobs = self.db_service.execute_query(query, (job_id,))
            return jobs[0] if jobs else None
        except Exception as e:
            logger.error(f"Error fetching job {job_id}: {str(e)}")
            return None
    
    def _perform_status_update(self, job_id: int, new_status: str, updated_by: int) -> Dict[str, Any]:
        """Perform the actual database update."""
        query = """
            UPDATE JobRequests 
            SET status = ?, updated_at = GETDATE()
            WHERE id = ?
        """
        
        try:
            self.db_service.execute_update(query, (new_status, job_id))
            
            # Get the updated record to return the timestamp
            updated_job = self._get_job_by_id(job_id)
            return {
                'updated_at': updated_job.get('updated_at', datetime.now())
            }
        except Exception as e:
            raise e
    
    def _log_status_change(self, job_id: int, old_status: str, new_status: str, updated_by: int) -> None:
        """Log status change to audit table (if exists) or application log."""
        # Try to log to database audit table
        try:
            audit_query = """
                INSERT INTO JobStatusAudit (job_id, old_status, new_status, updated_by, timestamp)
                VALUES (?, ?, ?, ?, GETDATE())
            """
            self.db_service.execute_insert(audit_query, (job_id, old_status, new_status, updated_by))
        except Exception as e:
            # If audit table doesn't exist, log to application log
            logger.warning(f"Could not log to audit table: {str(e)}")
            logger.info(f"STATUS_CHANGE: job_id={job_id}, old_status={old_status}, "
                       f"new_status={new_status}, updated_by={updated_by}, timestamp={datetime.now()}")
    
    def get_job_status_history(self, job_id: int) -> list:
        """Get status change history for a job."""
        try:
            # Try to get from audit table first
            query = """
                SELECT old_status, new_status, updated_by, timestamp
                FROM JobStatusAudit
                WHERE job_id = ?
                ORDER BY timestamp DESC
            """
            history = self.db_service.execute_query(query, (job_id,))
            
            if history:
                return history
            else:
                # If no audit table, return current status only
                job = self._get_job_by_id(job_id)
                if job:
                    return [{
                        'old_status': None,
                        'new_status': job['status'],
                        'updated_by': None,
                        'timestamp': job.get('date_created', datetime.now())
                    }]
                return []
                
        except Exception as e:
            logger.error(f"Error fetching status history for job {job_id}: {str(e)}")
            return []
    
    def get_jobs_by_status(self, status: str) -> list:
        """Get all jobs with a specific status."""
        if status.upper() not in JobStatusTransition.get_all_statuses():
            raise ValueError(f"Invalid status: {status}")
        
        query = """
            SELECT id, department, description, category, priority, status, date_created, updated_at
            FROM JobRequests
            WHERE status = ?
            ORDER BY date_created DESC
        """
        
        try:
            return self.db_service.execute_query(query, (status,))
        except Exception as e:
            logger.error(f"Error fetching jobs with status {status}: {str(e)}")
            return []
    
    def get_status_summary(self) -> Dict[str, int]:
        """Get count of jobs by status."""
        query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM JobRequests
            GROUP BY status
            ORDER BY count DESC
        """
        
        try:
            results = self.db_service.execute_query(query)
            return {row['status']: row['count'] for row in results}
        except Exception as e:
            logger.error(f"Error fetching status summary: {str(e)}")
            return {}
    
    def get_user_permission_level(self, user_id: int) -> str:
        """Get user permission level for status updates."""
        try:
            query = """
                SELECT role FROM Users WHERE id = ?
            """
            users = self.db_service.execute_query(query, (user_id,))
            
            if users:
                role = users[0]['role'].lower()
                if role in ['admin', 'supervisor']:
                    return 'override'  # Can override transitions
                else:
                    return 'standard'  # Standard transitions only
            else:
                return 'none'
                
        except Exception as e:
            logger.error(f"Error fetching user permissions for {user_id}: {str(e)}")
            return 'none'
    
    def can_user_update_job_status(self, user_id: int, job_id: int, new_status: str) -> Tuple[bool, str]:
        """
        Check if a user can update a job's status.
        
        Args:
            user_id: ID of the user
            job_id: ID of the job
            new_status: New status value
            
        Returns:
            Tuple of (can_update, reason_message)
        """
        # Check user permissions
        permission_level = self.get_user_permission_level(user_id)
        if permission_level == 'none':
            return False, "User not found or insufficient permissions"
        
        # Get current job
        job = self._get_job_by_id(job_id)
        if not job:
            return False, "Job not found"
        
        current_status = job['status']
        is_override = permission_level == 'override'
        
        # Check if transition is valid
        if not JobStatusTransition.is_valid_transition(current_status, new_status, is_override):
            valid_statuses = JobStatusTransition.get_valid_next_statuses(current_status, is_override)
            return False, f"Invalid transition. Valid next statuses: {valid_statuses}"
        
        return True, "Status update allowed"


# Create singleton instance
job_status_service = JobStatusService()
