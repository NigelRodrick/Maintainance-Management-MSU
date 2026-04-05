"""
Health Check Endpoints
Application health monitoring and readiness checks.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime, timedelta
import psutil
import os
from app.extensions import db, cache, celery
from app.repositories import UserRepository, JobRepository
from app.cache_service import cache_service
from app.performance_monitor import performance_monitor
import logging

logger = logging.getLogger(__name__)

# Create health check blueprint
health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """Basic health check endpoint."""
    try:
        # Check application components
        checks = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': current_app.config.get('VERSION', '1.0.0'),
            'environment': current_app.config.get('ENV', 'unknown'),
            'checks': {
                'database': _check_database(),
                'cache': _check_cache(),
                'celery': _check_celery(),
                'disk_space': _check_disk_space(),
                'memory': _check_memory()
            }
        }
        
        # Determine overall status
        failed_checks = [name for name, status in checks['checks'].items() if status['status'] != 'healthy']
        
        if failed_checks:
            checks['status'] = 'unhealthy'
            checks['failed_checks'] = failed_checks
            return jsonify(checks), 503
        
        return jsonify(checks), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503


@health_bp.route('/health/ready')
def readiness_check():
    """Readiness check for Kubernetes."""
    try:
        # Check if application is ready to serve traffic
        checks = {
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'database': _check_database(),
                'cache': _check_cache(),
                'migrations': _check_migrations(),
                'initial_data': _check_initial_data()
            }
        }
        
        # All checks must pass for readiness
        failed_checks = [name for name, status in checks['checks'].items() if status['status'] != 'healthy']
        
        if failed_checks:
            checks['status'] = 'not_ready'
            checks['failed_checks'] = failed_checks
            return jsonify(checks), 503
        
        return jsonify(checks), 200
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503


@health_bp.route('/health/live')
def liveness_check():
    """Liveness check for Kubernetes."""
    try:
        # Simple check to see if the application is running
        checks = {
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime': _get_uptime(),
            'checks': {
                'process': _check_process(),
                'memory': _check_memory()
            }
        }
        
        # Process must be running for liveness
        if checks['checks']['process']['status'] != 'healthy':
            checks['status'] = 'dead'
            return jsonify(checks), 503
        
        return jsonify(checks), 200
        
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return jsonify({
            'status': 'dead',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503


@health_bp.route('/health/detailed')
def detailed_health_check():
    """Detailed health check with comprehensive diagnostics."""
    try:
        checks = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': current_app.config.get('VERSION', '1.0.0'),
            'environment': current_app.config.get('ENV', 'unknown'),
            'uptime': _get_uptime(),
            'checks': {
                'database': _check_database(),
                'cache': _check_cache(),
                'celery': _check_celery(),
                'disk_space': _check_disk_space(),
                'memory': _check_memory(),
                'cpu': _check_cpu(),
                'network': _check_network(),
                'migrations': _check_migrations(),
                'initial_data': _check_initial_data(),
                'performance': _check_performance(),
                'security': _check_security()
            }
        }
        
        # Determine overall status
        failed_checks = [name for name, status in checks['checks'].items() if status['status'] != 'healthy']
        warning_checks = [name for name, status in checks['checks'].items() if status['status'] == 'warning']
        
        if failed_checks:
            checks['status'] = 'unhealthy'
            checks['failed_checks'] = failed_checks
            return jsonify(checks), 503
        elif warning_checks:
            checks['status'] = 'warning'
            checks['warning_checks'] = warning_checks
            return jsonify(checks), 200
        
        return jsonify(checks), 200
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503


def _check_database():
    """Check database connectivity."""
    try:
        # Try to execute a simple query
        result = db.session.execute('SELECT 1').scalar()
        
        if result == 1:
            return {
                'status': 'healthy',
                'message': 'Database connection successful',
                'response_time_ms': _measure_db_response_time()
            }
        else:
            return {
                'status': 'unhealthy',
                'message': 'Database query returned unexpected result'
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }


def _check_cache():
    """Check Redis cache connectivity."""
    try:
        # Try to set and get a value
        test_key = 'health_check_test'
        test_value = str(datetime.utcnow())
        
        cache_service.set(test_key, test_value, ttl=10)
        retrieved_value = cache_service.get(test_key)
        
        if retrieved_value == test_value:
            return {
                'status': 'healthy',
                'message': 'Cache connection successful',
                'response_time_ms': _measure_cache_response_time()
            }
        else:
            return {
                'status': 'unhealthy',
                'message': 'Cache test failed - value mismatch'
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Cache connection failed: {str(e)}'
        }


def _check_celery():
    """Check Celery worker status."""
    try:
        # Check if Celery is running
        inspect = celery.control.inspect()
        
        # Get active tasks
        active_tasks = inspect.active()
        
        # Get registered tasks
        registered_tasks = inspect.registered()
        
        # Get stats
        stats = inspect.stats()
        
        if stats and len(stats) > 0:
            return {
                'status': 'healthy',
                'message': 'Celery workers are running',
                'workers': len(stats),
                'active_tasks': len(active_tasks) if active_tasks else 0,
                'registered_tasks': len(registered_tasks) if registered_tasks else 0
            }
        else:
            return {
                'status': 'unhealthy',
                'message': 'No Celery workers found'
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Celery check failed: {str(e)}'
        }


def _check_disk_space():
    """Check available disk space."""
    try:
        disk_usage = psutil.disk_usage('/')
        
        # Calculate percentage used
        percent_used = (disk_usage.used / disk_usage.total) * 100
        
        # Determine status based on usage
        if percent_used < 80:
            status = 'healthy'
        elif percent_used < 90:
            status = 'warning'
        else:
            status = 'unhealthy'
        
        return {
            'status': status,
            'message': f'Disk usage: {percent_used:.1f}%',
            'total_gb': round(disk_usage.total / (1024**3), 2),
            'used_gb': round(disk_usage.used / (1024**3), 2),
            'free_gb': round(disk_usage.free / (1024**3), 2),
            'percent_used': round(percent_used, 1)
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Disk space check failed: {str(e)}'
        }


def _check_memory():
    """Check memory usage."""
    try:
        memory = psutil.virtual_memory()
        
        # Calculate percentage used
        percent_used = memory.percent
        
        # Determine status based on usage
        if percent_used < 80:
            status = 'healthy'
        elif percent_used < 90:
            status = 'warning'
        else:
            status = 'unhealthy'
        
        return {
            'status': status,
            'message': f'Memory usage: {percent_used:.1f}%',
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'percent_used': round(percent_used, 1)
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Memory check failed: {str(e)}'
        }


def _check_cpu():
    """Check CPU usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Determine status based on usage
        if cpu_percent < 70:
            status = 'healthy'
        elif cpu_percent < 85:
            status = 'warning'
        else:
            status = 'unhealthy'
        
        return {
            'status': status,
            'message': f'CPU usage: {cpu_percent:.1f}%',
            'cpu_percent': round(cpu_percent, 1),
            'core_count': psutil.cpu_count()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'CPU check failed: {str(e)}'
        }


def _check_network():
    """Check network connectivity."""
    try:
        # Check network I/O
        network_io = psutil.net_io_counters()
        
        # Check if we can resolve a common domain
        import socket
        try:
            socket.gethostbyname('google.com')
            dns_status = 'healthy'
        except:
            dns_status = 'unhealthy'
        
        return {
            'status': dns_status,
            'message': f'Network connectivity: {dns_status}',
            'bytes_sent': network_io.bytes_sent,
            'bytes_recv': network_io.bytes_recv,
            'packets_sent': network_io.packets_sent,
            'packets_recv': network_io.packets_recv
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Network check failed: {str(e)}'
        }


def _check_process():
    """Check if the application process is running."""
    try:
        # Get current process
        process = psutil.Process()
        
        return {
            'status': 'healthy',
            'message': 'Application process is running',
            'pid': process.pid,
            'status_code': process.status(),
            'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
            'cpu_percent': process.cpu_percent(),
            'memory_mb': round(process.memory_info().rss / (1024**2), 2)
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Process check failed: {str(e)}'
        }


def _check_migrations():
    """Check if database migrations are up to date."""
    try:
        # Check if migrations table exists
        migration_table_exists = db.session.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'schema_migrations'
        """).scalar()
        
        if not migration_table_exists:
            return {
                'status': 'unhealthy',
                'message': 'Migrations table does not exist'
            }
        
        # Get list of migration files
        import os
        migrations_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'database_migrations')
        migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql') and f.isdigit()]
        migration_files.sort()
        
        # Get applied migrations
        applied_migrations = db.session.execute("""
            SELECT filename FROM schema_migrations ORDER BY filename
        """).fetchall()
        applied_filenames = [row[0] for row in applied_migrations]
        
        # Check if all migrations are applied
        missing_migrations = []
        for migration_file in migration_files:
            if migration_file not in applied_filenames:
                missing_migrations.append(migration_file)
        
        if missing_migrations:
            return {
                'status': 'unhealthy',
                'message': f'Missing migrations: {", ".join(missing_migrations)}'
            }
        
        return {
            'status': 'healthy',
            'message': f'All {len(migration_files)} migrations applied successfully'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Migration check failed: {str(e)}'
        }


def _check_initial_data():
    """Check if initial data exists."""
    try:
        # Check if admin user exists
        admin_user_exists = db.session.execute("""
            SELECT COUNT(*) FROM users WHERE role = 'admin'
        """).scalar()
        
        if admin_user_exists == 0:
            return {
                'status': 'unhealthy',
                'message': 'No admin user found'
            }
        
        # Check if workers exist
        workers_exist = db.session.execute("""
            SELECT COUNT(*) FROM workers WHERE is_deleted = 0
        """).scalar()
        
        if workers_exist == 0:
            return {
                'status': 'unhealthy',
                'message': 'No workers found'
            }
        
        return {
            'status': 'healthy',
            'message': f'Initial data verified: {admin_user_exists} admin users, {workers_exist} workers'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Initial data check failed: {str(e)}'
        }


def _check_performance():
    """Check application performance metrics."""
    try:
        # Get performance summary
        perf_summary = performance_monitor.get_performance_summary()
        
        # Check response times
        avg_response_time = perf_summary.get('requests', {}).get('avg_response_time', 0)
        
        # Check cache hit rate
        cache_hit_rate = perf_summary.get('cache', {}).get('hit_rate_percent', 0)
        
        # Determine status
        if avg_response_time > 2.0 or cache_hit_rate < 50:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'message': f'Performance: {avg_response_time:.3f}s avg response, {cache_hit_rate:.1f}% cache hit rate',
            'avg_response_time_ms': round(avg_response_time * 1000, 2),
            'cache_hit_rate_percent': round(cache_hit_rate, 1)
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Performance check failed: {str(e)}'
        }


def _check_security():
    """Check security configuration."""
    try:
        security_issues = []
        
        # Check if HTTPS is enforced in production
        if current_app.config.get('ENV') == 'production':
            if not current_app.config.get('FORCE_HTTPS', False):
                security_issues.append('HTTPS not enforced')
        
        # Check if session cookies are secure
        if not current_app.config.get('SESSION_COOKIE_SECURE', True):
            security_issues.append('Session cookies not secure')
        
        # Check if CSRF protection is enabled
        if not current_app.config.get('WTF_CSRF_ENABLED', True):
            security_issues.append('CSRF protection disabled')
        
        # Determine status
        if security_issues:
            status = 'warning'
            message = f'Security issues: {", ".join(security_issues)}'
        else:
            status = 'healthy'
            message = 'Security configuration is properly set'
        
        return {
            'status': status,
            'message': message,
            'security_issues': security_issues
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Security check failed: {str(e)}'
        }


def _get_uptime():
    """Get application uptime."""
    try:
        process = psutil.Process()
        uptime_seconds = datetime.utcnow().timestamp() - process.create_time()
        
        # Convert to human readable format
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return {
            'seconds': int(uptime_seconds),
            'human_readable': f'{days}d {hours}h {minutes}m'
        }
    except Exception:
        return {
            'seconds': 0,
            'human_readable': 'Unknown'
        }


def _measure_db_response_time():
    """Measure database response time."""
    try:
        start_time = datetime.utcnow()
        db.session.execute('SELECT 1')
        end_time = datetime.utcnow()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        return round(response_time, 2)
    except Exception:
        return -1


def _measure_cache_response_time():
    """Measure cache response time."""
    try:
        start_time = datetime.utcnow()
        cache_service.get('non_existent_key')
        end_time = datetime.utcnow()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        return round(response_time, 2)
    except Exception:
        return -1


# Error handlers for health check endpoints
@health_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return jsonify({
        'status': 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'error': 'Internal server error',
        'message': str(error)
    }), 500


@health_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({
        'status': 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'error': 'Endpoint not found'
    }), 404
