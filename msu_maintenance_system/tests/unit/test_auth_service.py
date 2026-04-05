"""
Unit Tests for Auth Service
Tests all auth service operations with mocked repositories.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService
from app.domain.user import UserCreate, UserLogin, PasswordChange
from app.domain import UserRole


class TestAuthService:
    """Test cases for AuthService."""
    
    def test_init(self):
        """Test service initialization."""
        # Arrange
        mock_user_repo = Mock()
        
        # Act
        auth_service = AuthService(mock_user_repo)
        
        # Assert
        assert auth_service.user_repo == mock_user_repo
        assert auth_service.email_pattern == r'^[a-zA-Z0-9]+@staff\.msu\.ac\.zw$'
    
    def test_validate_email_success(self):
        """Test email validation with valid MSU email."""
        # Arrange
        mock_user_repo = Mock()
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.validate_email('test.user@staff.msu.ac.zw')
        
        # Assert
        assert result is True
    
    def test_validate_email_failure(self):
        """Test email validation with invalid email."""
        # Arrange
        mock_user_repo = Mock()
        auth_service = AuthService(mock_user_repo)
        
        # Act & Assert
        assert auth_service.validate_email('test@gmail.com') is False
        assert auth_service.validate_email('test@msu.ac.zw') is False
        assert auth_service.validate_email('invalid-email') is False
    
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@staff.msu.ac.zw'
        mock_user.role = 'staff'
        
        mock_user_repo.authenticate.return_value = mock_user
        
        auth_service = AuthService(mock_user_repo)
        login_data = UserLogin(email='test@staff.msu.ac.zw', password='password123')
        
        # Act
        result, message = auth_service.authenticate_user(login_data)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert message == "Login successful"
        mock_user_repo.authenticate.assert_called_once_with('test@staff.msu.ac.zw', 'password123')
    
    def test_authenticate_user_invalid_email(self):
        """Test authentication with invalid email format."""
        # Arrange
        mock_user_repo = Mock()
        auth_service = AuthService(mock_user_repo)
        login_data = UserLogin(email='test@gmail.com', password='password123')
        
        # Act
        result, message = auth_service.authenticate_user(login_data)
        
        # Assert
        assert result is None
        assert message == "Invalid MSU staff email format"
        mock_user_repo.authenticate.assert_not_called()
    
    def test_authenticate_user_invalid_credentials(self):
        """Test authentication with invalid credentials."""
        # Arrange
        mock_user_repo = Mock()
        mock_user_repo.authenticate.return_value = None
        
        auth_service = AuthService(mock_user_repo)
        login_data = UserLogin(email='test@staff.msu.ac.zw', password='wrongpassword')
        
        # Act
        result, message = auth_service.authenticate_user(login_data)
        
        # Assert
        assert result is None
        assert message == "Invalid email or password"
        mock_user_repo.authenticate.assert_called_once_with('test@staff.msu.ac.zw', 'wrongpassword')
    
    def test_create_user_success(self):
        """Test successful user creation."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@staff.msu.ac.zw'
        mock_user.role = 'staff'
        
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.is_valid_role.return_value = True
        mock_user_repo.create_user.return_value = mock_user
        
        auth_service = AuthService(mock_user_repo)
        user_data = UserCreate(
            email='test@staff.msu.ac.zw',
            password='Password123!',
            confirm_password='Password123!',
            role=UserRole.STAFF
        )
        
        # Act
        result, message = auth_service.create_user(user_data)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert message == "User created successfully"
        mock_user_repo.email_exists.assert_called_once_with('test@staff.msu.ac.zw')
        mock_user_repo.is_valid_role.assert_called_once_with('staff')
        mock_user_repo.create_user.assert_called_once_with('test@staff.msu.ac.zw', 'Password123!', 'staff')
    
    def test_create_user_invalid_email(self):
        """Test user creation with invalid email."""
        # Arrange
        mock_user_repo = Mock()
        auth_service = AuthService(mock_user_repo)
        user_data = UserCreate(
            email='test@gmail.com',
            password='Password123!',
            confirm_password='Password123!',
            role=UserRole.STAFF
        )
        
        # Act
        result, message = auth_service.create_user(user_data)
        
        # Assert
        assert result is None
        assert message == "Invalid MSU staff email format"
        mock_user_repo.email_exists.assert_not_called()
    
    def test_create_user_email_exists(self):
        """Test user creation when email already exists."""
        # Arrange
        mock_user_repo = Mock()
        mock_user_repo.email_exists.return_value = True
        
        auth_service = AuthService(mock_user_repo)
        user_data = UserCreate(
            email='existing@staff.msu.ac.zw',
            password='Password123!',
            confirm_password='Password123!',
            role=UserRole.STAFF
        )
        
        # Act
        result, message = auth_service.create_user(user_data)
        
        # Assert
        assert result is None
        assert message == "Email already registered"
        mock_user_repo.email_exists.assert_called_once_with('existing@staff.msu.ac.zw')
    
    def test_create_user_invalid_role(self):
        """Test user creation with invalid role."""
        # Arrange
        mock_user_repo = Mock()
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.is_valid_role.return_value = False
        
        auth_service = AuthService(mock_user_repo)
        user_data = UserCreate(
            email='test@staff.msu.ac.zw',
            password='Password123!',
            confirm_password='Password123!',
            role='invalid_role'
        )
        
        # Act
        result, message = auth_service.create_user(user_data)
        
        # Assert
        assert result is None
        assert message == "Invalid role specified"
        mock_user_repo.is_valid_role.assert_called_once_with('invalid_role')
    
    def test_get_user_by_id_success(self):
        """Test getting user by ID successfully."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@staff.msu.ac.zw'
        mock_user.role = 'staff'
        
        mock_user_repo.get_by_id.return_value = mock_user
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.get_user_by_id(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_user_repo.get_by_id.assert_called_once_with(1)
    
    def test_get_user_by_id_not_found(self):
        """Test getting user by ID when not found."""
        # Arrange
        mock_user_repo = Mock()
        mock_user_repo.get_by_id.return_value = None
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.get_user_by_id(999)
        
        # Assert
        assert result is None
        mock_user_repo.get_by_id.assert_called_once_with(999)
    
    def test_get_user_by_email_success(self):
        """Test getting user by email successfully."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@staff.msu.ac.zw'
        
        mock_user_repo.get_by_email.return_value = mock_user
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.get_user_by_email('test@staff.msu.ac.zw')
        
        # Assert
        assert result is not None
        assert result.email == 'test@staff.msu.ac.zw'
        mock_user_repo.get_by_email.assert_called_once_with('test@staff.msu.ac.zw')
    
    def test_get_user_profile_success(self):
        """Test getting user profile successfully."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@staff.msu.ac.zw'
        mock_user.role = 'staff'
        mock_user.is_active = True
        mock_user.created_at = '2024-01-01'
        
        mock_worker_profile = Mock()
        
        mock_user_repo.get_by_id.return_value = mock_user
        mock_user_repo.get_worker_profile.return_value = mock_worker_profile
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.get_user_profile(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert result.worker_profile == mock_worker_profile
        mock_user_repo.get_by_id.assert_called_once_with(1)
        mock_user_repo.get_worker_profile.assert_called_once_with(1)
    
    def test_change_password_success(self):
        """Test successful password change."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        mock_user.check_password.return_value = True
        mock_updated_user = Mock()
        
        mock_user_repo.get_by_id.return_value = mock_user
        mock_user_repo.update_password.return_value = mock_updated_user
        
        auth_service = AuthService(mock_user_repo)
        password_data = PasswordChange(
            current_password='OldPassword123!',
            new_password='NewPassword123!',
            confirm_password='NewPassword123!'
        )
        
        # Act
        result, message = auth_service.change_password(1, password_data)
        
        # Assert
        assert result is True
        assert message == "Password changed successfully"
        mock_user.check_password.assert_called_once_with('OldPassword123!')
        mock_user_repo.update_password.assert_called_once_with(1, 'NewPassword123!')
    
    def test_change_password_wrong_current_password(self):
        """Test password change with wrong current password."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        mock_user.check_password.return_value = False
        
        mock_user_repo.get_by_id.return_value = mock_user
        
        auth_service = AuthService(mock_user_repo)
        password_data = PasswordChange(
            current_password='WrongPassword123!',
            new_password='NewPassword123!',
            confirm_password='NewPassword123!'
        )
        
        # Act
        result, message = auth_service.change_password(1, password_data)
        
        # Assert
        assert result is False
        assert message == "Current password is incorrect"
        mock_user.check_password.assert_called_once_with('WrongPassword123!')
        mock_user_repo.update_password.assert_not_called()
    
    def test_deactivate_user_success(self):
        """Test successful user deactivation."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        
        mock_user_repo.deactivate_user.return_value = mock_user
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result, message = auth_service.deactivate_user(1)
        
        # Assert
        assert result is True
        assert message == "User deactivated successfully"
        mock_user_repo.deactivate_user.assert_called_once_with(1)
    
    def test_activate_user_success(self):
        """Test successful user activation."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock()
        
        mock_user_repo.activate_user.return_value = mock_user
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result, message = auth_service.activate_user(1)
        
        # Assert
        assert result is True
        assert message == "User activated successfully"
        mock_user_repo.activate_user.assert_called_once_with(1)
    
    def test_get_all_users_success(self):
        """Test getting all users successfully."""
        # Arrange
        mock_user_repo = Mock()
        mock_users = [Mock(), Mock(), Mock()]
        
        mock_user_repo.get_all.return_value = mock_users
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.get_all_users()
        
        # Assert
        assert len(result) == 3
        mock_user_repo.get_all.assert_called_once()
    
    def test_get_active_users_success(self):
        """Test getting active users successfully."""
        # Arrange
        mock_user_repo = Mock()
        mock_users = [Mock(), Mock()]
        
        mock_user_repo.get_active_users.return_value = mock_users
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.get_active_users()
        
        # Assert
        assert len(result) == 2
        mock_user_repo.get_active_users.assert_called_once()
    
    def test_get_users_by_role_success(self):
        """Test getting users by role successfully."""
        # Arrange
        mock_user_repo = Mock()
        mock_users = [Mock()]
        
        mock_user_repo.get_by_role.return_value = mock_users
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.get_users_by_role(UserRole.ADMIN)
        
        # Assert
        assert len(result) == 1
        mock_user_repo.get_by_role.assert_called_once_with('admin')
    
    def test_search_users_success(self):
        """Test searching users successfully."""
        # Arrange
        mock_user_repo = Mock()
        mock_users = [Mock(), Mock()]
        
        mock_user_repo.search_users.return_value = mock_users
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.search_users('test')
        
        # Assert
        assert len(result) == 2
        mock_user_repo.search_users.assert_called_once_with('test')
    
    def test_get_user_stats_success(self):
        """Test getting user statistics successfully."""
        # Arrange
        mock_user_repo = Mock()
        mock_stats = {
            'total_users': 10,
            'active_users': 8,
            'inactive_users': 2,
            'role_breakdown': {'admin': 2, 'staff': 6, 'supervisor': 2}
        }
        
        mock_user_repo.get_user_stats.return_value = mock_stats
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result = auth_service.get_user_stats()
        
        # Assert
        assert result == mock_stats
        mock_user_repo.get_user_stats.assert_called_once()
    
    def test_delete_user_success(self):
        """Test successful user deletion."""
        # Arrange
        mock_user_repo = Mock()
        mock_user_repo.soft_delete.return_value = True
        
        auth_service = AuthService(mock_user_repo)
        
        # Act
        result, message = auth_service.delete_user(1)
        
        # Assert
        assert result is True
        assert message == "User deleted successfully"
        mock_user_repo.soft_delete.assert_called_once_with(1)
    
    def test_is_valid_role_success(self):
        """Test valid role check."""
        # Arrange
        mock_user_repo = Mock()
        auth_service = AuthService(mock_user_repo)
        
        # Act & Assert
        assert auth_service.is_valid_role('admin') is True
        assert auth_service.is_valid_role('staff') is True
        assert auth_service.is_valid_role('supervisor') is True
        assert auth_service.is_valid_role('maintenance_admin') is True
        assert auth_service.is_valid_role('invalid_role') is False
