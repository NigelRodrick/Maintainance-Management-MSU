
import os
import sys
import coverage
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests_with_coverage():
    """Run tests with coverage directly."""
    print("Running tests with direct coverage...")
    
    # Start coverage
    cov = coverage.Coverage(source=['app'])
    cov.start()
    
    try:
        # Import and run tests
        load_dotenv()
        from app import create_app
        
        # Test 1: Flask app startup
        print("  Test 1: Flask app startup")
        app = create_app('development')
        assert app is not None
        assert app.name == 'app'
        print("    PASS: Flask app startup")
        
        # Test 2: Login page
        print("  Test 2: Login page")
        with app.test_client() as client:
            response = client.get('/auth/login')
            assert response.status_code == 200
            print("    PASS: Login page")
        
        # Test 3: Dashboard redirect
        print("  Test 3: Dashboard redirect")
        with app.test_client() as client:
            response = client.get('/dashboard')
            assert response.status_code in [302, 401, 403]
            print("    PASS: Dashboard redirect")
        
        # Test 4: API endpoints
        print("  Test 4: API endpoints")
        with app.test_client() as client:
            response = client.get('/api/v1/jobs')
            assert response.status_code != 500
            print("    PASS: API endpoints")
        
        # Test 5: Error handling
        print("  Test 5: Error handling")
        with app.test_client() as client:
            response = client.get('/nonexistent-page')
            assert response.status_code == 404
            print("    PASS: Error handling")
        
        print("  All tests completed successfully!")
        
    except Exception as e:
        print(f"  FAIL: Test failed - {e}")
        return False
    finally:
        # Stop coverage
        cov.stop()
        cov.save()
        
        # Generate reports
        print("  Generating coverage reports...")
        cov.html_report(directory='htmlcov')
        cov.xml_report(outfile='coverage.xml')
        
        # Show coverage summary
        total = cov.report()
        print(f"  Coverage: {total:.1f}%")
        
        return total >= 80.0

if __name__ == '__main__':
    success = run_tests_with_coverage()
    sys.exit(0 if success else 1)
