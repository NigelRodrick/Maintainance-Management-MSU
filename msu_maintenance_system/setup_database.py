"""
Database Connection Setup and Phase 2 Execution
Configures database connection and runs integrity validation
"""

import os
import subprocess
from dotenv import load_dotenv

def setup_database_connection():
    """Set up database connection using provided credentials."""
    print("🔗 Setting Up Database Connection")
    print("=" * 50)
    
    # Update .env file with the database connection details
    env_updates = {
        'DB_SERVER': 'DESKTOP-IO9GJQS\\SQLEXPRESS',
        'DB_NAME': 'CentralServices_AM_DB',
        'DB_AUTHENTICATION': 'windows authentication'
    }
    
    print("\n📝 Updating .env file with database connection:")
    for key, value in env_updates.items():
        print(f"  → {key}: {value}")
    
    # Read current .env
    env_file = '.env'
    env_lines = []
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add database configuration
    updated_lines = []
    db_config_added = False
    
    for line in env_lines:
        line = line.strip()
        if line.startswith('#') or '=' not in line:
            updated_lines.append(line)
            continue
        
        key, value = line.split('=', 1)
        key = key.strip()
        
        if key in env_updates:
            updated_lines.append(f"{key}={env_updates[key]}")
            db_config_added = True
            print(f"  ✅ Updated {key}")
        else:
            updated_lines.append(line)
    
    # Add missing database config if not already present
    if not db_config_added:
        updated_lines.extend([
            "",
            "# Database Configuration",
            f"DB_SERVER={env_updates['DB_SERVER']}",
            f"DB_NAME={env_updates['DB_NAME']}",
            f"DB_AUTHENTICATION={env_updates['DB_AUTHENTICATION']}",
            ""
        ])
        print("  ✅ Added database configuration")
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"\n✅ Database connection configured: {env_file}")
    return True

def run_integrity_check():
    """Run the database integrity check."""
    print("\n🔍 Running Phase 2: Database Integrity Check")
    print("=" * 50)
    
    try:
        # Load updated environment
        load_dotenv()
        
        db_server = os.environ.get("DB_SERVER")
        db_name = os.environ.get("DB_NAME")
        
        # Run the integrity check script
        cmd = [
            'sqlcmd', 
            f'-S{db_server}', 
            f'-d{db_name}', 
            '-E',  # Use Windows authentication
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
                print("\n⚠️ PHASE 2 RESULT: ❌ ISSUES FOUND")
                print("   Review the results above for details")
                return False
                
        else:
            print(f"❌ SQL command failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main execution function."""
    print("🔍 MSU Maintenance System - Database Setup & Integrity Check")
    print()
    
    # Step 1: Setup database connection
    if setup_database_connection():
        print("\n✅ Database connection setup completed")
        
        # Step 2: Run integrity check
        success = run_integrity_check()
        
        print("\n" + "=" * 50)
        print("📊 SUMMARY:")
        
        if success:
            print("🎯 SUCCESS: Database integrity validation completed")
            print("🚀 READY FOR PHASE 3: SMOKE TESTS")
            print("\nNext Steps:")
            print("→ Run smoke tests to validate application functionality")
            print("→ Test critical paths manually via browser")
            print("→ Proceed with Phase 4: Coverage gate")
        else:
            print("⚠️ ISSUES FOUND: Review database integrity results")
            print("→ Fix any constraint violations")
            print("→ Re-run integrity check after fixes")
    else:
        print("❌ Database setup failed")
        print("→ Check SQL Server Express configuration")
        print("→ Verify network connectivity to database server")

if __name__ == '__main__':
    main()
