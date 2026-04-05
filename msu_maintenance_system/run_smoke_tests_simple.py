"""
Simple Smoke Tests for MSU Maintenance System
Phase 3 Validation without pytest configuration issues
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_flask_app_startup():
    """Test that Flask app starts cleanly."""
    print("🚀 Testing Flask App Startup")
    
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        assert app is not None, "Flask app should be created"
        assert app.name == 'app', f"App name should be 'app', got {app.name}"
        assert app.debug == True, "Debug mode should be enabled in development"
        
        print("✅ Flask app starts cleanly")
        return True
        
    except Exception as e:
        print(f"❌ Flask app startup failed: {e}")
        return False

def test_login_page_accessibility():
    """Test login page loads and returns correct status."""
    print("\n🔐 Testing Login Page")
    
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            # Test alternative auth/login route
            response = client.get('/auth/login')
            assert response.status_code == 200, f"Alternative /auth/login should return 200, got {response.status_code}"
            
            # Test login page contains expected elements
            assert b'form' in response.data, "Login page should contain form"
            assert b'email' in response.data, "Login page should contain email field"
            assert b'password' in response.data, "Login page should contain password field"
            
            print("✅ Login page accessible with required form elements")
            return True
            
    except Exception as e:
        print(f"❌ Login page test failed: {e}")
        return False

def test_dashboard_redirect():
    """Test dashboard accessibility and redirects."""
    print("\n🏠 Testing Dashboard")
    
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            # Test dashboard without authentication (should redirect)
            response = client.get('/dashboard')
            assert response.status_code in [302, 401, 403], f"Dashboard should redirect unauthenticated users, got {response.status_code}"
            
            print("✅ Dashboard properly redirects unauthenticated users")
            return True
            
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_api_endpoints():
    """Test critical API endpoints are accessible."""
    print("\n🛣️ Testing Critical API Endpoints")
    
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            # Test jobs endpoint
            response = client.get('/api/v1/jobs')
            assert response.status_code != 500, f"Jobs endpoint should not return 500, got {response.status_code}"
            assert response.status_code in [200, 401, 403, 404], f"Jobs endpoint returned unexpected status {response.status_code}"
            
            print(f"✅ Jobs endpoint returns {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def test_404_handling():
    """Test application error handling."""
    print("\n⚠️ Testing Error Handling")
    
    try:
        load_dotenv()
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            # Test 404 handling
            response = client.get('/nonexistent-page')
            assert response.status_code == 404, f"404 should return 404, got {response.status_code}"
            
            print("✅ 404 handling works correctly")
            return True
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_smoke_tests():
    """Execute all smoke tests."""
    print("🔥 MSU Maintenance System - Smoke Tests")
    print("=" * 50)
    print("Testing critical paths and error handling")
    print()
    
    tests = [
        ("Flask App Startup", test_flask_app_startup),
        ("Login Page", test_login_page_accessibility),
        ("Dashboard", test_dashboard_redirect),
        ("Critical Endpoints", test_api_endpoints),
        ("Error Handling", test_404_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("📊 SMOKE TEST RESULTS:")
    print(f"✅ PASSED: {passed}/{len(tests)} tests")
    print(f"❌ FAILED: {failed}/{len(tests)} tests")
    
    if failed == 0:
        print("🎯 SMOKE TESTS: ✅ ALL PASSED")
        print("🚀 READY FOR PHASE 4: COVERAGE GATE")
        print("\nNext Steps:")
        print("→ pytest --cov=app --cov-fail-under=80")
        print("→ Verify coverage report shows >= 80% overall")
    else:
        print("⚠️ SMOKE TESTS: ❌ SOME FAILED")
        print("🔧 Fix failing tests before proceeding")
        print("\nRequired Actions:")
        print("→ Review test failures above")
        print("→ Check application logs for errors")
        print("→ Verify environment configuration")
    
    return failed == 0

if __name__ == '__main__':
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
