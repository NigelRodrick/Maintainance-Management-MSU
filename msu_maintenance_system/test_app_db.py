"""
Test Application Database Connection
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['SECRET_KEY'] = 'test-key-123456789012345678901234567890'
os.environ['DB_SERVER'] = 'DESKTOP-IO9GJQS\\SQLEXPRESS'
os.environ['DB_NAME'] = 'CentralServices_AM_DB'

try:
    from app import create_app
    from app.extensions import db
    from sqlalchemy import text
    
    # Create app and test database connection
    app = create_app('development')
    
    with app.app_context():
        # Test database connection
        result = db.session.execute(text("SELECT COUNT(*) FROM job_requests"))
        count = result.scalar()
        print(f"✅ Database Connection SUCCESS: {count} job requests found")
        
        # Test analytics view
        result = db.session.execute(text("SELECT COUNT(*) FROM vw_job_analytics"))
        analytics_count = result.scalar()
        print(f"✅ Analytics View SUCCESS: {analytics_count} records found")
        
        # Test user table
        result = db.session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"✅ User Table SUCCESS: {user_count} users found")
        
        print("\n🎉 All database connections working correctly!")
        print("🚀 Application is ready for beta testing!")
        
except Exception as e:
    print(f"❌ Database Connection FAILED: {e}")
    import traceback
    traceback.print_exc()
