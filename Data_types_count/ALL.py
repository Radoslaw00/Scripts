import os
import sys
import subprocess
import msvcrt
import random
import time
import webbrowser

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
PURPLE = "\033[95m"
RESET = "\033[0m"

def get_random_color():
    colors = [CYAN, GREEN, RED, YELLOW, "\033[95m", "\033[97m"]
    return random.choice(colors)

import shutil

def print_menu():
    # Move cursor to top-left
    print("\033[H", end="")
    
    # Get terminal size
    try:
        columns, lines = shutil.get_terminal_size()
    except:
        columns, lines = 80, 24
        
    menu_width = 40
    menu_height = 14 # Number of lines in the menu
    
    # Calculate padding
    pad_left = max(0, (columns - menu_width) // 2)
    pad_top = max(0, (lines - menu_height) // 2)
    
    padding = " " * pad_left
    
    # Flashing Title
    title = "SCAN TOOL LAUNCHER"
    colored_title = ""
    for char in title:
        colored_title += f"{get_random_color()}{char}"
    
    # Print top padding (newlines)
    print("\n" * pad_top, end="")
    
    print(f"{padding}{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{padding}{CYAN}║          {colored_title}{CYAN}          ║{RESET}")
    print(f"{padding}{CYAN}╠══════════════════════════════════════╣{RESET}")
    print(f"{padding}{CYAN}║                                      ║{RESET}")
    print(f"{padding}{CYAN}║   1. {GREEN}Local / Custom Scan{CYAN}             ║{RESET}")
    print(f"{padding}{CYAN}║   2. {GREEN}Full System Scan{CYAN}                ║{RESET}")
    print(f"{padding}{CYAN}║   3. {GREEN}Select Drive Scan{CYAN}               ║{RESET}")
    print(f"{padding}{CYAN}║   4. {GREEN}Installed Programs{CYAN}              ║{RESET}")
    print(f"{padding}{CYAN}║   5. {GREEN}Image Converter{CYAN}                 ║{RESET}")
    print(f"{padding}{CYAN}║                                      ║{RESET}")
    print(f"{padding}{CYAN}║   H. {PURPLE}Readme{CYAN}                          ║{RESET}")
    print(f"{padding}{CYAN}║   X. {RED}Quit{CYAN}                            ║{RESET}")
    print(f"{padding}{CYAN}║                                      ║{RESET}")
    print(f"{padding}{CYAN}╚══════════════════════════════════════╝{RESET}")
    
    # Move cursor to bottom or specific input location?
    # Let's just print the prompt centered too
    prompt = "Select an option: "
    prompt_pad = " " * max(0, (columns - len(prompt)) // 2)
    print(f"\n{prompt_pad}{prompt}", end='', flush=True)

def main():
    # Enable ANSI support in Windows 10/11 CMD/Powershell
    os.system("") 
    # Clear screen once at start
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        # Redraw menu frequently to animate the title
        # We need to check for input without blocking
        
        while not msvcrt.kbhit():
            print_menu()
            time.sleep(0.1) # Flashing speed
            
        # Input detected
        key = msvcrt.getch()
        try:
            key = key.decode('utf-8').lower()
        except:
            continue
            
        if key == '1':
            os.system('cls')
            subprocess.run([sys.executable, "what.py"])
        elif key == '2':
            os.system('cls')
            subprocess.run([sys.executable, "enterieos.py"])
        elif key == '3':
            os.system('cls')
            subprocess.run([sys.executable, "SELfile.py"])
        elif key == '4':
            os.system('cls')
            subprocess.run([sys.executable, "programlist.py"])
        elif key == '5':
            os.system('cls')
            subprocess.run([sys.executable, "image_converter.py"])
        elif key == 'h':
            readme_path = os.path.abspath(os.path.join("HTMLREAD", "index.html"))
            if os.path.exists(readme_path):
                webbrowser.open(f"file:///{readme_path}")
            else:
                print("\nReadme file not found!")
                time.sleep(1)
        elif key == 'x':
            print("\nExiting...")
            sys.exit()
            
        # Clear screen again after returning from a script
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
