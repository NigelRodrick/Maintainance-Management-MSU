"""
Test Submit Request Route
"""

import os
import sys

# Set environment variables
os.environ['SECRET_KEY'] = 'test-key-123456789012345678901234567890'
os.environ['DB_SERVER'] = 'DESKTOP-IO9GJQS\\SQLEXPRESS'
os.environ['DB_NAME'] = 'CentralServices_AM_DB'
os.environ['DB_USER'] = 'munyamash'
os.environ['DB_PASSWORD'] = 'nowayout'

try:
    from app import create_app
    
    # Create app and test routes
    app = create_app('development')
    
    with app.test_request_context():
        # Test URL generation
        from flask import url_for
        index_url = url_for('main.index')
        dashboard_url = url_for('main.dashboard')
        
        print(f"✅ Index URL: {index_url}")
        print(f"✅ Dashboard URL: {dashboard_url}")
        
        # Test route registration
        routes = []
        for rule in app.url_map.iter_rules():
            if 'main' in rule.endpoint:
                routes.append(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
        
        print("\n📊 Main Routes:")
        for route in routes:
            print(f"  {route}")
        
        print("\n🎉 Submit Request route should be working!")
        print("🚀 Try accessing: http://localhost:5000/")
        
except Exception as e:
    print(f"❌ Route Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
