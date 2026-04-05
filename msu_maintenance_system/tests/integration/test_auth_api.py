"""
Integration Tests for Auth API
Tests authentication endpoints with real database and Flask app.
"""

import pytest
import json
from app.domain.user import UserCreate, UserLogin


class TestAuthAPI:
    """Integration tests for authentication API endpoints."""
    
    def test_login_success(self, client, sample_user):
        """Test successful login."""
        # Arrange
        login_data = {
            'email': 'test.user@staff.msu.ac.zw',
            'password': 'TestPassword123!',
            'remember_me': False
        }
        
        # Act
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'user' in data['data']
        assert data['data']['user']['email'] == 'test.user@staff.msu.ac.zw'
    
    def test_login_invalid_email(self, client):
        """Test login with invalid email format."""
        # Arrange
        login_data = {
            'email': 'test@gmail.com',
            'password': 'TestPassword123!'
        }
        
        # Act
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid MSU staff email format' in data['error']
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials."""
        # Arrange
        login_data = {
            'email': 'test.user@staff.msu.ac.zw',
            'password': 'WrongPassword123!'
        }
        
        # Act
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid email or password' in data['error']
    
    def test_login_no_data(self, client):
        """Test login without data."""
        # Act
        response = client.post('/api/v1/auth/login',
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No data provided' in data['error']
    
    def test_register_success(self, client):
        """Test successful user registration."""
        # Arrange
        user_data = {
            'email': 'new.user@staff.msu.ac.zw',
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!',
            'role': 'staff'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data['data']
        assert data['data']['user']['email'] == 'new.user@staff.msu.ac.zw'
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        # Arrange
        user_data = {
            'email': 'new.user@gmail.com',
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!',
            'role': 'staff'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid MSU staff email format' in data['error']
    
    def test_register_email_exists(self, client, sample_user):
        """Test registration with existing email."""
        # Arrange
        user_data = {
            'email': 'test.user@staff.msu.ac.zw',
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!',
            'role': 'staff'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Email already registered' in data['error']
    
    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch."""
        # Arrange
        user_data = {
            'email': 'new.user@staff.msu.ac.zw',
            'password': 'NewPassword123!',
            'confirm_password': 'DifferentPassword123!',
            'role': 'staff'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Passwords do not match' in data['error']
    
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        # Arrange
        user_data = {
            'email': 'new.user@staff.msu.ac.zw',
            'password': 'weak',
            'confirm_password': 'weak',
            'role': 'staff'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Password must be at least 10 characters long' in data['error']
    
    def test_get_current_user_success(self, client, sample_user, jwt_headers):
        """Test getting current user profile with valid token."""
        # Act
        response = client.get('/api/v1/auth/me',
                            headers=jwt_headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['email'] == 'test.user@staff.msu.ac.zw'
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user profile without token."""
        # Act
        response = client.get('/api/v1/auth/me')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Token required' in data['error']
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user profile with invalid token."""
        # Arrange
        headers = {'Authorization': 'Bearer invalid_token'}
        
        # Act
        response = client.get('/api/v1/auth/me',
                            headers=headers)
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid token' in data['error']
    
    def test_change_password_success(self, client, sample_user, jwt_headers):
        """Test successful password change."""
        # Arrange
        password_data = {
            'current_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        
        # Act
        response = client.post('/api/v1/auth/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json',
                             headers=jwt_headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Password changed successfully' in data['message']
    
    def test_change_password_wrong_current_password(self, client, sample_user, jwt_headers):
        """Test password change with wrong current password."""
        # Arrange
        password_data = {
            'current_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        
        # Act
        response = client.post('/api/v1/auth/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json',
                             headers=jwt_headers)
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Current password is incorrect' in data['error']
    
    def test_change_password_no_token(self, client):
        """Test password change without token."""
        # Arrange
        password_data = {
            'current_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        
        # Act
        response = client.post('/api/v1/auth/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_users_success(self, client, sample_admin_user, admin_jwt_headers):
        """Test getting all users with admin token."""
        # Act
        response = client.get('/api/v1/auth/users',
                            headers=admin_jwt_headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_get_user_by_id_success(self, client, sample_user, jwt_headers):
        """Test getting user by ID successfully."""
        # Act
        response = client.get(f'/api/v1/auth/users/{sample_user.id}',
                            headers=jwt_headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['id'] == sample_user.id
    
    def test_get_user_by_id_not_found(self, client, jwt_headers):
        """Test getting user by ID when not found."""
        # Act
        response = client.get('/api/v1/auth/users/999',
                            headers=jwt_headers)
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'User not found' in data['error']
    
    def test_register_admin_user(self, client):
        """Test registering an admin user."""
        # Arrange
        user_data = {
            'email': 'admin.user@staff.msu.ac.zw',
            'password': 'AdminPassword123!',
            'confirm_password': 'AdminPassword123!',
            'role': 'admin'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['user']['role'] == 'admin'
    
    def test_register_supervisor_user(self, client):
        """Test registering a supervisor user."""
        # Arrange
        user_data = {
            'email': 'supervisor.user@staff.msu.ac.zw',
            'password': 'SupervisorPassword123!',
            'confirm_password': 'SupervisorPassword123!',
            'role': 'supervisor'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['user']['role'] == 'supervisor'
    
    def test_register_maintenance_admin_user(self, client):
        """Test registering a maintenance admin user."""
        # Arrange
        user_data = {
            'email': 'maintenance.admin@staff.msu.ac.zw',
            'password': 'MaintenancePassword123!',
            'confirm_password': 'MaintenancePassword123!',
            'role': 'maintenance_admin'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['user']['role'] == 'maintenance_admin'
    
    def test_register_invalid_role(self, client):
        """Test registration with invalid role."""
        # Arrange
        user_data = {
            'email': 'invalid.user@staff.msu.ac.zw',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'role': 'invalid_role'
        }
        
        # Act
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid role specified' in data['error']
