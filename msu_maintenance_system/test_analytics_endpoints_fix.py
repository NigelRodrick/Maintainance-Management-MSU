"""
Test Analytics Endpoint Fix
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
    
    # Create app and test analytics endpoints
    app = create_app('development')
    
    with app.test_request_context():
        # Test URL generation
        from flask import url_for
        
        analytics_dashboard_url = url_for('analytics.analytics_dashboard')
        worker_performance_url = url_for('analytics.get_worker_performance')
        job_trends_url = url_for('analytics.get_job_trends')
        
        print(f"✅ Analytics Dashboard URL: {analytics_dashboard_url}")
        print(f"✅ Worker Performance URL: {worker_performance_url}")
        print(f"✅ Job Trends URL: {job_trends_url}")
        
        # Test route registration
        routes = []
        for rule in app.url_map.iter_rules():
            if 'analytics' in rule.endpoint:
                routes.append(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
        
        print("\n📊 Analytics Routes:")
        for route in routes:
            print(f"  {route}")
        
        print("\n🎉 All analytics endpoints should be working!")
        print("🚀 Try accessing: http://localhost:5000/analytics/")
        
except Exception as e:
    print(f"❌ Analytics Endpoint Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
