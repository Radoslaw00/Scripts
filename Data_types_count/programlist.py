import winreg
import os
import re
import concurrent.futures
import threading
import sys
import time
import shutil

# ANSI Colors
YELLOW = "\033[93m"
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Global progress tracking
scan_progress = {
    "scanned_files": 0,
    "total_size": 0
}
progress_lock = threading.Lock()

def get_terminal_width():
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except:
        return 80

def get_folder_size_parallel(path):
    """
    Calculates folder size using parallel workers.
    Updates global progress for visual reference.
    """
    total_size = 0
    futures = []
    
    # Reset progress
    with progress_lock:
        scan_progress["scanned_files"] = 0
        scan_progress["total_size"] = 0

    def scan_worker(dir_path):
        local_size = 0
        local_count = 0
        try:
            # os.scandir is faster than os.walk
            with os.scandir(dir_path) as it:
                for entry in it:
                    if entry.is_file(follow_symlinks=False):
                        try:
                            local_size += entry.stat().st_size
                            local_count += 1
                        except OSError:
                            pass
                    elif entry.is_dir(follow_symlinks=False):
                        # Recurse directly in this thread for small depth, 
                        # or could submit new tasks. For simplicity and speed in deep trees,
                        # we recurse here.
                        s, c = scan_worker(entry.path)
                        local_size += s
                        local_count += c
        except (OSError, PermissionError):
            pass
        return local_size, local_count

    # We split the top-level directories into separate tasks
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        futures.append(executor.submit(scan_worker, entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        try:
                            total_size += entry.stat().st_size
                            with progress_lock:
                                scan_progress["scanned_files"] += 1
                        except OSError:
                            pass
            
            # Wait for futures and aggregate
            for future in concurrent.futures.as_completed(futures):
                s, c = future.result()
                total_size += s
                with progress_lock:
                    scan_progress["scanned_files"] += c
                    scan_progress["total_size"] += s
                    
    except (OSError, PermissionError):
        pass
        
    return total_size

def progress_spinner(stop_event, message):
    """Shows a spinner and file count while scanning."""
    chars = "|/-\\"
    i = 0
    while not stop_event.is_set():
        with progress_lock:
            count = scan_progress["scanned_files"]
            size_mb = scan_progress["total_size"] / (1024*1024)
        
        term_width = get_terminal_width()
        line = f"{message} {chars[i]} [ Files: {count} | Size: {size_mb:.0f} MB ]"
        padding = max(0, (term_width - len(line) + 10) // 2) # +10 roughly for ANSI codes compensation
        # Actually, let's strip ansi for len calc
        clean_line = f"Scanning Windows... {chars[i]} [ Files: {count} | Size: {size_mb:.0f} MB ]"
        padding = max(0, (term_width - len(clean_line)) // 2)
        
        sys.stdout.write(f"\r{' ' * padding}{line}")
        sys.stdout.flush()
        time.sleep(0.1)
        i = (i + 1) % 4
    sys.stdout.write("\r" + " " * (term_width) + "\r") # Clear line

def get_windows_size():
    """Calculates C:\\Windows size with parallel scanning and visual feedback."""
    system_root = os.environ.get('SystemRoot', r'C:\Windows')
    
    stop_event = threading.Event()
    t = threading.Thread(target=progress_spinner, args=(stop_event, f"{CYAN}Scanning Windows ({system_root})...{RESET}"))
    t.start()
    
    size = get_folder_size_parallel(system_root)
    
    stop_event.set()
    t.join()
    
    # print(f"{GREEN}Windows Scan Complete!{RESET}")
    return {"name": f"[System] Windows ({system_root})", "size": size}

def get_steam_games():
    games = []
    steam_path = None
    
    term_width = get_terminal_width()
    msg = "Scanning Steam Libraries..."
    padding = " " * max(0, (term_width - len(msg)) // 2)
    print(f"{padding}{CYAN}{msg}{RESET}", end='')
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
            steam_path = steam_path.replace("/", "\\")
    except OSError:
        pass
        
    if not steam_path or not os.path.exists(steam_path):
        print(f" {RED}Not Found{RESET}")
        return []

    library_folders = set()
    library_folders.add(steam_path)

    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if os.path.exists(vdf_path):
        try:
            with open(vdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = re.findall(r'"path"\s+"(.+?)"', content, re.IGNORECASE)
                for m in matches:
                    path = m.replace("\\\\", "\\")
                    if os.path.exists(path):
                        library_folders.add(path)
        except Exception:
            pass

    count = 0
    for lib in library_folders:
        steamapps = os.path.join(lib, "steamapps")
        if not os.path.exists(steamapps):
            continue
            
        for filename in os.listdir(steamapps):
            if filename.startswith("appmanifest_") and filename.endswith(".acf"):
                try:
                    full_path = os.path.join(steamapps, filename)
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        manifest = f.read()
                        name_match = re.search(r'"name"\s+"(.+?)"', manifest)
                        size_match = re.search(r'"SizeOnDisk"\s+"(\d+)"', manifest)
                        
                        if name_match:
                            name = name_match.group(1)
                            size = int(size_match.group(1)) if size_match else 0
                            games.append({"name": f"[Steam] {name}", "size": size})
                            count += 1
                except Exception:
                    pass
    
    print(f" {GREEN}Done ({count} games found){RESET}")
    return games

def get_installed_programs():
    term_width = get_terminal_width()
    msg = "Scanning Registry Programs..."
    padding = " " * max(0, (term_width - len(msg)) // 2)
    print(f"{padding}{CYAN}{msg}{RESET}", end='')
    
    programs = []
    uninstall_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    seen_names = set()

    count = 0
    for hkey, key_path in uninstall_keys:
        try:
            with winreg.OpenKey(hkey, key_path) as key:
                num_subkeys = winreg.QueryInfoKey(key)[0]
                for i in range(num_subkeys):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            try:
                                name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                name = str(name).strip()
                                if not name or name in seen_names:
                                    continue
                                
                                size_bytes = 0
                                try:
                                    size_kb = winreg.QueryValueEx(sub_key, "EstimatedSize")[0]
                                    size_bytes = int(size_kb) * 1024
                                except (FileNotFoundError, ValueError, TypeError):
                                    size_bytes = 0
                                
                                programs.append({"name": name, "size": size_bytes})
                                seen_names.add(name)
                                count += 1
                            except FileNotFoundError:
                                pass 
                    except OSError:
                        pass
        except OSError:
            pass
            
    print(f" {GREEN}Done ({count} apps found){RESET}")
    return programs

def format_size(bytes_val):
    if bytes_val == 0:
        return f"{RED}Unknown{RESET}"
    
    val = float(bytes_val)
    unit = 'B'
    
    if val < 1024:
        unit = 'B'
    elif val < 1024**2:
        val /= 1024
        unit = 'KB'
    elif val < 1024**3:
        val /= 1024**2
        unit = 'MB'
    elif val < 1024**4:
        val /= 1024**3
        unit = 'GB'
    else:
        val /= 1024**4
        unit = 'TB'
        
    color = RESET
    if unit == 'B':
        color = YELLOW
    elif unit == 'KB':
        color = BLUE
    elif unit == 'MB':
        color = GREEN
    elif unit in ('GB', 'TB', 'PB'):
        color = PURPLE
        
    return f"{color}{val:.2f} {unit}{RESET}"

def display_list(items, filter_text=None):
    """Prints the list of programs, optionally filtered."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    term_width = get_terminal_width()
    width = 80
    margin = " " * max(0, (term_width - width) // 2)
    
    print("")
    print(f"{margin}{CYAN}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 24)//2)}{BOLD}{WHITE}SYSTEM SOFTWARE ANALYZER{RESET}{' ' * ((width - 2 - 24 + 1)//2)}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    if filter_text:
        print(f"{margin}{CYAN}║{RESET} {YELLOW}Filter: {filter_text}{RESET}{' ' * (width - 4 - 8 - len(filter_text))} {CYAN}║{RESET}")
        print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")

    # Header
    # Width is 80. Borders take 2. Content 78.
    # Name 55, Size ~20.
    
    header_name = "PROGRAM NAME"
    header_size = "ESTIMATED SIZE"
    
    print(f"{margin}{CYAN}║{RESET} {BOLD}{WHITE}{header_name:<55} | {header_size}{RESET} {CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    count = 0
    # Limit items to fit on screen? No, it's a scrolling list.
    # But we should probably keep the borders?
    # Printing borders on every line for a long list is fine.
    
    for app in items:
        name = app['name']
        
        # Filter logic
        if filter_text and filter_text.lower() not in name.lower():
            continue
            
        size_str = format_size(app["size"])
        
        # Truncate name to fit
        if len(name) > 52:
            name = name[:49] + "..."
            
        # Calculate padding for the line
        # Name is padded to 55. " | " is 3 chars. Size is variable but format_size returns color codes.
        # We need visible length.
        
        # format_size returns string with colors.
        # Let's strip colors for length calc? Or just assume fixed width for size column?
        # format_size output like "12.34 MB" is approx 8-10 chars.
        # Let's align size to right?
        
        # Re-implement row printing
        # Left part: " Name..." (55 chars)
        # Separator: " | "
        # Right part: Size
        
        # We need to know the visible length of size_str
        visible_size = re.sub(r'\033\[\d+m', '', size_str)
        
        # Construct line
        # We want the pipe at fixed position?
        # Header has pipe at 55+1+1 = 57?
        # "PROGRAM NAME" is at index 1.
        # {header_name:<55} takes 55 chars.
        # " | " takes 3.
        # {header_size} takes rest.
        
        # So: " {name:<55} | {size_str} "
        # But size_str has colors.
        
        # Let's just print it and pad the end with spaces to reach width-2
        
        left = f" {name:<55} | "
        right = f"{size_str}"
        
        # Calculate how much space 'right' takes visually
        right_len = len(visible_size)
        
        total_visible = len(left) + right_len
        padding = width - 2 - total_visible
        if padding < 0: padding = 0
        
        print(f"{margin}{CYAN}║{RESET}{left}{right}{' ' * padding}{CYAN}║{RESET}")
        count += 1
        
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    # Footer
    total_str = f"Total Items Listed: {count}"
    print(f"{margin}{CYAN}║{RESET} {BOLD}{total_str}{RESET}{' ' * (width - 4 - len(total_str))} {CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    # Legend
    # Legend is long, might need multiple lines or careful formatting
    # Legend: Byte | KB | MB | GB | Unknown
    # Let's center it
    
    l_byte = f"{YELLOW}Byte{RESET}"
    l_kb = f"{BLUE}KB{RESET}"
    l_mb = f"{GREEN}MB{RESET}"
    l_gb = f"{PURPLE}GB{RESET}"
    l_unk = f"{RED}Unknown{RESET}"
    
    legend_content = f"Legend: {l_byte} | {l_kb} | {l_mb} | {l_gb} | {l_unk}"
    legend_visible = "Legend: Byte | KB | MB | GB | Unknown"
    
    pad_l = (width - 2 - len(legend_visible)) // 2
    pad_r = width - 2 - len(legend_visible) - pad_l
    
    print(f"{margin}{CYAN}║{RESET}{' ' * pad_l}{legend_content}{' ' * pad_r}{CYAN}║{RESET}")
    term_width = get_terminal_width()
    msg = "Scanning Registry Programs..."
    padding = " " * max(0, (term_width - len(msg)) // 2)
    print(f"{padding}{CYAN}{msg}{RESET}", end='')
    
    programs = []
    uninstall_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    seen_names = set()

    count = 0
    for hkey, key_path in uninstall_keys:
        try:
            with winreg.OpenKey(hkey, key_path) as key:
                num_subkeys = winreg.QueryInfoKey(key)[0]
                for i in range(num_subkeys):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            try:
                                name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                name = str(name).strip()
                                if not name or name in seen_names:
                                    continue
                                
                                size_bytes = 0
                                try:
                                    size_kb = winreg.QueryValueEx(sub_key, "EstimatedSize")[0]
                                    size_bytes = int(size_kb) * 1024
                                except (FileNotFoundError, ValueError, TypeError):
                                    size_bytes = 0
                                
                                programs.append({"name": name, "size": size_bytes})
                                seen_names.add(name)
                                count += 1
                            except FileNotFoundError:
                                pass 
                    except OSError:
                        pass
        except OSError:
            pass
            
    print(f" {GREEN}Done ({count} apps found){RESET}")
    return programs

def format_size(bytes_val):
    if bytes_val == 0:
        return f"{RED}Unknown{RESET}"
    
    val = float(bytes_val)
    unit = 'B'
    
    if val < 1024:
        unit = 'B'
    elif val < 1024**2:
        val /= 1024
        unit = 'KB'
    elif val < 1024**3:
        val /= 1024**2
        unit = 'MB'
    elif val < 1024**4:
        val /= 1024**3
        unit = 'GB'
    else:
        val /= 1024**4
        unit = 'TB'
        
    color = RESET
    if unit == 'B':
        color = YELLOW
    elif unit == 'KB':
        color = BLUE
    elif unit == 'MB':
        color = GREEN
    elif unit in ('GB', 'TB', 'PB'):
        color = PURPLE
        
    return f"{color}{val:.2f} {unit}{RESET}"

def display_list(items, filter_text=None):
    """Prints the list of programs, optionally filtered."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    term_width = get_terminal_width()
    width = 80
    margin = " " * max(0, (term_width - width) // 2)
    
    print("")
    print(f"{margin}{CYAN}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 24)//2)}{BOLD}{WHITE}SYSTEM SOFTWARE ANALYZER{RESET}{' ' * ((width - 2 - 24 + 1)//2)}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    if filter_text:
        print(f"{margin}{CYAN}║{RESET} {YELLOW}Filter: {filter_text}{RESET}{' ' * (width - 4 - 8 - len(filter_text))} {CYAN}║{RESET}")
        print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")

    # Header
    # Width is 80. Borders take 2. Content 78.
    # Name 55, Size ~20.
    
    header_name = "PROGRAM NAME"
    header_size = "ESTIMATED SIZE"
    
    print(f"{margin}{CYAN}║{RESET} {BOLD}{WHITE}{header_name:<55} | {header_size}{RESET} {CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    count = 0
    # Limit items to fit on screen? No, it's a scrolling list.
    # But we should probably keep the borders?
    # Printing borders on every line for a long list is fine.
    
    for app in items:
        name = app['name']
        
        # Filter logic
        if filter_text and filter_text.lower() not in name.lower():
            continue
            
        size_str = format_size(app["size"])
        
        # Truncate name to fit
        if len(name) > 52:
            name = name[:49] + "..."
            
        # Calculate padding for the line
        # Name is padded to 55. " | " is 3 chars. Size is variable but format_size returns color codes.
        # We need visible length.
        
        # format_size returns string with colors.
        # Let's strip colors for length calc? Or just assume fixed width for size column?
        # format_size output like "12.34 MB" is approx 8-10 chars.
        # Let's align size to right?
        
        # Re-implement row printing
        # Left part: " Name..." (55 chars)
        # Separator: " | "
        # Right part: Size
        
        # We need to know the visible length of size_str
        visible_size = re.sub(r'\033\[\d+m', '', size_str)
        
        # Construct line
        # We want the pipe at fixed position?
        # Header has pipe at 55+1+1 = 57?
        # "PROGRAM NAME" is at index 1.
        # {header_name:<55} takes 55 chars.
        # " | " takes 3.
        # {header_size} takes rest.
        
        # So: " {name:<55} | {size_str} "
        # But size_str has colors.
        
        # Let's just print it and pad the end with spaces to reach width-2
        
        left = f" {name:<55} | "
        right = f"{size_str}"
        
        # Calculate how much space 'right' takes visually
        right_len = len(visible_size)
        
        total_visible = len(left) + right_len
        padding = width - 2 - total_visible
        if padding < 0: padding = 0
        
        print(f"{margin}{CYAN}║{RESET}{left}{right}{' ' * padding}{CYAN}║{RESET}")
        count += 1
        
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    # Footer
    total_str = f"Total Items Listed: {count}"
    print(f"{margin}{CYAN}║{RESET} {BOLD}{total_str}{RESET}{' ' * (width - 4 - len(total_str))} {CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    # Legend
    # Legend is long, might need multiple lines or careful formatting
    # Let's center it
    
    l_byte = f"{YELLOW}Byte{RESET}"
    l_kb = f"{BLUE}KB{RESET}"
    l_mb = f"{GREEN}MB{RESET}"
    l_gb = f"{PURPLE}GB{RESET}"
    l_unk = f"{RED}Unknown{RESET}"
    
    legend_content = f"Legend: {l_byte} | {l_kb} | {l_mb} | {l_gb} | {l_unk}"
    legend_visible = "Legend: Byte | KB | MB | GB | Unknown"
    
    pad_l = (width - 2 - len(legend_visible)) // 2
    pad_r = width - 2 - len(legend_visible) - pad_l
    
    print(f"{margin}{CYAN}║{RESET}{' ' * pad_l}{legend_content}{' ' * pad_r}{CYAN}║{RESET}")
    
    # Commands
    cmds = "Commands: [ \\ ] Search | [ X ] Return to Menu"
    pad_c = (width - 2 - len(cmds)) // 2
    pad_cr = width - 2 - len(cmds) - pad_c
    
    print(f"{margin}{CYAN}║{RESET}{' ' * pad_c}{WHITE}{cmds}{RESET}{' ' * pad_cr}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╚{'═' * (width - 2)}╝{RESET}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("") # Enable ANSI
    
    # Initial Scan
    term_width = get_terminal_width()
    try:
        _, term_height = shutil.get_terminal_size()
    except:
        term_height = 24
        
    width = 80
    height = 10 # Approx
    
    margin = " " * max(0, (term_width - width) // 2)
    top_margin = max(0, (term_height - height) // 2)
    
    print("\n" * top_margin)
    print(f"{margin}{BOLD}{WHITE}=== SYSTEM SOFTWARE ANALYZER ==={RESET}\n")
    
    apps = get_installed_programs()
    steam_games = get_steam_games()
    win_folder = get_windows_size()
    
    final_list = apps + steam_games
    final_list.append(win_folder)
    final_list.sort(key=lambda x: x["size"], reverse=True)
    
    # Interactive Loop
    import msvcrt
    
    current_filter = ""
    searching = False
    
    while True:
        if searching:
            # Search Mode
            display_list(final_list, current_filter)
            
            # Print search prompt below the box
            prompt = f"Search Query: {current_filter}"
            pad_p = " " * max(0, (term_width - len(prompt)) // 2)
            print(f"\n{pad_p}{CYAN}{prompt}{RESET}", end='', flush=True)
            
            # Read char by char for search input
            ch = msvcrt.getwch()
            
            if ch == '\r': # Enter to confirm/exit search
                searching = False
            elif ch == '\x08': # Backspace
                current_filter = current_filter[:-1]
            elif ch == '\x03': # Ctrl+C
                return # Return to menu
            else:
                current_filter += ch
        else:
            # View Mode
            display_list(final_list, current_filter if current_filter else None)
            
            # Wait for command
            ch = msvcrt.getwch()
            
            if ch == '\\':
                searching = True
                current_filter = "" # Reset filter on new search start? Or keep? Let's reset.
            elif ch.lower() == 'x': # X to return
                break
            elif ch == '\x03': # Ctrl+C
                return # Return to menu

if __name__ == "__main__":
    main()
