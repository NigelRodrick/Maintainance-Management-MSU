"""
Material Domain Model
Pydantic models for material business logic.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class MaterialBase(BaseModel):
    """Base material model."""
    job_id: int = Field(..., gt=0)
    item_name: str = Field(..., max_length=150)
    unit: str = Field("units", max_length=30)
    quantity_required: float = Field(..., gt=0)
    quantity_used: float = Field(0.0, ge=0)
    
    @validator('item_name')
    def validate_item_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Item name must be at least 2 characters long')
        return v.strip()
    
    @validator('unit')
    def validate_unit(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Unit must be at least 1 character long')
        return v.strip().lower()
    
    @validator('quantity_used')
    def validate_quantity_used(cls, v, values):
        if 'quantity_required' in values and v > values['quantity_required']:
            raise ValueError('Quantity used cannot exceed quantity required')
        return v


class MaterialCreate(MaterialBase):
    """Material creation model."""
    pass


class MaterialUpdate(BaseModel):
    """Material update model."""
    item_name: Optional[str] = Field(None, max_length=150)
    unit: Optional[str] = Field(None, max_length=30)
    quantity_required: Optional[float] = Field(None, gt=0)
    quantity_used: Optional[float] = Field(None, ge=0)
    
    @validator('item_name')
    def validate_item_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Item name must be at least 2 characters long')
        return v.strip() if v else v
    
    @validator('unit')
    def validate_unit(cls, v):
        if v is not None and len(v.strip()) < 1:
            raise ValueError('Unit must be at least 1 character long')
        return v.strip().lower() if v else v


class MaterialResponse(MaterialBase):
    """Material response model."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MaterialUsage(BaseModel):
    """Material usage model."""
    material_id: int
    additional_usage: float = Field(..., gt=0)
    
    @validator('additional_usage')
    def validate_additional_usage(cls, v):
        if v <= 0:
            raise ValueError('Additional usage must be positive')
        return v


class MaterialSummary(BaseModel):
    """Material summary model."""
    job_id: int
    total_materials: int
    total_required: float
    total_used: float
    remaining: float
    usage_percentage: float
    materials: List[MaterialResponse]


class MaterialStats(BaseModel):
    """Material statistics model."""
    total_materials: int
    most_used_materials: List[dict]
    unit_breakdown: dict


class MaterialSearchRequest(BaseModel):
    """Material search request model."""
    keyword: Optional[str] = None
    job_id: Optional[int] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(25, ge=1, le=100)
    
    @validator('keyword')
    def validate_keyword(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Search keyword must be at least 2 characters long')
        return v.strip() if v else v
