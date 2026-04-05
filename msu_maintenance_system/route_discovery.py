"""
Route Discovery for MSU Maintenance System
Check what routes are actually available
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_environment():
    """Setup environment variables for testing."""
    os.environ['SECRET_KEY'] = 'test-secret-key-for-smoke-tests'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['DB_SERVER'] = 'DESKTOP-IO9GJQS\\SQLEXPRESS'
    os.environ['DB_NAME'] = 'CentralServices_AM_DB'
    os.environ['ENV'] = 'development'

def discover_routes():
    """Discover all available routes."""
    print("🔍 DISCOVERING AVAILABLE ROUTES")
    print("=" * 50)
    
    try:
        from app import create_app
        app = create_app('development')
        
        # Setup environment
        setup_environment()
        
        print("Available routes:")
        
        # Get all routes
        for rule in app.url_map.iter_rules():
            print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
        
        print(f"\nTotal routes found: {len(list(app.url_map.iter_rules()))}")
        
        # Test specific routes
        print("\n🔍 TESTING SPECIFIC ROUTES:")
        
        with app.test_client() as client:
            # Test root
            try:
                response = client.get('/')
                print(f"  GET / -> {response.status_code}")
            except Exception as e:
                print(f"  GET / -> ERROR: {e}")
            
            # Test login
            try:
                response = client.get('/login')
                print(f"  GET /login -> {response.status_code}")
            except Exception as e:
                print(f"  GET /login -> ERROR: {e}")
            
            # Test dashboard
            try:
                response = client.get('/dashboard')
                print(f"  GET /dashboard -> {response.status_code}")
            except Exception as e:
                print(f"  GET /dashboard -> ERROR: {e}")
            
            # Test API routes
            try:
                response = client.get('/api/jobs')
                print(f"  GET /api/jobs -> {response.status_code}")
            except Exception as e:
                print(f"  GET /api/jobs -> ERROR: {e}")
            
            # Test common routes
            common_routes = ['/auth', '/admin', '/reports', '/analytics', '/user', '/supervisor']
            for route in common_routes:
                try:
                    response = client.get(route)
                    print(f"  GET {route} -> {response.status_code}")
                except Exception as e:
                    print(f"  GET {route} -> ERROR: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Route discovery failed: {e}")
        return False

def main():
    """Main execution."""
    print("🔍 MSU MAINTENANCE SYSTEM - ROUTE DISCOVERY")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Discover routes
    discover_routes()

if __name__ == '__main__':
    main()
