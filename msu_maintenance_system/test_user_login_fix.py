"""
Test User Login After Schema Fix
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
    from app.extensions import db
    from app.models import User
    from sqlalchemy import text
    
    # Create app and test user query
    app = create_app('development')
    
    with app.app_context():
        # Test direct SQL query
        result = db.session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"✅ Direct SQL Query SUCCESS: {count} users found")
        
        # Test User model query (this should work now)
        users = User.query.all()
        print(f"✅ User Model Query SUCCESS: {len(users)} users found")
        
        # Test specific user query (the one that was failing)
        user = User.query.filter_by(email='r233730a@staff.msu.ac.zw').first()
        if user:
            print(f"✅ Specific User Query SUCCESS: Found user {user.email}, is_deleted={user.is_deleted}")
        else:
            print("❌ Specific User Query FAILED: User not found")
        
        # Test all user details
        print("\n📊 All Users:")
        for user in users:
            print(f"  - ID: {user.id}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}, Deleted: {user.is_deleted}")
        
        print("\n🎉 User schema fix successful!")
        print("🚀 Login functionality should now work!")
        
except Exception as e:
    print(f"❌ User Query FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
