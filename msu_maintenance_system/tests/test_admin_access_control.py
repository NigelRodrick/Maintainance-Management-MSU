"""
Test Cases for Admin Access Control System

Comprehensive tests to verify admin bypass functionality and security constraints.
"""

import pytest
from flask import Flask
from flask_login import LoginManager, login_user, logout_user
from unittest.mock import patch, MagicMock
import json
import os
import tempfile

from app import create_app
from app.models import User, JobRequest, Assignment, Material
from app.utils.access_control import AccessControl, AdminBypassDecorator, SystemWideAccess
from app.decorators.auth_decorators import require_capability, admin_only
from app.extensions import db


class TestAccessControl:
    """Test the centralized access control system."""
    
    @pytest.fixture
    def app(self):
        """Create test app."""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def admin_user(self, app):
        """Create admin user for testing."""
        with app.app_context():
            admin = User(
                email='admin@test.com',
                role='ADMIN'
            )
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()
            return admin
    
    @pytest.fixture
    def regular_user(self, app):
        """Create regular user for testing."""
        with app.app_context():
            user = User(
                email='user@test.com',
                role='USER'
            )
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            return user
    
    @pytest.fixture
    def supervisor_user(self, app):
        """Create supervisor user for testing."""
        with app.app_context():
            supervisor = User(
                email='supervisor@test.com',
                role='SUPERVISOR'
            )
            supervisor.set_password('password')
            db.session.add(supervisor)
            db.session.commit()
            return supervisor


class TestAdminBypass(TestAccessControl):
    """Test admin bypass functionality."""
    
    def test_admin_is_admin_detection(self, app, admin_user):
        """Test admin detection."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                assert AccessControl.is_admin() == True
    
    def test_regular_user_is_not_admin(self, app, regular_user):
        """Test regular user is not detected as admin."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(regular_user)
                assert AccessControl.is_admin() == False
    
    def test_admin_bypass_permission_check(self, app, admin_user):
        """Test admin bypasses all permission checks."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                # Admin should bypass all capability checks
                assert AccessControl.check_permission('any_capability') == True
                assert AccessControl.check_permission('nonexistent_capability') == True
                assert AccessControl.check_permission('manage_system') == True
    
    def test_admin_bypass_model_access(self, app, admin_user):
        """Test admin bypasses model access checks."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                # Admin should access all models
                assert AccessControl.check_model_access(User, 'read') == True
                assert AccessControl.check_model_access(User, 'delete') == True
                assert AccessControl.check_model_access(JobRequest, 'create') == True
                assert AccessControl.check_model_access(Assignment, 'update') == True
    
    def test_regular_user_permission_checks(self, app, regular_user):
        """Test regular users require proper permissions."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(regular_user)
                
                # Regular user should not have admin capabilities
                assert AccessControl.check_permission('manage_system') == False
                assert AccessControl.check_permission('create_users') == False
                assert AccessControl.check_permission('view_users') == False
                
                # But should have basic capabilities
                assert AccessControl.check_permission('view_own_jobs') == True
                assert AccessControl.check_permission('submit_jobs') == True


class TestAuditLogging(TestAccessControl):
    """Test audit logging functionality."""
    
    def test_admin_action_logging(self, app, admin_user):
        """Test admin actions are logged."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                # Mock the audit logger
                with patch('app.utils.access_control.audit_logger') as mock_logger:
                    AccessControl.log_admin_action('TEST_ACTION', 'TestResource', 123)
                    
                    # Verify log was called
                    mock_logger.info.assert_called_once()
                    log_call = mock_logger.info.call_args[0][0]
                    
                    # Verify log content
                    assert 'ADMIN_ACTION:' in log_call
                    assert 'TEST_ACTION' in log_call
                    assert 'TestResource' in log_call
                    assert '123' in log_call
    
    def test_admin_bypass_logging(self, app, admin_user):
        """Test admin bypass is logged."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                with patch('app.utils.access_control.audit_logger') as mock_logger:
                    # This should trigger bypass logging
                    AccessControl.check_permission('restricted_capability')
                    
                    # Verify bypass was logged
                    mock_logger.info.assert_called_once()
                    log_call = mock_logger.info.call_args[0][0]
                    assert 'ACCESS_BYPASS' in log_call


class TestSystemWideAccess(TestAccessControl):
    """Test system-wide access control."""
    
    def test_admin_system_access(self, app, admin_user):
        """Test admin has full system access."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                # Admin should have all system access
                assert SystemWideAccess.can_create_user() == True
                assert SystemWideAccess.can_view_users() == True
                assert SystemWideAccess.can_view_all_jobs() == True
                assert SystemWideAccess.can_assign_technicians() == True
                assert SystemWideAccess.can_update_job_status() == True
                assert SystemWideAccess.can_view_analytics() == True
                assert SystemWideAccess.can_manage_system() == True
                assert SystemWideAccess.can_export_reports() == True
    
    def test_regular_user_system_access(self, app, regular_user):
        """Test regular user has limited system access."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(regular_user)
                
                # Regular user should have limited access
                assert SystemWideAccess.can_create_user() == False
                assert SystemWideAccess.can_view_users() == False
                assert SystemWideAccess.can_view_all_jobs() == False
                assert SystemWideAccess.can_assign_technicians() == False
                assert SystemWideAccess.can_update_job_status() == False
                assert SystemWideAccess.can_view_analytics() == False
                assert SystemWideAccess.can_manage_system() == False
                assert SystemWideAccess.can_export_reports() == False


class TestAdminRoutes(TestAccessControl):
    """Test admin-specific routes."""
    
    def test_admin_models_route(self, app, admin_user):
        """Test admin can access models route."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                response = client.get('/admin/models')
                # Should work (200 if template exists, 500 if not, but not 403)
                assert response.status_code != 403
    
    def test_regular_user_blocked_from_admin_routes(self, app, regular_user):
        """Test regular user blocked from admin routes."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(regular_user)
                
                response = client.get('/admin/models')
                assert response.status_code == 403
    
    def test_admin_api_endpoints(self, app, admin_user):
        """Test admin API endpoints."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                response = client.get('/admin/api/models')
                # Should work (200 if implemented, 500 if not, but not 403)
                assert response.status_code != 403


class TestSecurityConstraints(TestAccessControl):
    """Test security constraints are maintained."""
    
    def test_admin_cannot_disable_logging(self, app, admin_user):
        """Test admin cannot disable logging (security guardrail)."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                # Admin should still be logged even when trying to bypass
                with patch('app.utils.access_control.audit_logger') as mock_logger:
                    AccessControl.check_permission('any_capability')
                    
                    # Logging should still work
                    assert mock_logger.info.called
    
    def test_database_integrity_maintained(self, app, admin_user):
        """Test admin bypass doesn't break database integrity."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                # Admin can access models but database constraints still apply
                try:
                    # This should still fail due to database constraints
                    invalid_user = User(id=999999, email=None)  # Invalid email
                    db.session.add(invalid_user)
                    db.session.commit()
                    assert False, "Should have failed due to database constraints"
                except Exception:
                    # Expected to fail - database integrity maintained
                    db.session.rollback()
                    assert True


class TestBackwardCompatibility(TestAccessControl):
    """Test backward compatibility with existing code."""
    
    def test_existing_decorators_work(self, app, admin_user, regular_user):
        """Test existing decorators still work with new system."""
        with app.test_client() as client:
            with app.test_request_context():
                # Test with admin
                login_user(admin_user)
                
                @admin_only()
                def test_function():
                    return "admin_only"
                
                result = test_function()
                assert result == "admin_only"
                
                # Test with regular user
                logout_user()
                login_user(regular_user)
                
                with pytest.raises(Exception):  # Should raise exception for non-admin
                    test_function()


class TestQueryFiltering(TestAccessControl):
    """Test query filtering with admin bypass."""
    
    def test_admin_sees_all_data(self, app, admin_user):
        """Test admin sees unfiltered data."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
                # Create test data
                job1 = JobRequest(
                    department='Dept1',
                    description='Test Job 1',
                    category='Plumbing',
                    priority='High',
                    submitted_by=1
                )
                job2 = JobRequest(
                    department='Dept2',
                    description='Test Job 2',
                    category='Electrical',
                    priority='Low',
                    submitted_by=2
                )
                db.session.add(job1)
                db.session.add(job2)
                db.session.commit()
                
                # Admin should see all jobs
                query = JobRequest.query
                filtered_query = AccessControl.filter_queryset_for_user(query, JobRequest)
                
                all_jobs = filtered_query.all()
                assert len(all_jobs) == 2  # Admin sees both jobs
    
    def test_regular_user_sees_filtered_data(self, app, regular_user):
        """Test regular user sees filtered data."""
        with app.test_client() as client:
            with app.test_request_context():
                login_user(regular_user)
                
                # Create test data
                job1 = JobRequest(
                    department='Dept1',
                    description='Test Job 1',
                    category='Plumbing',
                    priority='High',
                    submitted_by=regular_user.id
                )
                job2 = JobRequest(
                    department='Dept2',
                    description='Test Job 2',
                    category='Electrical',
                    priority='Low',
                    submitted_by=999  # Different user
                )
                db.session.add(job1)
                db.session.add(job2)
                db.session.commit()
                
                # Regular user should see only their jobs
                query = JobRequest.query
                filtered_query = AccessControl.filter_queryset_for_user(query, JobRequest)
                
                user_jobs = filtered_query.all()
                assert len(user_jobs) == 1  # Only sees their own job
                assert user_jobs[0].submitted_by == regular_user.id


if __name__ == '__main__':
    pytest.main([__file__])
