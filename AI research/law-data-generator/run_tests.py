#!/usr/bin/env python3
"""
Simple test runner to identify any problematic test files.
"""
import subprocess
import os
import glob

def run_test_file(test_file):
    """Run a single test file and return the result."""
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', test_file, '-v'
        ], capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Test timed out"
    except Exception as e:
        return False, "", str(e)

def main():
    # Find all test files
    test_files = glob.glob('tests/test_*.py')
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  {test_file}")
    
    print("\nRunning tests...")
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        print(f"\nTesting {test_file}...")
        success, stdout, stderr = run_test_file(test_file)
        
        if success:
            print(f"  ✓ PASSED")
            passed += 1
        else:
            print(f"  ✗ FAILED")
            failed += 1
            if stderr:
                print(f"    Error: {stderr[:200]}...")
    
    print(f"\nSummary: {passed} passed, {failed} failed")
    
    # Check if lawdata is clean
    lawdata_contents = os.listdir('lawdata') if os.path.exists('lawdata') else []
    if lawdata_contents:
        print(f"\nWARNING: lawdata/ is not empty: {lawdata_contents}")
    else:
        print("\n✓ lawdata/ is clean (test isolation working)")

if __name__ == '__main__':
    main()
