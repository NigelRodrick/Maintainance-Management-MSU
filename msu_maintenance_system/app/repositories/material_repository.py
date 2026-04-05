"""
Material Repository
Handles all material related database operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, desc, asc, func
from app.repositories import BaseRepository
from app.models import Material


class MaterialRepository(BaseRepository[Material]):
    """Repository for material operations."""
    
    def __init__(self, session=None):
        super().__init__(Material, session)
    
    def get_by_job_id(self, job_id: int) -> List[Material]:
        """Get materials for a specific job."""
        return self.session.query(Material).filter(
            and_(
                Material.job_id == job_id,
                Material.is_deleted == False
            )
        ).all()
    
    def get_by_item_name(self, item_name: str) -> List[Material]:
        """Get materials by item name."""
        return self.session.query(Material).filter(
            and_(
                Material.item_name.contains(item_name),
                Material.is_deleted == False
            )
        ).all()
    
    def get_materials_with_usage_stats(self) -> List[Dict[str, Any]]:
        """Get materials with usage statistics."""
        materials = self.session.query(Material).filter(
            Material.is_deleted == False
        ).all()
        
        result = []
        for material in materials:
            usage_rate = 0
            if material.quantity_required > 0:
                usage_rate = (material.quantity_used / material.quantity_required) * 100
            
            result.append({
                'id': material.id,
                'job_id': material.job_id,
                'item_name': material.item_name,
                'unit': material.unit,
                'quantity_required': float(material.quantity_required),
                'quantity_used': float(material.quantity_used),
                'usage_rate': round(usage_rate, 2),
                'remaining': float(material.quantity_required - material.quantity_used)
            })
        
        return result
    
    def create_material(self, job_id: int, item_name: str, quantity_required: float,
                      unit: str = 'units') -> Optional[Material]:
        """Create a new material record."""
        material_data = {
            'job_id': job_id,
            'item_name': item_name,
            'quantity_required': quantity_required,
            'quantity_used': 0,
            'unit': unit
        }
        
        return self.create(material_data)
    
    def update_usage(self, material_id: int, quantity_used: float) -> Optional[Material]:
        """Update material usage."""
        material = self.get_by_id(material_id)
        if material:
            # Ensure we don't exceed required quantity
            if quantity_used <= material.quantity_required:
                material.quantity_used = quantity_used
                self.session.commit()
                self.session.refresh(material)
            else:
                raise ValueError(f"Quantity used ({quantity_used}) cannot exceed required quantity ({material.quantity_required})")
        return material
    
    def add_usage(self, material_id: int, additional_usage: float) -> Optional[Material]:
        """Add to material usage."""
        material = self.get_by_id(material_id)
        if material:
            new_usage = material.quantity_used + additional_usage
            if new_usage <= material.quantity_required:
                material.quantity_used = new_usage
                self.session.commit()
                self.session.refresh(material)
            else:
                raise ValueError(f"Additional usage would exceed required quantity")
        return material
    
    def get_material_summary_by_job(self, job_id: int) -> Dict[str, Any]:
        """Get material summary for a job."""
        materials = self.get_by_job_id(job_id)
        
        total_required = sum(m.quantity_required for m in materials)
        total_used = sum(m.quantity_used for m in materials)
        
        return {
            'job_id': job_id,
            'total_materials': len(materials),
            'total_required': float(total_required),
            'total_used': float(total_used),
            'remaining': float(total_required - total_used),
            'usage_percentage': round((total_used / total_required * 100) if total_required > 0 else 0, 2),
            'materials': [
                {
                    'id': m.id,
                    'item_name': m.item_name,
                    'unit': m.unit,
                    'quantity_required': float(m.quantity_required),
                    'quantity_used': float(m.quantity_used),
                    'remaining': float(m.quantity_required - m.quantity_used)
                }
                for m in materials
            ]
        }
    
    def get_overdue_materials(self) -> List[Material]:
        """Get materials that might need attention (high usage)."""
        materials = self.session.query(Material).filter(
            Material.is_deleted == False
        ).all()
        
        overdue = []
        for material in materials:
            if material.quantity_required > 0:
                usage_rate = (material.quantity_used / material.quantity_required) * 100
                if usage_rate >= 90:  # 90% or more used
                    overdue.append(material)
        
        return overdue
    
    def get_material_cost_estimates(self, job_id: int) -> Dict[str, Any]:
        """Get cost estimates for job materials (placeholder for future cost tracking)."""
        materials = self.get_by_job_id(job_id)
        
        # This is a placeholder - in a real implementation, you'd have cost data
        return {
            'job_id': job_id,
            'estimated_cost': 0.0,  # Would calculate based on material costs
            'material_count': len(materials),
            'materials': [
                {
                    'item_name': m.item_name,
                    'quantity_required': float(m.quantity_required),
                    'unit_cost': 0.0,  # Would come from material catalog
                    'total_cost': 0.0
                }
                for m in materials
            ]
        }
    
    def search_materials(self, keyword: str) -> List[Material]:
        """Search materials by item name."""
        return self.session.query(Material).filter(
            and_(
                Material.item_name.contains(keyword),
                Material.is_deleted == False
            )
        ).all()
    
    def get_material_stats(self) -> Dict[str, Any]:
        """Get overall material statistics."""
        total_materials = self.session.query(Material).filter(
            Material.is_deleted == False
        ).count()
        
        # Most used materials
        most_used = self.session.query(
            Material.item_name,
            func.sum(Material.quantity_used).label('total_used')
        ).filter(
            Material.is_deleted == False
        ).group_by(Material.item_name).order_by(
            desc(func.sum(Material.quantity_used))
        ).limit(10).all()
        
        # Materials by unit
        unit_stats = self.session.query(
            Material.unit,
            func.count(Material.id).label('count')
        ).filter(
            Material.is_deleted == False
        ).group_by(Material.unit).all()
        
        return {
            'total_materials': total_materials,
            'most_used_materials': [{'item_name': name, 'total_used': float(used)} for name, used in most_used],
            'unit_breakdown': dict(unit_stats)
        }
