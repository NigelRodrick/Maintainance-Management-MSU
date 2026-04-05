"""
Testing Strategy Documentation
Comprehensive testing approach for the MSU Maintenance System.
"""

# 6. Testing Strategy

## 6.1 Test Architecture

| Test Type | Tool | Coverage Target | What Is Tested |
|-----------|------|----------------|----------------|
| Unit | pytest + pytest-mock | 90% on services, 100% on domain | All service methods, classification rules, state machine transitions, domain validators |
| Integration | pytest + Flask test client + test DB | 80% on API layer | All API endpoints (auth, jobs, assignments, materials, analytics, reports). All DB migrations. |
| End-to-End | pytest-playwright | All critical user journeys | Login flows, job submission, assignment, status update, report download, mobile viewport rendering |
| Security | Bandit + OWASP ZAP | Zero HIGH/CRITICAL findings | Static code analysis, DAST scan against staging, dependency vulnerability audit |

## 6.2 Test Data Strategy

- **Use factory-boy factories** to generate realistic test fixtures — never hard-coded dictionaries.
- **Maintain a separate test database** (CentralServices_AM_DB_Test) reset between test runs via conftest.py session fixture.
- **Seed data mimics production distributions**: 40% PENDING, 35% IN_PROGRESS, 25% COMPLETED.
- **No production data used in tests** — anonymised factory data only.
- **conftest.py provides**: db_session, authenticated_client (staff/supervisor/admin variants), sample_job, sample_worker fixtures.

## 6.3 Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests
│   ├── test_auth_service.py
│   ├── test_job_service.py
│   ├── test_worker_service.py
│   ├── test_material_service.py
│   ├── test_assignment_service.py
│   ├── test_job_repository.py
│   ├── test_user_repository.py
│   ├── test_worker_repository.py
│   ├── test_material_repository.py
│   ├── test_assignment_repository.py
│   └── test_domain_models.py
├── integration/                # Integration tests
│   ├── test_auth_api.py
│   ├── test_jobs_api.py
│   ├── test_workers_api.py
│   ├── test_materials_api.py
│   ├── test_assignments_api.py
│   ├── test_analytics_api.py
│   └── test_reports_api.py
└── e2e/                       # End-to-end tests
    ├── test_critical_journeys.py
    ├── test_mobile_responsive.py
    └── test_accessibility.py
```

## 6.4 Test Configuration

### pytest.ini Configuration
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --verbose
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    database: Tests that require database
    auth: Authentication related tests
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### Test Database Setup
- **SQLite in-memory** for unit tests
- **SQL Server test instance** for integration tests
- **Automatic cleanup** between test runs
- **Seed data** with realistic distributions

## 6.5 Factory Boy Implementation

### User Factory
```python
class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    password_hash = factory.LazyAttribute(lambda obj: generate_password_hash('TestPassword123!'))
    role = factory.Iterator([UserRole.STAFF, UserRole.SUPERVISOR, UserRole.ADMIN])
    is_active = True
    created_at = factory.Faker('date_time_this_year')
```

### Job Request Factory
```python
class JobRequestFactory(factory.Factory):
    class Meta:
        model = JobRequest
    
    department = factory.Faker('company')
    description = factory.Faker('text', max_nb_chars=200)
    category = factory.Iterator(['electrical', 'plumbing', 'mechanical', 'civil', 'carpentry'])
    priority = factory.Iterator([Priority.LOW, Priority.MEDIUM, Priority.HIGH])
    status = factory.Iterator([
        JobStatus.PENDING, JobStatus.PENDING, JobStatus.PENDING, JobStatus.PENDING,  # 40%
        JobStatus.IN_PROGRESS, JobStatus.IN_PROGRESS, JobStatus.IN_PROGRESS,       # 35%
        JobStatus.COMPLETED, JobStatus.COMPLETED                                    # 25%
    ])
    submitted_at = factory.Faker('date_time_this_year')
```

### Worker Factory
```python
class WorkerFactory(factory.Factory):
    class Meta:
        model = Worker
    
    full_name = factory.Faker('name')
    department = factory.Faker('company')
    skill_category = factory.Iterator([
        SkillCategory.ELECTRICAL, SkillCategory.PLUMBING, SkillCategory.MECHANICAL,
        SkillCategory.CIVIL, SkillCategory.CARPENTRY, SkillCategory.GENERAL
    ])
    is_active = True
    created_at = factory.Faker('date_time_this_year')
```

## 6.6 Test Categories

### Unit Tests (90% coverage target)
- **Service Layer**: All business logic methods
- **Repository Layer**: All data access methods
- **Domain Models**: All validators and business rules
- **Utilities**: Helper functions and utilities

### Integration Tests (80% coverage target)
- **API Endpoints**: All REST API endpoints
- **Database Operations**: All CRUD operations
- **Authentication**: Login, logout, token validation
- **Authorization**: Role-based access control
- **Data Validation**: Input validation and sanitization

### End-to-End Tests
- **Critical User Journeys**:
  - Staff login → Job submission → Status tracking
  - Supervisor login → Job assignment → Worker management
  - Admin login → User management → System configuration
- **Mobile Responsiveness**: All pages on mobile viewports
- **Accessibility**: Screen reader compatibility, keyboard navigation

### Security Tests
- **Static Analysis**: Bandit security scanning
- **Dynamic Analysis**: OWASP ZAP penetration testing
- **Dependency Scanning**: Safety vulnerability checks
- **Authentication Testing**: Brute force protection, session management
- **Authorization Testing**: Privilege escalation attempts

## 6.7 Test Execution

### Running Tests
```bash
# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run e2e tests only
pytest -m e2e

# Run with coverage
pytest --cov=app --cov-report=html

# Run security tests
bandit -r app/
safety check
```

### Continuous Integration
- **Unit tests** on every push
- **Integration tests** on pull requests
- **E2E tests** on merge to main
- **Security tests** on release candidates

## 6.8 Test Data Management

### Test Database
- **Separate test database**: CentralServices_AM_DB_Test
- **Automatic reset**: Clean state for each test run
- **Seed data**: Realistic production-like data
- **Isolation**: No interference between tests

### Data Privacy
- **Anonymized data**: No real personal information
- **Synthetic data**: Generated via factories
- **Compliance**: GDPR and data protection regulations
- **Cleanup**: Automatic data removal after tests

## 6.9 Performance Testing

### Load Testing
- **K6 scripts**: Automated load testing
- **Performance benchmarks**: Response time thresholds
- **Stress testing**: System behavior under load
- **Scalability testing**: Horizontal scaling validation

### Monitoring
- **Response time tracking**: API endpoint performance
- **Resource utilization**: CPU, memory, database
- **Error rates**: Failure rate monitoring
- **User experience**: Real user monitoring

## 6.10 Quality Gates

### Pre-commit Checks
- **Code formatting**: Black, isort
- **Linting**: flake8, pylint
- **Type checking**: mypy
- **Security scanning**: bandit

### CI/CD Gates
- **Unit test coverage**: Minimum 80%
- **Integration test success**: All tests pass
- **Security scan**: No HIGH/CRITICAL findings
- **Performance benchmarks**: Response time < 2s

### Release Gates
- **E2E test success**: All critical journeys pass
- **Security audit**: Zero vulnerabilities
- **Performance validation**: Meets SLA requirements
- **Documentation**: Complete and up-to-date

## 6.11 Test Reporting

### Coverage Reports
- **HTML coverage**: Detailed coverage visualization
- **XML coverage**: CI/CD integration
- **Trend analysis**: Coverage over time
- **Threshold alerts**: Coverage drop notifications

### Test Results
- **JUnit XML**: CI/CD integration
- **HTML reports**: Detailed test results
- **Failure analysis**: Root cause identification
- **Trend tracking**: Test success rates

### Security Reports
- **Vulnerability reports**: Security findings
- **Risk assessment**: Severity classification
- **Remediation tracking: Issue resolution
- **Compliance reports**: Regulatory requirements

## 6.12 Maintenance

### Test Maintenance
- **Regular updates**: Keep tests aligned with code
- **Refactoring**: Improve test structure and clarity
- **Documentation**: Update test documentation
- **Training**: Team education on best practices

### Environment Maintenance
- **Test data refresh**: Regular data updates
- **Environment cleanup**: Remove obsolete data
- **Configuration updates**: Keep environments current
- **Monitoring**: Environment health checks

This comprehensive testing strategy ensures the MSU Maintenance System meets the highest quality standards for reliability, security, and performance.
