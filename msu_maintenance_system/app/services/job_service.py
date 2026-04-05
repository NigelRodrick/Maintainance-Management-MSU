"""
Refactored Job Service
Uses repository pattern and dependency injection for clean architecture.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository
from app.domain.job import (
    JobRequestCreate, JobRequestUpdate, JobRequestResponse, 
    JobStatusTransition, JobSearchRequest, JobStats
)
from app.domain import JobStatus, Priority
from ..classification_service import classify_request


class JobService:
    """Service for job request business logic."""
    
    def __init__(self, job_repo: JobRepository = None, user_repo: UserRepository = None):
        self.job_repo = job_repo
        self.user_repo = user_repo
    
    def create_job(self, job_data: JobRequestCreate, submitter_id: int) -> JobRequestResponse:
        """Create a new job request."""
        # Validate submitter exists
        submitter = self.user_repo.get_by_id(submitter_id)
        if not submitter:
            raise ValueError(f"Submitter with ID {submitter_id} not found")
        
        # Auto-classify if not provided
        if not hasattr(job_data, 'category') or not job_data.category:
            category, priority = classify_request(job_data.description)
            job_data.category = category
            job_data.priority = Priority(priority.upper()) if priority.upper() in [p.value for p in Priority] else Priority.MEDIUM
        
        # Create job
        job_dict = job_data.dict()
        job_dict['submitted_by'] = submitter_id
        job_dict['status'] = JobStatus.PENDING
        
        job = self.job_repo.create(job_dict)
        return JobRequestResponse.from_orm(job)
    
    def get_job_by_id(self, job_id: int) -> Optional[JobRequestResponse]:
        """Get job by ID."""
        job = self.job_repo.get_by_id(job_id)
        return JobRequestResponse.from_orm(job) if job else None
    
    def update_job(self, job_id: int, update_data: JobRequestUpdate) -> Optional[JobRequestResponse]:
        """Update job details."""
        # Validate status transition if status is being updated
        if hasattr(update_data, 'status') and update_data.status:
            current_job = self.job_repo.get_by_id(job_id)
            if not current_job:
                raise ValueError(f"Job with ID {job_id} not found")
            
            # Validate transition
            valid_transitions = JobStatus.valid_transitions()
            if current_job.status not in valid_transitions:
                raise ValueError(f"Invalid current status: {current_job.status}")
            
            if update_data.status not in valid_transitions[current_job.status]:
                raise ValueError(f"Cannot transition from {current_job.status} to {update_data.status}")
        
        job = self.job_repo.update(job_id, update_data.dict(exclude_unset=True))
        return JobRequestResponse.from_orm(job) if job else None
    
    def update_job_status(self, job_id: int, status_transition: JobStatusTransition) -> Optional[JobRequestResponse]:
        """Update job status with audit trail."""
        job = self.job_repo.update_status(
            job_id, 
            status_transition.to_status.value, 
            status_transition.changed_by,
            status_transition.notes
        )
        return JobRequestResponse.from_orm(job) if job else None
    
    def search_jobs(self, search_request: JobSearchRequest) -> Dict[str, Any]:
        """Search jobs with filters."""
        # Build criteria from search request
        criteria = {}
        if search_request.status:
            criteria['status'] = search_request.status.value
        if search_request.department:
            criteria['department'] = search_request.department
        if search_request.category:
            criteria['category'] = search_request.category
        if search_request.priority:
            criteria['priority'] = search_request.priority.value
        
        # Get jobs with pagination
        if search_request.keyword:
            jobs = self.job_repo.search_by_description(search_request.keyword)
            # Apply additional filters
            if criteria:
                filtered_jobs = []
                for job in jobs:
                    match = True
                    for key, value in criteria.items():
                        if getattr(job, key, None) != value:
                            match = False
                            break
                    if match:
                        filtered_jobs.append(job)
                jobs = filtered_jobs
        else:
            jobs = self.job_repo.find_by_criteria(criteria)
        
        # Manual pagination for search results
        start = (search_request.page - 1) * search_request.per_page
        end = start + search_request.per_page
        paginated_jobs = jobs[start:end]
        
        return {
            'items': [JobRequestResponse.from_orm(job) for job in paginated_jobs],
            'total': len(jobs),
            'page': search_request.page,
            'per_page': search_request.per_page,
            'pages': (len(jobs) + search_request.per_page - 1) // search_request.per_page
        }
    
    def get_jobs_by_status(self, status: JobStatus) -> List[JobRequestResponse]:
        """Get jobs by status."""
        jobs = self.job_repo.get_by_status(status.value)
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_jobs_by_department(self, department: str) -> List[JobRequestResponse]:
        """Get jobs by department."""
        jobs = self.job_repo.get_by_department(department)
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_jobs_by_category(self, category: str) -> List[JobRequestResponse]:
        """Get jobs by category."""
        jobs = self.job_repo.get_by_category(category)
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_jobs_by_priority(self, priority: Priority) -> List[JobRequestResponse]:
        """Get jobs by priority."""
        jobs = self.job_repo.get_by_priority(priority.value)
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_jobs_by_submitter(self, submitter_id: int) -> List[JobRequestResponse]:
        """Get jobs submitted by a user."""
        jobs = self.job_repo.get_by_submitter(submitter_id)
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_pending_jobs(self) -> List[JobRequestResponse]:
        """Get all pending jobs."""
        jobs = self.job_repo.get_pending_jobs()
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_in_progress_jobs(self) -> List[JobRequestResponse]:
        """Get all in-progress jobs."""
        jobs = self.job_repo.get_in_progress_jobs()
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_completed_jobs(self) -> List[JobRequestResponse]:
        """Get all completed jobs."""
        jobs = self.job_repo.get_completed_jobs()
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_recent_jobs(self, days: int = 7) -> List[JobRequestResponse]:
        """Get recent jobs within N days."""
        jobs = self.job_repo.get_recent_jobs(days)
        return [JobRequestResponse.from_orm(job) for job in jobs]
    
    def get_job_statistics(self) -> JobStats:
        """Get job statistics."""
        stats = self.job_repo.get_dashboard_stats()
        return JobStats(**stats)
    
    def delete_job(self, job_id: int) -> bool:
        """Soft delete a job."""
        return self.job_repo.soft_delete(job_id)
    
    def get_jobs_with_pagination(self, page: int = 1, per_page: int = 25,
                              status: str = None, department: str = None,
                              priority: str = None) -> Dict[str, Any]:
        """Get paginated jobs with optional filters."""
        result = self.job_repo.get_jobs_with_pagination(
            page, per_page, status, department, priority
        )
        
        # Convert to response models
        result['items'] = [JobRequestResponse.from_orm(job) for job in result['items']]
        return result


# Create service instance
job_service = JobService(job_repo=None, user_repo=None)  # Will be injected properly in app factory
