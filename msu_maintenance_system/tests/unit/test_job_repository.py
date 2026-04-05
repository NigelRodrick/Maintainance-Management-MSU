"""
Unit Tests for Job Repository
Tests all job repository operations with mocked database session.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from app.repositories.job_repository import JobRepository
from app.models import JobRequest, JobStatusHistory
from app.domain import JobStatus


class TestJobRepository:
    """Test cases for JobRepository."""
    
    def test_get_by_id_success(self, db_session):
        """Test getting job by ID successfully."""
        # Arrange
        mock_job = Mock()
        mock_job.is_deleted = False
        
        db_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_by_id(1)
        
        # Assert
        assert result == mock_job
        db_session.query.assert_called_once_with(JobRequest)
    
    def test_get_by_id_deleted(self, db_session):
        """Test getting job by ID when job is deleted."""
        # Arrange
        mock_job = Mock()
        mock_job.is_deleted = True
        
        db_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_by_id(1)
        
        # Assert
        assert result is None
    
    def test_get_by_reference_no_success(self, db_session):
        """Test getting job by reference number successfully."""
        # Arrange
        mock_job = Mock()
        mock_job.is_deleted = False
        
        db_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_by_reference_no('JR-2026-00001')
        
        # Assert
        assert result == mock_job
    
    def test_get_by_status_success(self, db_session):
        """Test getting jobs by status successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_jobs
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_by_status('PENDING')
        
        # Assert
        assert result == mock_jobs
    
    def test_get_by_department_success(self, db_session):
        """Test getting jobs by department successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_jobs
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_by_department('Electrical Services')
        
        # Assert
        assert result == mock_jobs
    
    def test_get_by_category_success(self, db_session):
        """Test getting jobs by category successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_jobs
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_by_category('electrical')
        
        # Assert
        assert result == mock_jobs
    
    def test_get_by_priority_success(self, db_session):
        """Test getting jobs by priority successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_jobs
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_by_priority('HIGH')
        
        # Assert
        assert result == mock_jobs
    
    def test_get_by_submitter_success(self, db_session):
        """Test getting jobs by submitter successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_jobs
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_by_submitter(1)
        
        # Assert
        assert result == mock_jobs
    
    def test_search_by_description_success(self, db_session):
        """Test searching jobs by description successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = mock_jobs
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.search_by_description('broken light')
        
        # Assert
        assert result == mock_jobs
    
    def test_get_recent_jobs_success(self, db_session):
        """Test getting recent jobs successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_jobs
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_recent_jobs(7)
        
        # Assert
        assert result == mock_jobs
    
    def test_get_jobs_by_date_range_success(self, db_session):
        """Test getting jobs by date range successfully."""
        # Arrange
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        mock_jobs = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_jobs
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_jobs_by_date_range(start_date, end_date)
        
        # Assert
        assert result == mock_jobs
    
    def test_get_pending_jobs_success(self, db_session):
        """Test getting pending jobs successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        with patch.object(JobRepository, 'get_by_status', return_value=mock_jobs) as mock_get:
            job_repo = JobRepository(db_session)
            
            # Act
            result = job_repo.get_pending_jobs()
            
            # Assert
            assert result == mock_jobs
            mock_get.assert_called_once_with('PENDING')
    
    def test_get_in_progress_jobs_success(self, db_session):
        """Test getting in-progress jobs successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        with patch.object(JobRepository, 'get_by_status', return_value=mock_jobs) as mock_get:
            job_repo = JobRepository(db_session)
            
            # Act
            result = job_repo.get_in_progress_jobs()
            
            # Assert
            assert result == mock_jobs
            mock_get.assert_called_once_with('IN_PROGRESS')
    
    def test_get_completed_jobs_success(self, db_session):
        """Test getting completed jobs successfully."""
        # Arrange
        mock_jobs = [Mock(), Mock()]
        with patch.object(JobRepository, 'get_by_status', return_value=mock_jobs) as mock_get:
            job_repo = JobRepository(db_session)
            
            # Act
            result = job_repo.get_completed_jobs()
            
            # Assert
            assert result == mock_jobs
            mock_get.assert_called_once_with('COMPLETED')
    
    def test_update_status_success(self, db_session):
        """Test updating job status successfully."""
        # Arrange
        mock_job = Mock()
        mock_job.status = 'PENDING'
        mock_job.updated_at = datetime.now()
        
        mock_history = Mock()
        
        with patch.object(JobRepository, 'get_by_id', return_value=mock_job) as mock_get:
            with patch.object(db_session, 'add') as mock_add:
                with patch.object(db_session, 'commit') as mock_commit:
                    job_repo = JobRepository(db_session)
                    
                    # Act
                    result = job_repo.update_status(1, 'IN_PROGRESS', 1, 'Started work')
                    
                    # Assert
                    assert result == mock_job
                    assert mock_job.status == 'IN_PROGRESS'
                    mock_add.assert_called_once()
                    mock_commit.assert_called_once()
    
    def test_update_status_job_not_found(self, db_session):
        """Test updating job status when job not found."""
        # Arrange
        with patch.object(JobRepository, 'get_by_id', return_value=None) as mock_get:
            job_repo = JobRepository(db_session)
            
            # Act
            result = job_repo.update_status(999, 'IN_PROGRESS', 1, 'Started work')
            
            # Assert
            assert result is None
    
    def test_get_dashboard_stats_success(self, db_session):
        """Test getting dashboard statistics successfully."""
        # Arrange
        mock_query_result = Mock()
        mock_query_result.__getitem__ = Mock(side_effect=lambda key: {
            'total_jobs': 10,
            'pending_jobs': 3,
            'in_progress_jobs': 4,
            'completed_jobs': 3,
            'department_breakdown': {'Electrical': 5, 'Plumbing': 3, 'Mechanical': 2},
            'category_breakdown': {'electrical': 6, 'plumbing': 2, 'mechanical': 2}
        }[key])
        
        db_session.query.return_value.count.return_value = 10
        db_session.query.return_value.filter.return_value.count.return_value = 3
        
        # Mock the complex queries
        def mock_query_side_effect(*args, **kwargs):
            if 'department' in str(args):
                return Mock(group_by=Mock(return_value=[('Electrical', 5), ('Plumbing', 3), ('Mechanical', 2)]))
            elif 'category' in str(args):
                return Mock(group_by=Mock(return_value=[('electrical', 6), ('plumbing', 2), ('mechanical', 2)]))
            return mock_query_result
        
        db_session.query.side_effect = mock_query_side_effect
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_dashboard_stats()
        
        # Assert
        assert 'total_jobs' in result
        assert 'pending_jobs' in result
        assert 'department_breakdown' in result
        assert 'category_breakdown' in result
    
    def test_get_jobs_with_pagination_success(self, db_session):
        """Test getting paginated jobs successfully."""
        # Arrange
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.count.return_value = 25
        mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [Mock(), Mock()]
        
        db_session.query.return_value = mock_query
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_jobs_with_pagination(1, 25, 'PENDING', 'Electrical', 'HIGH')
        
        # Assert
        assert 'items' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert result['page'] == 1
        assert result['per_page'] == 25
    
    def test_get_jobs_with_pagination_no_filters(self, db_session):
        """Test getting paginated jobs without filters."""
        # Arrange
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.count.return_value = 25
        mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [Mock(), Mock()]
        
        db_session.query.return_value = mock_query
        
        job_repo = JobRepository(db_session)
        
        # Act
        result = job_repo.get_jobs_with_pagination()
        
        # Assert
        assert 'items' in result
        assert result['page'] == 1
        assert result['per_page'] == 25
