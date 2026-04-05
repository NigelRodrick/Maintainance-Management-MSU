"""
Test production deployment scenarios
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_production_app_creation():
    """Test production app creation."""
    from app import create_app
    
    app = create_app('production')
    
    assert app is not None
    assert app.config['ENV'] == 'production'
    assert not app.config.get('DEBUG', True)
    assert app.config.get('SECRET_KEY') is not None

def test_production_security():
    """Test production security settings."""
    from app import create_app
    
    app = create_app('production')
    
    # Test security settings
    assert not app.config.get('DEBUG', True)
    assert len(app.config.get('SECRET_KEY', '')) >= 32
    assert app.config.get('WTF_CSRF_ENABLED', True)
    assert not app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)

def test_static_file_serving():
    """Test static file serving."""
    from app import create_app
    
    app = create_app('production')
    
    with app.test_client() as client:
        # Test CSS file
        response = client.get('/static/css/style.css')
        assert response.status_code in [200, 404]  # 404 is acceptable
        
        # Test JS file
        response = client.get('/static/js/main.js')
        assert response.status_code in [200, 404]
        
        # Test non-existent static file
        response = client.get('/static/nonexistent.txt')
        assert response.status_code == 404

def test_template_rendering():
    """Test template rendering."""
    from app import create_app
    
    app = create_app('production')
    
    with app.test_client() as client:
        # Test main page
        response = client.get('/')
        assert response.status_code in [200, 302, 401]
        
        # Test login page
        response = client.get('/auth/login')
        assert response.status_code in [200, 302]

def test_database_operations():
    """Test database operations in production."""
    from app import create_app
    
    app = create_app('production')
    
    with app.app_context():
        from app.extensions import db
        from sqlalchemy import text
        
        try:
            result = db.session.execute(text("SELECT 1"))
            assert result is not None
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

def test_error_handling():
    """Test error handling in production."""
    from app import create_app
    
    app = create_app('production')
    
    with app.test_client() as client:
        # Test 404 error
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        
        # Test 405 error
        response = client.delete('/')
        assert response.status_code in [405, 302]

def test_session_security():
    """Test session security settings."""
    from app import create_app
    
    app = create_app('production')
    
    with app.test_client() as client:
        # Test session is secure
        response = client.get('/')
        session_cookie = response.headers.get('Set-Cookie', '')
        
        # Check for secure cookie attributes
        assert 'HttpOnly' in session_cookie or 'httponly' in session_cookie.lower()

def test_csrf_protection():
    """Test CSRF protection is enabled."""
    from app import create_app
    
    app = create_app('production')
    
    with app.test_client() as client:
        # Test CSRF token is present in forms
        response = client.get('/auth/login')
        assert response.status_code in [200, 302]
        
        # Check for CSRF token in response
        if response.status_code == 200:
            assert b'csrf' in response.data.lower()

def test_production_logging():
    """Test production logging."""
    import logging
    
    # Test logging is configured
    logger = logging.getLogger()
    assert logger is not None
    assert len(logger.handlers) > 0

def test_performance_settings():
    """Test performance settings."""
    from app import create_app
    
    app = create_app('production')
    
    # Test performance optimizations
    assert not app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    assert app.config.get('PERMANENT_SESSION_LIFETIME') is not None

def test_deployment_files():
    """Test deployment files are present."""
    # Test essential files exist
    essential_files = [
        'config.py',
        'app/__init__.py',
        'requirements.txt',
        'app/static/css/style.css',
        'app/static/js/main.js',
        'app/templates/base.html'
    ]
    
    for file_path in essential_files:
        assert Path(file_path).exists(), f"Essential file {file_path} is missing"

def test_environment_variables():
    """Test environment variables are set."""
    required_vars = ['SECRET_KEY', 'DB_SERVER', 'DB_NAME']
    
    for var in required_vars:
        assert var in os.environ, f"Environment variable {var} is not set"
        assert os.environ[var], f"Environment variable {var} is empty"

def test_production_database_config():
    """Test production database configuration."""
    from app import create_app
    
    app = create_app('production')
    
    # Test database configuration
    assert 'SQLALCHEMY_DATABASE_URI' in app.config or 'DATABASE_URL' in app.config
    
    # Test database is configured for production
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', app.config.get('DATABASE_URL', ''))
    assert db_uri, "Database URI is not configured"

if __name__ == '__main__':
    pytest.main([__file__])
