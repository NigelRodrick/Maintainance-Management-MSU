"""
pytest configuration for MSU Maintenance System
Provides fixtures for database sessions, authenticated clients, and test data
"""

import pytest
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@pytest.fixture(scope='session')
def app():
    """Create test application for all tests."""
    load_dotenv()
    from app import create_app
    app = create_app('testing')
    
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db_session(app):
    """Create test database session."""
    from app.extensions import db
    
    # Configure test database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'TEST_DATABASE_URL', 
        'sqlite:///:memory:'
    )
    
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def authenticated_client(app, db_session):
    """Create authenticated test client for staff."""
    from app.models import User
    
    # Create test staff user
    test_user = User(
        email='staff@msu.ac.zw',
        password_hash='test_password_hash',
        role='staff',
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['_fresh'] = True
    
    yield client

@pytest.fixture
def admin_client(app, db_session):
    """Create authenticated test client for admin."""
    from app.models import User
    
    # Create test admin user
    test_admin = User(
        email='admin@msu.ac.zw',
        password_hash='admin_password_hash', 
        role='admin',
        is_active=True
    )
    db_session.add(test_admin)
    db_session.commit()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = test_admin.id
        sess['_fresh'] = True
    
    yield client

@pytest.fixture
def supervisor_client(app, db_session):
    """Create authenticated test client for supervisor."""
    from app.models import User
    
    # Create test supervisor user
    test_supervisor = User(
        email='supervisor@msu.ac.zw',
        password_hash='supervisor_password_hash',
        role='supervisor',
        is_active=True
    )
    db_session.add(test_supervisor)
    db_session.commit()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = test_supervisor.id
        sess['_fresh'] = True
    
    yield client

@pytest.fixture
def sample_job(db_session):
    """Create sample job request for testing."""
    from app.models import JobRequest
    from datetime import datetime
    
    job = JobRequest(
        title='Test Maintenance Request',
        description='Test maintenance request for smoke testing',
        priority='MEDIUM',
        status='PENDING',
        submitted_by=1,
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

@pytest.fixture
def test_data_distribution(db_session):
    """Create test data mimicking production distributions."""
    from app.models import JobRequest
    from datetime import datetime, timedelta
    import random
    
    # Create test jobs with production-like distribution
    statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED']
    status_weights = [0.4, 0.35, 0.25]  # 40%, 35%, 25%
    
    for i in range(20):  # Create 20 test jobs
        status = random.choices(statuses, weights=status_weights)[0]
        
        job = JobRequest(
            title=f'Test Job {i+1}',
            description=f'Test maintenance request {i+1}',
            priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
            status=status,
            submitted_by=1,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        db_session.add(job)
    
    db_session.commit()
    
    # Verify distribution
    total_jobs = db_session.query(JobRequest).count()
    pending_jobs = db_session.query(JobRequest).filter_by(status='PENDING').count()
    in_progress_jobs = db_session.query(JobRequest).filter_by(status='IN_PROGRESS').count()
    completed_jobs = db_session.query(JobRequest).filter_by(status='COMPLETED').count()
    
    print(f"📊 Test Data Distribution:")
    print(f"   Total: {total_jobs}")
    print(f"   PENDING: {pending_jobs} ({pending_jobs/total_jobs*100:.1f}%)")
    print(f"   IN_PROGRESS: {in_progress_jobs} ({in_progress_jobs/total_jobs*100:.1f}%)")
    print(f"   COMPLETED: {completed_jobs} ({completed_jobs/total_jobs*100:.1f}%)")
    
    yield {
        'total': total_jobs,
        'pending': pending_jobs,
        'in_progress': in_progress_jobs,
        'completed': completed_jobs
    }

