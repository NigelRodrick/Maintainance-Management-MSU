
# Secure subprocess execution without shell=True
import shlex
import logging

logger = logging.getLogger(__name__)

def safe_subprocess_execute(command_list, timeout=3600):
    """Execute subprocess safely without shell=True."""
    try:
        # Validate command list
        if not isinstance(command_list, list):
            raise ValueError("Command must be a list")
        
        # Validate each command component
        for cmd_part in command_list:
            if not isinstance(cmd_part, str):
                raise ValueError("All command parts must be strings")
            
            # Check for dangerous patterns
            dangerous_patterns = ['&&', '||', ';', '`', '$', '|']
            if any(pattern in cmd_part for pattern in dangerous_patterns):
                logger.warning(f"Potentially dangerous command pattern detected: {cmd_part}")
        
        # Execute without shell=True
        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        
        logger.info(f"Command executed successfully: {' '.join(command_list)}")
        return result
        
    except subprocess.TimeoutExpired:
        logger.error("Command execution timed out")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Command execution failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during command execution: {e}")
        raise

# Example usage in backup function
def secure_backup_function(backup_path, backup_type='full'):
    """Secure backup function implementation."""
    try:
        # Validate backup path
        if not os.path.exists(backup_path):
            raise ValueError(f"Backup path does not exist: {backup_path}")
        
        # Validate backup type
        if backup_type not in ['full', 'incremental', 'database']:
            raise ValueError(f"Invalid backup type: {backup_type}")
        
        # Construct safe command list
        if backup_type == 'full':
            command_list = [
                'pg_dump',
                '--host=localhost',
                '--username=postgres',
                '--no-password',
                '--format=custom',
                '--compress=9',
                backup_path
            ]
        elif backup_type == 'database':
            command_list = [
                'pg_dump',
                '--host=localhost',
                '--username=postgres',
                '--no-password',
                '--data-only',
                '--format=custom',
                backup_path
            ]
        else:  # incremental
            command_list = [
                'rsync',
                '--archive',
                '--compress',
                '/path/to/source',
                backup_path
            ]
        
        # Execute safely
        result = safe_subprocess_execute(command_list)
        
        print(f"Backup completed successfully: {backup_path}")
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

# Replace the vulnerable code in app/tasks.py
# OLD CODE (vulnerable):
# result = subprocess.run(backup_command, shell=True, capture_output=True, text=True)

# NEW CODE (secure):
# result = safe_subprocess_execute(command_list)
# OR: result = secure_backup_function(backup_path, backup_type)
