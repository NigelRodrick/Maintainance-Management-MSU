
"""
Fix for subprocess shell=True vulnerability in app/tasks.py:391
"""

import subprocess
import shlex

def safe_backup_command(backup_path, backup_type='full'):
    """Safe backup execution without shell=True."""
    try:
        # Validate backup path
        if not os.path.exists(backup_path):
            raise ValueError(f"Backup path does not exist: {backup_path}")
        
        # Validate backup type
        if backup_type not in ['full', 'incremental', 'database']:
            raise ValueError(f"Invalid backup type: {backup_type}")
        
        # Construct safe command
        if backup_type == 'full':
            cmd = [
                'pg_dump',
                '--host=localhost',
                '--username=postgres',
                '--no-password',
                '--format=custom',
                '--compress=9',
                backup_path
            ]
        elif backup_type == 'database':
            cmd = [
                'pg_dump',
                '--host=localhost',
                '--username=postgres',
                '--no-password',
                '--data-only',
                '--format=custom',
                backup_path
            ]
        else:  # incremental
            cmd = [
                'rsync',
                '--archive',
                '--compress',
                '/path/to/source',
                backup_path
            ]
        
        # Execute without shell=True
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=3600  # 1 hour timeout
        )
        
        print(f"Backup completed successfully: {backup_path}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Backup timed out after 1 hour")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during backup: {e}")
        return False

# Replace the vulnerable code in app/tasks.py
# OLD CODE (vulnerable):
# result = subprocess.run(backup_command, shell=True, capture_output=True, text=True)

# NEW CODE (secure):
result = safe_backup_command(backup_path, backup_type)
