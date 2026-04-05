"""
Enhanced Error Handler

Provides centralized error handling with logging and user-friendly messages.
"""

import logging
import traceback
from functools import wraps
from typing import Callable, Any, Optional
from flask import flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user

from ..utils.logging_config import log_system_error, get_logger

# Setup logger
logger = get_logger('error_handler')


class ErrorHandler:
    """Centralized error handling with logging and user feedback."""
    
    def __init__(self):
        self.user_friendly_messages = {
            'database': 'Database operation failed. Please try again.',
            'authentication': 'Authentication error. Please log in again.',
            'authorization': 'Access denied. You do not have permission for this action.',
            'validation': 'Invalid input. Please check your data and try again.',
            'not_found': 'The requested resource was not found.',
            'server': 'Server error occurred. Our team has been notified.',
            'network': 'Network connection error. Please check your internet connection.',
            'unknown': 'An unexpected error occurred. Please try again.'
        }
    
    def handle_exception(self, error: Exception, context: str = None) -> str:
        """
        Handle exception with logging and return user-friendly message.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            
        Returns:
            User-friendly error message
        """
        error_type = self._classify_error(error)
        error_message = self.user_friendly_messages.get(error_type, self.user_friendly_messages['unknown'])
        
        # Log the full error for debugging
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'user_id': getattr(current_user, 'id', 'anonymous'),
            'user_email': getattr(current_user, 'email', 'anonymous'),
            'request_url': request.url if request else 'unknown',
            'traceback': traceback.format_exc()
        }
        
        log_system_error(error, context or "unknown", error_details)
        
        # Add user-friendly flash message
        flash(error_message, 'error')
        
        return error_message
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for appropriate user message."""
        error_name = type(error).__name__.lower()
        
        if 'database' in error_name or 'sql' in error_name:
            return 'database'
        elif 'permission' in error_name or 'access' in error_name:
            return 'authorization'
        elif 'value' in error_name or 'validation' in error_name:
            return 'validation'
        elif 'notfound' in error_name or 'not_found' in error_name:
            return 'not_found'
        elif 'connection' in error_name or 'network' in error_name:
            return 'network'
        elif 'authentication' in error_name or 'auth' in error_name:
            return 'authentication'
        else:
            return 'server'
    
    def safe_execute(self, func: Callable, *args, default_return: Any = None, 
                    context: str = None, **kwargs) -> Any:
        """
        Safely execute function with error handling.
        
        Args:
            func: Function to execute
            *args: Function arguments
            default_return: Value to return on error
            context: Context for error logging
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or default_return on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_exception(e, context or f"Function: {func.__name__}")
            return default_return
    
    def api_error_response(self, error: Exception, context: str = None) -> tuple:
        """
        Create API error response with proper formatting.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            
        Returns:
            Tuple of (json_response, status_code)
        """
        error_type = self._classify_error(error)
        
        status_codes = {
            'validation': 400,
            'authentication': 401,
            'authorization': 403,
            'not_found': 404,
            'database': 500,
            'server': 500,
            'network': 503,
            'unknown': 500
        }
        
        status_code = status_codes.get(error_type, 500)
        
        response_data = {
            'success': False,
            'error': {
                'type': error_type,
                'message': self.user_friendly_messages.get(error_type, self.user_friendly_messages['unknown']),
                'details': str(error) if current_app.debug else None
            }
        }
        
        # Log the error
        self.handle_exception(error, context)
        
        return jsonify(response_data), status_code


# Global error handler instance
error_handler = ErrorHandler()


# Decorators for easy error handling
def handle_errors(default_return: Any = None, context: str = None, 
                 flash_message: bool = True, redirect_url: str = None):
    """
    Decorator for automatic error handling.
    
    Args:
        default_return: Value to return on error
        context: Context for error logging
        flash_message: Whether to show flash message
        redirect_url: URL to redirect on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_message = error_handler.handle_exception(
                    e, context or f"Route: {func.__name__}"
                )
                
                if redirect_url:
                    return redirect(redirect_url)
                elif default_return is not None:
                    return default_return
                else:
                    # Return to previous page or home
                    return redirect(request.referrer or url_for('main.dashboard'))
        return wrapper
    return decorator


def handle_api_errors(context: str = None):
    """
    Decorator for API route error handling.
    
    Args:
        context: Context for error logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.api_error_response(
                    e, context or f"API: {func.__name__}"
                )
        return wrapper
    return decorator


def safe_database_operation(default_return: Any = None, context: str = None):
    """
    Decorator specifically for database operations.
    
    Args:
        default_return: Value to return on error
        context: Context for error logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_message = error_handler.handle_exception(
                    e, context or f"Database: {func.__name__}"
                )
                return default_return
        return wrapper
    return decorator


# Utility functions for common error scenarios
def handle_not_found(resource: str = "Resource", redirect_url: str = None):
    """Handle not found errors."""
    message = f"{resource} not found."
    flash(message, 'error')
    return redirect(redirect_url or request.referrer or url_for('main.dashboard'))


def handle_permission_denied(action: str = "perform this action", redirect_url: str = None):
    """Handle permission denied errors."""
    message = f"You do not have permission to {action}."
    flash(message, 'error')
    return redirect(redirect_url or request.referrer or url_for('main.dashboard'))


def handle_validation_error(errors: list, redirect_url: str = None):
    """Handle validation errors."""
    for error in errors:
        flash(error, 'error')
    return redirect(redirect_url or request.referrer or url_for('main.dashboard'))


def handle_database_error(operation: str = "Database operation", redirect_url: str = None):
    """Handle database errors."""
    message = f"{operation} failed. Please try again."
    flash(message, 'error')
    return redirect(redirect_url or request.referrer or url_for('main.dashboard'))
