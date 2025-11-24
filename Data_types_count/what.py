import os
import sys
import shutil

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
PURPLE = "\033[95m"
WHITE = "\033[97m"
BLUE = "\033[94m"
RESET = "\033[0m"

def get_terminal_width():
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except:
        return 80

def print_centered_line(content, width, border_color=CYAN, text_color=RESET):
    padding = width - 2 - len(content) # -2 for borders
    left_pad = padding // 2
    right_pad = padding - left_pad
    print(f"{border_color}║{RESET}{' ' * left_pad}{text_color}{content}{RESET}{' ' * right_pad}{border_color}║{RESET}")

def print_border_top(width, color=CYAN):
    print(f"{color}╔{'═' * (width - 2)}╗{RESET}")

def print_border_bottom(width, color=CYAN):
    print(f"{color}╚{'═' * (width - 2)}╝{RESET}")

def analyze_directory(path):
    """
    Counts files and folders in the given directory and breaks down by file extension.
    """
    width = 60
    term_width = get_terminal_width()
    try:
        _, term_height = shutil.get_terminal_size()
    except:
        term_height = 24
    
    left_margin = (term_width - width) // 2
    margin = " " * left_margin

    if not os.path.exists(path):
        print(f"\n{margin}{RED}Error: The path '{path}' does not exist.{RESET}")
        return

    if not os.path.isdir(path):
        print(f"\n{margin}{RED}Error: The path '{path}' is not a directory.{RESET}")
        return

    folder_count = 0
    file_count = 0
    extensions = {}

    # Clear screen and show scanning message
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Calculate vertical centering for the "Scanning..." message
    scan_height = 3
    top_margin = max(0, (term_height - scan_height) // 2)
    print("\n" * top_margin)
    print(f"{margin}{CYAN}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 12)//2)}{YELLOW}Scanning...{RESET}{' ' * ((width - 2 - 12 + 1)//2)}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╚{'═' * (width - 2)}╝{RESET}")

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
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{margin}{RED}An error occurred: {e}{RESET}")
        return

    # Clear screen before showing results
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Calculate vertical centering for results
    # Approximate height: title(3) + 2 rows + separator + extensions + bottom
    result_height = 8 + len(extensions) if extensions else 9
    top_margin = max(0, (term_height - result_height) // 2)
    
    print("\n" * top_margin)
    print(f"{margin}{CYAN}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 15)//2)}{GREEN}REPORT FOR PATH{RESET}{' ' * ((width - 2 - 15 + 1)//2)}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    # Content formatting
    def print_row(label, value, color=WHITE):
        left_part = f"   {label:<25} : "
        right_part = f"{value}"
        
        total_visible = len(left_part) + len(str(value))
        padding = width - 2 - total_visible
        
        print(f"{margin}{CYAN}║{RESET}{left_part}{color}{right_part}{RESET}{' ' * padding}{CYAN}║{RESET}")

    print_row("Total Folders Found", folder_count, PURPLE)
    print_row("Total Files Found", file_count, PURPLE)
    
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 23)//2)}{YELLOW}File Formats Breakdown{RESET}{' ' * ((width - 2 - 23 + 1)//2)}{CYAN}║{RESET}")
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")

    if not extensions:
        print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 16)//2)}{RED}(No files found){RESET}{' ' * ((width - 2 - 16)//2)}{CYAN}║{RESET}")
    else:
        # Sort by count descending
        sorted_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_exts:
            display_ext = ext if ext else "[No Extension]"
            print_row(display_ext, count, BLUE)
            
    print(f"{margin}{CYAN}╚{'═' * (width - 2)}╝{RESET}\n")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("") # Enable ANSI
    
    while True:
        term_width = get_terminal_width()
        try:
            _, term_height = shutil.get_terminal_size()
        except:
            term_height = 24
            
        width = 50
        height = 10 # Approx height of menu
        
        left_margin = (term_width - width) // 2
        top_margin = max(0, (term_height - height) // 2)
        
        margin = " " * left_margin
        
        # Center vertically
        print("\n" * top_margin) 

        print(f"{margin}{CYAN}╔{'═' * (width - 2)}╗{RESET}")
        print(f"{margin}{CYAN}║{RESET}{' ' * ((width - 2 - 18)//2)}{GREEN}LOCAL FILE SCANNER{RESET}{' ' * ((width - 2 - 18 + 1)//2)}{CYAN}║{RESET}")
        print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
        print(f"{margin}{CYAN}║{RESET}{' ' * (width - 2)}{CYAN}║{RESET}")
        
        opt1 = "1. Local (Current Directory)"
        opt2 = "2. Custom Path"
        
        pad1 = width - 2 - len(opt1) - 4
        pad2 = width - 2 - len(opt2) - 4
        
        print(f"{margin}{CYAN}║{RESET}    {WHITE}{opt1}{RESET}{' ' * pad1}{CYAN}║{RESET}")
        print(f"{margin}{CYAN}║{RESET}    {WHITE}{opt2}{RESET}{' ' * pad2}{CYAN}║{RESET}")
        print(f"{margin}{CYAN}║{RESET}{' ' * (width - 2)}{CYAN}║{RESET}")
        print(f"{margin}{CYAN}╚{'═' * (width - 2)}╝{RESET}")
        
        print(f"\n{margin}Selection: ", end='')
        choice = input().strip()
        
        target_path = None
        
        if choice == '1':
            target_path = os.getcwd()
        elif choice == '2':
            print(f"{margin}Enter path: ", end='')
            user_path = input().strip()
            if len(user_path) >= 2 and user_path[0] == '"' and user_path[-1] == '"':
                user_path = user_path[1:-1]
            target_path = user_path
        else:
            # print(f"{margin}{RED}Invalid selection.{RESET}")
            continue
            
        if target_path:
            analyze_directory(target_path)
        
        # Loop prompt
        while True:
            print(f"{margin}{YELLOW}return - x | repeat - r : {RESET}", end='')
            cmd = input().strip().lower()
            if cmd == 'x':
                # Return to ALL.py
                return
            elif cmd == 'r':
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            else:
                pass

if __name__ == "__main__":
    main()
