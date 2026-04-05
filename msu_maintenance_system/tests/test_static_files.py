"""
Test static files and templates
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_static_css_exists():
    """Test CSS static file exists."""
    css_path = Path('app/static/css/style.css')
    assert css_path.exists(), "CSS file should exist"

def test_static_js_exists():
    """Test JS static file exists."""
    js_path = Path('app/static/js/main.js')
    assert js_path.exists(), "JS file should exist"

def test_static_images_dir():
    """Test images directory exists."""
    images_dir = Path('app/static/images')
    assert images_dir.exists(), "Images directory should exist"

def test_templates_base_exists():
    """Test base template exists."""
    base_template = Path('app/templates/base.html')
    assert base_template.exists(), "Base template should exist"

def test_templates_login_exists():
    """Test login template exists."""
    login_template = Path('app/templates/login.html')
    assert login_template.exists(), "Login template should exist"

def test_templates_dashboard_exists():
    """Test dashboard template exists."""
    dashboard_template = Path('app/templates/dashboard.html')
    assert dashboard_template.exists(), "Dashboard template should exist"

def test_static_file_content():
    """Test static files have content."""
    css_path = Path('app/static/css/style.css')
    if css_path.exists():
        with open(css_path, 'r') as f:
            content = f.read()
            assert len(content) > 0, "CSS file should have content"
            assert 'body' in content, "CSS should contain body styles"

def test_template_content():
    """Test templates have content."""
    base_template = Path('app/templates/base.html')
    if base_template.exists():
        with open(base_template, 'r') as f:
            content = f.read()
            assert len(content) > 0, "Base template should have content"
            assert '<html' in content, "Template should be valid HTML"

if __name__ == '__main__':
    pytest.main([__file__])
