"""
Refactored Assignment Service
Uses repository pattern and dependency injection for clean architecture.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.worker_repository import WorkerRepository
from app.repositories.job_repository import JobRepository
from app.domain.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, 
    AssignmentTransition, AssignmentPerformance
)
from app.domain import AssignmentStatus


class AssignmentService:
    """Service for assignment business logic."""
    
    def __init__(self, assignment_repo: AssignmentRepository = None, worker_repo: WorkerRepository = None, job_repo: JobRepository = None):
        self.assignment_repo = assignment_repo
        self.worker_repo = worker_repo
        self.job_repo = job_repo
    
    def create_assignment(self, job_id: int, worker_id: int) -> AssignmentResponse:
        """Create a new assignment."""
        # Validate job exists
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")
        
        # Validate worker exists and is available
        worker = self.worker_repo.get_by_id(worker_id)
        if not worker:
            raise ValueError(f"Worker with ID {worker_id} not found")
        
        current_assignment = self.assignment_repo.get_current_assignment(worker_id)
        if current_assignment:
            raise ValueError(f"Worker {worker_id} already has an active assignment")
        
        # Create assignment
        assignment_data = {
            'job_id': job_id,
            'worker_id': worker_id,
            'status': AssignmentStatus.ASSIGNED
        }
        
        assignment = self.assignment_repo.create(assignment_data)
        return AssignmentResponse.from_orm(assignment)
    
    def start_assignment(self, assignment_id: int) -> Optional[AssignmentResponse]:
        """Start an assignment."""
        assignment = self.assignment_repo.start_assignment(assignment_id)
        return AssignmentResponse.from_orm(assignment) if assignment else None
    
    def complete_assignment(self, assignment_id: int) -> Optional[AssignmentResponse]:
        """Complete an assignment."""
        assignment = self.assignment_repo.complete_assignment(assignment_id)
        return AssignmentResponse.from_orm(assignment) if assignment else None
    
    def cancel_assignment(self, assignment_id: int) -> Optional[AssignmentResponse]:
        """Cancel an assignment."""
        assignment = self.assignment_repo.cancel_assignment(assignment_id)
        return AssignmentResponse.from_orm(assignment) if assignment else None
    
    def reassign_worker(self, assignment_id: int, new_worker_id: int) -> Optional[AssignmentResponse]:
        """Reassign an assignment to a different worker."""
        # Validate new worker is available
        current_assignment = self.assignment_repo.get_current_assignment(new_worker_id)
        if current_assignment and current_assignment.id != assignment_id:
            raise ValueError(f"Worker {new_worker_id} already has an active assignment")
        
        assignment = self.assignment_repo.reassign_worker(assignment_id, new_worker_id)
        return AssignmentResponse.from_orm(assignment) if assignment else None
    
    def get_assignment_by_id(self, assignment_id: int) -> Optional[AssignmentResponse]:
        """Get assignment by ID."""
        assignment = self.assignment_repo.get_by_id(assignment_id)
        return AssignmentResponse.from_orm(assignment) if assignment else None
    
    def get_assignments_by_job(self, job_id: int) -> List[AssignmentResponse]:
        """Get assignments for a specific job."""
        assignments = self.assignment_repo.get_by_job_id(job_id)
        return [AssignmentResponse.from_orm(assignment) for assignment in assignments]
    
    def get_assignments_by_worker(self, worker_id: int) -> List[AssignmentResponse]:
        """Get assignments for a specific worker."""
        assignments = self.assignment_repo.get_by_worker_id(worker_id)
        return [AssignmentResponse.from_orm(assignment) for assignment in assignments]
    
    def get_active_assignments(self) -> List[AssignmentResponse]:
        """Get all active assignments."""
        assignments = self.assignment_repo.get_active_assignments()
        return [AssignmentResponse.from_orm(assignment) for assignment in assignments]
    
    def get_current_assignment(self, worker_id: int) -> Optional[AssignmentResponse]:
        """Get current active assignment for a worker."""
        assignment = self.assignment_repo.get_current_assignment(worker_id)
        return AssignmentResponse.from_orm(assignment) if assignment else None
    
    def get_assignments_by_status(self, status: AssignmentStatus) -> List[AssignmentResponse]:
        """Get assignments by status."""
        assignments = self.assignment_repo.get_by_status(status.value)
        return [AssignmentResponse.from_orm(assignment) for assignment in assignments]
    
    def get_assignment_duration(self, assignment_id: int) -> Optional[Dict[str, Any]]:
        """Calculate assignment duration."""
        return self.assignment_repo.get_assignment_duration(assignment_id)
    
    def get_worker_performance(self, worker_id: int, days: int = 30) -> AssignmentPerformance:
        """Get worker performance statistics."""
        performance = self.assignment_repo.get_worker_performance(worker_id, days)
        return AssignmentPerformance(**performance)
    
    def get_assignment_stats(self) -> Dict[str, Any]:
        """Get overall assignment statistics."""
        return self.assignment_repo.get_assignment_stats()
    
    def get_overdue_assignments(self, hours: int = 24) -> List[AssignmentResponse]:
        """Get assignments that have been active for too long."""
        assignments = self.assignment_repo.get_overdue_assignments(hours)
        return [AssignmentResponse.from_orm(assignment) for assignment in assignments]
    
    def get_recommended_workers(self, job_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recommended workers for a job."""
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")
        
        # Get available workers for the job's skill category
        available_workers = self.worker_repo.get_available_workers(job.category)
        
        # Get worker performance data
        recommendations = []
        for worker in available_workers[:limit]:
            performance = self.assignment_repo.get_worker_performance(worker.id, 30)
            workload = self.worker_repo.get_worker_workload(worker.id)
            
            # Calculate recommendation score
            skill_match_score = 100 if worker.skill_category == job.category else 50
            availability_score = 100 if workload['is_available'] else 0
            performance_score = min(performance['completion_rate'], 100)
            overall_score = (skill_match_score * 0.4 + availability_score * 0.3 + performance_score * 0.3)
            
            recommendations.append({
                'worker_id': worker.id,
                'worker_name': worker.full_name,
                'skill_category': worker.skill_category,
                'skill_match_score': skill_match_score,
                'availability_score': availability_score,
                'performance_score': performance_score,
                'overall_score': round(overall_score, 2)
            })
        
        # Sort by overall score
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        return recommendations
    
    def get_assignments_with_pagination(self, page: int = 1, per_page: int = 25,
                                    status: str = None, worker_id: int = None) -> Dict[str, Any]:
        """Get paginated assignments with optional filters."""
        result = self.assignment_repo.get_assignments_with_pagination(
            page, per_page, status, worker_id
        )
        
        # Convert to response models
        result['items'] = [AssignmentResponse.from_orm(assignment) for assignment in result['items']]
        return result
    
    def delete_assignment(self, assignment_id: int) -> bool:
        """Soft delete an assignment."""
        return self.assignment_repo.soft_delete(assignment_id)


# Create service instance
assignment_service = AssignmentService(None, None, None)