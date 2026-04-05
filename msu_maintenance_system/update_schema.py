"""
Database Schema Update
Adds missing is_deleted columns to match current application expectations
"""

import os
import subprocess
from dotenv import load_dotenv

def update_database_schema():
    """Update database schema to add is_deleted columns where needed."""
    print("🔧 Updating Database Schema")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    db_server = os.environ.get('DB_SERVER', 'localhost')
    db_name = os.environ.get('DB_NAME', 'CentralServices_AM_DB')
    batch_file = 'update_schema_batch.sql'
    
    print(f"\n📝 Applying schema updates to {db_name}:")
    print(f"📄 Using batch file: {batch_file}")
    
    try:
        # Run the batch file
        cmd = [
            'sqlcmd', 
            f'-S{db_server}', 
            f'-d{db_name}', 
            '-E',  # Windows authentication
            '-N',  # Disable encryption/SSL
            '-i', batch_file
        ]
        
        print(f"\n🚀 Executing: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        print("\n📊 Schema Update Results:")
        print("=" * 40)
        
        if result.returncode == 0:
            print("✅ Schema update completed successfully")
            
            # Parse and display results
            output_lines = result.stdout.split('\n')
            
            for line in output_lines:
                line = line.strip()
                if line:
                    print(f"  {line}")
            
            # Look for completion message
            if 'Schema update completed' in result.stdout:
                print("\n🎯 PHASE 2 RESULT: ✅ PASS")
                print("   All database schema updates applied")
                print("   🚀 READY FOR PHASE 3: SMOKE TESTS")
                return True
            else:
                print("\n⚠️ PHASE 2 RESULT: ⚠️ PARTIAL")
                print("   Review output above for issues")
                return False
                
        else:
            print(f"❌ Schema update failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error during schema update: {e}")
        return False

def run_integrity_check_after_update():
    """Run integrity check after schema update."""
    print("\n🔍 Running Integrity Check After Schema Update")
    print("=" * 50)
    
    try:
        load_dotenv()
        
        cmd = [
            'sqlcmd', 
            f'-S{os.environ.get("DB_SERVER")}', 
            f'-d{os.environ.get("DB_NAME")}', 
            '-E',  # Windows authentication
            '-N',  # Disable encryption/SSL
            '-C',  # Trust server certificate
            '-i', 'database_migrations/integrity_check.sql'
        ]
        
        print(f"\n🚀 Executing: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        print("\n📊 Integrity Check Results:")
        print("=" * 40)
        
        if result.returncode == 0:
            print("✅ SQL command executed successfully")
            
            # Parse and display results
            output_lines = result.stdout.split('\n')
            
            for line in output_lines:
                line = line.strip()
                if line:
                    print(f"  {line}")
            
            # Look for final result
            if 'ALL INTEGRITY CHECKS PASSED' in result.stdout:
                print("\n🎯 PHASE 2 RESULT: ✅ PASS")
                print("   All database integrity checks passed")
                print("   🚀 READY FOR PHASE 3: SMOKE TESTS")
                return True
            else:
                print("\n⚠️ PHASE 2 RESULT: ❌ ISSUES REMAIN")
                print("   Review detailed results above")
                return False
                
        else:
            print(f"❌ SQL command failed with exit code {result.returncode}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main execution."""
    print("🔍 MSU Maintenance System - Schema Update & Integrity Check")
    print()
    
    # Step 1: Update schema
    if update_database_schema():
        print("\n✅ Schema update completed")
        
        # Step 2: Run integrity check
        if run_integrity_check_after_update():
            print("\n🎯 READY FOR PHASE 3: SMOKE TESTS")
        else:
            print("\n⚠️ Schema update completed but integrity check failed")
            print("→ Review integrity check results")

if __name__ == '__main__':
    main()
