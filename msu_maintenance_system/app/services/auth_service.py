"""
Refactored Auth Service
Uses repository pattern and dependency injection for clean architecture.
"""

import re
from typing import Optional, Tuple, Dict, Any, List
from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.user_repository import UserRepository
from app.domain.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    PasswordChange, UserProfile
)
from app.domain import UserRole
from app.security import validate_password_complexity, brute_force_protection


class AuthService:
    """Service for authentication and user management."""
    
    def __init__(self, user_repo: UserRepository = None):
        self.user_repo = user_repo
        # MSU staff email pattern
        self.email_pattern = r'^[a-zA-Z0-9]+@staff\.msu\.ac\.zw$'
    
    def validate_email(self, email: str) -> bool:
        """Validate MSU staff email format."""
        return re.match(self.email_pattern, email) is not None
    
    def authenticate_user(self, login_data: UserLogin) -> Tuple[Optional[UserResponse], str]:
        """
        Authenticate user with email and password.
        
        Args:
            login_data: User login credentials
            
        Returns:
            tuple: (user_response, message) or (None, error_message)
        """
        if not self.validate_email(login_data.email):
            return None, "Invalid MSU staff email format"
        
        # Check brute force protection
        is_locked, remaining_time = brute_force_protection.is_locked(login_data.email)
        if is_locked:
            return None, f"Account locked. Try again in {remaining_time // 60} minutes"
        
        user = self.user_repo.authenticate(login_data.email, login_data.password)
        if user:
            # Record successful attempt and reset counter
            brute_force_protection.record_successful_attempt(login_data.email)
            
            user_response = UserResponse.from_orm(user)
            return user_response, "Login successful"
        else:
            # Record failed attempt
            is_locked, remaining_time = brute_force_protection.record_failed_attempt(login_data.email)
            if is_locked:
                return None, f"Account locked due to too many failed attempts. Try again in {remaining_time // 60} minutes"
            else:
                return None, "Invalid email or password"
    
    def create_user(self, user_data: UserCreate) -> Tuple[Optional[UserResponse], str]:
        """
        Create a new user with validation.
        
        Args:
            user_data: User creation data
            
        Returns:
            tuple: (user_response, message)
        """
        if not self.validate_email(user_data.email):
            return None, "Invalid MSU staff email format"
        
        # Validate password complexity
        is_valid, message = validate_password_complexity(user_data.password)
        if not is_valid:
            return None, message
        
        # Check if email already exists
        if self.user_repo.email_exists(user_data.email):
            return None, "Email already registered"
        
        # Validate role
        if not self.user_repo.is_valid_role(user_data.role.value):
            return None, "Invalid role specified"
        
        # Create user
        user = self.user_repo.create_user(
            user_data.email, 
            user_data.password, 
            user_data.role.value
        )
        
        if user:
            user_response = UserResponse.from_orm(user)
            return user_response, "User created successfully"
        else:
            return None, "Error creating user"
    
    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        user = self.user_repo.get_by_id(user_id)
        return UserResponse.from_orm(user) if user else None
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        user = self.user_repo.get_by_email(email)
        return UserResponse.from_orm(user) if user else None
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get complete user profile with worker details."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        # Get worker profile if exists
        worker_profile = self.user_repo.get_worker_profile(user_id)
        
        profile_data = {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at,
            'worker_profile': worker_profile
        }
        
        return UserProfile(**profile_data)
    
    def update_user(self, user_id: int, update_data: UserUpdate) -> Tuple[Optional[UserResponse], str]:
        """Update user details."""
        # Validate role if being updated
        if update_data.role and not self.user_repo.is_valid_role(update_data.role.value):
            return None, "Invalid role specified"
        
        # Check email uniqueness if being updated
        if update_data.email:
            existing_user = self.user_repo.get_by_email(update_data.email)
            if existing_user and existing_user.id != user_id:
                return None, "Email already registered"
        
        user = self.user_repo.update(user_id, update_data.dict(exclude_unset=True))
        if user:
            user_response = UserResponse.from_orm(user)
            return user_response, "User updated successfully"
        else:
            return None, "Error updating user"
    
    def change_password(self, user_id: int, password_data: PasswordChange) -> Tuple[bool, str]:
        """Change user password."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False, "User not found"
        
        # Verify current password
        if not user.check_password(password_data.current_password):
            return False, "Current password is incorrect"
        
        # Validate new password complexity
        is_valid, message = validate_password_complexity(password_data.new_password)
        if not is_valid:
            return False, message
        
        # Update password
        updated_user = self.user_repo.update_password(user_id, password_data.new_password)
        if updated_user:
            return True, "Password changed successfully"
        else:
            return False, "Error changing password"
    
    def deactivate_user(self, user_id: int) -> Tuple[bool, str]:
        """Deactivate a user."""
        user = self.user_repo.deactivate_user(user_id)
        if user:
            return True, "User deactivated successfully"
        else:
            return False, "Error deactivating user"
    
    def activate_user(self, user_id: int) -> Tuple[bool, str]:
        """Activate a user."""
        user = self.user_repo.activate_user(user_id)
        if user:
            return True, "User activated successfully"
        else:
            return False, "Error activating user"
    
    def get_all_users(self) -> List[UserResponse]:
        """Get all users."""
        users = self.user_repo.get_all()
        return [UserResponse.from_orm(user) for user in users]
    
    def get_active_users(self) -> List[UserResponse]:
        """Get all active users."""
        users = self.user_repo.get_active_users()
        return [UserResponse.from_orm(user) for user in users]
    
    def get_users_by_role(self, role: UserRole) -> List[UserResponse]:
        """Get users by role."""
        users = self.user_repo.get_by_role(role.value)
        return [UserResponse.from_orm(user) for user in users]
    
    def get_admins(self) -> List[UserResponse]:
        """Get all admin users."""
        return self.get_users_by_role(UserRole.ADMIN)
    
    def get_supervisors(self) -> List[UserResponse]:
        """Get all supervisor users."""
        return self.get_users_by_role(UserRole.SUPERVISOR)
    
    def get_staff(self) -> List[UserResponse]:
        """Get all staff users."""
        return self.get_users_by_role(UserRole.STAFF)
    
    def search_users(self, keyword: str) -> List[UserResponse]:
        """Search users by email."""
        users = self.user_repo.search_users(keyword)
        return [UserResponse.from_orm(user) for user in users]
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        return self.user_repo.get_user_stats()
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Soft delete a user."""
        user = self.user_repo.soft_delete(user_id)
        if user:
            return True, "User deleted successfully"
        else:
            return False, "Error deleting user"
    
    def is_valid_role(self, role: str) -> bool:
        """Check if role is valid."""
        return self.user_repo.is_valid_role(role)
    
    def hash_password(self, password: str) -> str:
        """Hash password using secure method."""
        return generate_password_hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(hashed_password, password)
    
    def create_session(self, user_data: dict) -> bool:
        """Create secure session for authenticated user."""
        try:
            from flask import session
            session.clear()
            session['user_id'] = user_data.get('id')
            session['email'] = user_data.get('email')
            session['role'] = user_data.get('role')
            session['full_name'] = user_data.get('full_name')
            session.permanent = True
            return True
        except Exception:
            return False
    
    def logout_user(self) -> bool:
        """Securely logout user and invalidate session."""
        try:
            from flask import session
            session.clear()
            return True
        except Exception:
            return False
    
    def invalidate_session(self) -> bool:
        """Invalidate current session."""
        return self.logout_user()
    
    def check_role(self, required_role: UserRole) -> bool:
        """Check if current user has required role."""
        try:
            from flask import session
            if 'role' not in session:
                return False
            
            user_role = session.get('role')
            
            # Role hierarchy
            role_hierarchy = {
                UserRole.STAFF: 1,
                UserRole.SUPERVISOR: 2,
                UserRole.ADMIN: 3
            }
            
            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(required_role, 0)
            
            return user_level >= required_level
        except Exception:
            return False
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission."""
        try:
            from flask import session
            if 'role' not in session:
                return False
            
            user_role = session.get('role')
            
            # Permission mapping
            role_permissions = {
                UserRole.STAFF: ['view_jobs', 'create_jobs', 'update_own_jobs'],
                UserRole.SUPERVISOR: ['view_jobs', 'create_jobs', 'update_jobs', 'assign_jobs', 'view_reports'],
                UserRole.ADMIN: ['view_jobs', 'create_jobs', 'update_jobs', 'assign_jobs', 'view_reports', 'manage_users', 'system_admin']
            }
            
            return permission in role_permissions.get(user_role, [])
        except Exception:
            return False


# Create service instance
auth_service = AuthService(user_repo=None)  # Will be injected properly in app factory
