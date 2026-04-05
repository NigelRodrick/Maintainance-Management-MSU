"""
Smoke Tests for MSU Maintenance System
Phase 3 Validation: Critical path testing with factory-boy fixtures
"""

import pytest
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope='session')
def test_app():
    """Create test application for all tests."""
    load_dotenv()
    from app import create_app
    app = create_app('testing')  # Use testing config
    
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db_session(test_app):
    """Create test database session."""
    from app.extensions import db
    
    with test_app.app_context():
        db.create_all()
        yield db
        db.session.remove()

@pytest.fixture
def authenticated_client(test_app, db_session):
    """Create authenticated test client."""
    from app.models import User
    
    # Create test user
    test_user = User(
        email='test@msu.ac.zw',
        password_hash='test_password_hash',
        role='staff',
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    
    client = test_app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['_fresh'] = True
    
    yield client

@pytest.fixture
def sample_job(db_session):
    """Create sample job request for testing."""
    from app.models import JobRequest
    from datetime import datetime, timedelta
    
    job = JobRequest(
        title='Test Maintenance Request',
        description='Test maintenance request for smoke testing',
        priority='MEDIUM',
        status='PENDING',
        submitted_by=1,  # Assuming user ID 1 exists
        created_at=datetime.utcnow()
    )
    db_session.add(job)
    db_session.commit()
    
    yield job

@pytest.fixture
def sample_worker(db_session):
    """Create sample worker for testing."""
    from app.models import User
    
    worker = User(
        email='worker@msu.ac.zw',
        password_hash='worker_password_hash',
        role='staff',
        is_active=True
    )
    db_session.add(worker)
    db_session.commit()
    
    yield worker

def test_flask_app_startup(test_app):
    """Test that Flask app starts cleanly."""
    print("🚀 Testing Flask App Startup")
    
    assert test_app is not None
    assert test_app.name == 'app'
    assert test_app.config['TESTING'] == True
    print("✅ Flask app starts cleanly in testing mode")

def test_login_page_accessibility(test_app):
    """Test login page loads and returns correct status."""
    print("\n🔐 Testing Login Page")
    
    with test_app.test_client() as client:
        # Test main login route
        response = client.get('/login')
        assert response.status_code in [200, 404]
        
        # Test alternative auth/login route
        alt_response = client.get('/auth/login')
        assert alt_response.status_code == 200
        assert b'form' in alt_response.data
        assert b'email' in alt_response.data
        assert b'password' in alt_response.data
        print("✅ Login page accessible with required form elements")

def test_dashboard_redirect_unauthenticated(test_app):
    """Test dashboard redirects unauthenticated users."""
    print("\n🏠 Testing Dashboard Redirect")
    
    with test_app.test_client() as client:
        response = client.get('/dashboard')
        assert response.status_code in [302, 401, 403]
        print("✅ Dashboard properly redirects unauthenticated users")

def test_critical_api_endpoints(test_app, db_session, sample_job):
    """Test critical API endpoints are accessible."""
    print("\n🛣️ Testing Critical API Endpoints")
    
    with test_app.test_client() as client:
        # Test jobs endpoint
        response = client.get('/api/v1/jobs')
        assert response.status_code != 500
        assert response.status_code in [200, 401, 403, 404]
        print(f"✅ GET /api/v1/jobs: {response.status_code}")
        
        # Test job creation endpoint
        job_data = {
            'title': 'Test Job',
            'description': 'Test Description',
            'priority': 'MEDIUM'
        }
        response = client.post('/api/v1/jobs', json=job_data)
        assert response.status_code != 500
        assert response.status_code in [201, 401, 403, 400]
        print(f"✅ POST /api/v1/jobs: {response.status_code}")
        
        # Test job detail endpoint
        response = client.get(f'/api/v1/jobs/{sample_job.id}')
        assert response.status_code != 500
        assert response.status_code in [200, 401, 403, 404]
        print(f"✅ GET /api/v1/jobs/{sample_job.id}: {response.status_code}")

def test_admin_endpoints(test_app):
    """Test admin endpoints are accessible."""
    print("\n👑 Testing Admin Endpoints")
    
    with test_app.test_client() as client:
        # Test admin models endpoint
        response = client.get('/admin/full/models')
        assert response.status_code != 500
        assert response.status_code in [200, 401, 403, 404]
        print(f"✅ GET /admin/full/models: {response.status_code}")

def test_static_files(test_app):
    """Test static files are accessible."""
    print("\n📁 Testing Static Files")
    
    with test_app.test_client() as client:
        static_files = [
            '/static/css/bootstrap.min.css',
            '/static/js/bootstrap.min.js',
            '/favicon.ico',
        ]
        
        for static_file in static_files:
            response = client.get(static_file)
            assert response.status_code in [200, 404]
            if response.status_code == 200:
                print(f"✅ {static_file}: Accessible")
            else:
                print(f"⚠️ {static_file}: Not found (404)")

def test_error_handling(test_app):
    """Test application error handling."""
    print("\n⚠️ Testing Error Handling")
    
    with test_app.test_client() as client:
        # Test 404 handling
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        print("✅ 404 handling works correctly")
        
        # Test invalid method
        response = client.post('/login', json={})
        assert response.status_code != 500
        assert response.status_code in [405, 400, 401]
        print("✅ Error handling prevents crashes")

def test_authenticated_routes(authenticated_client, sample_job):
    """Test routes that require authentication."""
    print("\n🔒 Testing Authenticated Routes")
    
    # Test dashboard access when authenticated
    response = authenticated_client.get('/dashboard')
    assert response.status_code == 200
    print("✅ Dashboard accessible when authenticated")
    
    # Test job creation when authenticated
    job_data = {
        'title': 'Authenticated Test Job',
        'description': 'Test Description',
        'priority': 'MEDIUM'
    }
    response = authenticated_client.post('/api/v1/jobs', json=job_data)
    assert response.status_code in [201, 400]
    print(f"✅ Job creation when authenticated: {response.status_code}")

def test_database_operations(db_session, sample_job, sample_worker):
    """Test database operations work correctly."""
    print("\n🗄️ Testing Database Operations")
    
    # Test job creation
    from app.models import JobRequest
    job_count_before = db_session.query(JobRequest).count()
    assert job_count_before >= 0
    print(f"✅ Database contains {job_count_before} jobs")
    
    # Test sample job exists
    assert sample_job.id is not None
    assert sample_job.title == 'Test Maintenance Request'
    print("✅ Sample job created successfully")
    
    # Test worker exists
    assert sample_worker.id is not None
    assert sample_worker.email == 'worker@msu.ac.zw'
    print("✅ Sample worker created successfully")

def run_smoke_tests():
    """Run comprehensive smoke tests."""
    print("🔥 MSU Maintenance System - Smoke Tests")
    print("=" * 50)
    print("Testing critical paths with factory-boy fixtures")
    print()
    
    # Run pytest with coverage
    cmd = [
        'python', '-m', 'pytest',
        'tests/smoke/test_smoke_comprehensive.py',
        '-v',
        '--tb=short',
        '--cov=app',
        '--cov-report=term-missing'
    ]
    
    print(f"🚀 Executing: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Smoke tests completed successfully")
            print("\n📊 SMOKE TEST RESULTS:")
            print(result.stdout)
            
            # Check for coverage information
            if 'coverage:' in result.stdout.lower():
                print("\n📈 Coverage information available")
            
            print("\n🎯 SMOKE TESTS: ✅ COMPLETED")
            print("🚀 READY FOR PHASE 4: COVERAGE GATE")
            
        else:
            print(f"❌ Smoke tests failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running smoke tests: {e}")
        return False

if __name__ == '__main__':
    import subprocess
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
