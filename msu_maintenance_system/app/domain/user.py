"""
User Domain Model
Pydantic models for user business logic.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr
from . import UserRole


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    role: UserRole = UserRole.STAFF
    is_active: bool = True
    
    @validator('role')
    def validate_role(cls, v):
        return v.value if hasattr(v, 'value') else v


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=10)
    confirm_password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 10:
            raise ValueError('Password must be at least 10 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)
        
        if not has_upper:
            raise ValueError('Password must contain at least one uppercase letter')
        if not has_lower:
            raise ValueError('Password must contain at least one lowercase letter')
        if not has_digit:
            raise ValueError('Password must contain at least one digit')
        if not has_special:
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            return v.value if hasattr(v, 'value') else v
        return v


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str
    remember_me: bool = False


class UserResponse(UserBase):
    """User response model."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile model."""
    id: int
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    worker_profile: Optional['WorkerResponse'] = None
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change model."""
    current_password: str
    new_password: str = Field(..., min_length=10)
    confirm_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 10:
            raise ValueError('Password must be at least 10 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)
        
        if not has_upper:
            raise ValueError('Password must contain at least one uppercase letter')
        if not has_lower:
            raise ValueError('Password must contain at least one lowercase letter')
        if not has_digit:
            raise ValueError('Password must contain at least one digit')
        if not has_special:
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserSearchRequest(BaseModel):
    """User search request model."""
    keyword: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(25, ge=1, le=100)
    
    @validator('keyword')
    def validate_keyword(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Search keyword must be at least 2 characters long')
        return v.strip() if v else v


class UserStats(BaseModel):
    """User statistics model."""
    total_users: int
    active_users: int
    inactive_users: int
    role_breakdown: dict
