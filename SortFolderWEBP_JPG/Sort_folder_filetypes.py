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

def undo_sort():
    """Restore files to their original locations."""
    base_dir = os.getcwd()
    backup_path = os.path.join(base_dir, BACKUP_FILE)
    
    if not os.path.exists(backup_path):
        print("No backup found. Nothing to undo.")
        return False
    
    try:
        with open(backup_path, 'r') as f:
            movements = json.load(f)
        
        # Reverse the movements (move files back to original locations)
        for dest_path, original_path in movements.items():
            if os.path.exists(dest_path):
                shutil.move(dest_path, original_path)
        
        # Remove the backup file and empty extension folders
        os.remove(backup_path)
        
        # Remove empty directories
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and not os.listdir(item_path):
                os.rmdir(item_path)
        
        print(f"Undone! Restored {len(movements)} file(s) to original locations.")
        return True
    except Exception as e:
        print(f"Error during undo: {e}")
        return False

if __name__ == "__main__":
    while True:
        print("\n--- File Sorter ---")
        action = input("Sort files by type (s), Undo last sort (u), or Quit (q)? ").strip().lower()
        
        if action == 's':
            sort_files()
        elif action == 'u':
            undo_sort()
        elif action == 'q':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please enter 's', 'u', or 'q'.")