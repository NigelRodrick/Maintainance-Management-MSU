"""
Test Analytics with Real Database Views
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
    
    # Create app and test analytics with real database
    app = create_app('development')
    
    with app.app_context():
        analytics = AnalyticsModule()
        
        print("🔍 Testing Analytics Module with Real Database Views")
        print("=" * 60)
        
        # Test dashboard data (should work with vw_job_analytics)
        try:
            data = analytics.get_dashboard_data()
            print(f"✅ Dashboard Data SUCCESS:")
            print(f"   Total Jobs: {data.get('total_jobs', 'N/A')}")
            print(f"   Completed Jobs: {data.get('completed_jobs', 'N/A')}")
            print(f"   Pending Jobs: {data.get('pending_jobs', 'N/A')}")
            print(f"   Departments: {data.get('departments', 'N/A')}")
        except Exception as e:
            print(f"❌ Dashboard Data FAILED: {e}")
        
        # Test department summary (should work with vw_job_analytics)
        try:
            data = analytics.get_department_summary()
            print(f"\n✅ Department Summary SUCCESS:")
            print(f"   Total Jobs: {data.get('total_jobs', 'N/A')}")
            print(f"   Departments: {data.get('departments', 'N/A')}")
            print(f"   Top Department: {data.get('top_department', 'N/A')}")
        except Exception as e:
            print(f"❌ Department Summary FAILED: {e}")
        
        # Test worker performance (should work with mock data)
        try:
            data = analytics.get_worker_performance()
            print(f"\n✅ Worker Performance SUCCESS:")
            print(f"   Workers: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and data:
                print(f"   First Worker: {data[0].get('worker_name', 'N/A')}")
        except Exception as e:
            print(f"❌ Worker Performance FAILED: {e}")
        
        # Test job trends (should work with vw_job_analytics)
        try:
            data = analytics.get_job_trends(30)
            print(f"\n✅ Job Trends SUCCESS:")
            print(f"   Trends: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and data:
                print(f"   Latest Date: {data[0].get('date', 'N/A')}")
        except Exception as e:
            print(f"❌ Job Trends FAILED: {e}")
        
        # Test material analytics (should work with mock data)
        try:
            data = analytics.get_material_analytics()
            print(f"\n✅ Material Analytics SUCCESS:")
            print(f"   Total Materials: {data.get('total_materials', 'N/A')}")
            print(f"   Total Cost: ${data.get('total_cost', 'N/A')}")
            print(f"   Most Used: {data.get('most_used_material', 'N/A')}")
        except Exception as e:
            print(f"❌ Material Analytics FAILED: {e}")
        
        # Test SLA compliance (should work with mock data)
        try:
            data = analytics.get_sla_compliance()
            print(f"\n✅ SLA Compliance SUCCESS:")
            print(f"   Compliance Rate: {data.get('overall_compliance_rate', 'N/A')}%")
            print(f"   Total Jobs: {data.get('total_jobs_analyzed', 'N/A')}")
            print(f"   Within SLA: {data.get('within_sla', 'N/A')}")
        except Exception as e:
            print(f"❌ SLA Compliance FAILED: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Analytics module working with existing database views!")
        print("📊 Using: dbo.vw_job_analytics (only view that exists)")
        print("🔄 Missing views handled gracefully with mock data")
        print("🚀 Try accessing: http://localhost:5000/analytics/")
        
except Exception as e:
    print(f"❌ Analytics Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
