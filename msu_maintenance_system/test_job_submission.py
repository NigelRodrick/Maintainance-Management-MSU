"""
Test Job Submission Fix
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
    from app.models import JobRequest, User
    from app.classification_service import classify_request
    
    # Create app and test job submission
    app = create_app('development')
    
    with app.app_context():
        # Get a test user
        test_user = User.query.first()
        if not test_user:
            print("❌ No users found in database")
            sys.exit(1)
        
        print(f"✅ Test User: {test_user.email} (ID: {test_user.id})")
        
        # Test classification
        test_description = "The air conditioner in room 201 is not working properly"
        category, priority = classify_request(test_description)
        print(f"✅ Classification: {category} - {priority}")
        
        # Test job creation
        try:
            new_job = JobRequest(
                department="ICT Department",
                description=test_description,
                category=category,
                priority=priority,
                status='PENDING',
                submitted_by=test_user.id
            )
            
            db.session.add(new_job)
            db.session.commit()
            
            print(f"✅ Job Created Successfully: ID {new_job.id}")
            print(f"   Department: {new_job.department}")
            print(f"   Category: {new_job.category}")
            print(f"   Priority: {new_job.priority}")
            print(f"   Status: {new_job.status}")
            
            # Don't access relationships - just clean up directly
            db.session.delete(new_job)
            db.session.commit()
            print("✅ Test job cleaned up")
            
        except Exception as e:
            print(f"❌ Job Creation FAILED: {e}")
            db.session.rollback()
            sys.exit(1)
        
        print("\n🎉 Job submission should be working!")
        print("🚀 Try submitting a request via the web form")
        
except Exception as e:
    print(f"❌ Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
