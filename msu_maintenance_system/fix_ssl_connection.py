"""
SSL Certificate Fix for SQL Server Connection
Disables SSL encryption and trusts server certificate
"""

import os
import sys

# Force environment variables
os.environ['SECRET_KEY'] = 'test-key-123456789012345678901234567890'
os.environ['DB_SERVER'] = 'DESKTOP-IO9GJQS\\SQLEXPRESS'
os.environ['DB_NAME'] = 'CentralServices_AM_DB'
os.environ['DB_USER'] = ''
os.environ['DB_PASSWORD'] = ''

# Test database connection with SSL disabled
import pyodbc

try:
    # Test connection with SSL disabled
    conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS;DATABASE=CentralServices_AM_DB;Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_requests")
    count = cursor.fetchone()[0]
    print(f"✅ SSL-disabled Connection Test SUCCESS: {count} job requests found")
    conn.close()
    
    # Test SQLAlchemy connection with SSL disabled
    from sqlalchemy import create_engine, text
    engine = create_engine(
        "mssql+pyodbc://@DESKTOP-IO9GJQS\\SQLEXPRESS/CentralServices_AM_DB"
        "?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&Encrypt=no&TrustServerCertificate=yes"
    )
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM job_requests"))
        count = result.scalar()
        print(f"✅ SQLAlchemy SSL-disabled Connection SUCCESS: {count} job requests found")
        
        result = connection.execute(text("SELECT COUNT(*) FROM vw_job_analytics"))
        analytics_count = result.scalar()
        print(f"✅ Analytics View SUCCESS: {analytics_count} records found")
        
    print("\n🎉 SSL certificate issue resolved!")
    print("🚀 Starting application with SSL disabled...")
    
    # Now start the Flask app
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        from app.extensions import db
        result = db.session.execute(text("SELECT COUNT(*) FROM job_requests"))
        count = result.scalar()
        print(f"✅ Flask App SSL-disabled Connection SUCCESS: {count} job requests found")
    
    print("✅ All database connections working with SSL disabled!")
    print("🚀 Application ready to start!")
    
except Exception as e:
    print(f"❌ SSL-disabled Database Connection FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
