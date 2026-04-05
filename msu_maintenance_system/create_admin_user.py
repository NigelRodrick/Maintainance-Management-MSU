"""
Create Admin User Script
Creates an admin user with specified credentials
"""

import os
import sys
import pyodbc
from werkzeug.security import generate_password_hash
from datetime import datetime

# ENV guard - only allow execution in development
if os.environ.get('ENV') != 'development':
    print('ERROR: This script can only be run in development environment')
    print('Set ENV=development to proceed')
    sys.exit(1)

def create_admin_user():
    """Create admin user with specified credentials."""
    
    # Database connection
    conn_str = 'DRIVER={SQL Server};SERVER=DESKTOP-IO9GJQS\\SQLEXPRESS;DATABASE=CentralServices_AM_DB;Trusted_Connection=yes'
    
    # User credentials
    email = 'r233730a@staff.msu.ac.zw'
    password = '@r233730a'
    role = 'admin'
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print('🔐 Creating Admin User...')
        print(f'Email: {email}')
        print(f'Role: {role}')
        print()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM Users WHERE email = ?", email)
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f'⚠️  User {email} already exists with ID: {existing_user[0]}')
            
            # Update existing user to admin role
            cursor.execute("""
                UPDATE Users 
                SET role = ?, password_hash = ?, is_active = 1 
                WHERE email = ?
            """, role, generate_password_hash(password), email)
            
            print('✅ Existing user updated to admin role')
        else:
            # Create new user
            password_hash = generate_password_hash(password)
            
            cursor.execute("""
                INSERT INTO Users (email, password_hash, role, created_at, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, email, password_hash, role, datetime.now(), True)
            
            print('✅ New admin user created successfully')
        
        # Verify the user was created/updated
        cursor.execute("SELECT id, email, role, is_active FROM Users WHERE email = ?", email)
        user_info = cursor.fetchone()
        
        if user_info:
            print()
            print('📋 User Details:')
            print(f'  ID: {user_info[0]}')
            print(f'  Email: {user_info[1]}')
            print(f'  Role: {user_info[2]}')
            print(f'  Active: {user_info[3]}')
            print()
            print('🎯 Admin user is ready for login!')
        else:
            print('❌ Failed to verify user creation')
        
        conn.commit()
        conn.close()
        
        print('✅ Database connection closed')
        
    except Exception as e:
        print(f'❌ Error creating admin user: {str(e)}')
        if conn:
            conn.rollback()
            conn.close()

if __name__ == '__main__':
    create_admin_user()
