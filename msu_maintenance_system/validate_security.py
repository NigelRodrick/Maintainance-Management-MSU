#!/usr/bin/env python3
import subprocess
import sys

def validate_security():
    print("Running security validation...")
    
    # Run Bandit
    bandit_result = subprocess.run(['bandit', '-r', 'app/', '-f', 'json'], capture_output=True, text=True)
    print(f"Bandit result: {bandit_result.returncode}")
    
    # Run Safety
    safety_result = subprocess.run(['safety', 'check', '-r', 'requirements.txt'], capture_output=True, text=True)
    print(f"Safety result: {safety_result.returncode}")
    
    if bandit_result.returncode == 0 and safety_result.returncode == 0:
        print("SECURITY VALIDATION: PASSED")
        return True
    else:
        print("SECURITY VALIDATION: FAILED")
        return False

if __name__ == '__main__':
    success = validate_security()
    sys.exit(0 if success else 1)
