"""
Unit Tests for User Repository
Tests all user repository operations with mocked database session.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from app.repositories.user_repository import UserRepository
from app.models import User
from app.domain import UserRole


class TestUserRepository:
    """Test cases for UserRepository."""
    
    def test_get_by_email_success(self, db_session):
        """Test getting user by email successfully."""
        # Arrange
        mock_user = Mock()
        mock_user.email = 'test@staff.msu.ac.zw'
        mock_user.is_deleted = False
        
        db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.get_by_email('test@staff.msu.ac.zw')
        
        # Assert
        assert result == mock_user
        db_session.query.assert_called_once_with(User)
        db_session.query.return_value.filter.assert_called_once()
    
    def test_get_by_email_not_found(self, db_session):
        """Test getting user by email when not found."""
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.get_by_email('nonexistent@staff.msu.ac.zw')
        
        # Assert
        assert result is None
    
    def test_get_active_users(self, db_session):
        """Test getting all active users."""
        # Arrange
        mock_users = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_users
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.get_active_users()
        
        # Assert
        assert result == mock_users
        db_session.query.assert_called_once_with(User)
    
    def test_get_by_role(self, db_session):
        """Test getting users by role."""
        # Arrange
        mock_users = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_users
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.get_by_role('admin')
        
        # Assert
        assert result == mock_users
    
    def test_authenticate_success(self, db_session):
        """Test successful authentication."""
        # Arrange
        mock_user = Mock()
        mock_user.check_password.return_value = True
        
        db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.authenticate('test@staff.msu.ac.zw', 'password123')
        
        # Assert
        assert result == mock_user
        mock_user.check_password.assert_called_once_with('password123')
    
    def test_authenticate_failure_wrong_password(self, db_session):
        """Test authentication failure with wrong password."""
        # Arrange
        mock_user = Mock()
        mock_user.check_password.return_value = False
        
        db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.authenticate('test@staff.msu.ac.zw', 'wrongpassword')
        
        # Assert
        assert result is None
        mock_user.check_password.assert_called_once_with('wrongpassword')
    
    def test_authenticate_failure_user_not_found(self, db_session):
        """Test authentication failure when user not found."""
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.authenticate('nonexistent@staff.msu.ac.zw', 'password123')
        
        # Assert
        assert result is None
    
    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_user.set_password = Mock()
        db_session.add.return_value = None
        db_session.commit.return_value = None
        db_session.refresh.return_value = None
        
        with patch.object(UserRepository, 'create', return_value=mock_user) as mock_create:
            user_repo = UserRepository(db_session)
            
            # Act
            result = user_repo.create_user('test@staff.msu.ac.zw', 'password123', 'admin')
            
            # Assert
            assert result == mock_user
            mock_create.assert_called_once()
    
    def test_create_user_email_exists(self, db_session):
        """Test user creation when email already exists."""
        # Arrange
        existing_user = Mock()
        db_session.query.return_value.filter.return_value.first.return_value = existing_user
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.create_user('existing@staff.msu.ac.zw', 'password123', 'admin')
        
        # Assert
        assert result is None
    
    def test_update_password(self, db_session):
        """Test updating user password."""
        # Arrange
        mock_user = Mock()
        mock_user.set_password = Mock()
        
        with patch.object(UserRepository, 'get_by_id', return_value=mock_user) as mock_get:
            user_repo = UserRepository(db_session)
            
            # Act
            result = user_repo.update_password(1, 'newpassword123')
            
            # Assert
            assert result == mock_user
            mock_get.assert_called_once_with(1)
            mock_user.set_password.assert_called_once_with('newpassword123')
    
    def test_update_role(self, db_session):
        """Test updating user role."""
        # Arrange
        mock_user = Mock()
        
        with patch.object(UserRepository, 'get_by_id', return_value=mock_user) as mock_get:
            user_repo = UserRepository(db_session)
            
            # Act
            result = user_repo.update_role(1, 'admin')
            
            # Assert
            assert result == mock_user
            mock_get.assert_called_once_with(1)
    
    def test_deactivate_user(self, db_session):
        """Test deactivating a user."""
        # Arrange
        mock_user = Mock()
        
        with patch.object(UserRepository, 'get_by_id', return_value=mock_user) as mock_get:
            user_repo = UserRepository(db_session)
            
            # Act
            result = user_repo.deactivate_user(1)
            
            # Assert
            assert result == mock_user
            assert mock_user.is_active is False
            mock_get.assert_called_once_with(1)
    
    def test_activate_user(self, db_session):
        """Test activating a user."""
        # Arrange
        mock_user = Mock()
        
        with patch.object(UserRepository, 'get_by_id', return_value=mock_user) as mock_get:
            user_repo = UserRepository(db_session)
            
            # Act
            result = user_repo.activate_user(1)
            
            # Assert
            assert result == mock_user
            assert mock_user.is_active is True
            mock_get.assert_called_once_with(1)
    
    def test_search_users(self, db_session):
        """Test searching users by keyword."""
        # Arrange
        mock_users = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_users
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.search_users('test')
        
        # Assert
        assert result == mock_users
    
    def test_email_exists_true(self, db_session):
        """Test email exists check when email exists."""
        # Arrange
        mock_user = Mock()
        db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.email_exists('test@staff.msu.ac.zw')
        
        # Assert
        assert result is True
    
    def test_email_exists_false(self, db_session):
        """Test email exists check when email doesn't exist."""
        # Arrange
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.email_exists('nonexistent@staff.msu.ac.zw')
        
        # Assert
        assert result is False
    
    def test_is_valid_role_true(self, db_session):
        """Test valid role check with valid role."""
        # Arrange
        user_repo = UserRepository(db_session)
        
        # Act & Assert
        assert user_repo.is_valid_role('admin') is True
        assert user_repo.is_valid_role('staff') is True
        assert user_repo.is_valid_role('supervisor') is True
        assert user_repo.is_valid_role('maintenance_admin') is True
    
    def test_is_valid_role_false(self, db_session):
        """Test valid role check with invalid role."""
        # Arrange
        user_repo = UserRepository(db_session)
        
        # Act
        result = user_repo.is_valid_role('invalid_role')
        
        # Assert
        assert result is False
    
    def test_get_user_stats(self, db_session):
        """Test getting user statistics."""
        # Arrange
        mock_result = Mock()
        mock_result.__getitem__ = Mock(side_effect=lambda key: {
            'total_users': 10,
            'active_users': 8,
            'inactive_users': 2,
            'role_breakdown': {'admin': 2, 'staff': 6, 'supervisor': 2}
        }[key])
        
        db_session.query.return_value.count.return_value = 10
        db_session.query.return_value.filter.return_value.count.return_value = 8
        
        with patch.object(UserRepository, 'get_by_role', return_value=[Mock(), Mock]):
            with patch.object(UserRepository, 'get_by_role', return_value=[Mock(), Mock(), Mock(), Mock(), Mock(), Mock]):
                user_repo = UserRepository(db_session)
                
                # Act
                result = user_repo.get_user_stats()
                
                # Assert
                assert 'total_users' in result
                assert 'active_users' in result
                assert 'role_breakdown' in result
