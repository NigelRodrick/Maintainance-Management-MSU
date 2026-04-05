"""
User Repository
Handles all user related database operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from app.repositories import BaseRepository
from app.models import User


class UserRepository(BaseRepository[User]):
    """Repository for user operations."""
    
    def __init__(self, session=None):
        super().__init__(User, session)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.session.query(User).filter(
            and_(
                User.email == email,
                User.is_deleted == False
            )
        ).first()
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return self.session.query(User).filter(
            and_(
                User.is_active == True,
                User.is_deleted == False
            )
        ).all()
    
    def get_by_role(self, role: str) -> List[User]:
        """Get users by role."""
        return self.session.query(User).filter(
            and_(
                User.role == role,
                User.is_active == True,
                User.is_deleted == False
            )
        ).all()
    
    def get_admins(self) -> List[User]:
        """Get all admin users."""
        return self.get_by_role('admin')
    
    def get_supervisors(self) -> List[User]:
        """Get all supervisor users."""
        return self.get_by_role('supervisor')
    
    def get_staff(self) -> List[User]:
        """Get all staff users."""
        return self.get_by_role('staff')
    
    def get_maintenance_admins(self) -> List[User]:
        """Get all maintenance admin users."""
        return self.get_by_role('maintenance_admin')
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_by_email(email)
        if user and user.check_password(password):
            return user
        return None
    
    def create_user(self, email: str, password: str, role: str = 'staff') -> Optional[User]:
        """Create a new user."""
        # Check if user already exists
        if self.get_by_email(email):
            return None
        
        user_data = {
            'email': email,
            'role': role,
            'is_active': True
        }
        
        user = self.create(user_data)
        user.set_password(password)
        self.session.commit()
        self.session.refresh(user)
        
        return user
    
    def update_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Update user password."""
        user = self.get_by_id(user_id)
        if user:
            user.set_password(new_password)
            self.session.commit()
            self.session.refresh(user)
        return user
    
    def update_role(self, user_id: int, new_role: str) -> Optional[User]:
        """Update user role."""
        user = self.get_by_id(user_id)
        if user:
            user.role = new_role
            self.session.commit()
            self.session.refresh(user)
        return user
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            self.session.commit()
            self.session.refresh(user)
        return user
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = True
            self.session.commit()
            self.session.refresh(user)
        return user
    
    def search_users(self, keyword: str) -> List[User]:
        """Search users by email."""
        return self.session.query(User).filter(
            and_(
                User.email.contains(keyword),
                User.is_active == True,
                User.is_deleted == False
            )
        ).all()
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        total_users = self.session.query(User).filter(
            User.is_deleted == False
        ).count()
        
        active_users = self.session.query(User).filter(
            and_(
                User.is_active == True,
                User.is_deleted == False
            )
        ).count()
        
        # Role breakdown
        role_stats = self.session.query(
            User.role,
            self.session.query(User).filter(
                and_(
                    User.role == User.role,
                    User.is_active == True,
                    User.is_deleted == False
                )
            ).count().label('count')
        ).filter(
            and_(
                User.is_active == True,
                User.is_deleted == False
            )
        ).group_by(User.role).all()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'role_breakdown': dict(role_stats)
        }
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return self.session.query(User).filter(
            and_(
                User.email == email,
                User.is_deleted == False
            )
        ).first() is not None
    
    def is_valid_role(self, role: str) -> bool:
        """Check if role is valid."""
        valid_roles = ['admin', 'supervisor', 'staff', 'maintenance_admin']
        return role in valid_roles
