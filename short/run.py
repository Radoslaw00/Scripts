#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from PIL import Image

TARGET_FORMAT = "webp"

def convert_to_webp():
    """Convert all images to WebP."""
    folder = Path.cwd()
    for f in folder.iterdir():
        if f.is_file() and f.name not in ("run.py", "Sort_folder_filetypes.py", "p.py", "x.bat", ".sort_backup.json"):
            try:
                with Image.open(f) as img:
                    if f.suffix.lower() != f'.{TARGET_FORMAT}':
                        target_path = f.with_suffix(f'.{TARGET_FORMAT}')
                        if img.mode in ("RGBA", "LA", "P"):
                            img = img.convert("RGB")
                        img.save(target_path, "WEBP", quality=90)
            except Exception:
                pass

def sort_by_extension():
    """Sort all files into folders by extension."""
    folder = Path.cwd()
    for f in folder.iterdir():
        if f.is_file() and f.name not in ("run.py", "Sort_folder_filetypes.py", "p.py", "x.bat", ".sort_backup.json"):
            ext = f.suffix.lstrip('.').upper() or "NO_EXTENSION"
            ext_dir = folder / ext
            ext_dir.mkdir(exist_ok=True)
            shutil.move(str(f), str(ext_dir / f.name))

if __name__ == '__main__':
    convert_to_webp()
    sort_by_extension()
