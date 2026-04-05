
"""
Maximum Route Coverage Tests
Tests all Flask routes and endpoints
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_test_app():
    """Setup test Flask app."""
    os.environ['SECRET_KEY'] = 'test-secret-key'
    from app import create_app
    return create_app('development')

def test_auth_routes():
    """Test authentication routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test login route
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        # Test login route with role parameter
        response = client.get('/auth/login/staff')
        assert response.status_code == 200
        
        # Test logout route
        response = client.get('/auth/logout')
        assert response.status_code in [200, 302]

def test_main_routes():
    """Test main application routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test dashboard route
        response = client.get('/dashboard')
        assert response.status_code in [302, 200]  # Redirect if not authenticated
        
        # Test assign route
        response = client.get('/assign/1')
        assert response.status_code in [302, 200]
        
        # Test complete route
        response = client.get('/complete/1')
        assert response.status_code in [302, 200]
        
        # Test update status route
        response = client.post('/update-status/1')
        assert response.status_code in [302, 200]

def test_user_routes():
    """Test user-specific routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test user dashboard
        response = client.get('/user/dashboard')
        assert response.status_code in [302, 200]
        
        # Test submit job route
        response = client.get('/user/submit')
        assert response.status_code in [302, 200]
        
        # Test view job route
        response = client.get('/user/jobs/1')
        assert response.status_code in [302, 200]
        
        # Test job history route
        response = client.get('/user/history')
        assert response.status_code in [302, 200]
        
        # Test user profile route
        response = client.get('/user/profile')
        assert response.status_code in [302, 200]

def test_supervisor_routes():
    """Test supervisor-specific routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test supervisor dashboard
        response = client.get('/supervisor/dashboard')
        assert response.status_code in [302, 200]
        
        # Test assign technician route
        response = client.get('/supervisor/jobs/1/assign')
        assert response.status_code in [302, 200]
        
        # Test update job status route
        response = client.post('/supervisor/jobs/1/status')
        assert response.status_code in [302, 200]
        
        # Test job analysis route
        response = client.get('/supervisor/jobs/1/analysis')
        assert response.status_code in [302, 200]

def test_admin_routes():
    """Test admin-specific routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test admin dashboard
        response = client.get('/admin/dashboard')
        assert response.status_code in [302, 200]
        
        # Test manage users route
        response = client.get('/admin/users')
        assert response.status_code in [302, 200]
        
        # Test create user route
        response = client.get('/admin/users/create')
        assert response.status_code in [302, 200]
        
        # Test activity logs route
        response = client.get('/admin/activity')
        assert response.status_code in [302, 200]
        
        # Test system overview route
        response = client.get('/admin/system')
        assert response.status_code in [302, 200]

def test_analytics_routes():
    """Test analytics routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test analytics dashboard
        response = client.get('/analytics/')
        assert response.status_code in [302, 200]
        
        # Test performance analytics
        response = client.get('/analytics/performance')
        assert response.status_code in [302, 200]
        
        # Test hotspots analytics
        response = client.get('/analytics/hotspots')
        assert response.status_code in [302, 200]

def test_reports_routes():
    """Test reports routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test reports dashboard
        response = client.get('/reports/')
        assert response.status_code in [302, 200]
        
        # Test generate report route
        response = client.post('/reports/generate')
        assert response.status_code in [302, 200]
        
        # Test download report route
        response = client.get('/reports/download/test.pdf')
        assert response.status_code in [302, 200, 404]

def test_staff_routes():
    """Test staff-specific routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test staff dashboard
        response = client.get('/staff/dashboard')
        assert response.status_code in [302, 200]
        
        # Test submit request route
        response = client.get('/staff/submit')
        assert response.status_code in [302, 200]
        
        # Test view job route
        response = client.get('/staff/job/1')
        assert response.status_code in [302, 200]

def test_maintenance_admin_routes():
    """Test maintenance admin routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test maintenance dashboard
        response = client.get('/maintenance_admin/dashboard')
        assert response.status_code in [302, 200]
        
        # Test jobs route
        response = client.get('/maintenance_admin/jobs')
        assert response.status_code in [302, 200]
        
        # Test assign job route
        response = client.get('/maintenance_admin/job/1/assign')
        assert response.status_code in [302, 200]

def test_api_routes():
    """Test API routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test API endpoints
        api_endpoints = [
            '/user/api/my-jobs',
            '/user/api/activity-summary',
            '/supervisor/api/queue-metrics',
            '/supervisor/api/jobs/1/analysis',
            '/admin/api/metrics'
        ]
        
        for endpoint in api_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403, 200]  # Auth required or success

def test_error_routes():
    """Test error handling routes."""
    app = setup_test_app()
    
    with app.test_client() as client:
        # Test 404 error
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        
        # Test method not allowed
        response = client.delete('/dashboard')
        assert response.status_code in [405, 302]

if __name__ == '__main__':
    pytest.main([__file__])
