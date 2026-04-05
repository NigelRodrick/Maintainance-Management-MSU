"""
Base Repository Pattern
Provides common database operations and enforces consistent data access patterns.
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[T], session: Session = None):
        self.model = model
        self.session = session or db.session
    
    def create(self, entity_data: Dict[str, Any]) -> T:
        """Create a new entity."""
        entity = self.model(**entity_data)
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID, respecting soft delete."""
        return self.session.query(self.model).filter(
            and_(
                self.model.id == entity_id,
                getattr(self.model, 'is_deleted', False) == False
            )
        ).first()
    
    def get_all(self, include_deleted: bool = False) -> List[T]:
        """Get all entities, optionally including deleted ones."""
        query = self.session.query(self.model)
        
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        return query.all()
    
    def update(self, entity_id: int, update_data: Dict[str, Any]) -> Optional[T]:
        """Update an entity."""
        entity = self.get_by_id(entity_id)
        if entity:
            for key, value in update_data.items():
                setattr(entity, key, value)
            self.session.commit()
            self.session.refresh(entity)
        return entity
    
    def soft_delete(self, entity_id: int) -> bool:
        """Soft delete an entity if it supports soft delete."""
        entity = self.get_by_id(entity_id)
        if entity and hasattr(entity, 'is_deleted'):
            entity.is_deleted = True
            self.session.commit()
            return True
        return False
    
    def hard_delete(self, entity_id: int) -> bool:
        """Hard delete an entity."""
        entity = self.session.query(self.model).filter(self.model.id == entity_id).first()
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
    
    def count(self, include_deleted: bool = False) -> int:
        """Count entities."""
        query = self.session.query(self.model)
        
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        return query.count()
    
    def exists(self, entity_id: int) -> bool:
        """Check if entity exists."""
        return self.session.query(self.model).filter(
            and_(
                self.model.id == entity_id,
                getattr(self.model, 'is_deleted', False) == False
            )
        ).first() is not None
    
    def find_by_criteria(self, criteria: Dict[str, Any], 
                        include_deleted: bool = False) -> List[T]:
        """Find entities by custom criteria."""
        query = self.session.query(self.model)
        
        # Apply criteria filters
        for key, value in criteria.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        # Apply soft delete filter
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        return query.all()
    
    def find_one_by_criteria(self, criteria: Dict[str, Any], 
                          include_deleted: bool = False) -> Optional[T]:
        """Find one entity by custom criteria."""
        query = self.session.query(self.model)
        
        # Apply criteria filters
        for key, value in criteria.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        # Apply soft delete filter
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        return query.first()
    
    def paginate(self, page: int = 1, per_page: int = 25, 
                include_deleted: bool = False) -> Dict[str, Any]:
        """Paginate results."""
        query = self.session.query(self.model)
        
        # Apply soft delete filter
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        # Calculate pagination
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
