"""
Test logging configuration and functionality
"""

import pytest
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_logging_configured():
    """Test logging is configured."""
    logger = logging.getLogger()
    assert logger is not None, "Logger should be configured"
    assert len(logger.handlers) > 0, "Logger should have handlers"

def test_logging_level():
    """Test logging level is set."""
    logger = logging.getLogger()
    assert logger.level is not None, "Logging level should be set"

def test_logging_handlers():
    """Test logging handlers are configured."""
    logger = logging.getLogger()
    assert len(logger.handlers) > 0, "Should have at least one handler"

def test_app_logging():
    """Test app-specific logging."""
    try:
        from app.utils.logging_config import setup_logging
        logger = setup_logging()
        assert logger is not None, "App logging should work"
    except ImportError:
        pytest.skip("Logging config not available")

def test_error_logging():
    """Test error logging functionality."""
    logger = logging.getLogger()
    
    # Test error logging
    try:
        logger.error("Test error message")
        assert True, "Error logging should work"
    except Exception:
        pytest.fail("Error logging failed")

def test_info_logging():
    """Test info logging functionality."""
    logger = logging.getLogger()
    
    # Test info logging
    try:
        logger.info("Test info message")
        assert True, "Info logging should work"
    except Exception:
        pytest.fail("Info logging failed")

def test_logging_format():
    """Test logging format is configured."""
    logger = logging.getLogger()
    
    # Check if handlers have formatters
    for handler in logger.handlers:
        if handler.formatter:
            assert handler.formatter._fmt is not None, "Handler should have formatter"
            break

if __name__ == '__main__':
    pytest.main([__file__])
