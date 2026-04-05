"""
Assignment Repository
Handles all assignment related database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc, asc, func
from app.repositories import BaseRepository
from app.models import Assignment, JobRequest, Worker


class AssignmentRepository(BaseRepository[Assignment]):
    """Repository for assignment operations."""
    
    def __init__(self, session=None):
        super().__init__(Assignment, session)
    
    def get_by_job_id(self, job_id: int) -> List[Assignment]:
        """Get assignments for a specific job."""
        return self.session.query(Assignment).filter(
            and_(
                Assignment.job_id == job_id,
                Assignment.is_deleted == False
            )
        ).all()
    
    def get_by_worker_id(self, worker_id: int) -> List[Assignment]:
        """Get assignments for a specific worker."""
        return self.session.query(Assignment).filter(
            and_(
                Assignment.worker_id == worker_id,
                Assignment.is_deleted == False
            )
        ).all()
    
    def get_active_assignments(self) -> List[Assignment]:
        """Get all active assignments (ASSIGNED or IN_PROGRESS)."""
        return self.session.query(Assignment).filter(
            and_(
                Assignment.status.in_(['ASSIGNED', 'IN_PROGRESS']),
                Assignment.is_deleted == False
            )
        ).all()
    
    def get_by_status(self, status: str) -> List[Assignment]:
        """Get assignments by status."""
        return self.session.query(Assignment).filter(
            and_(
                Assignment.status == status,
                Assignment.is_deleted == False
            )
        ).all()
    
    def get_current_assignment(self, worker_id: int) -> Optional[Assignment]:
        """Get current active assignment for a worker."""
        return self.session.query(Assignment).filter(
            and_(
                Assignment.worker_id == worker_id,
                Assignment.status.in_(['ASSIGNED', 'IN_PROGRESS']),
                Assignment.is_deleted == False
            )
        ).first()
    
    def create_assignment(self, job_id: int, worker_id: int) -> Optional[Assignment]:
        """Create a new assignment."""
        # Check if worker is available
        current_assignment = self.get_current_assignment(worker_id)
        if current_assignment:
            raise ValueError(f"Worker {worker_id} already has an active assignment")
        
        assignment_data = {
            'job_id': job_id,
            'worker_id': worker_id,
            'status': 'ASSIGNED'
        }
        
        return self.create(assignment_data)
    
    def start_assignment(self, assignment_id: int) -> Optional[Assignment]:
        """Start an assignment (change status to IN_PROGRESS)."""
        assignment = self.get_by_id(assignment_id)
        if assignment and assignment.status == 'ASSIGNED':
            assignment.status = 'IN_PROGRESS'
            assignment.start_time = datetime.utcnow()
            self.session.commit()
            self.session.refresh(assignment)
        return assignment
    
    def complete_assignment(self, assignment_id: int) -> Optional[Assignment]:
        """Complete an assignment."""
        assignment = self.get_by_id(assignment_id)
        if assignment and assignment.status == 'IN_PROGRESS':
            assignment.status = 'COMPLETED'
            assignment.end_time = datetime.utcnow()
            self.session.commit()
            self.session.refresh(assignment)
        return assignment
    
    def cancel_assignment(self, assignment_id: int) -> Optional[Assignment]:
        """Cancel an assignment."""
        assignment = self.get_by_id(assignment_id)
        if assignment and assignment.status in ['ASSIGNED', 'IN_PROGRESS']:
            assignment.status = 'CANCELLED'
            assignment.end_time = datetime.utcnow()
            self.session.commit()
            self.session.refresh(assignment)
        return assignment
    
    def reassign_worker(self, assignment_id: int, new_worker_id: int) -> Optional[Assignment]:
        """Reassign an assignment to a different worker."""
        assignment = self.get_by_id(assignment_id)
        if assignment:
            # Check if new worker is available
            current_assignment = self.get_current_assignment(new_worker_id)
            if current_assignment and current_assignment.id != assignment_id:
                raise ValueError(f"Worker {new_worker_id} already has an active assignment")
            
            assignment.worker_id = new_worker_id
            assignment.status = 'ASSIGNED'
            assignment.start_time = None
            assignment.end_time = None
            self.session.commit()
            self.session.refresh(assignment)
        return assignment
    
    def get_assignment_duration(self, assignment_id: int) -> Optional[Dict[str, Any]]:
        """Calculate assignment duration."""
        assignment = self.get_by_id(assignment_id)
        if not assignment or not assignment.start_time:
            return None
        
        end_time = assignment.end_time or datetime.utcnow()
        duration = end_time - assignment.start_time
        
        return {
            'assignment_id': assignment_id,
            'start_time': assignment.start_time,
            'end_time': assignment.end_time,
            'duration_seconds': duration.total_seconds(),
            'duration_hours': duration.total_seconds() / 3600,
            'is_completed': assignment.status == 'COMPLETED'
        }
    
    def get_worker_performance(self, worker_id: int, days: int = 30) -> Dict[str, Any]:
        """Get worker performance statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        assignments = self.session.query(Assignment).filter(
            and_(
                Assignment.worker_id == worker_id,
                Assignment.created_at >= cutoff_date,
                Assignment.is_deleted == False
            )
        ).all()
        
        total_assignments = len(assignments)
        completed_assignments = len([a for a in assignments if a.status == 'COMPLETED'])
        
        # Calculate average completion time
        completed_with_times = [a for a in assignments if a.status == 'COMPLETED' and a.start_time and a.end_time]
        avg_completion_time = 0
        if completed_with_times:
            total_time = sum([(a.end_time - a.start_time).total_seconds() for a in completed_with_times])
            avg_completion_time = total_time / len(completed_with_times) / 3600  # Convert to hours
        
        return {
            'worker_id': worker_id,
            'period_days': days,
            'total_assignments': total_assignments,
            'completed_assignments': completed_assignments,
            'completion_rate': round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0, 2),
            'avg_completion_time_hours': round(avg_completion_time, 2)
        }
    
    def get_assignment_stats(self) -> Dict[str, Any]:
        """Get overall assignment statistics."""
        total_assignments = self.session.query(Assignment).filter(
            Assignment.is_deleted == False
        ).count()
        
        status_breakdown = self.session.query(
            Assignment.status,
            func.count(Assignment.id).label('count')
        ).filter(
            Assignment.is_deleted == False
        ).group_by(Assignment.status).all()
        
        # Active assignments
        active_assignments = self.session.query(Assignment).filter(
            and_(
                Assignment.status.in_(['ASSIGNED', 'IN_PROGRESS']),
                Assignment.is_deleted == False
            )
        ).count()
        
        return {
            'total_assignments': total_assignments,
            'active_assignments': active_assignments,
            'status_breakdown': dict(status_breakdown)
        }
    
    def get_overdue_assignments(self, hours: int = 24) -> List[Assignment]:
        """Get assignments that have been active for too long."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return self.session.query(Assignment).filter(
            and_(
                Assignment.status.in_(['ASSIGNED', 'IN_PROGRESS']),
                Assignment.created_at < cutoff_time,
                Assignment.is_deleted == False
            )
        ).all()
    
    def get_assignments_with_pagination(self, page: int = 1, per_page: int = 25,
                                    status: str = None, worker_id: int = None) -> Dict[str, Any]:
        """Get paginated assignments with optional filters."""
        query = self.session.query(Assignment).filter(Assignment.is_deleted == False)
        
        # Apply filters
        if status:
            query = query.filter(Assignment.status == status)
        if worker_id:
            query = query.filter(Assignment.worker_id == worker_id)
        
        # Order by created date (newest first)
        query = query.order_by(desc(Assignment.created_at))
        
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
