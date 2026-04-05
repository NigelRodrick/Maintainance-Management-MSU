"""
CSAM Database Cleanup Script
Focused cleanup for orphaned job_requests and user roles
"""

import os
import subprocess
from dotenv import load_dotenv

def run_sql_cmd(command, desc):
    """Execute SQL command."""
    print(f"🔧 {desc}")
    try:
        load_dotenv()
        db_server = os.getenv('DB_SERVER', 'DESKTOP-IO9GJQS\\SQLEXPRESS')
        db_name = os.getenv('DB_NAME', 'CentralServices_AM_DB')
        
        cmd = ['sqlcmd', '-S', db_server, '-d', db_name, '-Q', command, '-b', '-r', '1', '-C', '-N']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            return True
        else:
            print(f"❌ FAILED: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🔧 CSAM DATABASE CLEANUP")
    print("=" * 40)
    
    print("ISSUES TO FIX:")
    print("1. ORPHANED JOB_REQUESTS")
    print("2. INVALID USER ROLES")
    
    # Step 1: Backup
    print("\n📦 STEP 1: BACKUP")
    backup_cmd = "BACKUP DATABASE CentralServices_AM_DB TO DISK = 'C:\\backup\\CSAM_cleanup.bak' WITH INIT"
    run_sql_cmd(backup_cmd, "Creating backup")
    
    # Step 2: Fix orphaned job_requests
    print("\n🗑️ STEP 2: CLEAN ORPHANED JOB_REQUESTS")
    
    # Count orphans first
    count_cmd = "SELECT COUNT(*) FROM job_requests jr LEFT JOIN users u ON jr.submitted_by = u.id WHERE u.id IS NULL"
    run_sql_cmd(count_cmd, "Counting orphaned records")
    
    # Delete orphans
    delete_cmd = "DELETE jr FROM job_requests jr LEFT JOIN users u ON jr.submitted_by = u.id WHERE u.id IS NULL"
    run_sql_cmd(delete_cmd, "Deleting orphaned records")
    
    # Verify cleanup
    verify_cmd = "SELECT COUNT(*) FROM job_requests jr LEFT JOIN users u ON jr.submitted_by = u.id WHERE u.id IS NULL"
    run_sql_cmd(verify_cmd, "Verifying cleanup")
    
    # Step 3: Fix user roles
    print("\n👤 STEP 3: FIX USER ROLES")
    
    # Count invalid roles
    role_count_cmd = "SELECT COUNT(*) FROM users WHERE role NOT IN ('admin','supervisor','staff','maintenance') AND role IS NOT NULL"
    run_sql_cmd(role_count_cmd, "Counting invalid roles")
    
    # Fix invalid roles
    role_fix_cmd = "UPDATE users SET role = 'staff' WHERE role NOT IN ('admin','supervisor','staff','maintenance') AND role IS NOT NULL"
    run_sql_cmd(role_fix_cmd, "Fixing invalid roles")
    
    # Verify role fix
    role_verify_cmd = "SELECT COUNT(*) FROM users WHERE role NOT IN ('admin','supervisor','staff','maintenance') AND role IS NOT NULL"
    run_sql_cmd(role_verify_cmd, "Verifying role fix")
    
    print("\n✅ CLEANUP COMPLETE")
    print("🔍 Re-run integrity check to verify")

if __name__ == '__main__':
    main()
