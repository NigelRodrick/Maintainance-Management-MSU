"""
Job Domain Model
Pydantic models for job request business logic.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from . import JobStatus, Priority


class JobRequestBase(BaseModel):
    """Base job request model."""
    department: str = Field(..., max_length=100)
    description: str = Field(..., max_length=2000)
    category: str = Field(..., max_length=50)
    priority: Priority = Priority.MEDIUM
    submitted_by: int = Field(..., gt=0)
    
    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip()
    
    @validator('department')
    def validate_department(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Department must be at least 2 characters long')
        return v.strip().title()
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            'electrical', 'plumbing', 'mechanical', 'civil', 
            'carpentry', 'general', 'hvac', 'painting'
        ]
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()


class JobRequestCreate(JobRequestBase):
    """Job request creation model."""
    pass


class JobRequestUpdate(BaseModel):
    """Job request update model."""
    department: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=50)
    priority: Optional[Priority] = None
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip() if v else v
    
    @validator('department')
    def validate_department(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Department must be at least 2 characters long')
        return v.strip().title() if v else v
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            valid_categories = [
                'electrical', 'plumbing', 'mechanical', 'civil', 
                'carpentry', 'general', 'hvac', 'painting'
            ]
            if v.lower() not in valid_categories:
                raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
            return v.lower()
        return v


class JobRequestResponse(JobRequestBase):
    """Job request response model."""
    id: int
    status: JobStatus
    date_created: datetime
    updated_at: datetime
    reference_no: Optional[str] = None
    
    class Config:
        from_attributes = True


class JobStatusTransition(BaseModel):
    """Job status transition model."""
    from_status: Optional[JobStatus] = None
    to_status: JobStatus
    changed_by: int
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('to_status')
    def validate_transition(cls, v, values):
        from_status = values.get('from_status')
        if from_status:
            valid_transitions = JobStatus.valid_transitions()
            if from_status not in valid_transitions:
                raise ValueError(f'Invalid from_status: {from_status}')
            if v not in valid_transitions[from_status]:
                raise ValueError(f'Cannot transition from {from_status} to {v}')
        return v


class JobSearchRequest(BaseModel):
    """Job search request model."""
    keyword: Optional[str] = None
    status: Optional[JobStatus] = None
    department: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[Priority] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(25, ge=1, le=100)
    
    @validator('keyword')
    def validate_keyword(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Search keyword must be at least 2 characters long')
        return v.strip() if v else v


class JobStats(BaseModel):
    """Job statistics model."""
    total_jobs: int
    pending_jobs: int
    in_progress_jobs: int
    completed_jobs: int
    department_breakdown: dict
    category_breakdown: dict


class JobDashboard(BaseModel):
    """Job dashboard model."""
    stats: JobStats
    recent_jobs: List[JobRequestResponse]
    pending_jobs: List[JobRequestResponse]
    urgent_jobs: List[JobRequestResponse]
