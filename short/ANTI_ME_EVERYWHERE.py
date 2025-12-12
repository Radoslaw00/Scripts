#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import sys

SCRIPT_NAME = "run_fast.py"

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

def remove_all_scripts():
    """Remove run_fast.py from all subdirectories."""
    current_dir = Path.cwd()
    
    print(f"Scanning for {SCRIPT_NAME} in all subdirectories...\n")
    
    removed_count = 0
    failed_count = 0
    
    for folder in get_all_subdirectories(current_dir):
        target = folder / SCRIPT_NAME
        if target.exists():
            try:
                target.unlink()
                print(f"  ✓ Removed: {folder.relative_to(current_dir)}/{SCRIPT_NAME}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Failed to remove from {folder.relative_to(current_dir)}: {e}")
                failed_count += 1
    
    print(f"\n=======================================")
    print(f"Removal complete!")
    print(f"  Removed: {removed_count}")
    if failed_count > 0:
        print(f"  Failed: {failed_count}")
    print(f"=======================================")

if __name__ == '__main__':
    try:
        remove_all_scripts()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
