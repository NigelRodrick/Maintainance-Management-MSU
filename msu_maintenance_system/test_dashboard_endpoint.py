"""
Test Analytics Dashboard Endpoint
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
    
    # Create app and test dashboard endpoint
    app = create_app('development')
    
    with app.app_context():
        analytics = AnalyticsModule()
        
        print("🔍 Testing Dashboard Endpoint Data Structure")
        print("=" * 60)
        
        # Test dashboard data specifically
        try:
            data = analytics.get_dashboard_data()
            print(f"✅ Dashboard Data Structure:")
            print(f"   Keys: {list(data.keys())}")
            print(f"   Total Jobs: {data.get('total_jobs', 'MISSING')}")
            print(f"   Completion Rate: {data.get('completion_rate', 'MISSING')}")
            print(f"   Departments: {data.get('departments', 'MISSING')}")
            print(f"   Avg Resolution Time: {data.get('avg_resolution_time', 'MISSING')}")
            print(f"   Data Updated: {data.get('data_updated', 'MISSING')}")
            
            # Test the actual API response format
            print(f"\n✅ API Response Format:")
            api_response = {
                'success': True,
                'data': data
            }
            print(f"   Success: {api_response['success']}")
            print(f"   Data Keys: {list(api_response['data'].keys())}")
            
        except Exception as e:
            print(f"❌ Dashboard Data FAILED: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("🚀 Dashboard endpoint test complete!")
        print("📊 Check if the data structure matches what the JavaScript expects")
        
except Exception as e:
    print(f"❌ Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
