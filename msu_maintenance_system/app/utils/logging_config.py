"""
Logging Configuration for MSU Maintenance System

Provides centralized logging setup and utilities.
"""

import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logging(app_name: str = "MSU_Maintenance", level: int = logging.INFO):
    """
    Setup logging configuration for the application.
    
    Args:
        app_name: Name of the application
        level: Logging level (default: INFO)
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Setup file handler
    file_handler = logging.FileHandler(f'{app_name}.log')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Create specific logger for the application
    app_logger = logging.getLogger(app_name)
    app_logger.setLevel(level)
    
    return app_logger


def log_authentication_attempt(email: str, success: bool, ip_address: Optional[str] = None):
    """
    Log authentication attempts.
    
    Args:
        email: User email
        success: Whether authentication was successful
        ip_address: IP address of the request
    """
    logger = logging.getLogger('MSU_Maintenance.auth')
    
    status = "SUCCESS" if success else "FAILED"
    message = f"AUTH_{status}: email={email}"
    
    if ip_address:
        message += f", ip={ip_address}"
    
    if success:
        logger.info(message)
    else:
        logger.warning(message)


def log_access_attempt(user_id: int, user_role: str, route: str, success: bool, ip_address: Optional[str] = None):
    """
    Log access attempts to protected routes.
    
    Args:
        user_id: User ID
        user_role: User role
        route: Route being accessed
        success: Whether access was successful
        ip_address: IP address of the request
    """
    logger = logging.getLogger('MSU_Maintenance.access')
    
    status = "GRANTED" if success else "DENIED"
    message = f"ACCESS_{status}: user_id={user_id}, role={user_role}, route={route}"
    
    if ip_address:
        message += f", ip={ip_address}"
    
    if success:
        logger.info(message)
    else:
        logger.warning(message)


def log_database_operation(operation: str, table: str, success: bool, error: Optional[str] = None):
    """
    Log database operations.
    
    Args:
        operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        success: Whether operation was successful
        error: Error message if operation failed
    """
    logger = logging.getLogger('MSU_Maintenance.database')
    
    status = "SUCCESS" if success else "FAILED"
    message = f"DB_{status}: operation={operation}, table={table}"
    
    if error:
        message += f", error={error}"
    
    if success:
        logger.debug(message)
    else:
        logger.error(message)


def log_ml_prediction(description: str, category: str, priority: str, confidence: Optional[float] = None):
    """
    Log ML prediction requests and results.
    
    Args:
        description: Job description
        category: Predicted category
        priority: Predicted priority
        confidence: Confidence score if available
    """
    logger = logging.getLogger('MSU_Maintenance.ml')
    
    message = f"ML_PREDICTION: category={category}, priority={priority}"
    
    if confidence:
        message += f", confidence={confidence:.2f}"
    
    # Truncate description for logging
    truncated_desc = description[:50] + "..." if len(description) > 50 else description
    message += f", description='{truncated_desc}'"
    
    logger.info(message)


def log_job_status_change(job_id: int, old_status: str, new_status: str, user_id: int):
    """
    Log job status changes.
    
    Args:
        job_id: Job ID
        old_status: Previous status
        new_status: New status
        user_id: User who made the change
    """
    logger = logging.getLogger('MSU_Maintenance.jobs')
    
    message = f"STATUS_CHANGE: job_id={job_id}, old_status={old_status}, new_status={new_status}, user_id={user_id}"
    logger.info(message)


def log_system_error(error: Exception, context: str, user_id: Optional[int] = None):
    """
    Log system errors with context.
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
        user_id: User ID if applicable
    """
    logger = logging.getLogger('MSU_Maintenance.errors')
    
    message = f"SYSTEM_ERROR: context={context}, error={str(error)}, type={type(error).__name__}"
    
    if user_id:
        message += f", user_id={user_id}"
    
    logger.error(message, exc_info=True)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"MSU_Maintenance.{name}")


# Initialize logging when module is imported
setup_logging()
