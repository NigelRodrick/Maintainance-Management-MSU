"""
Worker Service
Uses repository pattern and dependency injection for clean architecture.
"""

from typing import List, Optional, Dict, Any
from app.repositories.worker_repository import WorkerRepository
from app.repositories.user_repository import UserRepository
from app.domain.worker import (
    WorkerCreate, WorkerUpdate, WorkerResponse, 
    WorkerSearchRequest, WorkerWorkload, WorkerPerformance
)
from app.domain import SkillCategory


class WorkerService:
    """Service for worker business logic."""
    
    def __init__(self, worker_repo: WorkerRepository, user_repo: UserRepository):
        self.worker_repo = worker_repo
        self.user_repo = user_repo
    
    def create_worker(self, worker_data: WorkerCreate) -> WorkerResponse:
        """Create a new worker."""
        # Link to user if user_id is provided
        if worker_data.user_id:
            user = self.user_repo.get_by_id(worker_data.user_id)
            if not user:
                raise ValueError(f"User with ID {worker_data.user_id} not found")
        
        worker = self.worker_repo.create(worker_data.dict())
        return WorkerResponse.from_orm(worker)
    
    def get_worker_by_id(self, worker_id: int) -> Optional[WorkerResponse]:
        """Get worker by ID."""
        worker = self.worker_repo.get_by_id(worker_id)
        return WorkerResponse.from_orm(worker) if worker else None
    
    def get_worker_by_user_id(self, user_id: int) -> Optional[WorkerResponse]:
        """Get worker profile associated with a user."""
        worker = self.worker_repo.get_worker_by_user_id(user_id)
        return WorkerResponse.from_orm(worker) if worker else None
    
    def update_worker(self, worker_id: int, update_data: WorkerUpdate) -> Optional[WorkerResponse]:
        """Update worker details."""
        # Link to user if user_id is provided
        if hasattr(update_data, 'user_id') and update_data.user_id:
            user = self.user_repo.get_by_id(update_data.user_id)
            if not user:
                raise ValueError(f"User with ID {update_data.user_id} not found")
        
        worker = self.worker_repo.update(worker_id, update_data.dict(exclude_unset=True))
        return WorkerResponse.from_orm(worker) if worker else None
    
    def get_active_workers(self) -> List[WorkerResponse]:
        """Get all active workers."""
        workers = self.worker_repo.get_active_workers()
        return [WorkerResponse.from_orm(worker) for worker in workers]
    
    def get_workers_by_skill_category(self, skill_category: SkillCategory) -> List[WorkerResponse]:
        """Get workers by skill category."""
        workers = self.worker_repo.get_by_skill_category(skill_category.value)
        return [WorkerResponse.from_orm(worker) for worker in workers]
    
    def get_workers_by_department(self, department: str) -> List[WorkerResponse]:
        """Get workers by department."""
        workers = self.worker_repo.get_by_department(department)
        return [WorkerResponse.from_orm(worker) for worker in workers]
    
    def get_available_workers(self, skill_category: SkillCategory = None) -> List[WorkerResponse]:
        """Get workers who are not currently assigned to active jobs."""
        workers = self.worker_repo.get_available_workers(
            skill_category.value if skill_category else None
        )
        return [WorkerResponse.from_orm(worker) for worker in workers]
    
    def search_workers(self, search_request: WorkerSearchRequest) -> Dict[str, Any]:
        """Search workers with filters."""
        # Build criteria from search request
        criteria = {}
        if search_request.skill_category:
            criteria['skill_category'] = search_request.skill_category.value
        if search_request.department:
            criteria['department'] = search_request.department
        if search_request.is_active is not None:
            criteria['is_active'] = search_request.is_active
        
        # Get workers
        if search_request.keyword:
            workers = self.worker_repo.search_workers(search_request.keyword)
            # Apply additional filters
            if criteria:
                filtered_workers = []
                for worker in workers:
                    match = True
                    for key, value in criteria.items():
                        if getattr(worker, key, None) != value:
                            match = False
                            break
                    if match:
                        filtered_workers.append(worker)
                workers = filtered_workers
        else:
            workers = self.worker_repo.find_by_criteria(criteria)
        
        # Filter by availability if requested
        if search_request.available_only:
            available_workers = []
            for worker in workers:
                workload = self.worker_repo.get_worker_workload(worker.id)
                if workload['is_available']:
                    available_workers.append(worker)
            workers = available_workers
        
        # Manual pagination
        start = (search_request.page - 1) * search_request.per_page
        end = start + search_request.per_page
        paginated_workers = workers[start:end]
        
        return {
            'items': [WorkerResponse.from_orm(worker) for worker in paginated_workers],
            'total': len(workers),
            'page': search_request.page,
            'per_page': search_request.per_page,
            'pages': (len(workers) + search_request.per_page - 1) // search_request.per_page
        }
    
    def get_worker_workload(self, worker_id: int) -> WorkerWorkload:
        """Get current workload statistics for a worker."""
        workload = self.worker_repo.get_worker_workload(worker_id)
        return WorkerWorkload(**workload)
    
    def get_worker_performance(self, worker_id: int, days: int = 30) -> WorkerPerformance:
        """Get worker performance statistics."""
        performance = self.worker_repo.get_worker_performance_stats(worker_id, days)
        return WorkerPerformance(**performance)
    
    def update_availability(self, worker_id: int, is_active: bool) -> Optional[WorkerResponse]:
        """Update worker availability status."""
        worker = self.worker_repo.update_availability(worker_id, is_active)
        return WorkerResponse.from_orm(worker) if worker else None
    
    def assign_to_user(self, worker_id: int, user_id: int) -> Optional[WorkerResponse]:
        """Link worker to a user account."""
        # Validate user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        worker = self.worker_repo.assign_to_user(worker_id, user_id)
        return WorkerResponse.from_orm(worker) if worker else None
    
    def get_recommended_workers(self, skill_category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recommended workers for a skill category."""
        workers = self.worker_repo.get_recommended_workers(skill_category, limit)
        
        recommendations = []
        for worker in workers:
            workload = self.worker_repo.get_worker_workload(worker.id)
            performance = self.worker_repo.get_worker_performance_stats(worker.id, 30)
            
            # Calculate recommendation scores
            availability_score = 100 if workload['is_available'] else 0
            performance_score = min(performance['completion_rate'], 100)
            skill_match_score = 100 if worker.skill_category.lower() == skill_category.lower() else 50
            overall_score = (skill_match_score * 0.4 + availability_score * 0.3 + performance_score * 0.3)
            
            recommendations.append({
                'worker_id': worker.id,
                'worker_name': worker.full_name,
                'skill_category': worker.skill_category,
                'department': worker.department,
                'availability_score': availability_score,
                'performance_score': performance_score,
                'skill_match_score': skill_match_score,
                'overall_score': round(overall_score, 2)
            })
        
        # Sort by overall score
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        return recommendations
    
    def get_workers_by_skill_breakdown(self) -> Dict[str, int]:
        """Get breakdown of workers by skill category."""
        return self.worker_repo.get_workers_by_skill_breakdown()
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get overall worker statistics."""
        active_workers = self.worker_repo.get_active_workers()
        skill_breakdown = self.worker_repo.get_workers_by_skill_breakdown()
        
        return {
            'total_workers': len(active_workers),
            'active_workers': len(active_workers),
            'skill_category_breakdown': skill_breakdown
        }
    
    def delete_worker(self, worker_id: int) -> bool:
        """Soft delete a worker."""
        return self.worker_repo.soft_delete(worker_id)
