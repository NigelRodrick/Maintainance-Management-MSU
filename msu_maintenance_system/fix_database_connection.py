"""
Comprehensive Database Connection Fix
Forces Windows Authentication and prevents SQL Server authentication
"""

import os
import sys

# Force environment variables to prevent SQL Server authentication
os.environ['SECRET_KEY'] = 'test-key-123456789012345678901234567890'
os.environ['DB_SERVER'] = 'DESKTOP-IO9GJQS\\SQLEXPRESS'
os.environ['DB_NAME'] = 'CentralServices_AM_DB'
os.environ['DB_USER'] = ''  # Force empty to prevent SQL Server auth
os.environ['DB_PASSWORD'] = ''  # Force empty to prevent SQL Server auth

# Test database connection with Windows authentication
import pyodbc

try:
    # Test Windows Trusted Connection
    conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS;DATABASE=CentralServices_AM_DB;Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_requests")
    count = cursor.fetchone()[0]
    print(f"✅ Windows Authentication Test SUCCESS: {count} job requests found")
    conn.close()
    
    # Test SQLAlchemy connection
    from sqlalchemy import create_engine, text
    engine = create_engine(
        "mssql+pyodbc://@DESKTOP-IO9GJQS\\SQLEXPRESS/CentralServices_AM_DB"
        "?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&Encrypt=no&TrustServerCertificate=yes"
    )
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM job_requests"))
        count = result.scalar()
        print(f"✅ SQLAlchemy Windows Authentication SUCCESS: {count} job requests found")
        
        result = connection.execute(text("SELECT COUNT(*) FROM vw_job_analytics"))
        analytics_count = result.scalar()
        print(f"✅ Analytics View SUCCESS: {analytics_count} records found")
        
    print("\n🎉 Database connection tests passed!")
    print("🚀 Starting application with Windows authentication...")
    
    # Now start the Flask app
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        from app.extensions import db
        result = db.session.execute(text("SELECT COUNT(*) FROM job_requests"))
        count = result.scalar()
        print(f"✅ Flask App Database Connection SUCCESS: {count} job requests found")
    
    print("✅ All database connections working correctly!")
    print("🚀 Application ready to start!")
    
except Exception as e:
    print(f"❌ Database Connection FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
