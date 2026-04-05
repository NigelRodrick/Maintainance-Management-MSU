"""
Test Database Connection
"""

import pyodbc
import os

# Test different connection methods
print("Testing database connections...")

# Method 1: Trusted Connection (Windows Authentication)
try:
    conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS;DATABASE=CentralServices_AM_DB;Trusted_Connection=yes;Encrypt=no;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_requests")
    count = cursor.fetchone()[0]
    print(f"✅ Trusted Connection SUCCESS: {count} job requests found")
    conn.close()
except Exception as e:
    print(f"❌ Trusted Connection FAILED: {e}")

# Method 2: SQL Server Authentication
try:
    conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS;DATABASE=CentralServices_AM_DB;UID=sa;PWD=YourStrong!Passw0rd;Encrypt=no;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_requests")
    count = cursor.fetchone()[0]
    print(f"✅ SQL Server Authentication SUCCESS: {count} job requests found")
    conn.close()
except Exception as e:
    print(f"❌ SQL Server Authentication FAILED: {e}")

# Method 3: Test with existing user
try:
    conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS;DATABASE=CentralServices_AM_DB;UID=admin;PWD=admin123;Encrypt=no;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_requests")
    count = cursor.fetchone()[0]
    print(f"✅ Admin User SUCCESS: {count} job requests found")
    conn.close()
except Exception as e:
    print(f"❌ Admin User FAILED: {e}")

print("\nDatabase connection test completed.")
