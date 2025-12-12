#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from PIL import Image
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

TARGET_FORMAT = "webp"
RESIZE_WIDTH = 1000
SKIP_FILES = {"run.py", "run_fast.py", "x.bat", "x_fast.bat", ".sort_backup.json", "readme.md"}
MAX_WORKERS = 8

# Image extensions for fast processing
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

def is_image_file(path):
    """Fast image file check."""
    return path.suffix.lower() in IMAGE_EXTENSIONS

def convert_to_webp_worker(file_path):
    """Worker function for parallel WebP conversion."""
    try:
        if file_path.suffix.lower() == '.webp':
            return None
        
        with Image.open(file_path) as img:
            target_path = file_path.with_suffix('.webp')
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            img.save(target_path, "WEBP", quality=90, method=6)
            return target_path
    except Exception:
        return None

def convert_to_format_worker(file_path, target_fmt):
    """Worker function for parallel format conversion."""
    try:
        if file_path.suffix.lower() == f'.{target_fmt}':
            return None
        
        with Image.open(file_path) as img:
            target_path = file_path.with_suffix(f'.{target_fmt}')
            
            if target_fmt in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            
            save_params = {}
            fmt_upper = target_fmt.upper()
            if fmt_upper == "JPG":
                fmt_upper = "JPEG"
            
            if fmt_upper == "JPEG":
                save_params['quality'] = 90
            elif fmt_upper == "PNG":
                save_params['optimize'] = True
            
            img.save(target_path, fmt_upper, **save_params)
            return target_path
    except Exception:
        return None

def convert_to_webp():
    """Convert all images to WebP."""
    print("Converting to WebP...")
    folder = Path.cwd()
    files_to_process = [f for f in folder.iterdir() 
                       if f.is_file() and f.name not in SKIP_FILES and is_image_file(f)]
    
    if not files_to_process:
        print("  No images found")
        return
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(convert_to_webp_worker, f): f for f in files_to_process}
        converted = 0
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"  ✓ Converted: {futures[future].name} → {result.name}")
                converted += 1
        if converted > 0:
            print(f"  Total: {converted} files converted to WebP")

def convert_to_png_jpg():
    """Convert images to PNG and JPG."""
    folder = Path.cwd()
    
    for fmt in ["png", "jpg"]:
        print(f"Converting to {fmt.upper()}...")
        files_to_process = [f for f in folder.iterdir() 
                           if f.is_file() and f.name not in SKIP_FILES and is_image_file(f)]
        
        if not files_to_process:
            print(f"  No images found")
            continue
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(convert_to_format_worker, f, fmt): f for f in files_to_process}
            converted = 0
            for future in as_completed(futures):
                result = future.result()
                if result:
                    print(f"  ✓ Converted: {futures[future].name} → {result.name}")
                    converted += 1
            if converted > 0:
                print(f"  Total: {converted} files converted to {fmt.upper()}")

def sort_by_extension():
    """Sort files by extension."""
    print("Sorting by extension...")
    folder = Path.cwd()
    
    files_by_ext = {}
    for f in folder.iterdir():
        if f.is_file() and f.name not in SKIP_FILES:
            ext = f.suffix.lstrip('.').upper() or "NO_EXTENSION"
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(f)
    
    if not files_by_ext:
        print("  No files to sort")
        return
    
    for ext, files in files_by_ext.items():
        ext_dir = folder / ext
        ext_dir.mkdir(exist_ok=True)
        
        for f in files:
            try:
                dest = ext_dir / f.name
                shutil.move(str(f), str(dest))
                print(f"  ✓ Moved: {f.name} → {ext}/")
            except Exception as e:
                print(f"  ✗ Failed: {f.name} ({e})")

def resize_image_worker(args):
    """Worker function for parallel image resizing."""
    f, resized_dir = args
    try:
        with Image.open(f) as img:
            width, height = img.size
            bigger_dim = max(width, height)
            
            if bigger_dim > RESIZE_WIDTH:
                ratio = RESIZE_WIDTH / bigger_dim
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_dir.mkdir(exist_ok=True, parents=True)
                
                resized_path = resized_dir / f.name
                if f.suffix.lower() == '.webp':
                    resized_img.save(resized_path, "WEBP", quality=90, method=6)
                else:
                    resized_img.save(resized_path)
                
                return resized_path
    except Exception:
        pass
    return None

def resize_images():
    """Resize images in extension folders."""
    print("Resizing images...")
    folder = Path.cwd()
    
    tasks = []
    for ext_dir in folder.iterdir():
        if not ext_dir.is_dir() or ext_dir.name in SKIP_FILES:
            continue
        
        resized_dir = ext_dir / "RESIZED"
        
        for f in ext_dir.iterdir():
            if f.is_file() and is_image_file(f):
                tasks.append((f, resized_dir))
    
    if not tasks:
        print("  No images to resize")
        return
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(resize_image_worker, task): task for task in tasks}
        resized = 0
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"  ✓ Resized: {futures[future][0].name} → {result.name}")
                resized += 1
        if resized > 0:
            print(f"  Total: {resized} images resized")

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
    """Optimize resized images."""
    print("Optimizing images...")
    folder = Path.cwd()
    
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
    
    if not tasks:
        print("  No resized images to optimize")
        return
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(optimize_image_worker, task): task for task in tasks}
        optimized = 0
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"  ✓ Optimized: {futures[future][0].name}")
                optimized += 1
        if optimized > 0:
            print(f"  Total: {optimized} images optimized")

def create_shortcut():
    """Create shortcuts to OPTIMIZED folders."""
    print("Creating shortcuts...")
    folder = Path.cwd()
    vbs_script = folder / "create_link_fast.vbs"
    
    shortcuts = []
    for ext_dir in folder.iterdir():
        if not ext_dir.is_dir() or ext_dir.name in SKIP_FILES:
            continue
        
        optimized_dir = ext_dir / "RESIZED" / "OPTIMIZED"
        if not optimized_dir.exists():
            continue
        
        link_path = folder / f"OPTIMIZED & RESIZED ({ext_dir.name}).lnk"
        shortcuts.append((link_path, optimized_dir))
    
    if not shortcuts:
        print("  No optimized folders found")
        return
    
    vbs_content = ""
    for link_path, optimized_dir in shortcuts:
        vbs_content += f'''Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{link_path}")
oLink.TargetPath = "{optimized_dir}"
oLink.Save
'''
    
    try:
        vbs_script.write_text(vbs_content)
        subprocess.run([str(vbs_script)], shell=True, capture_output=True)
        for link_path, _ in shortcuts:
            print(f"  ✓ Created: {link_path.name}")
    except Exception as e:
        print(f"  ✗ Error creating shortcuts: {e}")
    finally:
        vbs_script.unlink(missing_ok=True)

if __name__ == '__main__':
    print("=======================================")
    print("Fast Image Processor (JPG/PNG/WebP)")
    print("=======================================\n")
    
    start_time = time.time()
    
    convert_to_webp()
    convert_to_png_jpg()
    sort_by_extension()
    resize_images()
    optimize_images()
    create_shortcut()
    
    elapsed = time.time() - start_time
    print(f"\n=======================================")
    print(f"Done! ({elapsed:.2f}s)")
    print(f"=======================================")
