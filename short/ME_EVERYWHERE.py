#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import subprocess
import time
import sys

SCRIPT_NAME = "run_fast.py"
BAT_NAME = "x_fast.bat"
CLEANUP_FLAG = "--cleanup"

def get_all_subdirectories(start_path=None):
    """Get all subdirectories recursively."""
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)
    
    directories = []
    for root, dirs, files in os.walk(start_path):
        for d in dirs:
            directories.append(Path(root) / d)
    
    return directories

def copy_script_to_folder(folder_path, script_path):
    """Copy run_fast.py to a folder."""
    try:
        destination = folder_path / SCRIPT_NAME
        if not destination.exists():
            shutil.copy(script_path, destination)
            return True
    except Exception:
        pass
    return False

def deploy_everywhere(cleanup=False):
    """Deploy or cleanup run_fast.py in all subdirectories."""
    current_dir = Path.cwd()
    script_path = current_dir / SCRIPT_NAME
    
    if not script_path.exists():
        print(f"Error: {SCRIPT_NAME} not found in current directory!")
        return
    
    if cleanup:
        print(f"Removing {SCRIPT_NAME} from all folders...\n")
        
        removed_count = 0
        for folder in get_all_subdirectories(current_dir):
            target = folder / SCRIPT_NAME
            if target.exists():
                try:
                    target.unlink()
                    print(f"  ✓ Removed from: {folder.relative_to(current_dir)}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ✗ Failed to remove from {folder.relative_to(current_dir)}: {e}")
        
        print(f"\nCleanup complete! Removed from {removed_count} folder(s)")
    else:
        print(f"Deploying {SCRIPT_NAME} to all folders...\n")
        
        deployed_count = 0
        for folder in get_all_subdirectories(current_dir):
            if copy_script_to_folder(folder, script_path):
                print(f"  ✓ Deployed to: {folder.relative_to(current_dir)}")
                deployed_count += 1
        
        print(f"\nDeployed to {deployed_count} folder(s)")

def run_in_sequence():
    """Run run_fast.py in all subdirectories that have it."""
    current_dir = Path.cwd()
    
    print(f"Running {SCRIPT_NAME} in all folders in sequence...\n")
    
    folders_with_script = []
    for folder in get_all_subdirectories(current_dir):
        if (folder / SCRIPT_NAME).exists():
            folders_with_script.append(folder)
    
    if not folders_with_script:
        print("No folders found with run_fast.py")
        return
    
    print(f"Found {len(folders_with_script)} folder(s) with {SCRIPT_NAME}\n")
    
    for idx, folder in enumerate(folders_with_script, 1):
        print(f"[{idx}/{len(folders_with_script)}] Processing: {folder.relative_to(current_dir)}")
        
        try:
            result = subprocess.run(
                [sys.executable, SCRIPT_NAME],
                cwd=str(folder),
                capture_output=True,
                timeout=300,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✓ Completed")
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            print(f"    {line}")
            else:
                print(f"  ✗ Failed")
                if result.stderr:
                    print(f"    Error: {result.stderr[:100]}")
            print()
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")

def show_help():
    """Show help message."""
    print("""
ME_EVERYWHERE.py - Deploy and run run_fast.py everywhere

Usage:
  python ME_EVERYWHERE.py                 # Deploy and run in sequence
  python ME_EVERYWHERE.py --run-only      # Only run in existing folders
  python ME_EVERYWHERE.py --deploy-only   # Only deploy, don't run
  python ME_EVERYWHERE.py --cleanup       # Remove all deployed copies
  python ME_EVERYWHERE.py --help          # Show this help

Options:
  --deploy-only      Copy run_fast.py to all subdirectories only
  --run-only         Run run_fast.py in all folders that already have it
  --cleanup          Remove all copied run_fast.py files from subdirectories
  --help             Show this help message
""")

if __name__ == '__main__':
    mode = "deploy_and_run"
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--help":
            show_help()
            sys.exit(0)
        elif arg == "--cleanup":
            deploy_everywhere(cleanup=True)
            sys.exit(0)
        elif arg == "--deploy-only":
            mode = "deploy_only"
        elif arg == "--run-only":
            mode = "run_only"
    
    if mode == "deploy_and_run":
        deploy_everywhere(cleanup=False)
        print()
        run_in_sequence()
    elif mode == "deploy_only":
        deploy_everywhere(cleanup=False)
    elif mode == "run_only":
        run_in_sequence()
    
    print("\nDone!")
