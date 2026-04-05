"""
Smoke Tests - Fixed Version
Critical path validation for MSU Maintenance System
"""

import pytest
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_flask_app_startup():
    print("Testing Flask App Startup")
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        assert app is not None
        assert app.name == 'app'
        assert app.debug == True
        print("PASS: Flask app starts cleanly")
        return True
    except Exception as e:
        pytest.fail(f"Flask app startup failed: {e}")
        return False

def test_login_page_accessibility():
    print("Testing Login Page")
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            response = client.get('/login')
            assert response.status_code in [200, 404]
            
            alt_response = client.get('/auth/login')
            assert alt_response.status_code == 200
            assert b'form' in alt_response.data
            print("PASS: Login page accessible")
            return True
    except Exception as e:
        pytest.fail(f"Login page test failed: {e}")
        return False

def test_dashboard_accessibility():
    print("Testing Dashboard")
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            response = client.get('/dashboard')
            assert response.status_code in [302, 401, 403]
            print("PASS: Dashboard redirects unauthenticated users")
            return True
    except Exception as e:
        pytest.fail(f"Dashboard test failed: {e}")
        return False

def test_critical_endpoints():
    print("Testing Critical API Endpoints")
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            endpoints = [
                ('/api/v1/auth/login', 'POST'),
                ('/api/v1/jobs', 'GET'),
                ('/admin/full/models', 'GET'),
            ]
            
            for endpoint, method in endpoints:
                if method == 'GET':
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint, json={})
                
                assert response.status_code != 500
                assert response.status_code in [200, 401, 403, 404]
                print(f"PASS: {endpoint} returns {response.status_code}")
            
            return True
    except Exception as e:
        pytest.fail(f"Critical endpoints test failed: {e}")
        return False

def test_error_handling():
    print("Testing Error Handling")
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            response = client.get('/nonexistent-page')
            assert response.status_code == 404
            print("PASS: 404 handling works")
            return True
    except Exception as e:
        pytest.fail(f"Error handling test failed: {e}")
        return False

def run_smoke_tests():
    print("MSU Maintenance System - Smoke Tests")
    print("=" * 50)
    
    tests = [
        ("Flask App Startup", test_flask_app_startup),
        ("Login Page", test_login_page_accessibility),
        ("Dashboard", test_dashboard_accessibility),
        ("Critical Endpoints", test_critical_endpoints),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"PASS: {test_name}")
            else:
                failed += 1
                print(f"FAIL: {test_name}")
        except Exception as e:
            failed += 1
            print(f"ERROR: {test_name} - {e}")
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("SMOKE TESTS: ALL PASSED")
        print("READY FOR PHASE 4: COVERAGE GATE")
    else:
        print("SMOKE TESTS: SOME FAILED")
    
    return failed == 0

if __name__ == '__main__':
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
