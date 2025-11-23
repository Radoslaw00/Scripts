import os
import sys
import time
import shutil
import random
import string
import threading

# Global stats container
stats = {
    "folders": 0,
    "files": 0,
    "extensions": {},
    "scanned_bytes": 0,
    "total_bytes": 0
}

stop_animation = False

def get_drives():
    """Returns a list of available drive letters (e.g., ['C:\\', 'D:\\'])."""
    drives = []
    # Windows drives A-Z
    for x in string.ascii_uppercase:
        drive_path = f"{x}:\\"
        if os.path.exists(drive_path):
            drives.append(drive_path)
    return drives

def get_total_used_space(drives):
    """Calculates total used space across all drives to estimate progress."""
    total = 0
    for d in drives:
        try:
            usage = shutil.disk_usage(d)
            total += usage.used
        except:
            pass
    return total

def animation_thread():
    """Runs a fancy animation with progress percentage in a separate thread."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    while not stop_animation:
        # Calculate percentage
        if stats["total_bytes"] > 0:
            pct = (stats["scanned_bytes"] / stats["total_bytes"]) * 100
            # Cap at 99.99 until actually done, because scanned_bytes might differ slightly from used space
            if pct > 100: pct = 100
        else:
            pct = 0
            
        # Generate random "matrix/hacker" string
        deco = "".join(random.choices(chars, k=15))
        
        # Progress bar
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "-" * (bar_len - filled)
        
        # Print status line (overwrite previous line using \r)
        # Format: [████------] 45.20% | a8j#9kL... | Files: 1205 | Folders: 45
        sys.stdout.write(f"\r[{bar}] {pct:6.2f}% | {deco} | Files: {stats['files']} | Folders: {stats['folders']}")
        sys.stdout.flush()
        time.sleep(0.08)

def scan_drive(drive_path):
    """Recursively scans a drive for files and folders."""
    try:
        for root, dirs, files in os.walk(drive_path):
            stats["folders"] += len(dirs)
            stats["files"] += len(files)
            
            for f in files:
                # Extension counting
                _, ext = os.path.splitext(f)
                ext = ext.lower()
                stats["extensions"][ext] = stats["extensions"].get(ext, 0) + 1
                
                # Size for progress (try/except for permission errors on system files)
                try:
                    full_path = os.path.join(root, f)
                    # We add size to track progress against total disk usage
                    stats["scanned_bytes"] += os.path.getsize(full_path)
                except (OSError, PermissionError):
                    pass
                    
    except (OSError, PermissionError):
        # Skip drives/folders we can't access
        pass

def main():
    global stop_animation
    
    # 1. Setup and Clear Screen
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Initializing System Scan...")
    
    drives = get_drives()
    stats["total_bytes"] = get_total_used_space(drives)
    
    print(f"Detected Drives: {', '.join(drives)}")
    print(f"Total Data to Scan: {stats['total_bytes'] / (1024**3):.2f} GB")
    print("Starting Scan... (This may take a while)")
    time.sleep(1.5)
    
    # 2. Start Animation Thread
    t = threading.Thread(target=animation_thread)
    t.daemon = True
    t.start()
    
    # 3. Perform Scan
    start_time = time.time()
    for drive in drives:
        scan_drive(drive)
        
    # 4. Finish
    stop_animation = True
    t.join()
    
    # 5. Report
    os.system('cls' if os.name == 'nt' else 'clear')
    duration = time.time() - start_time
    
    print("="*50)
    print("              SYSTEM SCAN COMPLETE")
    print("="*50)
    print(f"Scanned Drives:      {', '.join(drives)}")
    print(f"Time Elapsed:        {duration:.2f} seconds")
    print(f"Total Folders:       {stats['folders']}")
    print(f"Total Files:         {stats['files']}")
    print(f"Total Data Scanned:  {stats['scanned_bytes'] / (1024**3):.2f} GB")
    print("-" * 50)
    print("File Formats Breakdown:")
    
    if not stats["extensions"]:
        print("  (No files found)")
    else:
        # Sort by count descending
        sorted_exts = sorted(stats["extensions"].items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_exts:
            display_ext = ext if ext else "[No Extension]"
            print(f"  {display_ext:<15} : {count}")
            
    print("="*50)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_animation = True
        print("\n\nScan aborted by user.")
        sys.exit()
