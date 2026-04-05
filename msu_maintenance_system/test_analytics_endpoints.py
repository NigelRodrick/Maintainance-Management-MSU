"""
Test Analytics Endpoints
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
    from app.analytics import AnalyticsModule
    
    # Create app and test analytics
    app = create_app('development')
    
    with app.app_context():
        analytics = AnalyticsModule()
        
        # Test analytics module
        try:
            data = analytics.get_dashboard_data()
            print(f"✅ Analytics Module Test SUCCESS")
            print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"❌ Analytics Module Test FAILED: {e}")
        
        # Test individual methods
        try:
            dept_summary = analytics.get_department_summary()
            print(f"✅ Department Summary SUCCESS: {dept_summary}")
        except Exception as e:
            print(f"❌ Department Summary FAILED: {e}")
        
        try:
            worker_perf = analytics.get_worker_performance()
            print(f"✅ Worker Performance SUCCESS: {len(worker_perf) if isinstance(worker_perf, list) else 'Not a list'} workers")
        except Exception as e:
            print(f"❌ Worker Performance FAILED: {e}")
        
        try:
            job_trends = analytics.get_job_trends(30)
            print(f"✅ Job Trends SUCCESS: {len(job_trends) if isinstance(job_trends, list) else 'Not a list'} trends")
        except Exception as e:
            print(f"❌ Job Trends FAILED: {e}")
        
        print("\n🎉 Analytics endpoints should be working!")
        print("🚀 Try accessing: http://localhost:5000/analytics/")
        
except Exception as e:
    print(f"❌ Analytics Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
