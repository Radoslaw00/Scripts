import os
import sys

def analyze_directory(path):
    """
    Counts files and folders in the given directory and breaks down by file extension.
    """
    if not os.path.exists(path):
        print(f"Error: The path '{path}' does not exist.")
        return

    if not os.path.isdir(path):
        print(f"Error: The path '{path}' is not a directory.")
        return

    folder_count = 0
    file_count = 0
    extensions = {}

    print(f"Scanning directory: {path} ...")

    try:
        # os.walk allows recursive counting. 
        for root, dirs, files in os.walk(path):
            folder_count += len(dirs)
            file_count += len(files)
            for file in files:
                _, ext = os.path.splitext(file)
                ext = ext.lower()
                if ext in extensions:
                    extensions[ext] += 1
                else:
                    extensions[ext] = 1
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print("\n" + "="*40)
    print(f"REPORT FOR: {path}")
    print("="*40)
    print(f"Total Folders Found: {folder_count}")
    print(f"Total Files Found:   {file_count}")
    print("-" * 40)
    print("File Formats Breakdown:")
    
    if not extensions:
        print("  (No files found)")
    else:
        # Sort by count descending
        sorted_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_exts:
            # Handle files with no extension
            display_ext = ext if ext else "[No Extension]"
            print(f"  {display_ext:<15} : {count}")
            
    print("="*40 + "\n")

def main():
    while True:
        print("Choose an option:")
        print("1. local (Current Directory)")
        print("2. pwd   (Enter Custom Path)")
        
        choice = input("Selection: ").strip()
        
        target_path = None
        
        if choice == '1':
            target_path = os.getcwd()
        elif choice == '2':
            user_path = input("Enter path: ").strip()
            # Remove quotes if present (common when copying paths in Windows)
            if len(user_path) >= 2 and user_path[0] == '"' and user_path[-1] == '"':
                user_path = user_path[1:-1]
            target_path = user_path
        else:
            print("Invalid selection. Please type 1 or 2.")
            continue
            
        if target_path:
            analyze_directory(target_path)
        
        # Loop prompt
        while True:
            cmd = input("quit - q | repeat - r : ").strip().lower()
            if cmd == 'q':
                print("Exiting.")
                return
            elif cmd == 'r':
                print("\nRestarting...\n")
                break
            else:
                print("Invalid command.")

if __name__ == "__main__":
    main()
