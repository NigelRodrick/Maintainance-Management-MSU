"""
Test SQL Server Authentication with New Credentials
"""

import os
import sys

# Set environment variables with new SQL Server credentials
os.environ['SECRET_KEY'] = 'test-key-123456789012345678901234567890'
os.environ['DB_SERVER'] = 'DESKTOP-IO9GJQS\\SQLEXPRESS'
os.environ['DB_NAME'] = 'CentralServices_AM_DB'
os.environ['DB_USER'] = 'munyamash'
os.environ['DB_PASSWORD'] = 'nowayout'

# Test SQL Server authentication
import pyodbc

try:
    # Test SQL Server authentication
    conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS;DATABASE=CentralServices_AM_DB;UID=munyamash;PWD=nowayout;Encrypt=no;TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_requests")
    count = cursor.fetchone()[0]
    print(f"✅ SQL Server Authentication Test SUCCESS: {count} job requests found")
    conn.close()
    
    # Test SQLAlchemy connection with SQL Server authentication
    from sqlalchemy import create_engine, text
    engine = create_engine(
        "mssql+pyodbc://munyamash:nowayout@DESKTOP-IO9GJQS\\SQLEXPRESS/CentralServices_AM_DB"
        "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no&TrustServerCertificate=yes"
    )
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM job_requests"))
        count = result.scalar()
        print(f"✅ SQLAlchemy SQL Server Authentication SUCCESS: {count} job requests found")
        
        result = connection.execute(text("SELECT COUNT(*) FROM vw_job_analytics"))
        analytics_count = result.scalar()
        print(f"✅ Analytics View SUCCESS: {analytics_count} records found")
        
    print("\n🎉 SQL Server authentication working!")
    print("🚀 Starting application with SQL Server authentication...")
    
    # Now start the Flask app
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        from app.extensions import db
        result = db.session.execute(text("SELECT COUNT(*) FROM job_requests"))
        count = result.scalar()
        print(f"✅ Flask App SQL Server Authentication SUCCESS: {count} job requests found")
    
    print("✅ All database connections working with SQL Server authentication!")
    print("🚀 Application ready to start!")
    
except Exception as e:
    print(f"❌ SQL Server Authentication FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
