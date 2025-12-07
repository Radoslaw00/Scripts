#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from PIL import Image
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict
import time

TARGET_FORMAT = "webp"
OUTPUT_FORMATS = ["webp", "png", "jpg", "bmp", "tiff", "gif", "ico", "avif", "heic"]
RESIZE_WIDTH = 1000
SKIP_FILES = {"run.py", "Sort_folder_filetypes.py", "p.py", "x.bat", ".sort_backup.json", "readme.md", "run.c", "run.exe"}
MAX_WORKERS = 8  # Parallel threads
CHUNK_SIZE = 32  # Process files in batches

# Image extensions cache
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ico', '.avif', '.heic', '.heif'}

# Thread-safe progress counter
progress_lock = threading.Lock()
processed_count = 0
total_count = 0

def is_image_file(path):
    """Fast image file check using cached extensions."""
    return path.suffix.lower() in IMAGE_EXTENSIONS

def get_files_batch(folder, condition=None):
    """Get files in batches for faster processing."""
    files = []
    for f in folder.iterdir():
        if condition is None or condition(f):
            files.append(f)
        if len(files) >= CHUNK_SIZE:
            yield files
            files = []
    if files:
        yield files

def convert_to_webp_worker(file_path):
    """Worker function for parallel WebP conversion."""
    try:
        if file_path.suffix.lower() == f'.{TARGET_FORMAT}':
            return None
        
        with Image.open(file_path) as img:
            target_path = file_path.with_suffix(f'.{TARGET_FORMAT}')
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            img.save(target_path, "WEBP", quality=90, method=6)
            return target_path
    except Exception as e:
        return None

def convert_to_format_worker(file_path, target_fmt):
    """Worker function for parallel format conversion."""
    try:
        if file_path.suffix.lower() == f'.{target_fmt}':
            return None
        
        with Image.open(file_path) as img:
            target_path = file_path.with_suffix(f'.{target_fmt}')
            
            # Handle RGBA for formats that don't support transparency
            if target_fmt in ("jpg", "jpeg", "bmp") and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            elif target_fmt == "ico" and img.mode == "RGBA":
                pass  # ICO supports RGBA
            elif img.mode == "P":
                img = img.convert("RGBA")
            
            # Format-specific quality settings
            save_params = {}
            fmt_upper = target_fmt.upper()
            if fmt_upper == "JPG":
                fmt_upper = "JPEG"
            
            if fmt_upper == "WEBP":
                save_params['quality'] = 90
                save_params['method'] = 6
            elif fmt_upper == "JPEG":
                save_params['quality'] = 90
            elif fmt_upper == "PNG":
                save_params['optimize'] = True
            elif fmt_upper == "AVIF":
                save_params['quality'] = 85
            
            img.save(target_path, fmt_upper, **save_params)
            return target_path
    except Exception as e:
        return None

def convert_to_webp():
    """Convert all images to WebP and other formats using parallel processing."""
    print("Converting images to WebP...")
    folder = Path.cwd()
    files_to_process = [f for f in folder.iterdir() 
                       if f.is_file() and f.name not in SKIP_FILES and is_image_file(f)]
    
    if not files_to_process:
        return
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(convert_to_webp_worker, f): f for f in files_to_process}
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"  Converted: {futures[future].name} -> {result.name}")

def convert_to_all_formats():
    """Convert images to all supported formats."""
    folder = Path.cwd()
    
    for fmt in OUTPUT_FORMATS:
        if fmt == "webp":
            continue  # Already done
        
        print(f"Converting to {fmt.upper()}...")
        files_to_process = [f for f in folder.iterdir() 
                           if f.is_file() and f.name not in SKIP_FILES and is_image_file(f)]
        
        if not files_to_process:
            continue
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(convert_to_format_worker, f, fmt): f for f in files_to_process}
            converted = 0
            for future in as_completed(futures):
                result = future.result()
                if result:
                    converted += 1
            if converted > 0:
                print(f"  Converted {converted} files to {fmt.upper()}")

def sort_by_extension():
    """Sort all files into folders by extension (optimized with caching)."""
    print("Sorting files by extension...")
    folder = Path.cwd()
    
    # Cache directory objects to avoid repeated creation
    ext_dirs = {}
    files_by_ext = defaultdict(list)
    
    # First pass: collect all files by extension
    for f in folder.iterdir():
        if f.is_file() and f.name not in SKIP_FILES:
            ext = f.suffix.lstrip('.').upper() or "NO_EXTENSION"
            files_by_ext[ext].append(f)
    
    # Second pass: create directories and move files in batches
    for ext, files in files_by_ext.items():
        ext_dir = folder / ext
        ext_dir.mkdir(exist_ok=True)
        
        for f in files:
            try:
                dst = ext_dir / f.name
                shutil.move(str(f), str(dst))
                print(f"  Moved: {f.name} -> {ext}")
            except Exception:
                pass

def resize_image_worker(args):
    """Worker function for parallel image resizing."""
    f, resized_dir = args
    try:
        with Image.open(f) as img:
            width, height = img.size
            bigger_dim = max(width, height)
            smaller_dim = min(width, height)
            
            if bigger_dim > RESIZE_WIDTH:
                ratio = RESIZE_WIDTH / bigger_dim
                new_width = RESIZE_WIDTH if width > height else int(smaller_dim * ratio)
                new_height = int(smaller_dim * ratio) if width > height else RESIZE_WIDTH
                
                resized_dir.mkdir(exist_ok=True, parents=True)
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_path = resized_dir / f.name
                
                if f.suffix.lower() == '.webp':
                    resized_img.save(resized_path, "WEBP", quality=90, method=6)
                else:
                    resized_img.save(resized_path, optimize=True, quality=90)
                
                return resized_path
    except Exception:
        pass
    return None

def resize_images():
    """Resize all images in extension folders using parallel processing."""
    print("Resizing images...")
    folder = Path.cwd()
    
    # Collect all resize tasks
    tasks = []
    for ext_dir in folder.iterdir():
        if not ext_dir.is_dir() or ext_dir.name in SKIP_FILES:
            continue
        
        resized_dir = ext_dir / "RESIZED"
        
        for f in ext_dir.iterdir():
            if f.is_file() and is_image_file(f):
                tasks.append((f, resized_dir))
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(resize_image_worker, task): task for task in tasks}
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"  Resized: {result.name}")

def optimize_image_worker(args):
    """Worker function for parallel image optimization."""
    f, optimized_dir = args
    try:
        with Image.open(f) as img:
            optimized_path = optimized_dir / f.name
            optimized_dir.mkdir(exist_ok=True, parents=True)
            
            if f.suffix.lower() == '.webp':
                img.save(optimized_path, "WEBP", quality=75, method=6)
            else:
                img.save(optimized_path, optimize=True, quality=75)
            
            return optimized_path
    except Exception:
        pass
    return None

def optimize_images():
    """Optimize resized images using parallel processing."""
    print("Optimizing images...")
    folder = Path.cwd()
    
    # Collect all optimization tasks
    tasks = []
    for ext_dir in folder.iterdir():
        if not ext_dir.is_dir() or ext_dir.name in SKIP_FILES:
            continue
        
        resized_dir = ext_dir / "RESIZED"
        if not resized_dir.exists():
            continue
        
        optimized_dir = resized_dir / "OPTIMIZED"
        
        for f in resized_dir.iterdir():
            if f.is_file() and is_image_file(f):
                tasks.append((f, optimized_dir))
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(optimize_image_worker, task): task for task in tasks}
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"  Optimized: {result.name}")

def create_shortcut():
    """Create Windows shortcut to OPTIMIZED folders (batch processing)."""
    print("Creating shortcuts...")
    folder = Path.cwd()
    vbs_script = folder / "create_link.vbs"
    
    shortcuts = []
    for ext_dir in folder.iterdir():
        if not ext_dir.is_dir() or ext_dir.name in SKIP_FILES:
            continue
        
        optimized_dir = ext_dir / "RESIZED" / "OPTIMIZED"
        if not optimized_dir.exists():
            continue
        
        link_path = folder / f"OPTIMIZED & RESIZED ({ext_dir.name}).lnk"
        shortcuts.append((link_path, optimized_dir))
    
    # Create all shortcuts in one batch
    if shortcuts:
        vbs_content = ""
        for link_path, optimized_dir in shortcuts:
            vbs_content += f'''Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{link_path}")
oLink.TargetPath = "{optimized_dir}"
oLink.Save
'''
        
        vbs_script.write_text(vbs_content)
        subprocess.run([str(vbs_script)], shell=True, capture_output=True)
        
        for link_path, _ in shortcuts:
            print(f"  Created shortcut: {link_path.name}")
    
    vbs_script.unlink(missing_ok=True)

if __name__ == '__main__':
    print("========================================")
    print("Image Organization & Processing Tool")
    print("========================================\n")
    
    start_time = time.time()
    
    convert_to_webp()
    convert_to_all_formats()
    sort_by_extension()
    resize_images()
    optimize_images()
    create_shortcut()
    
    elapsed = time.time() - start_time
    print(f"\n========================================")
    print(f"Process Complete! ({elapsed:.2f}s)")
    print(f"========================================")

