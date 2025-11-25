import os
import sys
import shutil
from pathlib import Path

try:
    from PIL import Image
except Exception:
    print("Biblioteka Pillow nie jest zainstalowana. Zainstaluj ją: pip install pillow")
    sys.exit(1)

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
PURPLE = "\033[95m"
WHITE = "\033[97m"
BLUE = "\033[94m"
RESET = "\033[0m"

SUPPORTED = ["webp", "png", "jpg", "jpeg", "bmp", "tiff", "gif"]

# Translations (Polish)
TRANSLATIONS = {
    'choose_format': 'Wybierz format docelowy:',
    'invalid_choice': 'Nieprawidłowy wybór.',
    'no_files': 'Brak plików do przetworzenia w folderze.',
    'done': 'Gotowe. Przekonwertowano: {converted}. Pominięto: {skipped}.',
    'remove_query': 'Czy usunąć oryginalne pliki (tak/nie)?',
    'conversion_error': 'Błąd konwersji {name}: {err}',
    'delete_failed': 'Nie udało się usunąć {name}: {err}',
}


def t(key, **kwargs):
    return TRANSLATIONS.get(key, key).format(**kwargs)


def get_terminal_width():
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except:
        return 80


def print_centered_line(content, width, border_color=CYAN, text_color=RESET, margin=""):
    padding = width - 2 - len(content)
    left_pad = padding // 2
    right_pad = padding - left_pad
    print(f"{margin}{border_color}║{RESET}{' ' * left_pad}{text_color}{content}{RESET}{' ' * right_pad}{border_color}║{RESET}")


def print_border_top(width, color=CYAN, margin=""):
    print(f"{margin}{color}╔{'═' * (width - 2)}╗{RESET}")


def print_border_bottom(width, color=CYAN, margin=""):
    print(f"{margin}{color}╚{'═' * (width - 2)}╝{RESET}")


def choose_format():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    term_width = get_terminal_width()
    try:
        _, term_height = shutil.get_terminal_size()
    except:
        term_height = 24
    
    width = 50
    left_margin = (term_width - width) // 2
    margin = " " * left_margin
    
    # Calculate vertical centering
    box_height = 2 + 1 + len(SUPPORTED) + 1  # top + title + options + bottom
    top_margin = max(0, (term_height - box_height) // 2)
    
    print("\n" * top_margin)
    print_border_top(width, CYAN, margin)
    print_centered_line(t('choose_format'), width, CYAN, GREEN, margin)
    print(f"{margin}{CYAN}╠{'═' * (width - 2)}╣{RESET}")
    
    for i, fmt in enumerate(SUPPORTED, start=1):
        opt = f"{i}. {fmt.upper()}"
        print_centered_line(opt, width, CYAN, WHITE, margin)
    
    print_border_bottom(width, CYAN, margin)
    
    print(f"\n{margin}Selection: ", end='')
    choice = input().strip().lower()
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(SUPPORTED):
            return SUPPORTED[idx]
    if choice in SUPPORTED:
        return choice
    
    print(f"{margin}{RED}{t('invalid_choice')}{RESET}")
    return None


def convert_file(path: Path, target_ext: str) -> bool:
    try:
        with Image.open(path) as img:
            if path.suffix.lower() == f'.{target_ext}':
                return False
            
            target_path = path.with_suffix(f'.{target_ext}')
            
            if target_ext in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            
            save_params = {}
            fmt = target_ext.upper()
            if fmt == 'JPG':
                fmt = 'JPEG'
            if fmt == 'WEBP':
                save_params['quality'] = 90
            
            img.save(target_path, fmt, **save_params)
            return True
    except Exception as e:
        term_width = get_terminal_width()
        margin = " " * ((term_width - 50) // 2)
        print(f"{margin}{RED}{t('conversion_error', name=path.name, err=e)}{RESET}")
        return False


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("")  # Enable ANSI
    
    target = None
    while target is None:
        target = choose_format()
    
    folder = Path(__file__).resolve().parent
    files = [p for p in folder.iterdir() if p.is_file() and p.name != Path(__file__).name]
    
    if not files:
        term_width = get_terminal_width()
        margin = " " * ((term_width - 50) // 2)
        print(f"\n{margin}{YELLOW}{t('no_files')}{RESET}\n")
        return
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    converted = 0
    skipped = 0
    
    term_width = get_terminal_width()
    try:
        _, term_height = shutil.get_terminal_size()
    except:
        term_height = 24
    
    width = 50
    left_margin = (term_width - width) // 2
    margin = " " * left_margin
    
    # Show processing message centered
    box_height = 3
    top_margin = max(0, (term_height - box_height) // 2)
    print("\n" * top_margin)
    print_border_top(width, CYAN, margin)
    print_centered_line(YELLOW + "Processing..." + RESET, width, CYAN, RESET, margin)
    print_border_bottom(width, CYAN, margin)
    
    for f in files:
        try:
            with Image.open(f):
                pass
        except Exception:
            skipped += 1
            continue
        
        if convert_file(f, target):
            converted += 1
        else:
            skipped += 1
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    term_width = get_terminal_width()
    try:
        _, term_height = shutil.get_terminal_size()
    except:
        term_height = 24
    
    width = 50
    left_margin = (term_width - width) // 2
    margin = " " * left_margin
    
    # Calculate vertical centering for results
    box_height = 5
    top_margin = max(0, (term_height - box_height) // 2)
    
    print("\n" * top_margin)
    print_border_top(width, CYAN, margin)
    print_centered_line(t('done', converted=converted, skipped=skipped), width, CYAN, PURPLE, margin)
    print_border_bottom(width, CYAN, margin)
    
    print(f"\n{margin}{BLUE}{t('remove_query')} {RESET}", end='')
    ans = input().strip().lower()
    
    if ans in ('tak', 't', 'y', 'yes'):
        deleted = 0
        for f in files:
            if f.suffix.lower() == f'.{target}':
                continue
            try:
                newf = f.with_suffix(f'.{target}')
                if newf.exists():
                    f.unlink()
                    deleted += 1
            except Exception as e:
                print(f"{RED}{t('delete_failed', name=f.name, err=e)}{RESET}")
        print(f"\n{margin}{GREEN}Usunięto {deleted} oryginalnych plików.{RESET}\n")


if __name__ == "__main__":
    main()
