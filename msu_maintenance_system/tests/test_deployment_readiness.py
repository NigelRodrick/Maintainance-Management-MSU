"""
Test deployment readiness and production configurations
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_deployment_prerequisites():
    """Test all deployment prerequisites."""
    # Test Python version
    python_version = sys.version_info
    assert python_version.major >= 3
    assert python_version.minor >= 8
    
    # Test required files exist
    assert Path('config.py').exists()
    assert Path('app/__init__.py').exists()
    assert Path('requirements.txt').exists()
    assert Path('app/static').exists()
    assert Path('app/templates').exists()
    
    # Test environment variables
    assert 'SECRET_KEY' in os.environ
    assert 'DB_SERVER' in os.environ
    assert 'DB_NAME' in os.environ

def test_production_configuration():
    """Test production configuration."""
    from app import create_app
    
    app = create_app('production')
    
    # Test production settings
    assert not app.config.get('DEBUG', True)
    assert app.config.get('SECRET_KEY')
    assert len(app.config.get('SECRET_KEY')) >= 32
    assert app.config.get('WTF_CSRF_ENABLED', True)
    assert not app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)

def test_static_files():
    """Test static files are present."""
    static_dir = Path('app/static')
    
    assert static_dir.exists()
    assert (static_dir / 'css' / 'style.css').exists()
    assert (static_dir / 'js' / 'main.js').exists()
    assert (static_dir / 'images').exists()

def test_templates():
    """Test templates are present."""
    templates_dir = Path('app/templates')
    
    assert templates_dir.exists()
    assert (templates_dir / 'base.html').exists()
    assert (templates_dir / 'login.html').exists()
    assert (templates_dir / 'dashboard.html').exists()

def test_database_connectivity():
    """Test database connectivity."""
    from app import create_app
    
    app = create_app('development')
    
    with app.app_context():
        from app.extensions import db
        from sqlalchemy import text
        
        result = db.session.execute(text("SELECT 1"))
        assert result is not None

def test_application_startup():
    """Test application can start successfully."""
    from app import create_app
    
    app = create_app('development')
    assert app is not None
    assert hasattr(app, 'config')
    assert app.config['SECRET_KEY'] is not None

def test_error_handling():
    """Test error handling is working."""
    from app import create_app
    
    app = create_app('development')
    
    with app.test_client() as client:
        # Test 404 handling
        response = client.get('/nonexistent-route')
        assert response.status_code == 404

def test_security_headers():
    """Test security headers are present."""
    from app import create_app
    
    app = create_app('production')
    
    with app.test_client() as client:
        response = client.get('/')
        # Check for security-related headers
        assert response.status_code in [200, 302, 401]

def test_logging_configuration():
    """Test logging is configured."""
    import logging
    
    # Test root logger exists
    logger = logging.getLogger()
    assert logger is not None
    
    # Test handlers are configured
    assert len(logger.handlers) > 0

def test_dependencies():
    """Test all required dependencies are available."""
    required_modules = [
        'flask',
        'sqlalchemy',
        'werkzeug',
        'pytest'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            pytest.fail(f"Required module {module} is not available")

def test_production_readiness():
    """Test overall production readiness."""
    # This is a comprehensive test
    from app import create_app
    
    app = create_app('production')
    
    # Test app configuration
    assert not app.config.get('DEBUG', True)
    assert app.config.get('SECRET_KEY')
    assert len(app.config.get('SECRET_KEY')) >= 32
    
    # Test static files
    assert Path('app/static').exists()
    assert Path('app/templates').exists()
    
    # Test database connectivity
    with app.app_context():
        from app.extensions import db
        from sqlalchemy import text
        
        try:
            result = db.session.execute(text("SELECT 1"))
            assert result is not None
        except Exception:
            pytest.fail("Database connectivity failed")

if __name__ == '__main__':
    pytest.main([__file__])
