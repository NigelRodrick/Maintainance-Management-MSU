
"""
Security monitoring and logging for MSU Maintenance System
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Security event handler
def log_security_event(event_type: str, details: Dict[str, Any], severity: str = 'INFO'):
    """Log security events for monitoring."""
    event = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'severity': severity,
        'details': details,
        'source': 'msu_maintenance_system'
    }
    
    security_logger.info(f"SECURITY_EVENT: {event}")
    
    # In production, this would send to security monitoring system
    # send_to_security_monitoring_system(event)

def security_monitoring_decorator(func):
    """Decorator to add security monitoring to functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful execution
            log_security_event(
                event_type='function_execution',
                details={
                    'function': func.__name__,
                    'execution_time': time.time() - start_time,
                    'status': 'success'
                }
            )
            
            return result
            
        except Exception as e:
            # Log security-relevant errors
            log_security_event(
                event_type='security_error',
                details={
                    'function': func.__name__,
                    'error': str(e),
                    'execution_time': time.time() - start_time,
                    'status': 'error'
                },
                severity='WARNING'
            )
            
            raise
    
    return wrapper

# Input validation monitoring
def monitor_input_validation(input_data: Any, validation_function, context: str = 'unknown'):
    """Monitor input validation attempts."""
    try:
        is_valid = validation_function(input_data)
        
        log_security_event(
            event_type='input_validation',
            details={
                'context': context,
                'validation_result': is_valid,
                'input_type': type(input_data).__name__
            }
        )
        
        return is_valid
        
    except Exception as e:
        log_security_event(
            event_type='validation_error',
            details={
                'context': context,
                'error': str(e),
                'input_type': type(input_data).__name__
            },
            severity='ERROR'
        )
        
        return False

# Database operation monitoring
def monitor_database_operation(operation: str, table: str, success: bool, error: Optional[str] = None):
    """Monitor database operations for security."""
    log_security_event(
        event_type='database_operation',
        details={
            'operation': operation,
            'table': table,
            'success': success,
            'error': error
        }
    )

# Authentication monitoring
def monitor_authentication_attempt(username: str, success: bool, ip_address: str = 'unknown', failure_reason: Optional[str] = None):
    """Monitor authentication attempts."""
    log_security_event(
        event_type='authentication',
        details={
            'username': username,
            'success': success,
            'ip_address': ip_address,
            'failure_reason': failure_reason,
            'timestamp': datetime.utcnow().isoformat()
        },
        severity='WARNING' if not success else 'INFO'
    )

# Authorization monitoring
def monitor_authorization_check(user_id: int, resource: str, action: str, allowed: bool):
    """Monitor authorization checks."""
    log_security_event(
        event_type='authorization',
        details={
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'allowed': allowed
        }
    )

# Example usage in application
@security_monitoring_decorator
def sensitive_operation(user_input):
    """Example of monitoring a sensitive operation."""
    if monitor_input_validation(user_input, lambda x: len(x) > 0, 'user_input_validation'):
        # Process the input
        return f"Processed: {user_input}"
    else:
        raise ValueError("Invalid input")

@security_monitoring_decorator
def database_query(table: str, query: str):
    """Example of monitoring database queries."""
    try:
        # Execute database query
        result = execute_query(query)
        monitor_database_operation('SELECT', table, True)
        return result
    except Exception as e:
        monitor_database_operation('SELECT', table, False, str(e))
        raise
