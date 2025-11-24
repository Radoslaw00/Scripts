import os
import sys
import time
import shutil
import random
import string
import threading
import concurrent.futures
import msvcrt

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
PURPLE = "\033[95m"
WHITE = "\033[97m"
BLUE = "\033[94m"
RESET = "\033[0m"

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

def get_terminal_width():
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except:
        return 80

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
        term_width = get_terminal_width()
        
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
            
        deco = "".join(random.choices(chars, k=10))
        
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = f"{GREEN}{'█' * filled}{RESET}{' ' * (bar_len - filled)}"
        
        # Format numbers
        files_str = format_number(n_files)
        folders_str = format_number(n_folders)
        
        status_line = f"[{bar}] {pct:6.2f}% | {CYAN}{deco}{RESET} | Files: {YELLOW}{files_str}{RESET} | Folders: {PURPLE}{folders_str}{RESET}"
        
        # Center the line
        # Remove ANSI codes for length calculation
        clean_line = f"[{'█' * filled}{' ' * (bar_len - filled)}] {pct:6.2f}% | {deco} | Files: {files_str} | Folders: {folders_str}"
        padding = max(0, (term_width - len(clean_line)) // 2)
        
        sys.stdout.write(f"\r{' ' * padding}{status_line}   ")
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
    os.system("") # Enable ANSI
    
    term_width = get_terminal_width()
    try:
        _, term_height = shutil.get_terminal_size()
    except:
        term_height = 24
        
    width = 60
    height = 6 # Approx height of initial block
    
    margin = " " * ((term_width - width) // 2)
    top_margin = max(0, (term_height - height) // 2)
    
    print("\n" * top_margin)
    print(f"{margin}{CYAN}Initializing High-Performance Parallel Scan...{RESET}")
    
    drives = get_drives()
    stats["total_bytes"] = get_total_used_space(drives)
    
    print(f"{margin}Detected Drives: {GREEN}{', '.join(drives)}{RESET}")
    print(f"{margin}Total Data to Scan: {YELLOW}{stats['total_bytes'] / (1024**3):.2f} GB{RESET}")
    print(f"{margin}Starting Parallel Scan... (This utilizes multiple threads)")
    time.sleep(1.5)
    
    t = threading.Thread(target=animation_thread)
    t.daemon = True
    t.start()
    
    start_time = time.time()
    
    futures = []
    max_workers = min(64, (os.cpu_count() or 4) * 8)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for drive in drives:
            try:
                # 1. Scan root files of the drive immediately (fast)
                with os.scandir(drive) as it:
                    for entry in it:
                        if entry.is_dir(follow_symlinks=False):
                            # Submit subdirectory to pool
                            futures.append(executor.submit(scan_tree, entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            # Count root file immediately
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
        
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
        
    stop_animation = True
    t.join()
    
    duration = time.time() - start_time
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Final Report
    term_width = get_terminal_width()
    width = 60
    margin = " " * ((term_width - width) // 2)
    
    print("")
    print(f"{margin}{CYAN}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 20)//2)}{GREEN}SYSTEM SCAN COMPLETE{RESET}{' ' * ((width - 2 - 20 + 1)//2)}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    def print_row(label, value, color=WHITE):
        left_part = f"   {label:<20} : "
        right_part = f"{value}"
        total_visible = len(left_part) + len(str(value))
        padding = width - 2 - total_visible
        print(f"{margin}{CYAN}║{RESET}{left_part}{color}{right_part}{RESET}{' ' * padding}{CYAN}║{RESET}")

    print_row("Scanned Drives", ', '.join(drives), GREEN)
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
        term_width = get_terminal_width()
        
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
            
        deco = "".join(random.choices(chars, k=10))
        
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = f"{GREEN}{'█' * filled}{RESET}{' ' * (bar_len - filled)}"
        
        # Format numbers
        files_str = format_number(n_files)
        folders_str = format_number(n_folders)
        
        status_line = f"[{bar}] {pct:6.2f}% | {CYAN}{deco}{RESET} | Files: {YELLOW}{files_str}{RESET} | Folders: {PURPLE}{folders_str}{RESET}"
        
        # Center the line
        # Remove ANSI codes for length calculation
        clean_line = f"[{'█' * filled}{' ' * (bar_len - filled)}] {pct:6.2f}% | {deco} | Files: {files_str} | Folders: {folders_str}"
        padding = max(0, (term_width - len(clean_line)) // 2)
        
        sys.stdout.write(f"\r{' ' * padding}{status_line}   ")
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
    os.system("") # Enable ANSI
    
    term_width = get_terminal_width()
    try:
        _, term_height = shutil.get_terminal_size()
    except:
        term_height = 24
        
    width = 60
    height = 6 # Approx height of initial block
    
    margin = " " * ((term_width - width) // 2)
    top_margin = max(0, (term_height - height) // 2)
    
    print("\n" * top_margin)
    print(f"{margin}{CYAN}Initializing High-Performance Parallel Scan...{RESET}")
    
    drives = get_drives()
    stats["total_bytes"] = get_total_used_space(drives)
    
    print(f"{margin}Detected Drives: {GREEN}{', '.join(drives)}{RESET}")
    print(f"{margin}Total Data to Scan: {YELLOW}{stats['total_bytes'] / (1024**3):.2f} GB{RESET}")
    print(f"{margin}Starting Parallel Scan... (This utilizes multiple threads)")
    time.sleep(1.5)
    
    t = threading.Thread(target=animation_thread)
    t.daemon = True
    t.start()
    
    start_time = time.time()
    
    futures = []
    max_workers = min(64, (os.cpu_count() or 4) * 8)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for drive in drives:
            try:
                # 1. Scan root files of the drive immediately (fast)
                with os.scandir(drive) as it:
                    for entry in it:
                        if entry.is_dir(follow_symlinks=False):
                            # Submit subdirectory to pool
                            futures.append(executor.submit(scan_tree, entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            # Count root file immediately
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
        
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
        
    stop_animation = True
    t.join()
    
    duration = time.time() - start_time
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Final Report
    term_width = get_terminal_width()
    width = 60
    margin = " " * ((term_width - width) // 2)
    
    print("")
    print(f"{margin}{CYAN}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 20)//2)}{GREEN}SYSTEM SCAN COMPLETE{RESET}{' ' * ((width - 2 - 20 + 1)//2)}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    def print_row(label, value, color=WHITE):
        left_part = f"   {label:<20} : "
        right_part = f"{value}"
        total_visible = len(left_part) + len(str(value))
        padding = width - 2 - total_visible
        print(f"{margin}{CYAN}║{RESET}{left_part}{color}{right_part}{RESET}{' ' * padding}{CYAN}║{RESET}")

    print_row("Scanned Drives", ', '.join(drives), GREEN)
    print_row("Time Elapsed", f"{duration:.2f} seconds", YELLOW)
    print_row("Total Folders", stats['folders'], PURPLE)
    print_row("Total Files", stats['files'], PURPLE)
    print_row("Total Data Scanned", f"{stats['scanned_bytes'] / (1024**3):.2f} GB", BLUE)

    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 23)//2)}{YELLOW}File Formats Breakdown{RESET}{' ' * ((width - 2 - 23 + 1)//2)}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    if not stats["extensions"]:
        print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 16)//2)}{RED}(No files found){RESET}{' ' * ((width - 2 - 16)//2)}{CYAN}║{RESET}")
    else:
        sorted_exts = sorted(stats["extensions"].items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_exts:
            display_ext = ext if ext else "[No Extension]"
            print_row(display_ext, count, BLUE)
            
    print(f"{margin}{CYAN}╚{'═' * (width - 2)}╝{RESET}")
    print(f"\n{margin}Press X to return to menu...", end='', flush=True)
    
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getch().decode('utf-8').lower()
            if ch == 'x':
                break
        time.sleep(0.05)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_animation = True
        pass
