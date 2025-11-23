import os
import sys
import time
import random
import threading
import subprocess
import shutil

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

stop_menu = False

class ChaosRenderer:
    def __init__(self):
        self.width = 80
        self.height = 24
        self.matrix_columns = {}
        self.snakes = []
        self.math_equations = []
        
    def update_matrix(self):
        # Add new drops
        if random.random() < 0.3:
            col = random.randint(0, self.width - 1)
            self.matrix_columns[col] = 0
            
        # Update existing drops
        to_remove = []
        for col, row in self.matrix_columns.items():
            if row < self.height:
                self.matrix_columns[col] += 1
            else:
                to_remove.append(col)
        for col in to_remove:
            del self.matrix_columns[col]

    def get_matrix_char(self, r, c):
        if c in self.matrix_columns:
            head = self.matrix_columns[c]
            if head == r:
                return f"{BOLD}{os.urandom(1).hex()}{RESET}" # Bright head
            elif head > r > head - 5:
                return f"{GREEN}{os.urandom(1).hex()}{RESET}" # Trail
        return " "

    def render_frame(self):
        # Clear screen (ANSI)
        sys.stdout.write("\033[2J")
        
        # We will build a buffer of strings
        output = []
        
        self.update_matrix()
        
        # Generate background chaos
        for r in range(self.height):
            line = ""
            for c in range(self.width):
                # Matrix effect
                char = self.get_matrix_char(r, c)
                
                # Random math occasionally
                if char == " " and random.random() < 0.001:
                    char = f"{YELLOW}{random.randint(0,9)}{RESET}"
                
                line += char
            output.append(line)
            
        # Overlay Menu Box
        menu_w = 40
        menu_h = 12
        start_r = (self.height - menu_h) // 2
        start_c = (self.width - menu_w) // 2
        
        # Draw box
        for r in range(start_r, start_r + menu_h):
            row_content = list(output[r]) # Convert ANSI string to list is hard, simplifying overlay
            # Actually, string manipulation with ANSI codes is messy. 
            # Simplified approach: Print chaos, then move cursor to print menu on top.
            pass

        # Print chaos
        sys.stdout.write("\033[H") # Home
        print("\n".join(output))
        
        # Print Menu Overlay using cursor positioning
        self.print_at(start_r, start_c,     f"{CYAN}╔══════════════════════════════════════╗{RESET}")
        self.print_at(start_r+1, start_c,   f"{CYAN}║         SYSTEM SCANNER HUB           ║{RESET}")
        self.print_at(start_r+2, start_c,   f"{CYAN}╠══════════════════════════════════════╣{RESET}")
        self.print_at(start_r+3, start_c,   f"{CYAN}║                                      ║{RESET}")
        self.print_at(start_r+4, start_c,   f"{CYAN}║   1. {GREEN}Local / Custom Scan (what.py){CYAN}   ║{RESET}")
        self.print_at(start_r+5, start_c,   f"{CYAN}║   2. {GREEN}Full System Scan (enterieos){CYAN}    ║{RESET}")
        self.print_at(start_r+6, start_c,   f"{CYAN}║   3. {GREEN}Select Drive Scan (SELfile){CYAN}     ║{RESET}")
        self.print_at(start_r+7, start_c,   f"{CYAN}║                                      ║{RESET}")
        self.print_at(start_r+8, start_c,   f"{CYAN}║   Q. {RED}Quit{CYAN}                            ║{RESET}")
        self.print_at(start_r+9, start_c,   f"{CYAN}║                                      ║{RESET}")
        self.print_at(start_r+10, start_c,  f"{CYAN}╚══════════════════════════════════════╝{RESET}")
        
        # Random floating math around the box
        math_r = random.randint(0, self.height-1)
        math_c = random.randint(0, self.width-10)
        if not (start_r <= math_r <= start_r + menu_h and start_c <= math_c <= start_c + menu_w):
             eq = f"{random.randint(1,99)} + {random.randint(1,99)} = ?"
             self.print_at(math_r, math_c, f"{YELLOW}{eq}{RESET}")

    def print_at(self, r, c, text):
        sys.stdout.write(f"\033[{r+1};{c+1}H{text}")

def menu_loop():
    renderer = ChaosRenderer()
    while not stop_menu:
        renderer.render_frame()
        time.sleep(0.1)

def main():
    global stop_menu
    
    # Enable ANSI support in Windows 10/11 CMD/Powershell
    os.system("") 
    
    # Start animation thread
    t = threading.Thread(target=menu_loop)
    t.daemon = True
    t.start()
    
    while True:
        # Input needs to be captured without blocking the animation too much, 
        # but standard input() blocks. 
        # We will let the animation run, and the input cursor will be at the bottom.
        # To make it look clean, we position the cursor below the menu.
        
        # We can't easily do non-blocking input in standard python without curses/msvcrt on windows
        # So we will just accept that the prompt pauses the "render_frame" loop if we were single threaded,
        # but since we are multi-threaded, the background keeps moving!
        # HOWEVER, standard stdout and input() fighting for the console is glitchy.
        
        # TRICK: We will pause the animation thread briefly when we actually need to read input?
        # No, let's try to see if it works. If it glitches, we might need msvcrt.
        
        # Actually, msvcrt is standard on Windows Python. Let's use it for keypresses.
        import msvcrt
        
        choice = None
        while choice is None:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    key = key.decode('utf-8').lower()
                except:
                    continue
                    
                if key in ['1', '2', '3', 'q']:
                    choice = key
            time.sleep(0.05)
            
        # Stop animation to run the script
        stop_menu = True
        t.join()
        
        # Clear screen
        os.system('cls')
        
        if choice == '1':
            subprocess.run([sys.executable, "what.py"])
        elif choice == '2':
            subprocess.run([sys.executable, "enterieos.py"])
        elif choice == '3':
            subprocess.run([sys.executable, "SELfile.py"])
        elif choice == 'q':
            print("Exiting...")
            sys.exit()
            
        input("\nPress Enter to return to menu...")
        stop_menu = False
        t = threading.Thread(target=menu_loop)
        t.daemon = True
        t.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_menu = True
        sys.exit()
