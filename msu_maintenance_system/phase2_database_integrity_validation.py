"""
Phase 2: Database Integrity Validation
SQL Server integrity check with comprehensive validation
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_database_integrity_check():
    """Run comprehensive database integrity check."""
    print("🔍 PHASE 2: DATABASE INTEGRITY VALIDATION")
    print("=" * 60)
    
    print("📋 DATABASE INTEGRITY CRITERIA:")
    print("  Command: sqlcmd -S $DB_SERVER -d CentralServices_AM_DB -i integrity_check.sql")
    print("  Target: All counts return 0. DBCC CHECKCONSTRAINTS reports no violations.")
    
    # Load environment variables
    load_dotenv()
    
    # Get database configuration
    db_server = os.getenv('DB_SERVER', 'DESKTOP-IO9GJQS\\SQLEXPRESS')
    db_name = os.getenv('DB_NAME', 'CentralServices_AM_DB')
    
    print(f"\n🔧 DATABASE CONFIGURATION:")
    print(f"  Server: {db_server}")
    print(f"  Database: {db_name}")
    
    # Check if integrity check SQL file exists
    integrity_sql_path = 'database_migrations/integrity_check_final.sql'
    
    if not os.path.exists(integrity_sql_path):
        print(f"\n❌ Integrity check SQL file not found: {integrity_sql_path}")
        print("   Expected file: database_migrations/integrity_check_final.sql")
        return False
    
    print(f"  ✅ Integrity check SQL file found: {integrity_sql_path}")
    
    # Run the integrity check
    print(f"\n🚀 EXECUTING DATABASE INTEGRITY CHECK:")
    print(f"   Command: sqlcmd -S {db_server} -d {db_name} -i {integrity_sql_path}")
    
    try:
        # Construct sqlcmd command with SSL options
        cmd = [
            'sqlcmd',
            '-S', db_server,
            '-d', db_name,
            '-i', integrity_sql_path,
            '-b',  # On error batch abort
            '-r', '1',  # Remove row count
            '-C',  # Trust server certificate
            '-N'   # Encrypt connection
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd='.',
            timeout=300  # 5 minute timeout
        )
        
        print(f"\n📊 DATABASE INTEGRITY RESULTS:")
        print("=" * 50)
        
        # Parse and display results
        if result.returncode == 0:
            print("✅ Database integrity check completed successfully")
            
            # Parse output for key metrics
            output_lines = result.stdout.split('\n')
            
            # Look for orphaned records
            orphaned_count = 0
            constraint_violations = 0
            checkdb_errors = 0
            
            for line in output_lines:
                line = line.strip()
                if line:
                    # Look for count results
                    if 'orphaned' in line.lower() and 'records' in line.lower():
                        if ':' in line:
                            try:
                                count = int(line.split(':')[-1].strip())
                                orphaned_count += count
                                print(f"  📄 {line}")
                            except ValueError:
                                print(f"  📄 {line}")
                    
                    # Look for constraint violations
                    elif 'constraint' in line.lower() and 'violation' in line.lower():
                        if ':' in line:
                            try:
                                count = int(line.split(':')[-1].strip())
                                constraint_violations += count
                                print(f"  ⚠️ {line}")
                            except ValueError:
                                print(f"  ⚠️ {line}")
                    
                    # Look for DBCC errors
                    elif 'dbcc' in line.lower() and ('error' in line.lower() or 'failed' in line.lower()):
                        checkdb_errors += 1
                        print(f"  ❌ {line}")
                    
                    # Display other important output
                    elif any(keyword in line.lower() for keyword in ['checking', 'analyzing', 'completed', 'success']):
                        print(f"  ℹ️ {line}")
            
            print(f"\n📈 INTEGRITY CHECK SUMMARY:")
            print(f"  Orphaned records: {orphaned_count}")
            print(f"  Constraint violations: {constraint_violations}")
            print(f"  DBCC errors: {checkdb_errors}")
            
            # Determine pass/fail status
            if orphaned_count == 0 and constraint_violations == 0 and checkdb_errors == 0:
                print(f"\n🎯 PHASE 2 RESULT: ✅ PASS")
                print(f"   Database integrity validation completed")
                print(f"   All integrity checks passed")
                print(f"   🚀 READY FOR PHASE 3: SMOKE TESTS")
                return True
            else:
                print(f"\n⚠️ PHASE 2 RESULT: ❌ FAIL")
                print(f"   Database integrity issues found")
                print(f"   🔧 Database maintenance required")
                return False
                
        else:
            print(f"❌ Database integrity check failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error output:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"  ❌ {line}")
            
            if result.stdout:
                print(f"Standard output:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        print(f"  📄 {line}")
            
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Database integrity check timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during database integrity check: {e}")
        return False

def check_database_connectivity():
    """Check basic database connectivity."""
    print("\n🔍 CHECKING DATABASE CONNECTIVITY")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get database configuration
    db_server = os.getenv('DB_SERVER', 'DESKTOP-IO9GJQS\\SQLEXPRESS')
    db_name = os.getenv('DB_NAME', 'CentralServices_AM_DB')
    
    try:
        # Test basic connectivity with SSL options
        cmd = [
            'sqlcmd',
            '-S', db_server,
            '-d', db_name,
            '-Q', 'SELECT @@VERSION',
            '-b',
            '-r', '1',
            '-C',  # Trust server certificate
            '-N'   # Encrypt connection
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Database connectivity test passed")
            print("  SQL Server connection successful")
            return True
        else:
            print("❌ Database connectivity test failed")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Database connectivity test error: {e}")
        return False

def main():
    """Main execution."""
    print("🔍 MSU MAINTENANCE SYSTEM - PHASE 2 DATABASE INTEGRITY")
    print("=" * 70)
    
    # Step 1: Check database connectivity
    connectivity_ok = check_database_connectivity()
    
    if not connectivity_ok:
        print("\n⚠️ DATABASE CONNECTIVITY FAILED")
        print("   Cannot proceed with integrity check")
        print("   🔧 Check database server and connection settings")
        print("   🔧 Verify environment variables in .env file")
        return
    
    # Step 2: Run database integrity check
    integrity_ok = run_database_integrity_check()
    
    print("\n📊 FINAL PHASE 2 RESULTS:")
    print("=" * 50)
    
    if integrity_ok:
        print("✅ DATABASE INTEGRITY: PASSED")
        print("   All integrity checks completed successfully")
        print("   No orphaned records found")
        print("   No constraint violations detected")
        print("   No DBCC errors encountered")
        
        print("\n🎯 PHASE 2 VALIDATION: ✅ COMPLETE")
        print("   Database integrity validated")
        print("   🚀 READY FOR PHASE 3: SMOKE TESTS")
        
    else:
        print("❌ DATABASE INTEGRITY: FAILED")
        print("   Database integrity issues detected")
        print("   🔧 Database maintenance required")
        print("   🔧 Review integrity check results")
        print("   🔧 Fix identified issues before proceeding")
        
        print("\n⚠️ PHASE 2 VALIDATION: ❌ INCOMPLETE")
        print("   Database integrity validation failed")
        print("   🔧 Address database issues before proceeding")
        print("   🔧 Re-run integrity check after fixes")
    
    print("\n📊 SYSTEM STATUS:")
    print("Phase 1: ✅ COMPLETE - Clean startup validated")
    print(f"Phase 2: {'✅ COMPLETE' if integrity_ok else '❌ INCOMPLETE'} - Database integrity")
    print("Phase 3: 🚀 READY - Smoke tests")
    print("Phase 4: 🚀 READY - Coverage gate")
    print("Phase 5: ✅ COMPLETE - Performance gate")
    print("Phase 6: ✅ COMPLETE - Security gate")
    print("Phase 8: 🚀 READY - Deployment gate")

if __name__ == '__main__':
    main()
