"""
Worker Repository
Handles all worker related database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import and_, or_, desc, asc
from app.repositories import BaseRepository
from app.models import Worker, Assignment


class WorkerRepository(BaseRepository[Worker]):
    """Repository for worker operations."""
    
    def __init__(self, session=None):
        super().__init__(Worker, session)
    
    def get_active_workers(self) -> List[Worker]:
        """Get all active workers."""
        return self.session.query(Worker).filter(
            and_(
                Worker.is_active == True,
                Worker.is_deleted == False
            )
        ).all()
    
    def get_by_skill_category(self, skill_category: str) -> List[Worker]:
        """Get workers by skill category."""
        return self.session.query(Worker).filter(
            and_(
                Worker.skill_category == skill_category,
                Worker.is_active == True,
                Worker.is_deleted == False
            )
        ).all()
    
    def get_by_department(self, department: str) -> List[Worker]:
        """Get workers by department."""
        return self.session.query(Worker).filter(
            and_(
                Worker.department == department,
                Worker.is_active == True,
                Worker.is_deleted == False
            )
        ).all()
    
    def get_available_workers(self, skill_category: str = None) -> List[Worker]:
        """Get workers who are not currently assigned to active jobs."""
        # Subquery to get workers with active assignments
        active_worker_ids = self.session.query(Assignment.worker_id).filter(
            and_(
                Assignment.status.in_(['ASSIGNED', 'IN_PROGRESS']),
                Assignment.is_deleted == False
            )
        ).subquery()
        
        query = self.session.query(Worker).filter(
            and_(
                Worker.is_active == True,
                Worker.is_deleted == False,
                ~Worker.id.in_(active_worker_ids)
            )
        )
        
        if skill_category:
            query = query.filter(Worker.skill_category == skill_category)
        
        return query.all()
    
    def get_worker_workload(self, worker_id: int) -> Dict[str, Any]:
        """Get current workload statistics for a worker."""
        active_assignments = self.session.query(Assignment).filter(
            and_(
                Assignment.worker_id == worker_id,
                Assignment.status.in_(['ASSIGNED', 'IN_PROGRESS']),
                Assignment.is_deleted == False
            )
        ).count()
        
        completed_assignments = self.session.query(Assignment).filter(
            and_(
                Assignment.worker_id == worker_id,
                Assignment.status == 'COMPLETED',
                Assignment.is_deleted == False
            )
        ).count()
        
        return {
            'worker_id': worker_id,
            'active_assignments': active_assignments,
            'completed_assignments': completed_assignments,
            'is_available': active_assignments == 0
        }
    
    def search_workers(self, keyword: str) -> List[Worker]:
        """Search workers by name or department."""
        return self.session.query(Worker).filter(
            and_(
                or_(
                    Worker.full_name.contains(keyword),
                    Worker.department.contains(keyword),
                    Worker.skill_category.contains(keyword)
                ),
                Worker.is_active == True,
                Worker.is_deleted == False
            )
        ).all()
    
    def get_workers_by_skill_breakdown(self) -> Dict[str, int]:
        """Get breakdown of workers by skill category."""
        result = self.session.query(
            Worker.skill_category,
            self.session.query(Worker).filter(
                and_(
                    Worker.skill_category == Worker.skill_category,
                    Worker.is_active == True,
                    Worker.is_deleted == False
                )
            ).count().label('count')
        ).filter(
            and_(
                Worker.is_active == True,
                Worker.is_deleted == False
            )
        ).group_by(Worker.skill_category).all()
        
        return dict(result)
    
    def update_availability(self, worker_id: int, is_active: bool) -> Optional[Worker]:
        """Update worker availability status."""
        worker = self.get_by_id(worker_id)
        if worker:
            worker.is_active = is_active
            worker.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(worker)
        return worker
    
    def assign_to_user(self, worker_id: int, user_id: int) -> Optional[Worker]:
        """Link worker to a user account."""
        worker = self.get_by_id(worker_id)
        if worker:
            worker.user_id = user_id
            worker.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(worker)
        return worker
    
    def get_worker_by_user_id(self, user_id: int) -> Optional[Worker]:
        """Get worker profile associated with a user."""
        return self.session.query(Worker).filter(
            and_(
                Worker.user_id == user_id,
                Worker.is_deleted == False
            )
        ).first()
    
    def get_recommended_workers(self, skill_category: str, limit: int = 5) -> List[Worker]:
        """Get recommended workers for a skill category based on availability."""
        available_workers = self.get_available_workers(skill_category)
        
        # Sort by skill category match and return top recommendations
        matching_workers = [w for w in available_workers if w.skill_category == skill_category]
        other_workers = [w for w in available_workers if w.skill_category != skill_category]
        
        recommended = matching_workers + other_workers
        return recommended[:limit]
    
    def get_worker_performance_stats(self, worker_id: int) -> Dict[str, Any]:
        """Get performance statistics for a worker."""
        total_assignments = self.session.query(Assignment).filter(
            and_(
                Assignment.worker_id == worker_id,
                Assignment.is_deleted == False
            )
        ).count()
        
        completed_assignments = self.session.query(Assignment).filter(
            and_(
                Assignment.worker_id == worker_id,
                Assignment.status == 'COMPLETED',
                Assignment.is_deleted == False
            )
        ).count()
        
        # Calculate completion rate
        completion_rate = 0
        if total_assignments > 0:
            completion_rate = (completed_assignments / total_assignments) * 100
        
        return {
            'worker_id': worker_id,
            'total_assignments': total_assignments,
            'completed_assignments': completed_assignments,
            'completion_rate': round(completion_rate, 2)
        }
