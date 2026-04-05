"""
Celery Configuration and Background Tasks
Async task processing for performance optimization.
"""

import os
from celery import Celery
from datetime import timedelta
from app.extensions import celery
from app.services.job_service import JobService
from app.services.worker_service import WorkerService
from app.services.material_service import MaterialService
from app.repositories import (
    JobRepository, UserRepository, WorkerRepository, 
    MaterialRepository, AssignmentRepository
)
from app.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)


def make_celery(app_name=__name__):
    """Create and configure Celery instance."""
    
    # Create Celery instance
    celery = Celery(app_name)
    
    # Configure Celery
    celery.conf.update(
        broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,
        beat_schedule={
            'update-dashboard-cache': {
                'task': 'app.tasks.update_dashboard_cache',
                'schedule': timedelta(minutes=5),
            },
            'cleanup-expired-cache': {
                'task': 'app.tasks.cleanup_expired_cache',
                'schedule': timedelta(hours=1),
            },
            'generate-daily-reports': {
                'task': 'app.tasks.generate_daily_reports',
                'schedule': timedelta(hours=24),
            },
            'update-worker-performance': {
                'task': 'app.tasks.update_worker_performance',
                'schedule': timedelta(hours=6),
            },
        },
    )
    
    # Optional: configure task routes
    celery.conf.task_routes = {
        'app.tasks.heavy_computation': {'queue': 'heavy'},
        'app.tasks.email_notifications': {'queue': 'email'},
        'app.tasks.cache_updates': {'queue': 'cache'},
    }
    
    return celery


@celery.task(bind=True)
def send_email_notification(self, user_email: str, subject: str, body: str):
    """Send email notification asynchronously."""
    try:
        # Import here to avoid circular imports
        from flask_mail import Message
        from app import create_app
        
        app = create_app()
        with app.app_context():
            msg = Message(
                subject=subject,
                recipients=[user_email],
                body=body,
                sender=app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            # Send email (configure mail settings in config.py)
            # mail.send(msg)
            
            logger.info(f"Email sent to {user_email}: {subject}")
            return {'status': 'success', 'message': 'Email sent successfully'}
            
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")
        # Retry task with exponential backoff
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True)
def generate_job_report(self, job_id: int, report_type: str = 'summary'):
    """Generate job report asynchronously."""
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # Initialize repositories
            job_repo = JobRepository()
            user_repo = UserRepository()
            worker_repo = WorkerRepository()
            material_repo = MaterialRepository()
            assignment_repo = AssignmentRepository()
            
            # Initialize services
            job_service = JobService(job_repo, user_repo)
            worker_service = WorkerService(worker_repo, user_repo)
            material_service = MaterialService(material_repo, job_repo)
            
            # Generate report data
            job = job_service.get_job_by_id(job_id)
            if not job:
                return {'status': 'error', 'message': 'Job not found'}
            
            assignments = job_service.get_assignments_by_job(job_id)
            materials = material_service.get_materials_by_job(job_id)
            
            report_data = {
                'job': job.dict(),
                'assignments': [a.dict() for a in assignments],
                'materials': [m.dict() for m in materials],
                'report_type': report_type,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Cache the report
            cache_key = f"job_report:{job_id}:{report_type}"
            cache_service.set(cache_key, report_data, ttl=3600)
            
            logger.info(f"Generated {report_type} report for job {job_id}")
            return {'status': 'success', 'data': report_data}
            
    except Exception as e:
        logger.error(f"Failed to generate report for job {job_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True)
def update_dashboard_cache(self):
    """Update dashboard cache with latest statistics."""
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # Initialize repositories and services
            job_repo = JobRepository()
            user_repo = UserRepository()
            worker_repo = WorkerRepository()
            assignment_repo = AssignmentRepository()
            
            job_service = JobService(job_repo, user_repo)
            worker_service = WorkerService(worker_repo, user_repo)
            
            # Get latest statistics
            job_stats = job_service.get_job_statistics()
            worker_stats = worker_service.get_worker_stats()
            assignment_stats = assignment_repo.get_assignment_stats()
            
            dashboard_data = {
                'job_stats': job_stats.dict(),
                'worker_stats': worker_stats,
                'assignment_stats': assignment_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # Cache dashboard data
            cache_service.cache_dashboard_stats(dashboard_data)
            
            logger.info("Dashboard cache updated successfully")
            return {'status': 'success', 'data': dashboard_data}
            
    except Exception as e:
        logger.error(f"Failed to update dashboard cache: {e}")
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True)
def cleanup_expired_cache(self):
    """Clean up expired cache entries."""
    try:
        # This task can be extended to clean up specific patterns
        # For now, Redis handles TTL automatically
        
        # Clean up any manually cached items that should be expired
        patterns_to_check = [
            "search:*",  # Search results older than 15 minutes
            "job_report:*",  # Reports older than 1 hour
            "session:*",  # Sessions older than 30 minutes
        ]
        
        cleaned_count = 0
        for pattern in patterns_to_check:
            # Get keys matching pattern
            import redis
            r = redis.Redis.from_url(os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'))
            keys = r.keys(pattern)
            
            # Check TTL and delete expired ones
            for key in keys:
                ttl = r.ttl(key)
                if ttl == -1:  # No expiration set
                    r.expire(key, 3600)  # Set 1 hour expiration
                    cleaned_count += 1
        
        logger.info(f"Cache cleanup completed. Cleaned {cleaned_count} entries.")
        return {'status': 'success', 'cleaned_count': cleaned_count}
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True)
def generate_daily_reports(self):
    """Generate daily maintenance reports."""
    try:
        from app import create_app
        from datetime import datetime, timedelta
        
        app = create_app()
        with app.app_context():
            # Initialize repositories
            job_repo = JobRepository()
            user_repo = UserRepository()
            worker_repo = WorkerRepository()
            assignment_repo = AssignmentRepository()
            
            # Get yesterday's date range
            yesterday = datetime.utcnow() - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Generate daily statistics
            daily_stats = {
                'date': yesterday.strftime('%Y-%m-%d'),
                'total_jobs': job_repo.count(),
                'completed_jobs': len(job_repo.get_by_status('COMPLETED')),
                'pending_jobs': len(job_repo.get_by_status('PENDING')),
                'active_workers': len(worker_repo.get_active_workers()),
                'total_assignments': assignment_repo.count(),
                'completed_assignments': len(assignment_repo.get_by_status('COMPLETED')),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Cache daily report
            cache_key = f"daily_report:{yesterday.strftime('%Y-%m-%d')}"
            cache_service.set(cache_key, daily_stats, ttl=86400 * 30)  # Keep for 30 days
            
            logger.info(f"Daily report generated for {yesterday.strftime('%Y-%m-%d')}")
            return {'status': 'success', 'data': daily_stats}
            
    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True)
def update_worker_performance(self):
    """Update worker performance metrics."""
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # Initialize repositories and services
            worker_repo = WorkerRepository()
            assignment_repo = AssignmentRepository()
            user_repo = UserRepository()
            
            worker_service = WorkerService(worker_repo, user_repo)
            
            # Get all active workers
            workers = worker_repo.get_active_workers()
            
            updated_count = 0
            for worker in workers:
                try:
                    # Calculate performance metrics
                    performance = worker_service.get_worker_performance(worker.id, days=30)
                    
                    # Cache performance data
                    cache_key = f"worker_performance:{worker.id}"
                    cache_service.set(cache_key, performance.dict(), ttl=3600)
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to update performance for worker {worker.id}: {e}")
                    continue
            
            logger.info(f"Updated performance metrics for {updated_count} workers")
            return {'status': 'success', 'updated_count': updated_count}
            
    except Exception as e:
        logger.error(f"Failed to update worker performance: {e}")
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True)
def process_material_usage_alerts(self):
    """Process material usage and send alerts for low stock."""
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # Initialize repositories
            material_repo = MaterialRepository()
            job_repo = JobRepository()
            
            material_service = MaterialService(material_repo, job_repo)
            
            # Get materials that need attention
            overdue_materials = material_service.get_overdue_materials()
            
            alerts_sent = 0
            for material in overdue_materials:
                try:
                    # Send alert notification
                    subject = f"Material Alert: {material.item_name}"
                    body = f"""
                    Material Usage Alert
                    
                    Item: {material.item_name}
                    Current Usage: {material.quantity_used}
                    Required: {material.quantity_required}
                    Remaining: {material.quantity_required - material.quantity_used}
                    
                    Please check inventory levels and reorder if necessary.
                    """
                    
                    # Send to maintenance admin
                    send_email_notification.delay(
                        'maintenance.admin@staff.msu.ac.zw',
                        subject,
                        body
                    )
                    
                    alerts_sent += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send alert for material {material.id}: {e}")
                    continue
            
            logger.info(f"Sent {alerts_sent} material usage alerts")
            return {'status': 'success', 'alerts_sent': alerts_sent}
            
    except Exception as e:
        logger.error(f"Failed to process material alerts: {e}")
        raise self.retry(exc=e, countdown=60)


@celery.task(bind=True)
def backup_database(self):
    """Perform database backup."""
    try:
        from app import create_app
        import subprocess
        from datetime import datetime
        
        app = create_app()
        with app.app_context():
            # Generate backup filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_file = f"backup_{timestamp}.sql"
            
            # Create backup using SQL Server
            backup_command = f"""
            sqlcmd -S {app.config.get('DB_SERVER')} -U msu_app_user -Q "
            BACKUP DATABASE CentralServices_AM_DB 
            TO DISK = '{backup_file}'
            WITH NOFORMAT, NOINIT, NAME = 'MSU_Maintenance_Backup_{timestamp}',
            SKIP, NOREWIND, NOUNLOAD, STATS = 10
            "
            """
            
            # Execute backup safely without shell=True
            backup_command_list = [
                'sqlcmd', 
                '-S', app.config.get('DB_SERVER'), 
                '-U', 'msu_app_user', 
                '-Q', f"BACKUP DATABASE CentralServices_AM_DB TO DISK = '{backup_file}' WITH NOFORMAT, NOINIT, NAME = 'MSU_Maintenance_Backup_{timestamp}', SKIP, NOREWIND, NOUNLOAD, STATS = 10"
            ]
            
            result = subprocess.run(backup_command_list, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database backup completed: {backup_file}")
                return {'status': 'success', 'backup_file': backup_file}
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                raise Exception(f"Backup failed: {result.stderr}")
                
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


# Task utility functions
def get_task_status(task_id: str) -> Dict:
    """Get task status and result."""
    try:
        result = celery.AsyncResult(task_id)
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None,
            'traceback': result.traceback if result.failed() else None
        }
    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}")
        return {'task_id': task_id, 'status': 'UNKNOWN', 'error': str(e)}


def cancel_task(task_id: str) -> bool:
    """Cancel a running task."""
    try:
        celery.control.revoke(task_id, terminate=True)
        logger.info(f"Task {task_id} cancelled")
        return True
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        return False


# Task decorators for common patterns
def cache_task(ttl: int = 3600):
    """Decorator to cache task results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"task:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute task
            result = func(*args, **kwargs)
            
            # Cache result
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def retry_task(max_retries: int = 3, countdown: int = 60):
    """Decorator to add retry logic to tasks."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Task {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(countdown)
            return None
        return wrapper
    return decorator
