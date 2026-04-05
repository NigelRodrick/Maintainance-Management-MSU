"""
Assignment Domain Model
Pydantic models for assignment business logic.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from . import AssignmentStatus


class AssignmentBase(BaseModel):
    """Base assignment model."""
    job_id: int = Field(..., gt=0)
    worker_id: int = Field(..., gt=0)
    status: AssignmentStatus = AssignmentStatus.ASSIGNED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        start_time = values.get('start_time')
        if start_time and v and v <= start_time:
            raise ValueError('End time must be after start time')
        return v


class AssignmentCreate(AssignmentBase):
    """Assignment creation model."""
    pass


class AssignmentUpdate(BaseModel):
    """Assignment update model."""
    worker_id: Optional[int] = Field(None, gt=0)
    status: Optional[AssignmentStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        start_time = values.get('start_time')
        if start_time and v and v <= start_time:
            raise ValueError('End time must be after start time')
        return v


class AssignmentResponse(AssignmentBase):
    """Assignment response model."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssignmentTransition(BaseModel):
    """Assignment transition model."""
    assignment_id: int
    new_status: AssignmentStatus
    notes: Optional[str] = Field(None, max_length=500)


class AssignmentDuration(BaseModel):
    """Assignment duration model."""
    assignment_id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    duration_hours: Optional[float]
    is_completed: bool


class AssignmentPerformance(BaseModel):
    """Assignment performance model."""
    worker_id: int
    period_days: int
    total_assignments: int
    completed_assignments: int
    completion_rate: float
    avg_completion_time_hours: float


class AssignmentStats(BaseModel):
    """Assignment statistics model."""
    total_assignments: int
    active_assignments: int
    status_breakdown: dict


class AssignmentSearchRequest(BaseModel):
    """Assignment search request model."""
    status: Optional[AssignmentStatus] = None
    worker_id: Optional[int] = None
    job_id: Optional[int] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(25, ge=1, le=100)


class WorkerRecommendation(BaseModel):
    """Worker recommendation model."""
    job_id: int
    skill_category: str
    recommended_workers: List[dict]
    recommendation_score: float
