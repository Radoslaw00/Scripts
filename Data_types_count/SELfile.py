import os
import sys
import time
import shutil
import random
import string
import threading
import concurrent.futures

# Global stats container
stats = {
    "folders": 0,
    "files": 0,
    "extensions": {},
    "scanned_bytes": 0,
    "total_bytes": 0
}
stats_lock = threading.Lock()

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

def format_number(n):
    """Formats a number with K, M, B suffixes."""
    if n >= 1_000_000_000:
        return f"{n} ({n/1_000_000_000:.1f}B)"
    elif n >= 1_000_000:
        return f"{n} ({n/1_000_000:.1f}M)"
    elif n >= 1_000:
        return f"{n} ({n/1_000:.1f}K)"
    else:
        return str(n)

def animation_thread():
    """Runs a fancy animation with progress percentage."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    while not stop_animation:
        # Calculate percentage
        with stats_lock:
            s_bytes = stats["scanned_bytes"]
            t_bytes = stats["total_bytes"]
            n_files = stats["files"]
            n_folders = stats["folders"]

        if t_bytes > 0:
            pct = (s_bytes / t_bytes) * 100
            if pct > 100: pct = 100
        else:
            pct = 0
            
        deco = "".join(random.choices(chars, k=15))
        
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "-" * (bar_len - filled)
        
        # Format numbers
        files_str = format_number(n_files)
        folders_str = format_number(n_folders)
        
        sys.stdout.write(f"\r[{bar}] {pct:6.2f}% | {deco} | Files: {files_str} | Folders: {folders_str}   ")
        sys.stdout.flush()
        time.sleep(0.08)

def scan_tree(path):
    """
    Worker function: Recursively scans a directory tree using os.walk.
    Updates global stats safely.
    """
    local_folders = 0
    local_files = 0
    local_exts = {}
    local_bytes = 0
    
    try:
        for root, dirs, files in os.walk(path):
            local_folders += len(dirs)
            local_files += len(files)
            
            for f in files:
                _, ext = os.path.splitext(f)
                ext = ext.lower()
                local_exts[ext] = local_exts.get(ext, 0) + 1
                
                try:
                    full_path = os.path.join(root, f)
                    local_bytes += os.path.getsize(full_path)
                except (OSError, PermissionError):
                    pass
                    
    except (OSError, PermissionError):
        return

    # Batch update global stats to reduce lock contention
    with stats_lock:
        stats["folders"] += local_folders
        stats["files"] += local_files
        stats["scanned_bytes"] += local_bytes
        for ext, count in local_exts.items():
            stats["extensions"][ext] = stats["extensions"].get(ext, 0) + count

def main():
    global stop_animation
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Initializing Drive Selector...")
    
    drives = get_drives()
    
    print("\nAvailable Drives:")
    for i, d in enumerate(drives):
        try:
            usage = shutil.disk_usage(d)
            total_gb = usage.total / (1024**3)
            free_gb = usage.free / (1024**3)
            print(f"{i+1}. {d}  (Total: {total_gb:.1f} GB, Free: {free_gb:.1f} GB)")
        except:
            print(f"{i+1}. {d}")
            
    print("\n")
    selected_drive = None
    while True:
        choice = input("Select a drive number to scan: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(drives):
                selected_drive = drives[idx]
                break
        print("Invalid selection. Try again.")

    # Setup stats for the single drive
    stats["total_bytes"] = get_total_used_space([selected_drive])
    
    print(f"\nPreparing to scan: {selected_drive}")
    print(f"Total Data to Scan: {stats['total_bytes'] / (1024**3):.2f} GB")
    print("Starting Parallel Scan...")
    time.sleep(1.5)
    
    t = threading.Thread(target=animation_thread)
    t.daemon = True
    t.start()
    
    start_time = time.time()
    
    futures = []
    max_workers = min(64, (os.cpu_count() or 4) * 8)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            # Scan root of the selected drive
            with os.scandir(selected_drive) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        futures.append(executor.submit(scan_tree, entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        with stats_lock:
                            stats["files"] += 1
                            _, ext = os.path.splitext(entry.name)
                            ext = ext.lower()
                            stats["extensions"][ext] = stats["extensions"].get(ext, 0) + 1
                            try:
                                stats["scanned_bytes"] += entry.stat().st_size
                            except:
                                pass
        except PermissionError:
            pass
        
        concurrent.futures.wait(futures)
        
    stop_animation = True
    t.join()
    
    duration = time.time() - start_time
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*50)
    print(f"              SCAN COMPLETE: {selected_drive}")
    print("="*50)
    print(f"Time Elapsed:        {duration:.2f} seconds")
    print(f"Total Folders:       {format_number(stats['folders'])}")
    print(f"Total Files:         {format_number(stats['files'])}")
    print(f"Total Data Scanned:  {stats['scanned_bytes'] / (1024**3):.2f} GB")
    print("-" * 50)
    print("File Formats Breakdown:")
    
    if not stats["extensions"]:
        print("  (No files found)")
    else:
        sorted_exts = sorted(stats["extensions"].items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_exts:
            display_ext = ext if ext else "[No Extension]"
            print(f"  {display_ext:<15} : {format_number(count)}")
            
    print("="*50)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_animation = True
        print("\n\nScan aborted by user.")
        sys.exit()
