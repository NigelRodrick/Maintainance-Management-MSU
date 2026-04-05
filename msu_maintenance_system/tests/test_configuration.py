"""
Test configuration and settings
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_config_exists():
    """Test config file exists."""
    config_path = Path('config.py')
    assert config_path.exists(), "Config file should exist"

def test_app_init_exists():
    """Test app init file exists."""
    app_init_path = Path('app/__init__.py')
    assert app_init_path.exists(), "App init file should exist"

def test_requirements_exists():
    """Test requirements file exists."""
    requirements_path = Path('requirements.txt')
    assert requirements_path.exists(), "Requirements file should exist"

def test_development_config():
    """Test development configuration."""
    from app import create_app
    
    app = create_app('development')
    assert app is not None, "Development app should be created"
    assert app.config['ENV'] == 'development', "Should be development environment"
    assert app.config.get('DEBUG', False) is True, "Debug should be enabled in development"

def test_production_config():
    """Test production configuration."""
    from app import create_app
    
    app = create_app('production')
    assert app is not None, "Production app should be created"
    assert app.config['ENV'] == 'production', "Should be production environment"
    assert app.config.get('DEBUG', True) is False, "Debug should be disabled in production"

def test_secret_key():
    """Test secret key is configured."""
    from app import create_app
    
    app = create_app('development')
    secret_key = app.config.get('SECRET_KEY')
    assert secret_key is not None, "Secret key should be set"
    assert len(secret_key) >= 16, "Secret key should be sufficiently long"

def test_database_config():
    """Test database configuration."""
    from app import create_app
    
    app = create_app('development')
    
    # Check database configuration
    assert 'SQLALCHEMY_DATABASE_URI' in app.config or 'DATABASE_URL' in app.config, "Database should be configured"

def test_csrf_config():
    """Test CSRF configuration."""
    from app import create_app
    
    app = create_app('development')
    csrf_enabled = app.config.get('WTF_CSRF_ENABLED', True)
    assert csrf_enabled is True, "CSRF should be enabled"

def test_session_config():
    """Test session configuration."""
    from app import create_app
    
    app = create_app('development')
    session_lifetime = app.config.get('PERMANENT_SESSION_LIFETIME')
    assert session_lifetime is not None, "Session lifetime should be configured"

def test_environment_variables():
    """Test environment variables are set."""
    required_vars = ['SECRET_KEY', 'DB_SERVER', 'DB_NAME']
    
    for var in required_vars:
        assert var in os.environ, f"Environment variable {var} should be set"

if __name__ == '__main__':
    pytest.main([__file__])
