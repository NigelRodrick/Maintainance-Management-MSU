"""
Worker Domain Model
Pydantic models for worker business logic.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from . import SkillCategory


class WorkerBase(BaseModel):
    """Base worker model."""
    full_name: str = Field(..., max_length=150)
    department: str = Field(..., max_length=100)
    skill_category: SkillCategory
    is_active: bool = True
    user_id: Optional[int] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Full name must be at least 3 characters long')
        return v.strip().title()
    
    @validator('department')
    def validate_department(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Department must be at least 2 characters long')
        return v.strip().title()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('User ID must be positive')
        return v


class WorkerCreate(WorkerBase):
    """Worker creation model."""
    pass


class WorkerUpdate(BaseModel):
    """Worker update model."""
    full_name: Optional[str] = Field(None, max_length=150)
    department: Optional[str] = Field(None, max_length=100)
    skill_category: Optional[SkillCategory] = None
    is_active: Optional[bool] = None
    user_id: Optional[int] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError('Full name must be at least 3 characters long')
        return v.strip().title() if v else v
    
    @validator('department')
    def validate_department(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Department must be at least 2 characters long')
        return v.strip().title() if v else v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('User ID must be positive')
        return v


class WorkerResponse(WorkerBase):
    """Worker response model."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkerSearchRequest(BaseModel):
    """Worker search request model."""
    keyword: Optional[str] = None
    skill_category: Optional[SkillCategory] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    available_only: bool = False
    page: int = Field(1, ge=1)
    per_page: int = Field(25, ge=1, le=100)
    
    @validator('keyword')
    def validate_keyword(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Search keyword must be at least 2 characters long')
        return v.strip() if v else v


class WorkerWorkload(BaseModel):
    """Worker workload model."""
    worker_id: int
    active_assignments: int
    completed_assignments: int
    is_available: bool


class WorkerPerformance(BaseModel):
    """Worker performance model."""
    worker_id: int
    period_days: int
    total_assignments: int
    completed_assignments: int
    completion_rate: float
    avg_completion_time_hours: float


class WorkerRecommendation(BaseModel):
    """Worker recommendation model."""
    worker: WorkerResponse
    availability_score: float
    skill_match_score: float
    performance_score: float
    overall_score: float


class WorkerStats(BaseModel):
    """Worker statistics model."""
    total_workers: int
    active_workers: int
    skill_category_breakdown: dict
    department_breakdown: dict
