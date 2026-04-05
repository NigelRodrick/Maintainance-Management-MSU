
"""
Maximum Service Coverage Tests
Tests all service methods and business logic
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_auth_service_methods():
    """Test authentication service methods."""
    from app.services.auth_service import AuthService
    
    # Test service initialization
    auth_service = AuthService()
    
    # Test password hashing
    password = "testpassword123"
    hashed = auth_service.hash_password(password)
    assert len(hashed) > 0
    assert hashed != password
    
    # Test password verification
    assert auth_service.verify_password(password, hashed) == True
    assert auth_service.verify_password("wrong", hashed) == False

def test_job_service_methods():
    """Test job service methods."""
    from app.services.job_service import JobService
    from app.domain.job import JobStatus
    
    # Test service initialization
    job_service = JobService()
    
    # Test job status validation
    valid_statuses = [JobStatus.PENDING, JobStatus.IN_PROGRESS, JobStatus.COMPLETED, JobStatus.CANCELLED]
    for status in valid_statuses:
        assert job_service.is_valid_status(status)
    
    # Test job priority validation
    valid_priorities = ['low', 'medium', 'high']
    for priority in valid_priorities:
        assert job_service.is_valid_priority(priority)

def test_user_service_methods():
    """Test user service methods."""
    from app.services.user_service import UserService
    from app.domain.user import UserRole
    
    # Test service initialization
    user_service = UserService()
    
    # Test user role validation
    valid_roles = [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.STAFF, UserRole.MAINTENANCE]
    for role in valid_roles:
        assert user_service.is_valid_role(role)
    
    # Test email validation
    valid_emails = ['user@staff.msu.ac.zw', 'admin@staff.msu.ac.zw']
    for email in valid_emails:
        assert user_service.is_valid_email(email)

def test_notification_service_methods():
    """Test notification service methods."""
    from app.services.notification_service import NotificationService
    from app.domain.notification import NotificationType
    
    # Test service initialization
    notification_service = NotificationService()
    
    # Test notification type validation
    valid_types = [NotificationType.INFO, NotificationType.WARNING, NotificationType.ERROR, NotificationType.SUCCESS]
    for notification_type in valid_types:
        assert notification_service.is_valid_type(notification_type)

def test_report_service_methods():
    """Test report service methods."""
    from app.services.report_service import ReportService
    
    # Test service initialization
    report_service = ReportService()
    
    # Test report format validation
    valid_formats = ['pdf', 'excel', 'csv']
    for format_type in valid_formats:
        assert report_service.is_valid_format(format_type)

def test_analytics_service_methods():
    """Test analytics service methods."""
    from app.services.analytics_service import AnalyticsService
    
    # Test service initialization
    analytics_service = AnalyticsService()
    
    # Test data aggregation methods
    test_data = [1, 2, 3, 4, 5]
    
    # Test average calculation
    average = analytics_service.calculate_average(test_data)
    assert average == 3.0
    
    # Test sum calculation
    total = analytics_service.calculate_sum(test_data)
    assert total == 15

def test_email_service_methods():
    """Test email service methods."""
    from app.services.email_service import EmailService
    
    # Test service initialization
    email_service = EmailService()
    
    # Test email validation
    valid_emails = ['test@staff.msu.ac.zw', 'user@domain.com']
    for email in valid_emails:
        assert email_service.is_valid_email_format(email)

def test_file_service_methods():
    """Test file service methods."""
    from app.services.file_service import FileService
    
    # Test service initialization
    file_service = FileService()
    
    # Test file validation
    valid_extensions = ['pdf', 'doc', 'docx', 'jpg', 'png']
    for ext in valid_extensions:
        assert file_service.is_valid_extension(ext)
    
    # Test file size validation
    assert file_service.is_valid_size(1024 * 1024)  # 1MB
    assert not file_service.is_valid_size(100 * 1024 * 1024)  # 100MB

def test_validation_service_methods():
    """Test validation service methods."""
    from app.services.validation_service import ValidationService
    
    # Test service initialization
    validation_service = ValidationService()
    
    # Test string validation
    assert validation_service.validate_required("test") == True
    assert validation_service.validate_required("") == False
    
    # Test numeric validation
    assert validation_service.validate_positive_number(10) == True
    assert validation_service.validate_positive_number(-1) == False
    
    # Test date validation
    assert validation_service.validate_date("2024-01-01") == True
    assert validation_service.validate_date("invalid-date") == False

if __name__ == '__main__':
    pytest.main([__file__])
