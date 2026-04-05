"""
Comprehensive Model Test After Schema Fixes
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
    from app.models import User, JobRequest, Assignment, Material
    from sqlalchemy import text
    
    # Create app and test all models
    app = create_app('development')
    
    with app.app_context():
        print("🔍 Testing all SQLAlchemy models...")
        
        # Test User model
        users = User.query.all()
        print(f"✅ User Model: {len(users)} users found")
        
        # Test JobRequest model
        job_requests = JobRequest.query.all()
        print(f"✅ JobRequest Model: {len(job_requests)} job requests found")
        
        # Test Assignment model
        assignments = Assignment.query.all()
        print(f"✅ Assignment Model: {len(assignments)} assignments found")
        
        # Test Material model
        materials = Material.query.all()
        print(f"✅ Material Model: {len(materials)} materials found")
        
        # Test relationships
        if job_requests:
            first_job = job_requests[0]
            print(f"✅ Relationship Test: Job {first_job.id} submitted by {first_job.submitter.email if first_job.submitter else 'Unknown'}")
        
        # Test specific user query (the original failing query)
        user = User.query.filter_by(email='r233730a@staff.msu.ac.zw').first()
        if user:
            print(f"✅ Login Query Test: User {user.email} found, is_deleted={user.is_deleted}")
        
        # Test job requests with is_deleted
        active_jobs = JobRequest.query.filter_by(is_deleted=False).all()
        print(f"✅ Active Jobs: {len(active_jobs)} active job requests")
        
        print("\n🎉 All models working correctly!")
        print("🚀 Login functionality and all CRUD operations should work!")
        
        # Show sample data
        print("\n📊 Sample Data:")
        print(f"Users: {len(users)} total")
        print(f"Job Requests: {len(job_requests)} total")
        print(f"Assignments: {len(assignments)} total")
        print(f"Materials: {len(materials)} total")
        
except Exception as e:
    print(f"❌ Model Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
