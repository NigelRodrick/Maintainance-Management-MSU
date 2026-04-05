"""
Enhanced Test Configuration with Factory Boy
Implements comprehensive test data strategy with realistic distributions.
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import factory
from factory import fuzzy

from app import create_app
from app.extensions import db
from app.models import User, JobRequest, Worker, Assignment, Material, JobStatusHistory
from app.repositories import (
    JobRepository, UserRepository, WorkerRepository, 
    MaterialRepository, AssignmentRepository
)
from app.services import (
    JobService, AuthService, WorkerService, 
    MaterialService, AssignmentService
)
from app.domain import JobStatus, Priority, UserRole, SkillCategory


@pytest.fixture(scope='session')
def test_db_engine():
    """Create test database engine."""
    # Use SQLite for unit tests, SQL Server for integration tests
    if os.getenv('TEST_DB_TYPE') == 'sqlserver':
        engine = create_engine(
            'mssql+pyodbc://localhost/CentralServices_AM_DB_Test?driver=ODBC+Driver+17+for+SQL+Server',
            echo=False
        )
    else:
        engine = create_engine('sqlite:///:memory:', echo=False)
    
    return engine


@pytest.fixture(scope='function')
def app(test_db_engine):
    """Create test Flask application."""
    # Set test environment variables
    os.environ.update({
        'SECRET_KEY': 'test-secret-key',
        'DB_SERVER': 'localhost',
        'DB_NAME': 'CentralServices_AM_DB_Test',
        'ENV': 'testing',
        'TESTING': 'True',
        'WTF_CSRF_ENABLED': 'False',
        'JWT_SECRET_KEY': 'test-jwt-secret'
    })
    
    # Create app
    app = create_app('testing')
    
    # Override database configuration
    with app.app_context():
        if os.getenv('TEST_DB_TYPE') == 'sqlserver':
            app.config['SQLALCHEMY_DATABASE_URI'] = (
                'mssql+pyodbc://localhost/CentralServices_AM_DB_Test?driver=ODBC+Driver+17+for+SQL+Server'
            )
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create database session."""
    with app.app_context():
        yield db.session


# Factory Boy implementations
class UserFactory(factory.Factory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    email = factory.Faker('email')
    password_hash = factory.LazyAttribute(lambda obj: generate_password_hash('TestPassword123!'))
    role = fuzzy.FuzzyChoice([UserRole.STAFF, UserRole.SUPERVISOR, UserRole.ADMIN])
    is_active = True
    created_at = factory.Faker('date_time_this_year')
    last_login = factory.LazyAttribute(lambda obj: None)


class JobRequestFactory(factory.Factory):
    """Factory for creating JobRequest instances with realistic status distribution."""
    
    class Meta:
        model = JobRequest
    
    department = factory.Faker('company')
    description = factory.Faker('text', max_nb_chars=200)
    category = fuzzy.FuzzyChoice(['electrical', 'plumbing', 'mechanical', 'civil', 'carpentry'])
    priority = fuzzy.FuzzyChoice([Priority.LOW, Priority.MEDIUM, Priority.HIGH])
    status = fuzzy.FuzzyChoice([
        JobStatus.PENDING, JobStatus.PENDING, JobStatus.PENDING, JobStatus.PENDING,  # 40%
        JobStatus.IN_PROGRESS, JobStatus.IN_PROGRESS, JobStatus.IN_PROGRESS,       # 35%
        JobStatus.COMPLETED, JobStatus.COMPLETED                                    # 25%
    ])
    submitted_at = factory.Faker('date_time_this_year')
    submitted_by = 1  # Will be overridden in tests
    
    @factory.post_generation
    def set_submitter(obj, create, extracted, **kwargs):
        """Set the submitter after creation."""
        if extracted:
            obj.submitted_by = extracted.id


class WorkerFactory(factory.Factory):
    """Factory for creating Worker instances."""
    
    class Meta:
        model = Worker
    
    full_name = factory.Faker('name')
    department = factory.Faker('company')
    skill_category = fuzzy.FuzzyChoice([
        SkillCategory.ELECTRICAL, SkillCategory.PLUMBING, SkillCategory.MECHANICAL,
        SkillCategory.CIVIL, SkillCategory.CARPENTRY, SkillCategory.GENERAL
    ])
    is_active = True
    created_at = factory.Faker('date_time_this_year')


class AssignmentFactory(factory.Factory):
    """Factory for creating Assignment instances."""
    
    class Meta:
        model = Assignment
    
    job_id = 1  # Will be overridden in tests
    worker_id = 1  # Will be overridden in tests
    status = fuzzy.FuzzyChoice(['ASSIGNED', 'IN_PROGRESS', 'COMPLETED'])
    assigned_at = factory.Faker('date_time_this_year')
    completed_at = factory.LazyAttribute(
        lambda obj: datetime.utcnow() if obj.status == 'COMPLETED' else None
    )


class MaterialFactory(factory.Factory):
    """Factory for creating Material instances."""
    
    class Meta:
        model = Material
    
    job_id = 1  # Will be overridden in tests
    item_name = factory.Faker('word')
    unit = fuzzy.FuzzyChoice(['pieces', 'meters', 'liters', 'kg'])
    quantity_required = fuzzy.FuzzyFloat(1.0, 100.0)
    quantity_used = fuzzy.FuzzyFloat(0.0, 100.0)


# Enhanced fixtures using factories
@pytest.fixture
def user_factory():
    """Provide UserFactory for creating users."""
    return UserFactory


@pytest.fixture
def job_factory():
    """Provide JobRequestFactory for creating jobs."""
    return JobRequestFactory


@pytest.fixture
def worker_factory():
    """Provide WorkerFactory for creating workers."""
    return WorkerFactory


@pytest.fixture
def assignment_factory():
    """Provide AssignmentFactory for creating assignments."""
    return AssignmentFactory


@pytest.fixture
def material_factory():
    """Provide MaterialFactory for creating materials."""
    return MaterialFactory


@pytest.fixture
def sample_user(db_session, user_factory):
    """Create a sample user using factory."""
    user = user_factory.create(role=UserRole.STAFF)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_admin_user(db_session, user_factory):
    """Create a sample admin user using factory."""
    user = user_factory.create(role=UserRole.ADMIN)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_supervisor_user(db_session, user_factory):
    """Create a sample supervisor user using factory."""
    user = user_factory.create(role=UserRole.SUPERVISOR)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_worker(db_session, worker_factory):
    """Create a sample worker using factory."""
    worker = worker_factory.create()
    db_session.add(worker)
    db_session.commit()
    return worker


@pytest.fixture
def sample_job(db_session, sample_user, job_factory):
    """Create a sample job using factory."""
    job = job_factory.create(submitted_by=sample_user)
    db_session.add(job)
    db_session.commit()
    return job


@pytest.fixture
def sample_assignment(db_session, sample_job, sample_worker, assignment_factory):
    """Create a sample assignment using factory."""
    assignment = assignment_factory.create(job_id=sample_job.id, worker_id=sample_worker.id)
    db_session.add(assignment)
    db_session.commit()
    return assignment


@pytest.fixture
def sample_material(db_session, sample_job, material_factory):
    """Create a sample material using factory."""
    material = material_factory.create(job_id=sample_job.id)
    db_session.add(material)
    db_session.commit()
    return material


@pytest.fixture
def multiple_jobs(db_session, sample_user, job_factory):
    """Create multiple sample jobs with realistic status distribution."""
    jobs = []
    for i in range(10):
        job = job_factory.create(submitted_by=sample_user)
        db_session.add(job)
        jobs.append(job)
    
    db_session.commit()
    return jobs


@pytest.fixture
def multiple_workers(db_session, worker_factory):
    """Create multiple sample workers with diverse skills."""
    workers = []
    for i in range(10):
        worker = worker_factory.create()
        db_session.add(worker)
        workers.append(worker)
    
    db_session.commit()
    return workers


@pytest.fixture
def realistic_job_distribution(db_session, sample_user, job_factory):
    """Create realistic job distribution matching production: 40% PENDING, 35% IN_PROGRESS, 25% COMPLETED."""
    jobs = []
    
    # 40% PENDING (4 jobs)
    for i in range(4):
        job = job_factory.create(submitted_by=sample_user, status=JobStatus.PENDING)
        jobs.append(job)
    
    # 35% IN_PROGRESS (3-4 jobs)
    for i in range(3):
        job = job_factory.create(submitted_by=sample_user, status=JobStatus.IN_PROGRESS)
        jobs.append(job)
    
    # 25% COMPLETED (2-3 jobs)
    for i in range(3):
        job = job_factory.create(submitted_by=sample_user, status=JobStatus.COMPLETED)
        jobs.append(job)
    
    for job in jobs:
        db_session.add(job)
    
    db_session.commit()
    return jobs


# Repository fixtures
@pytest.fixture
def job_repository(db_session):
    """Create job repository instance."""
    return JobRepository(db_session)


@pytest.fixture
def user_repository(db_session):
    """Create user repository instance."""
    return UserRepository(db_session)


@pytest.fixture
def worker_repository(db_session):
    """Create worker repository instance."""
    return WorkerRepository(db_session)


@pytest.fixture
def material_repository(db_session):
    """Create material repository instance."""
    return MaterialRepository(db_session)


@pytest.fixture
def assignment_repository(db_session):
    """Create assignment repository instance."""
    return AssignmentRepository(db_session)


# Service fixtures
@pytest.fixture
def job_service(job_repository, user_repository):
    """Create job service instance."""
    return JobService(job_repository, user_repository)


@pytest.fixture
def auth_service(user_repository):
    """Create auth service instance."""
    return AuthService(user_repository)


@pytest.fixture
def worker_service(worker_repository, user_repository):
    """Create worker service instance."""
    return WorkerService(worker_repository, user_repository)


@pytest.fixture
def material_service(material_repository, job_repository):
    """Create material service instance."""
    return MaterialService(material_repository, job_repository)


@pytest.fixture
def assignment_service(assignment_repository, worker_repository, job_repository):
    """Create assignment service instance."""
    return AssignmentService(assignment_repository, worker_repository, job_repository)


# Authenticated client fixtures
@pytest.fixture
def staff_client(client, sample_user):
    """Create authenticated client with staff role."""
    with client.session_transaction() as sess:
        sess['user_id'] = sample_user.id
        sess['_fresh'] = True
    return client


@pytest.fixture
def admin_client(client, sample_admin_user):
    """Create authenticated client with admin role."""
    with client.session_transaction() as sess:
        sess['user_id'] = sample_admin_user.id
        sess['_fresh'] = True
    return client


@pytest.fixture
def supervisor_client(client, sample_supervisor_user):
    """Create authenticated client with supervisor role."""
    with client.session_transaction() as sess:
        sess['user_id'] = sample_supervisor_user.id
        sess['_fresh'] = True
    return client


# JWT fixtures for API testing
@pytest.fixture
def jwt_headers(sample_user):
    """Create JWT headers for API testing."""
    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=sample_user.id)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_jwt_headers(sample_admin_user):
    """Create JWT headers for admin API testing."""
    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=sample_admin_user.id)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def supervisor_jwt_headers(sample_supervisor_user):
    """Create JWT headers for supervisor API testing."""
    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=sample_supervisor_user.id)
    return {'Authorization': f'Bearer {token}'}


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data(db_session):
    """Automatically cleanup test data after each test."""
    yield
    # Clean up all test data
    db_session.query(JobStatusHistory).delete()
    db_session.query(Assignment).delete()
    db_session.query(Material).delete()
    db_session.query(JobRequest).delete()
    db_session.query(Worker).delete()
    db_session.query(User).delete()
    db_session.commit()


# Performance testing fixtures
@pytest.fixture
def performance_data():
    """Provide performance testing data."""
    return {
        'max_response_time': 2.0,  # seconds
        'max_memory_usage': 512,   # MB
        'max_cpu_usage': 80,       # percentage
        'concurrent_users': 100,
        'ramp_up_time': 60,        # seconds
        'test_duration': 300       # seconds
    }


# Mobile testing fixtures
@pytest.fixture
def mobile_viewport():
    """Mobile viewport dimensions for testing."""
    return {
        'width': 375,
        'height': 667,
        'device_scale_factor': 2,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
    }


# Accessibility testing fixtures
@pytest.fixture
def accessibility_config():
    """Accessibility testing configuration."""
    return {
        'wcag_level': 'AA',
        'contrast_ratio': 4.5,
        'keyboard_navigation': True,
        'screen_reader_support': True,
        'focus_management': True
    }
