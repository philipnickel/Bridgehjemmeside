#!/usr/bin/env python
"""
Clean test runner for Bridge Club Management System
Provides cleaner, more readable test output
"""
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
import glob

def run_tests(test_module=None, verbosity=0):
    """Run Django tests with clean output formatting."""
    # Set up environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bridge_club_management.settings.local')

    # Build test labels to EXCLUDE legacy package tests under club_management/tests/
    labels = []
    project_root = Path(__file__).resolve().parent
    top_level_tests = sorted(glob.glob(str(project_root / 'club_management' / 'test_*.py')))
    if not test_module and top_level_tests:
        # Convert file paths to module labels, e.g., club_management/test_views.py -> club_management.test_views
        for test_file in top_level_tests:
            module_name = Path(test_file).stem
            labels.append(f'club_management.{module_name}')

    # Prepare command
    if test_module:
        cmd = [sys.executable, 'manage.py', 'test', test_module, f'--verbosity={verbosity}', '--keepdb']
        test_description = f"Running tests for {test_module}"
    elif labels:
        cmd = [sys.executable, 'manage.py', 'test', *labels, f'--verbosity={verbosity}', '--keepdb']
        test_description = "Running top-level app tests (excluding legacy package)"
    else:
        cmd = [sys.executable, 'manage.py', 'test', 'club_management', f'--verbosity={verbosity}', '--keepdb']
        test_description = "Running all app tests"

    # Print header
    print("=" * 60)
    print(f"🧪 {test_description}")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    # Run tests and capture output
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))

        # Parse output for clean display
        output_lines = result.stdout.split('\n')

        # Find the actual test results (skip migrations and setup)
        test_output = []
        capture_output = False

        for line in output_lines:
            # Start capturing after "System check"
            if "System check identified no issues" in line:
                capture_output = True
                continue
            elif "Creating test database" in line:
                capture_output = True
                continue

            if capture_output:
                # Skip empty lines and database creation messages
                if line.strip() and not line.startswith("Operations to perform:") and \
                   not line.startswith("Synchronizing apps") and \
                   not line.startswith("Creating tables") and \
                   not line.startswith("Running deferred SQL") and \
                   not line.startswith("Running migrations:") and \
                   not line.startswith("Applying ") and \
                   not line.startswith("Destroying test database"):
                    test_output.append(line)

        # Display results
        if test_output:
            for line in test_output:
                if line.strip():
                    print(line)
        else:
            # Fallback
            relevant_lines = [line for line in output_lines if line.strip() and 
                            ("Ran " in line or "OK" == line.strip() or "FAILED" in line)]
            print('\n'.join(relevant_lines[-5:]))

        # Show stderr only if there are actual errors (not just test output)
        if result.stderr and result.stderr.strip() and "ERROR" in result.stderr.upper():
            print(f"\n🚨 Errors:")
            print(result.stderr)

        # Print footer
        print("\n" + "=" * 60)
        print(f"✅ Tests completed at: {datetime.now().strftime('%H:%M:%S')}" )
        if result.returncode == 0:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  Tests finished with return code: {result.returncode}")
        print("=" * 60)

        return result.returncode

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    # Handle command line arguments
    test_module = sys.argv[1] if len(sys.argv) > 1 else None
    verbosity = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    sys.exit(run_tests(test_module, verbosity))