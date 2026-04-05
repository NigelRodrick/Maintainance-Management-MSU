"""
Refactored Material Service
Uses repository pattern and dependency injection for clean architecture.
"""

from typing import List, Optional, Dict, Any
from app.repositories.material_repository import MaterialRepository
from app.repositories.job_repository import JobRepository
from app.domain.material import (
    MaterialCreate, MaterialUpdate, MaterialResponse, 
    MaterialUsage, MaterialSummary
)


class MaterialService:
    """Service for material business logic."""
    
    def __init__(self, material_repo: MaterialRepository = None, job_repo: JobRepository = None):
        self.material_repo = material_repo
        self.job_repo = job_repo
    
    def create_material(self, job_id: int, material_data: MaterialCreate) -> MaterialResponse:
        """Create a new material record."""
        # Validate job exists
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")
        
        # Create material
        material_dict = material_data.dict()
        material_dict['job_id'] = job_id
        
        material = self.material_repo.create(material_dict)
        return MaterialResponse.from_orm(material)
    
    def get_material_by_id(self, material_id: int) -> Optional[MaterialResponse]:
        """Get material by ID."""
        material = self.material_repo.get_by_id(material_id)
        return MaterialResponse.from_orm(material) if material else None
    
    def get_materials_by_job(self, job_id: int) -> List[MaterialResponse]:
        """Get materials for a specific job."""
        materials = self.material_repo.get_by_job_id(job_id)
        return [MaterialResponse.from_orm(material) for material in materials]
    
    def update_material(self, material_id: int, update_data: MaterialUpdate) -> Optional[MaterialResponse]:
        """Update material details."""
        material = self.material_repo.update(material_id, update_data.dict(exclude_unset=True))
        return MaterialResponse.from_orm(material) if material else None
    
    def update_usage(self, material_id: int, usage_data: MaterialUsage) -> Optional[MaterialResponse]:
        """Update material usage."""
        material = self.material_repo.add_usage(material_id, usage_data.additional_usage)
        return MaterialResponse.from_orm(material) if material else None
    
    def set_material_usage(self, material_id: int, quantity_used: float) -> Optional[MaterialResponse]:
        """Set material usage to specific amount."""
        material = self.material_repo.update_usage(material_id, quantity_used)
        return MaterialResponse.from_orm(material) if material else None
    
    def get_material_summary_by_job(self, job_id: int) -> MaterialSummary:
        """Get material summary for a job."""
        summary = self.material_repo.get_material_summary_by_job(job_id)
        return MaterialSummary(**summary)
    
    def get_materials_with_usage_stats(self) -> List[Dict[str, Any]]:
        """Get all materials with usage statistics."""
        return self.material_repo.get_materials_with_usage_stats()
    
    def get_overdue_materials(self) -> List[MaterialResponse]:
        """Get materials that need attention (high usage)."""
        materials = self.material_repo.get_overdue_materials()
        return [MaterialResponse.from_orm(material) for material in materials]
    
    def get_material_cost_estimates(self, job_id: int) -> Dict[str, Any]:
        """Get cost estimates for job materials."""
        return self.material_repo.get_material_cost_estimates(job_id)
    
    def search_materials(self, keyword: str) -> List[MaterialResponse]:
        """Search materials by item name."""
        materials = self.material_repo.search_materials(keyword)
        return [MaterialResponse.from_orm(material) for material in materials]
    
    def get_material_stats(self) -> Dict[str, Any]:
        """Get overall material statistics."""
        return self.material_repo.get_material_stats()
    
    def delete_material(self, material_id: int) -> bool:
        """Soft delete a material."""
        return self.material_repo.soft_delete(material_id)
    
    def validate_material_requirements(self, job_id: int) -> Dict[str, Any]:
        """Validate material requirements for a job."""
        materials = self.material_repo.get_by_job_id(job_id)
        
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        for material in materials:
            if material.quantity_used > material.quantity_required:
                validation_result['is_valid'] = False
                validation_result['errors'].append(
                    f"Material '{material.item_name}' usage exceeds required amount"
                )
            elif material.quantity_used >= material.quantity_required * 0.9:
                validation_result['warnings'].append(
                    f"Material '{material.item_name}' is nearly depleted"
                )
        
        return validation_result


# Create service instance
material_service = MaterialService(None, None)
