"""
Job Repository
Handles all job request related database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc, asc
from app.repositories import BaseRepository
from app.models import JobRequest, JobStatusHistory


class JobRepository(BaseRepository[JobRequest]):
    """Repository for job request operations."""
    
    def __init__(self, session=None):
        super().__init__(JobRequest, session)
    
    def get_by_reference_no(self, reference_no: str) -> Optional[JobRequest]:
        """Get job by reference number."""
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.reference_no == reference_no,
                JobRequest.is_deleted == False
            )
        ).first()
    
    def get_by_status(self, status: str) -> List[JobRequest]:
        """Get jobs by status."""
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.status == status,
                JobRequest.is_deleted == False
            )
        ).all()
    
    def get_by_department(self, department: str) -> List[JobRequest]:
        """Get jobs by department."""
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.department == department,
                JobRequest.is_deleted == False
            )
        ).all()
    
    def get_by_category(self, category: str) -> List[JobRequest]:
        """Get jobs by category."""
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.category == category,
                JobRequest.is_deleted == False
            )
        ).all()
    
    def get_by_priority(self, priority: str) -> List[JobRequest]:
        """Get jobs by priority."""
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.priority == priority,
                JobRequest.is_deleted == False
            )
        ).all()
    
    def get_by_submitter(self, submitter_id: int) -> List[JobRequest]:
        """Get jobs submitted by a user."""
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.submitted_by == submitter_id,
                JobRequest.is_deleted == False
            )
        ).all()
    
    def search_by_description(self, keyword: str) -> List[JobRequest]:
        """Search jobs by description keyword."""
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.description.contains(keyword),
                JobRequest.is_deleted == False
            )
        ).all()
    
    def get_recent_jobs(self, days: int = 7) -> List[JobRequest]:
        """Get jobs created in the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.date_created >= cutoff_date,
                JobRequest.is_deleted == False
            )
        ).order_by(desc(JobRequest.date_created)).all()
    
    def get_jobs_by_date_range(self, start_date: datetime, end_date: datetime) -> List[JobRequest]:
        """Get jobs within a date range."""
        return self.session.query(JobRequest).filter(
            and_(
                JobRequest.date_created >= start_date,
                JobRequest.date_created <= end_date,
                JobRequest.is_deleted == False
            )
        ).order_by(desc(JobRequest.date_created)).all()
    
    def get_pending_jobs(self) -> List[JobRequest]:
        """Get all pending jobs."""
        return self.get_by_status('PENDING')
    
    def get_in_progress_jobs(self) -> List[JobRequest]:
        """Get all in-progress jobs."""
        return self.get_by_status('IN_PROGRESS')
    
    def get_completed_jobs(self) -> List[JobRequest]:
        """Get all completed jobs."""
        return self.get_by_status('COMPLETED')
    
    def update_status(self, job_id: int, new_status: str, changed_by: int, 
                    notes: str = None) -> Optional[JobRequest]:
        """Update job status and create history record."""
        job = self.get_by_id(job_id)
        if not job:
            return None
        
        old_status = job.status
        
        # Update job status
        job.status = new_status
        job.updated_at = datetime.utcnow()
        
        # Create status history record
        history = JobStatusHistory(
            job_id=job_id,
            from_status=old_status,
            to_status=new_status,
            changed_by=changed_by,
            changed_at=datetime.utcnow(),
            notes=notes
        )
        
        self.session.add(history)
        self.session.commit()
        self.session.refresh(job)
        
        return job
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        total_jobs = self.session.query(JobRequest).filter(
            JobRequest.is_deleted == False
        ).count()
        
        pending_jobs = self.session.query(JobRequest).filter(
            and_(
                JobRequest.status == 'PENDING',
                JobRequest.is_deleted == False
            )
        ).count()
        
        in_progress_jobs = self.session.query(JobRequest).filter(
            and_(
                JobRequest.status == 'IN_PROGRESS',
                JobRequest.is_deleted == False
            )
        ).count()
        
        completed_jobs = self.session.query(JobRequest).filter(
            and_(
                JobRequest.status == 'COMPLETED',
                JobRequest.is_deleted == False
            )
        ).count()
        
        # Department breakdown
        dept_stats = self.session.query(
            JobRequest.department,
            self.session.query(JobRequest).filter(
                and_(
                    JobRequest.department == JobRequest.department,
                    JobRequest.is_deleted == False
                )
            ).count().label('count')
        ).filter(JobRequest.is_deleted == False).group_by(JobRequest.department).all()
        
        # Category breakdown
        category_stats = self.session.query(
            JobRequest.category,
            self.session.query(JobRequest).filter(
                and_(
                    JobRequest.category == JobRequest.category,
                    JobRequest.is_deleted == False
                )
            ).count().label('count')
        ).filter(JobRequest.is_deleted == False).group_by(JobRequest.category).all()
        
        return {
            'total_jobs': total_jobs,
            'pending_jobs': pending_jobs,
            'in_progress_jobs': in_progress_jobs,
            'completed_jobs': completed_jobs,
            'department_breakdown': dict(dept_stats),
            'category_breakdown': dict(category_stats)
        }
    
    def get_jobs_with_pagination(self, page: int = 1, per_page: int = 25, 
                              status: str = None, department: str = None,
                              priority: str = None) -> Dict[str, Any]:
        """Get paginated jobs with optional filters."""
        query = self.session.query(JobRequest).filter(JobRequest.is_deleted == False)
        
        # Apply filters
        if status:
            query = query.filter(JobRequest.status == status)
        if department:
            query = query.filter(JobRequest.department == department)
        if priority:
            query = query.filter(JobRequest.priority == priority)
        
        # Order by date created (newest first)
        query = query.order_by(desc(JobRequest.date_created))
        
        # Paginate
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
