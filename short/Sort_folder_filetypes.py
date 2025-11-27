import os
import shutil
import json
from pathlib import Path

BACKUP_FILE = ".sort_backup.json"

def get_file_extension(filename):
    """Extract file extension from filename."""
    if '.' not in filename:
        return "NO_EXTENSION"
    return filename.rsplit('.', 1)[-1].upper()

def sort_files():
    """Sort all files into folders based on their extensions."""
    base_dir = os.getcwd()
    movements = {}  # Track file movements for undo
    
    # Get all files in the base directory
    items = os.listdir(base_dir)
    
    for filename in items:
        filepath = os.path.join(base_dir, filename)
        
        # Skip directories and backup file
        if os.path.isdir(filepath) or filename == BACKUP_FILE:
            continue
        
        # Get the extension and create corresponding folder
        ext = get_file_extension(filename)
        ext_dir = os.path.join(base_dir, ext)
        
        # Create the extension folder if it doesn't exist
        os.makedirs(ext_dir, exist_ok=True)
        
        # Move the file
        dest_path = os.path.join(ext_dir, filename)
        if filepath != dest_path:
            shutil.move(filepath, dest_path)
            movements[dest_path] = filepath  # Store destination -> original path
    
    # Save backup for undo
    if movements:
        with open(os.path.join(base_dir, BACKUP_FILE), 'w') as f:
            json.dump(movements, f, indent=2)
        print(f"Sorted {len(movements)} file(s)!")
        return True
    else:
        print("No files to sort.")
        return False

if __name__ == "__main__":
    sort_files()