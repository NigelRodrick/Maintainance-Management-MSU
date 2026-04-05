"""
Test Analytics Module - Simple test without full Flask app
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['SECRET_KEY'] = 'test-key-123456789012345678901234567890'
os.environ['DB_SERVER'] = 'DESKTOP-IO9GJQS\\SQLEXPRESS'
os.environ['DB_NAME'] = 'CentralServices_AM_DB'

# Test SQL connection
import pyodbc

try:
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={os.environ['DB_SERVER']};DATABASE={os.environ['DB_NAME']};Trusted_Connection=yes;Encrypt=no;"
    conn = pyodbc.connect(conn_str)
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vw_job_analytics")
    count = cursor.fetchone()[0]
    
    print(f"Analytics view test: SUCCESS")
    print(f"Records in vw_job_analytics: {count}")
    
    # Test analytics module
    from app.analytics import AnalyticsModule
    analytics = AnalyticsModule()
    data = analytics.get_dashboard_data()
    
    print(f"Analytics module test: SUCCESS")
    print(f"Data keys: {list(data.keys())}")
    
    conn.close()
    
except Exception as e:
    print(f"Test failed: {e}")
