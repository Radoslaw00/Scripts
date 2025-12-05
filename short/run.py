#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from PIL import Image
import subprocess

TARGET_FORMAT = "webp"
RESIZE_WIDTH = 1000
SKIP_FILES = {"run.py", "Sort_folder_filetypes.py", "p.py", "x.bat", ".sort_backup.json", "readme.md"}

def convert_to_webp():
    """Convert all images to WebP."""
    folder = Path.cwd()
    for f in folder.iterdir():
        if f.is_file() and f.name not in SKIP_FILES:
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
        if f.is_file() and f.name not in SKIP_FILES:
            ext = f.suffix.lstrip('.').upper() or "NO_EXTENSION"
            ext_dir = folder / ext
            ext_dir.mkdir(exist_ok=True)
            shutil.move(str(f), str(ext_dir / f.name))

def get_best_dimension(width, height):
    """Pick the bigger dimension and return (bigger, smaller) for best orientation."""
    if width > height:
        return (width, height)
    else:
        return (height, width)

def resize_images():
    """Resize all images in extension folders, keeping originals."""
    folder = Path.cwd()
    for ext_dir in folder.iterdir():
        if not ext_dir.is_dir() or ext_dir.name in SKIP_FILES:
            continue
        
        resized_dir = ext_dir / "RESIZED"
        resized_count = 0
        
        for f in ext_dir.iterdir():
            if not f.is_file():
                continue
            
            try:
                with Image.open(f) as img:
                    width, height = img.size
                    bigger_dim, smaller_dim = get_best_dimension(width, height)
                    
                    # Calculate new dimensions maintaining aspect ratio
                    if bigger_dim > RESIZE_WIDTH:
                        ratio = RESIZE_WIDTH / bigger_dim
                        new_width = RESIZE_WIDTH if width > height else int(smaller_dim * ratio)
                        new_height = int(smaller_dim * ratio) if width > height else RESIZE_WIDTH
                        
                        # Create RESIZED folder on first resize
                        if resized_count == 0:
                            resized_dir.mkdir(exist_ok=True)
                        
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        resized_path = resized_dir / f.name
                        
                        if f.suffix.lower() == '.webp':
                            resized_img.save(resized_path, "WEBP", quality=90)
                        else:
                            resized_img.save(resized_path)
                        
                        resized_count += 1
            except Exception:
                pass

def optimize_images():
    """Optimize resized images to reduce file size."""
    folder = Path.cwd()
    for ext_dir in folder.iterdir():
        if not ext_dir.is_dir() or ext_dir.name in SKIP_FILES:
            continue
        
        resized_dir = ext_dir / "RESIZED"
        if not resized_dir.exists():
            continue
        
        optimized_dir = resized_dir / "OPTIMIZED"
        optimized_dir.mkdir(exist_ok=True)
        
        for f in resized_dir.glob("*"):
            if f.is_dir():
                continue
            
            try:
                with Image.open(f) as img:
                    optimized_path = optimized_dir / f.name
                    
                    if f.suffix.lower() == '.webp':
                        img.save(optimized_path, "WEBP", quality=75, method=6)
                    else:
                        img.save(optimized_path, optimize=True)
            except Exception:
                pass

def create_shortcut():
    """Create Windows shortcut to OPTIMIZED folders."""
    folder = Path.cwd()
    vbs_script = folder / "create_link.vbs"
    
    for ext_dir in folder.iterdir():
        if not ext_dir.is_dir() or ext_dir.name in SKIP_FILES:
            continue
        
        optimized_dir = ext_dir / "RESIZED" / "OPTIMIZED"
        if not optimized_dir.exists():
            continue
        
        link_path = folder / f"OPTIMIZED & RESIZED ({ext_dir.name}).lnk"
        
        vbs_content = f'''Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{link_path}")
oLink.TargetPath = "{optimized_dir}"
oLink.Save
'''
        
        vbs_script.write_text(vbs_content)
        subprocess.run([str(vbs_script)], shell=True, capture_output=True)
    
    vbs_script.unlink(missing_ok=True)

if __name__ == '__main__':
    convert_to_webp()
    sort_by_extension()
    resize_images()
    optimize_images()
    create_shortcut()
