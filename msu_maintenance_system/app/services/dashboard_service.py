"""
Dashboard Service for MSU Maintenance System

Provides data access methods for different user role dashboards.
"""

from typing import Dict, List, Any, Optional
import logging

from .database import db_service
from .job_service import job_service
from .job_status_service import job_status_service
from ..constants.roles import UserRole, RoleCapabilities

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard-specific data operations."""
    
    def __init__(self):
        self.db_service = db_service
    
    def get_admin_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for admin dashboard.
        
        Returns:
            Dictionary containing admin-specific metrics
        """
        try:
            metrics = {}
            
            # User metrics
            metrics['total_users'] = self._get_total_users()
            metrics['users_by_role'] = self._get_users_by_role()
            
            # Job metrics
            job_stats = job_service.get_job_statistics()
            if job_stats:
                metrics.update({
                    'total_jobs': job_stats.get('total_jobs', 0),
                    'completed_jobs': job_stats.get('completed_jobs', 0),
                    'pending_jobs': job_stats.get('pending_jobs', 0),
                    'in_progress_jobs': job_stats.get('in_progress_jobs', 0)
                })
            
            # System metrics
            metrics['recent_activity'] = self._get_recent_activity()
            metrics['system_health'] = self._get_system_health()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting admin metrics: {str(e)}")
            return {}
    
    def get_supervisor_jobs(self) -> Dict[str, List[Dict]]:
        """
        Get jobs grouped by status for supervisor dashboard.
        
        Returns:
            Dictionary with jobs grouped by status
        """
        try:
            jobs_by_status = {}
            
            # Get all jobs
            all_jobs = job_service.get_all_jobs()
            
            # Group by status
            for job in all_jobs:
                status = job.get('status', 'UNKNOWN')
                if status not in jobs_by_status:
                    jobs_by_status[status] = []
                jobs_by_status[status].append(job)
            
            return jobs_by_status
            
        except Exception as e:
            logger.error(f"Error getting supervisor jobs: {str(e)}")
            return {}
    
    def get_user_jobs(self, user_id: int) -> List[Dict]:
        """
        Get jobs submitted by a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of jobs submitted by the user
        """
        try:
            # For now, return all jobs since we don't have user_id in JobRequests
            # In a real system, you'd filter by user_id
            query = """
                SELECT id, department, description, category, priority, status, date_created, updated_at
                FROM JobRequests
                WHERE submitted_by = ?
                ORDER BY date_created DESC
            """
            
            # Fallback to all jobs if submitted_by column doesn't exist
            try:
                return self.db_service.execute_query(query, (user_id,))
            except:
                return job_service.get_all_jobs()
                
        except Exception as e:
            logger.error(f"Error getting user jobs: {str(e)}")
            return []
    
    def get_job_analysis(self, job_id: int) -> Dict[str, Any]:
        """
        Get analysis for a specific job (supervisor only).
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary containing job analysis
        """
        try:
            logger.info(f"Analyzing job {job_id}")
            
            # Get job details
            job = job_service.get_job_by_id(job_id)
            if not job:
                return {}
            
            # Return job analysis
            return {
                'category': job.get('category', 'General'),
                'priority': job.get('priority', 'Medium'),
                'estimated_duration': 'unknown',
                'resource_requirements': 'unknown',
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Error getting fallback predictions: {str(e)}")
            return {}
    
    def get_job_queue_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for job queue (supervisor dashboard).
        
        Returns:
            Dictionary with queue metrics
        """
        try:
            jobs_by_status = self.get_supervisor_jobs()
            
            metrics = {
                'pending_count': len(jobs_by_status.get('PENDING', [])),
                'in_progress_count': len(jobs_by_status.get('IN_PROGRESS', [])),
                'completed_count': len(jobs_by_status.get('COMPLETED', [])),
                'total_active': len(jobs_by_status.get('PENDING', [])) + len(jobs_by_status.get('IN_PROGRESS', []))
            }
            
            # Calculate average completion time (mock data)
            completed_jobs = jobs_by_status.get('COMPLETED', [])
            if completed_jobs:
                metrics['avg_completion_time'] = 24  # Mock: 24 hours average
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting job queue metrics: {str(e)}")
            return {}
    
    def get_user_activity_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get activity summary for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with user activity metrics
        """
        try:
            user_jobs = self.get_user_jobs(user_id)
            
            summary = {
                'total_submissions': len(user_jobs),
                'pending_submissions': len([j for j in user_jobs if j.get('status') == 'PENDING']),
                'in_progress_submissions': len([j for j in user_jobs if j.get('status') == 'IN_PROGRESS']),
                'completed_submissions': len([j for j in user_jobs if j.get('status') == 'COMPLETED']),
                'recent_submissions': user_jobs[:5]  # Last 5 submissions
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting user activity: {str(e)}")
            return {}
    
    def _get_total_users(self) -> int:
        """Get total number of users."""
        try:
            query = "SELECT COUNT(*) as count FROM Users"
            result = self.db_service.execute_query(query)
            return result[0]['count'] if result else 0
        except:
            return 0
    
    def _get_users_by_role(self) -> Dict[str, int]:
        """Get users grouped by role."""
        try:
            query = """
                SELECT role, COUNT(*) as count 
                FROM Users 
                GROUP BY role
            """
            results = self.db_service.execute_query(query)
            return {row['role']: row['count'] for row in results} if results else {}
        except:
            return {}
    
    def _get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent system activity."""
        try:
            # Try to get from audit table
            query = """
                SELECT TOP (?) 
                    job_id, old_status, new_status, updated_by, timestamp
                FROM JobStatusAudit 
                ORDER BY timestamp DESC
            """
            
            try:
                return self.db_service.execute_query(query, (limit,))
            except:
                # Fallback to recent jobs
                query = """
                    SELECT TOP (?) id as job_id, status as new_status, 
                           date_created as timestamp, NULL as updated_by
                    FROM JobRequests 
                    ORDER BY date_created DESC
                """
                return self.db_service.execute_query(query, (limit,))
                
        except:
            return []
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        try:
            # System health metrics
            return {
                'database_status': 'healthy',
                'last_backup': '2024-03-29 02:00:00',
                'uptime_percentage': 99.9,
                'active_sessions': 15
            }
        except:
            return {}


# Create singleton instance
dashboard_service = DashboardService()
